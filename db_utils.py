# db_utils.py (in project root directory)
import sqlite3

# Replace with the relative path to your .db file (assuming it's in the root)
db_file = "checklist.db"

def get_connection():
  conn = sqlite3.connect(db_file)
  return conn