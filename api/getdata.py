from fastapi import APIRouter, Body, Depends
from gemini import GenModel
import sqlite3
from firebase_admin import firestore
import json

model = GenModel()
router = APIRouter()
# conn = get_connection()
# cursor = conn.cursor()

# Dependency to get the Firestore client
def get_db():
    return firestore.client()

@router.get("/data")
async def get_data(db: firestore.Client = Depends(get_db)):
  collection_ref = db.collection("checklist-test")
  query = collection_ref.order_by("createdAt", direction=firestore.Query.DESCENDING).limit(1)
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
#   cached_data = cache.get("calculated_data")

  # if cached_data:
  #   return cached_data
  # else:
  #   return [{"Task": "No data found in cache", "Priority": 1, "Description": "N/A"}]