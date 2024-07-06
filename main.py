from fastapi import FastAPI, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import JSONResponse
import sqlite3

from api import callgemini
from api import getdata
from api import checklist


conn = sqlite3.connect("checklist.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS checklist_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        value TEXT NOT NULL CHECK(json_valid(value))
    );
''')
conn.commit()

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(callgemini.router)
app.include_router(getdata.router)
app.include_router(checklist.router)



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



    # output = model.generate_actual_checklist(og_checklist, school)

    return og_checklist