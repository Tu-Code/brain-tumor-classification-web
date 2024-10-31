from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the MongoDB connection string from the environment variables
mongodb_uri = os.getenv("MONGODB_URI")

client = MongoClient(mongodb_uri)

db = client['sarah-brain-tumor-detector']



def check_password(encrypted, test: str):

    return encrypted == test


def login(username, password):

    user = db['users'].find_one({'name': username})

    print(user)

    print("control.py")
    print(user)

    if not user:

        return False

    return check_password(user['password'], password)


def signup(**user_details):

    db['users'].insert_one(user_details)

    return True


def get_results():

    return list(db['results'].find({}, {'_id': 0}))


def register_results(data):

    db['results'].insert_one(data)

    return True

def delete_patient(email):

    result = db['results'].delete_one({'email': email})

    return result