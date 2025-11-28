from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from ultralytics import YOLO
from PIL import Image
import io
import logging

# Setup Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Detector")

app = FastAPI(title="Traffic & Object API", version="1.0")

# GLOBAL VARIABLES
traffic_model = None
object_model = None

def load_models():
    """Loads models safely. Fails gracefully if files are missing."""
    global traffic_model, object_model
    
    # 1. LOAD TRAFFIC SIGN MODEL (Custom)
    try:
        # Tries to load your trained model
        traffic_model = YOLO('traffic_custom.pt')
        logger.info("✅ Custom Traffic Sign model loaded!")
    except Exception:
        # Fallback if file is missing
        logger.warning("⚠️ 'traffic_custom.pt' not found. Using generic YOLOv8n (Results will be poor for signs).")
        traffic_model = YOLO('yolov8n.pt')

    # 2. LOAD OBJECT MODEL (Standard)
    # This automatically downloads if missing
    object_model = YOLO('yolov8n.pt')
    logger.info("✅ General Object model loaded!")

@app.on_event("startup")
async def startup_event():
    load_models()

@app.post("/detect")
async def detect_all(file: UploadFile = File(...)):
    try:
        # Read Image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # --- RUN PREDICTION ---
        # 1. Traffic Signs (Lower confidence because signs are hard)
        traffic_results = traffic_model.predict(image, conf=0.15)
        
        # 2. General Objects (Higher confidence, filter for Cars/Animals)
        # Class IDs: 2=Car, 5=Bus, 7=Truck, 15=Cat, 16=Dog, 0=Person
        relevant_ids = [0, 2, 5, 7, 15, 16]
        object_results = object_model.predict(image, conf=0.40, classes=relevant_ids)

        # --- FORMAT OUTPUT ---
        def parse_results(results):
            data = []
            for r in results:
                for box in r.boxes:
                    data.append({
                        "label": r.names[int(box.cls[0])],
                        "confidence": round(float(box.conf[0]), 2),
                        "box": box.xyxy[0].tolist()
                    })
            return data

        return JSONResponse(content={
            "status": "success",
            "traffic_signs": parse_results(traffic_results),
            "general_objects": parse_results(object_results)
        })

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)