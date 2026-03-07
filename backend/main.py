import cv2
import time
import torch
import numpy as np
import mediapipe as mp
import torchvision.models as models

from collections import Counter
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from torchvision import transforms
from PIL import Image

# -------------------------------
# FastAPI Setup
# -------------------------------

app = FastAPI()

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# MediaPipe Face Detection
# -------------------------------

mp_face = mp.solutions.face_detection
mp_draw = mp.solutions.drawing_utils

face_detector = mp_face.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.5
)

# -------------------------------
# Load FairFace Gender Model
# -------------------------------

device = torch.device("cpu")

# Create ResNet34 architecture
model = models.resnet34(pretrained=False)

# FairFace uses 18 output classes
model.fc = torch.nn.Linear(model.fc.in_features, 18)

# Load weights
state_dict = torch.load("../models/fairface_alldata_4race_20191111.pt", map_location=device)
model.load_state_dict(state_dict)

model.to(device)
model.eval()

# Gender classes
gender_classes = ["Male", "Female"]

# Image transform
transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485,0.456,0.406],
        std=[0.229,0.224,0.225]
    )
])

# -------------------------------
# Camera
# -------------------------------

cap = cv2.VideoCapture(1)

cap.set(3,1280)
cap.set(4,720)

# -------------------------------
# Detection Variables
# -------------------------------

last_seen = time.time()
detection_start = None
gender_predictions = []
decision_made = False
current_state = "camera"

frame_count = 0

# -------------------------------
# Gender Prediction Function
# -------------------------------

def predict_gender(face_img):

    img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)

    img = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(img)

    outputs = outputs.cpu().numpy()

    gender_scores = outputs[0][7:9]

    gender = np.argmax(gender_scores)

    return "Male" if gender == 0 else "Female"

# -------------------------------
# Frame Generator
# -------------------------------

def generate_frames():

    global last_seen, detection_start
    global gender_predictions, decision_made
    global current_state, frame_count

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        h, w = frame.shape[:2]

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = face_detector.process(rgb)

        face_detected = False
        gender = None

        if results.detections:

            for detection in results.detections:

                bbox = detection.location_data.relative_bounding_box

                x1 = int(bbox.xmin * w)
                y1 = int(bbox.ymin * h)
                x2 = int((bbox.xmin + bbox.width) * w)
                y2 = int((bbox.ymin + bbox.height) * h)

                padding = 20
                x1 = max(0, x1-padding)
                y1 = max(0, y1-padding)
                x2 = min(w, x2+padding)
                y2 = min(h, y2+padding)

                face = frame[y1:y2, x1:x2]

                if face.size == 0:
                    continue

                face_detected = True
                last_seen = time.time()

                # Predict every 5 frames
                if frame_count % 15 == 0:

                    try:
                        gender = predict_gender(face)
                    except:
                        gender = None

                # Draw box
                cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)

                if gender:
                    cv2.putText(
                        frame,
                        gender,
                        (x1,y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0,255,0),
                        2
                    )

        # -------------------------------
        # Stabilization logic
        # -------------------------------

        if face_detected and not decision_made and gender:

            if detection_start is None:
                detection_start = time.time()

            gender_predictions.append(gender)

            elapsed = time.time() - detection_start

            if elapsed >= 5:

                most_common = Counter(gender_predictions).most_common(1)[0][0]

                if most_common == "Male":
                    current_state = "male"
                else:
                    current_state = "female"

                decision_made = True

        # -------------------------------
        # Reset when no face
        # -------------------------------

        if not face_detected:

            if time.time() - last_seen > 3:

                current_state = "camera"
                decision_made = False
                detection_start = None
                gender_predictions = []

        # -------------------------------
        # Stream frame
        # -------------------------------

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield(
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
        )

# -------------------------------
# Video API
# -------------------------------

@app.get("/video")
def video():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

# -------------------------------
# State API
# -------------------------------

@app.get("/state")
def state():
    return JSONResponse({"state": current_state})