from typing import Optional
from fastapi import APIRouter, Body, Depends
from api.preprocess_func import preprocess
from gemini import GenModel
from pydantic import BaseModel
from firebase_admin import firestore
# from db_utils import get_connection
import json

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

# Dependency to get the Firestore client
def get_db():
    return firestore.client()

@router.post("/checklist")
async def checklist(data: dict = Body(...), db: firestore.Client = Depends(get_db)):
  """
  This route handler receives a JSON payload and returns it as a string.
  """
  finalInputData = preprocess(data)
  # json_string = json.dumps(data)
  # print(json_string)
  # print("------------> TRANSFORMED")
  # print(finalInputData)
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
    # data_list = json.loads(og_checklist)
    # print(type(og_checklist))
    # for item in og_checklist:
        # print(item)
        # print(type(item))
        # item = json.loads(item)
        # print(type(item))
    doc_ref = collection_ref.document()
    checklist_data = {"checklist": og_checklist}
    checklist_data["createdAt"] = firestore.SERVER_TIMESTAMP
    
    doc_ref.set(checklist_data)
    print(f"added with id: {doc_ref.id}")
    print("done!")
    return {"message": "Document added successfully"}
    # insert_stmt = "INSERT INTO checklist_table (value) VALUES (?)"
    # data_json = json.dumps(og_checklist)
    # cursor.execute(insert_stmt, (data_json, ))
    # conn.commit()

    # cache = await get_cache()
    # cache["calculated_data"] = og_checklist
    # print(cache.get("calculated_data"))
    # output = model.generate_actual_checklist(og_checklist, school)

    # return og_checklist
