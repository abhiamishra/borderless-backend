import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import time

# Replace these placeholders with your actual credentials
cred = credentials.Certificate('borderless-7aa31-firebase-adminsdk-1n51p-b1afa91697.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

# Replace this dictionary with your actual data
test_data = {
    "task": "Sample Task",
    "priority": "High",
    "description": "This is a sample description"
}

print("here!")
collection_ref = db.collection("checklist-test")

start_time = time.perf_counter()  # Record start time
print(start_time)
try:
    doc_ref = collection_ref.document()
    doc_ref.set(test_data)
    print(f"Document added with ID: {doc_ref.id}")
except Exception as e:
    print(f"Error adding document: {e}")

end_time = time.perf_counter()  # Record end time
elapsed_time = end_time - start_time
print(f"Time taken: {elapsed_time:.2f} seconds")
