from fastapi import FastAPI, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from api import question, getdata, checklist

import os
from dotenv import load_dotenv
load_dotenv()


from firebase_admin import credentials, initialize_app, firestore, auth
os.unsetenv("FIREBASE_KEY")

private_key = os.getenv("FIREBASE_KEY")
private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCnKNgUhHGurKeP\na0mUQxz9KWFEw7TyD2RA7E0/xWtCpqBWoq4Eui0GDMdlhaSMfOfNYv9ACJQW2hNU\n0Z2xcmJy1cabX1s7WVjXD07I8Lof3jYYhzcQbraCHNyLx1S2TC3S5UFpGQyKKK0C\niEFptAymINvCsgNO7oOleAlcLf2mk5wc0wsOyTJXzmbsK7qBeGqdqHw/AQw6Jd5X\nJK6QCspBzuy0gugn0Y7D41V3kAXmWfrXxEoWxRF7KA9m+Cta3xg1oO3IXxFtW/4L\nrhplbUK2m4TQItxowKAJ8855eFn2k2y8rrYo5FXL1I1okZ7X+bTlEh0pUAiYGhNO\n9uRN/5l5AgMBAAECggEAFJFIOwgL09X/HPyytjkmxziQ9QzOhg0iRQG+RIc2OiJ1\n7osANekxcoHeg+2UcEvLGsCgTwDvNbuZ7tEG4edE2UPX9tSeDViiP33s7/j8scCd\n79ktS4qPzsUd1t4NHIwVhFI8gOG54wL7vKjGwaqLduJqn9NW6F6dGJ5DKpInGFh0\nxomZEw/ALm048+ZQcWjwjuuQpDfpl2btmREBXuwt+hx/5eo1Ubovx/8XQCvjZx3e\nPG33JVo/8JNgM69BvueG7Cg73u8hoqhSAtdsSp/XPNrkH5GnHT9YEk67Hstp+mc6\nEF44ule0cL7YzUA4QKTZnFfXx5Op87CwABeBPgusLQKBgQDW9ahjq+a46Ep3eTAG\nFt4kUqpTGuHqtibDBoSVbj4K5cyBGbpQG0SiEpChPLXRs1MNIVzH/w5pcwC43yNq\nazjiV4qnka+uMUZSplnRABpYT5RPMDGfIkXQC1cT/kfeCUnSMb8UjLSerD5FkudG\nyEK2a6LCBjOf3552JtCBl+BIfQKBgQDHEuqBZVnBjR9dWHM6tQV4KfzllRd2TUmw\nOXh40eAFaGxcHWMtuO28oTs8MaxNpPdosOXTwHG7dWiwONBmCg/ix5zzwNsiAFSK\nBEHEGrzuZXftjWjAzGXdfXzNGZsdGK/my8lBCJzOEfNUYSk+oN/yki7p4dlNirka\nEIWl1LihrQKBgDXZwN+HVvuHpfAcOf2siOYMl4LOPz5vd3JwFZLh1UUhoIPPEC+1\nRRJdGEJsVRg9lla5vuaTbObZ2pp1vAeS6OM7Dw8/ngVDbtyRs/p5zh/Ff9/+sM+u\n5FJkJOJrV1G2ffncYIQjY7REbi07yhifXqcYe+OjbhdlC+uJeb6db6B5AoGBAJK8\ng7R7M0yyrALPNqh4VB69vFaxrciasY0+32kXMixqSy0e0EMcg8g9g/8bkijtRxyY\n/980g+Csa00xo5MDKbB8eFlHt355hdbxylQ1bTu/+UVVrXgncZJwc/RuQmKRFt9l\nKORR59sRai2xLIioZkpTrFbjDZzVexkWQpz4jltFAoGBAKDfT9i19yOBkX4wDPkB\nKQgaSNyqTvWCNdaFvS4tmZ6wS/GHPQlkYYutFd3EQatK8wNXmzMX7Ev1OyJjvD3i\nCAUMx/yxX+xjOvlacHK7/GMmjD5t+7SfwCSAuWDF6pPaF5v3/WtTQXR0PHTyd9iq\nAujW7GklIYDN0pS1egQ6jvzP\n-----END PRIVATE KEY-----\n"

try:
    cred = credentials.Certificate({
            "type": "service_account",
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": private_key,
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
except Exception as e:
    print("error:", e)

security = HTTPBearer()
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        # Verify the token with Firebase
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(getdata.router , prefix="/api")
app.include_router(checklist.router , prefix="/api")
app.include_router(question.router , prefix="/api")

# app.include_router(getdata.router)
# app.include_router(checklist.router)
# app.include_router(question.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}