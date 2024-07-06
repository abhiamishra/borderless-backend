from fastapi import APIRouter, Body, Depends
from gemini import GenModel
from db_utils import get_connection
import sqlite3
import json

model = GenModel()
router = APIRouter()
conn = get_connection()
cursor = conn.cursor()

@router.get("/data")
async def get_data():
  select_stmt = "SELECT * FROM checklist_table ORDER BY id DESC LIMIT 1"
  cursor.execute(select_stmt)
  cached_data = cursor.fetchone()
#   cached_data = cache.get("calculated_data")
  if cached_data:
    return json.loads(cached_data[1])
  else:
    return [{"Task": "No data found in cache", "Priority": 1, "Description": "N/A"}]