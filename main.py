from fastapi import FastAPI, Depends, Body
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import JSONResponse
from cachetools import TTLCache

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()
import google.generativeai as genai

from gemini import GenModel

model = GenModel()

app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cache = TTLCache(maxsize=100, ttl=600)
# creds = credentials.Certificate("./borderless-asmr-firebase-adminsdk.json")

# Initialize the app with a None auth variable, limiting the server's access
# firebase_admin.initialize_app(creds)
# db = firestore.client()

# # The app only has access to public data as defined in the Security Rules
# # ref = db.reference('/test')
# collection = db.collection('test').document('MYfL7vSJPmzYCPO6U9HX')
# data = collection.get().to_dict()
# print(data)
# print(ref.get())
# print(default_app)
import json

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/echo-json")
async def echo_json_data(data: dict = Body(...)):
  """
  This route handler receives a JSON payload and returns it as a string.
  """
  # Convert dictionary back to JSON string (optional)
  print(data)
  print(type(data))
  print(data.keys())
  fieldsLst = data["data"]["fields"]
  inputDataJSON = {
    0:"isEnroll",
    1:"school",
    2:"major",
    3:"degreeLevel",
    4:"startDate",
    5:"isenrollAlt",
    6:"nameAlt",
    7:"isfullTime",
    8:"englishLevel",
    9:"isTOEFL",
    10:"TOEFLScore",
    11:"isEnrollEnglishCourse",
    12:"isResidence",
    13:"isFamily",
    14:"isEmployed",
    15:"hasAssets",
    16:"isReturn"}

  inputValueLst = []
  for field in fieldsLst[1:]:
    value = ""
    if "options" in field.keys():
       valueKey = field["value"][0]
       for option in field["options"]:
          if option["id"] == valueKey:
            value = option["text"]
    elif field["value"] is not None:
       value = field["value"]
       if value == 'Yes':
          value = True
       elif value == 'No':
          value = False
    else:
       value = -1
    
    inputValueLst.append(value)

  finalInputData = {}

  for idx, val in enumerate(inputValueLst):
    key = inputDataJSON[idx]
    if val == -1:
       finalInputData[key] = None
    else:
        finalInputData[key] = val

  json_string = json.dumps(data)

  print(json_string)
  print("------------> TRANSFORMED")
  print(finalInputData)

  call_internalgemini(
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


  return json_string  # Or return the original dictionary (data)

def call_internalgemini(isEnroll: bool = True,
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
    cache["calculated_data"] = og_checklist

    # output = model.generate_actual_checklist(og_checklist, school)

    return og_checklist

@app.post("/gemini")
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
    cache["calculated_data"] = og_checklist

    # output = model.generate_actual_checklist(og_checklist, school)

    return og_checklist

@app.get("/data")
async def get_data():
  cached_data = cache.get("calculated_data")
  if cached_data:
    return cached_data
  else:
    return [{"Task": "No data found in cache", "Priority": 1, "Description": "N/A"}]