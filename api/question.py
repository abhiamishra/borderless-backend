import asyncio
import aiohttp
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth
from firebase_admin import firestore
from gemini import GenModel
from googlesearch import search
import asyncpraw
import os
from dotenv import load_dotenv

# Get the current working directory (cwd)
env_file_path = "../.env"
load_dotenv(dotenv_path=env_file_path)

model = GenModel()
router = APIRouter()
security = HTTPBearer()

# Global aiohttp ClientSession
client_session = None

@router.on_event("startup")
async def startup_event():
    global client_session
    client_session = aiohttp.ClientSession()

@router.on_event("shutdown")
async def shutdown_event():
    global client_session
    if client_session:
        await client_session.close()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
# Dependency to get the Firestore client
def get_db():
    return firestore.client()

async def fetch_reddit_content(reddit, url):
    try:
        submission = await reddit.submission(url=url)
        await submission.comments.replace_more(limit=0)
        top_comments = sorted(submission.comments, key=lambda comment: comment.score, reverse=True)[:5]
        doc = ""
        if submission.selftext:
            doc += f"Linked URL: {submission.url}\n\n\n"
            doc += f"Question : {submission.title}\n"
            doc += f"Context: {submission.selftext}\n"
            
            all_top_level_comments = "\n\n".join([comment.body for comment in top_comments])
            doc += f"Answer: {all_top_level_comments}"
        
        return doc
    except Exception as e:
        print(f"Error processing submission: {str(e)}")
        return None

import aiohttp
import asyncio

async def search_with_cse(query, api_key, cse_id, num_links=3):
    """
    Makes an asynchronous Google Custom Search API request and returns the top `num_links` results.

    Args:
    query: The search query string.
    api_key: Your Google Custom Search API key.
    cse_id: Your Custom Search Engine ID.
    num_links: The number of top links to return (default: 3).

    Returns:
    A list containing the top `num_links` search results or an error message.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": query
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return f"Error: HTTP {response.status}"
                
                results = await response.json()
                links = [item["link"] for item in results.get("items", [])][:num_links]
                return links
    except aiohttp.ClientError as e:
        return f"Error: {e}"

@router.post("/question")
async def get_answer(data: dict = Body(...),
                     db: firestore.Client = Depends(get_db),
                   current_user: dict = Depends(get_current_user)):
    question = data["question"]
    query = f"{question} immigration reddit"
    print(query)
    api_key = os.getenv("GOOGLE_SEARCH_KEY")
    cse_id = os.getenv("GOOGLE_SEARCH_ID")
    # listUrls = list(search(query, num=20, stop=3))
    listUrls = await search_with_cse(query, api_key, cse_id, num_links=3)
    print(listUrls)

    print(env_file_path)
    user_agt = os.environ.get("USR_AGT")
    # print(user_agt)

    reddit = asyncpraw.Reddit(
        client_id=os.getenv("PRAW_CID"),
        client_secret=os.getenv("PRAW_CID_SECRET"),
        user_agent=user_agt
    )

    doc_list = await asyncio.gather(*[fetch_reddit_content(reddit, url) for url in listUrls])
    doc_list = [doc for doc in doc_list if doc]
        
    print("doc retrieval done")
    print(len(doc_list))
    if len(doc_list) == 0:
        return "Query too complex. Try breaking it down and asking it!"
    
    combined_doc_string = "\n\n--NEXT DOCUMENT--\n\n".join(doc_list)

    # print("generating:")
    result = model.generate_answer(question, combined_doc_string)
    # print(result)
    return result