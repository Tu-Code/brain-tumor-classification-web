import io
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError 
from PIL import Image
import torch
import json
from controllers import (
    login,
    signup,
    get_results,
    register_results,
    delete_patient
)
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from fastapi.staticfiles import StaticFiles

# Load environment variables from .env file
load_dotenv()

# Get the MongoDB connection string from the environment variables
mongodb_uri = os.getenv("MONGODB_URI")

# Connect to MongoDB
client = MongoClient(mongodb_uri)
db = client['sarah-brain-tumor-detector']

unit_size = 224

class LoginForm(BaseModel):
    username: str
    password: str

class SignupForm(BaseModel):
    name: str
    email: str
    password: str

class Patient(BaseModel):
    name: str
    gender: str
    age: int
    email: str
    notes: str
    result: str = Field(default="Pending...")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

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
async def login_route(data: LoginForm) -> bool:
    data = data.model_dump()
    return login(**data)

@app.post("/signup")
async def signup_route(data: SignupForm) -> bool:
    data = data.model_dump()
    return signup(**data)

@app.get("/results")
async def get_results_route():
    return get_results()

@app.post("/results")
async def register_results_route(data: Patient):
    try:
        data = data.model_dump()
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