from fastapi import APIRouter, HTTPException, Depends
from gemini import GenModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth
from firebase_admin import firestore

model = GenModel()
router = APIRouter()
# conn = get_connection()
# cursor = conn.cursor()
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


@router.get("/datauser")
async def get_data(db: firestore.Client = Depends(get_db),
                   current_user: dict = Depends(get_current_user)):
  print("here!")
  email = current_user["email"]
  collection_ref = db.collection("checklist-test")
  query = collection_ref.where("email", "==",  email).limit(1)
  try:
      docs = query.get()
      if docs:
          last_doc  = docs[0]
          print(f"Last added document ID: {last_doc .id}")
          print(f"Last added data: {last_doc .to_dict()}")  # Access data fields
      else:
          print("No documents found in the collection.")
  except Exception as e:
      print(f"Error getting last document: {e}")
  
  if last_doc:
      checklist_data = last_doc.to_dict()["checklist"]
      return checklist_data