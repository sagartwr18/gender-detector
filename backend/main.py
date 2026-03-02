import cv2
import time
from collections import Counter
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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
# models
faceModel = "../models/res10_300x300_ssd_iter_140000.caffemodel"
faceProto = "../models/deploy.prototxt"

genderModel = "../models/gender_net.caffemodel"
genderProto = "../models/gender_deploy.prototxt"

faceNet = cv2.dnn.readNet(faceModel, faceProto)
genderNet = cv2.dnn.readNet(genderModel, genderProto)

genderList = ['Male','Female']

cap = cv2.VideoCapture(0)

last_seen = time.time()
detection_start = None
gender_predictions = []
decision_made = False
current_state = "camera"

def generate_frames():

    global last_seen,detection_start,gender_predictions,decision_made,current_state

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        h,w = frame.shape[:2]

        blob = cv2.dnn.blobFromImage(frame,1.0,(300,300),(104,177,123))
        faceNet.setInput(blob)
        detections = faceNet.forward()

        face_detected = False
        gender = None

        for i in range(detections.shape[2]):

            confidence = detections[0,0,i,2]

            if confidence > 0.7:

                face_detected = True
                last_seen = time.time()

                box = detections[0,0,i,3:7] * [w,h,w,h]
                (x1,y1,x2,y2) = box.astype("int")

                face = frame[y1:y2,x1:x2]

                if face.size == 0:
                    continue

                faceBlob = cv2.dnn.blobFromImage(
                    face,1.0,(227,227),
                    (78.4263377603,87.7689143744,114.895847746),
                    swapRB=False
                )

                genderNet.setInput(faceBlob)
                genderPred = genderNet.forward()

                gender = genderList[genderPred[0].argmax()]

        # stabilization
        if face_detected and not decision_made:

            if detection_start is None:
                detection_start = time.time()

            gender_predictions.append(gender)

            elapsed = time.time() - detection_start

            if elapsed >= 3:

                most_common = Counter(gender_predictions).most_common(1)[0][0]

                if most_common == "Male":
                    current_state = "male"
                else:
                    current_state = "female"

                decision_made = True

        if not face_detected:

            if time.time() - last_seen > 3:

                current_state = "camera"
                decision_made = False
                detection_start = None
                gender_predictions = []

        ret,buffer = cv2.imencode('.jpg',frame)
        frame = buffer.tobytes()

        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.get("/video")
def video():
    return StreamingResponse(generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/state")
def state():
    return JSONResponse({"state":current_state})