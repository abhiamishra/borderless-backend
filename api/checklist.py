from typing import Optional
from fastapi import APIRouter, Body, Depends, HTTPException
from api.preprocess_func import preprocess
from gemini import GenModel
from pydantic import BaseModel
from firebase_admin import firestore
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth

# from db_utils import get_connection

class ChecklistItem(BaseModel):
    isEnroll: bool = True
    school: Optional[str] = None
    major: Optional[str] = None
    degreeLevel: Optional[str] = None
    startDate: Optional[str] = None
    isenrollAlt: bool = True
    nameAlt: Optional[str] = None
    isfullTime: bool = True
    englishLevel: Optional[str] = None
    isTOEFL: bool = True
    TOEFLScore: Optional[str] = None
    isEnrollEnglishCourse: bool = True
    isResidence: bool = True
    isFamily: bool = True
    isEmployed: bool = True
    hasAssets: bool = True
    isReturn: bool = True
    
model = GenModel()
router = APIRouter()
# conn = get_connection()
# cursor = conn.cursor()

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

@router.post("/insert-user")
async def insert_user(data: dict = Body(...), 
                    db: firestore.Client = Depends(get_db),
                    current_user: dict = Depends(get_current_user)):
    user_id =  current_user["uid"]
    email = current_user["email"]
    print(email)

    collection_ref =  db.collection("checklist-test")

    query = collection_ref.where("email", "==",  email).limit(1)
    print(query.get())
    query_snapshot = query.get()

    if len(query_snapshot) == 0:
        doc_ref = collection_ref.document()
        checklist_data = {"email":email}
        checklist_data["createdAt"] = firestore.SERVER_TIMESTAMP
        doc_ref.set(checklist_data)
        print(f"added with id: {doc_ref.id}")
        print("done!")
        return {"message": "Users added successfully"}
    else:
        print("alr added lol!")
        return {"message": "Users alr existed successfully"} 

@router.post("/checklist")
def checklist(data: dict = Body(...), 
                    db: firestore.Client = Depends(get_db)):
  """
  This route handler receives a JSON payload and returns it as a string.
  """
  finalInputData = preprocess(data)
  # json_string = json.dumps(data)
  print(data)
  print("------------> TRANSFORMED")
  print(finalInputData)
  output = call_internalgemini(
      db,
    isEnroll=finalInputData["isEnroll"],
    school=finalInputData["school"],
    major = finalInputData["major"],
    degreeLevel= finalInputData["degreeLevel"],
    startDate = finalInputData["startDate"],
    isenrollAlt=finalInputData["isenrollAlt"],
    nameAlt = finalInputData["nameAlt"],
    isfullTime = finalInputData["isfullTime"],
    englishLevel = finalInputData["englishLevel"],
    isTOEFL = finalInputData["isTOEFL"],
    TOEFLScore = finalInputData["TOEFLScore"],
    isEnrollEnglishCourse = finalInputData["isEnrollEnglishCourse"],
    isResidence = finalInputData["isResidence"],
    isFamily = finalInputData["isFamily"],
    isEmployed = finalInputData["isEmployed"],
    hasAssets = finalInputData["hasAssets"],
    isReturn = finalInputData["isReturn"]
  )

  return output

  
def call_internalgemini(
                    db: firestore.Client,
                    isEnroll: bool = True,
                     school: str = None,
                     major: str = None,
                     degreeLevel: str = None,
                     startDate: str = None,
                     isenrollAlt: bool = True,
                     nameAlt: str = None,
                     isfullTime: bool = True,
                     englishLevel: str = None,
                     isTOEFL: bool = True,
                     TOEFLScore: str = None,
                     isEnrollEnglishCourse: bool = True,
                     isResidence: bool = True,
                     isFamily: bool = True,
                     isEmployed: bool = True,
                     hasAssets: bool = True,
                     isReturn: bool = True):
    
    og_checklist = model.generate_base_checklist(
        isEnroll,
        school,
        major,
        degreeLevel,
        startDate,
        isenrollAlt,
        nameAlt,
        isfullTime,
        englishLevel,
        isTOEFL,
        TOEFLScore,
        isEnrollEnglishCourse,
        isResidence,
        isFamily,
        isEmployed,
        hasAssets,
        isReturn
    )
    collection_ref = db.collection("checklist-test")
    
    query = collection_ref.order_by("createdAt", direction=firestore.Query.DESCENDING).limit(1)
    query_snapshot = query.get()

    if len(query_snapshot) == 0:
      print("No documents found!")
      return False
    last_doc = query_snapshot[0]
    last_doc_ref = collection_ref.document(last_doc.id)
    
    # last_doc = last_doc.to_dict()

    last_doc_ref.update({"checklist": og_checklist})
    last_doc_ref.update({"createdAt": firestore.SERVER_TIMESTAMP})

    print("done!")
    return {"message": "Document added successfully"}