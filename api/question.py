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



@router.post("/question")
async def get_answer(data: dict = Body(...),
                     db: firestore.Client = Depends(get_db),
                   current_user: dict = Depends(get_current_user)):
    question = data["question"]
    query = f"{question} immigration reddit"
    listUrls = list(search(query, num=20, stop=5))

    print(env_file_path)
    user_agt = os.environ.get("USR_AGT")
    # print(user_agt)

    reddit = asyncpraw.Reddit(
        client_id=os.getenv("PRAW_CID"),
        client_secret=os.getenv("PRAW_CID_SECRET"),
        user_agent=user_agt
    )

    doc_list =[]
    for url in listUrls:
        try:
            submission = await reddit.submission(url=url)
        except:
            print("Not valid URL")
        
        try:
            doc = ""
            # Check if it's a link-post (no selftext)
            if submission.selftext:
                doc += f"Linked URL: {submission.url}"
                doc += "\n\n\n"
                doc += f"Question : {submission.title}"
                doc += "\n"
                doc += f"Context: {submission.selftext}"
                doc += "\n"

                # print("This is a link-post:")
                # print(f"Linked URL: {submission.url}")
                # print(f"Title of the linked content: {submission.title}")
                # print(f"Content: {submission.selftext}")
                # # Combine all top-level comments into a single string
                # Combine all top-level comments into a single string
                # print("Onto Comments!")
                await submission.comments.replace_more(limit=0)

                top_comments = sorted(submission.comments, key=lambda comment: comment.score, reverse=True)[:5]

                all_top_level_comments = ""
                for comment in top_comments:
                    all_top_level_comments += comment.body + "\n\n"
                all_top_level_comments = all_top_level_comments.strip()
                # print(all_top_level_comments) 
                
                doc += f"Answer: {all_top_level_comments}"
            
            doc_list.append(doc)
        except:
            print("Error in processing comments!")
        
    print("doc retrieval done")
    if len(doc_list) == 0:
        return "Query too complex. Try breaking it down and asking it!"
    
    combined_doc_string = "\n\n--NEXT DOCUMENT--\n\n".join(doc_list)

    # print("generating:")
    result = model.generate_answer(question, combined_doc_string)
    # print(result)
    return result