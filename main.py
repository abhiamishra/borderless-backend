from fastapi import FastAPI, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import JSONResponse
import sqlite3

from api import callgemini
from api import getdata
from api import checklist

import os
from dotenv import load_dotenv
load_dotenv()


import firebase_admin
from firebase_admin import credentials, initialize_app, firestore

cred = credentials.Certificate({
        "type": "service_account",
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY"),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.environ.get('FIREBASE_CLIENT_EMAIL')}"
})
# cred = credentials.Certificate(service_account_key)  # Replace with your path
initialize_app(cred)

db = firestore.client()

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