from typing import Optional
from cachetools import TTLCache
from fastapi import APIRouter, Body, Depends, exceptions
from pydantic import BaseModel
from gemini import GenModel
import json
from firebase_admin import firestore

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

# Dependency to get the Firestore client
def get_db():
    return firestore.client()

@router.post("/gemini")
async def callgemini(isEnroll: bool = True,
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
                     isReturn: bool = True,
                     db: firestore.Client = Depends(get_db)):
    
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
    
    # data_json = json.dumps(og_checklist)
    return {"message": "Document added successfully"}


    # cache = await get_cache()
    # cache["calculated_data"] = og_checklist
    # print(cache.get("calculated_data"))
    # output = model.generate_actual_checklist(og_checklist, school)

    return og_checklist
