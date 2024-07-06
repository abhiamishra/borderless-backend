from cachetools import TTLCache
from fastapi import APIRouter, Body, Depends
from app.gemini import GenModel
import json
from db_utils import get_connection

model = GenModel()
router = APIRouter()
conn = get_connection()
cursor = conn.cursor()

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

    insert_stmt = "INSERT INTO checklist_table (value) VALUES (?)"
    data_json = json.dumps(og_checklist)
    cursor.execute(insert_stmt, (data_json, ))
    conn.commit()
    conn.close()

    # cache = await get_cache()
    # cache["calculated_data"] = og_checklist
    # print(cache.get("calculated_data"))
    # output = model.generate_actual_checklist(og_checklist, school)

    return og_checklist
