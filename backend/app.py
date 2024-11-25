import io
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError 
from PIL import Image
import torch
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse

from controllers.controllers import (
    login,
    signup,
    get_results,
    register_results,
    delete_patient
)
from model.models import LoginForm, SignupForm, Patient
from util.jwt_handler import create_jwt_token, verify_jwt_token

# Load environment variables from .env file
load_dotenv()

# Get the MongoDB connection string from the environment variables
mongodb_uri = os.getenv("MONGODB_URI")

# Connect to MongoDB
client = MongoClient(mongodb_uri)
db = client['sarah-brain-tumor-detector']

unit_size = 224

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt', source='local')

static_dir = os.path.join(os.path.dirname(__file__), '../frontend/assets')
frontend_dir = os.path.join(os.path.dirname(__file__), '../frontend/pages')

# Mount the static and frontend files directories
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/web", StaticFiles(directory=frontend_dir, html=True), name="frontend")


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(app, host="0.0.0.0", port=port)
    
@app.post("/login")
async def login_route(data: LoginForm):

    data = data.model_dump()

    user = login(**data)

    if not user:

        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = create_jwt_token({"username": data["username"]})
    
    print("app.py")
    print(token)

    response = JSONResponse(content={"message": "Login successful"})

    response.set_cookie(key="access_token", value=token, httponly=True)

    return response


@app.post("/signup")
async def signup_route(data: SignupForm) -> bool:

    data = data.model_dump()

    return signup(**data)


def get_current_user(token: str = Depends(oauth2_scheme)):

    return verify_jwt_token(token)


@app.get("/results")
async def get_results_route(user_id: str, token: str = Depends(oauth2_scheme)):

    current_user = verify_jwt_token(token)

    return get_results(current_user["username"])


@app.post("/results")
async def register_results_route(data: Patient, token: str = Depends(oauth2_scheme)):

    current_user = verify_jwt_token(token)

    try:

        data = data.model_dump()
        
        data['user_id'] = current_user["username"]

        return register_results(data)
    
    except ValidationError as e:

        raise HTTPException(status_code=422, detail=e.errors())


@app.post("/predict")

async def predict_route(file: UploadFile):

    # Load the uploaded image
    image_bytes = await file.read()

    image = Image.open(io.BytesIO(image_bytes))

    results = model(image)

    # Parse results
    predictions = results.pandas().xyxy[0].to_json(orient="records")

    predictions_list = json.loads(predictions)

    if predictions_list:

        prediction_name = predictions_list[0]["name"]

    else:

        prediction_name = "No prediction"

    return prediction_name

@app.delete("/patients/{email}")
async def delete_patient_route(email: str):

    try:

        result = delete_patient(email)

        if result.deleted_count == 0:

            raise HTTPException(status_code=404, detail="Patient not found")
        
        return {"message": "Patient deleted successfully"}
    
    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))