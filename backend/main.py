import cv2
import time
import torch
import numpy as np
import torchvision.models as models
import threading
import queue
from collections import Counter
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from torchvision import transforms
from PIL import Image

# -------------------------------
# Torch Optimization
# -------------------------------

torch.set_num_threads(4)
torch.set_grad_enabled(False)

# -------------------------------
# FastAPI Setup
# -------------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Haar Cascade (10x Faster than MediaPipe!)
# -------------------------------

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# -------------------------------
# Load FairFace Model
# -------------------------------

device = torch.device("cpu")

model = models.resnet34(pretrained=False)
model.fc = torch.nn.Linear(model.fc.in_features, 18)

state_dict = torch.load("../models/fairface_alldata_4race_20191111.pt", map_location=device)
model.load_state_dict(state_dict)

model.to(device)
model.eval()

# TorchScript for faster inference
try:
    model = torch.jit.script(model)
    print("Model compiled with TorchScript")
except:
    print("TorchScript compilation failed, using regular model")

# -------------------------------
# Image Transform
# -------------------------------

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# -------------------------------
# Camera Thread (REAL WEBCAM)
# -------------------------------

class CameraStream:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        
        # Optimized settings
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Try MJPEG codec
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

        self.ret, self.frame = self.cap.read()
        self.running = True
        self.lock = threading.Lock()

        thread = threading.Thread(target=self.update)
        thread.daemon = True
        thread.start()
        
        print("Camera initialized")

    def update(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.ret = ret
                    self.frame = frame

    def read(self):
        with self.lock:
            return self.ret, self.frame.copy()

    def release(self):
        self.running = False
        self.cap.release()

camera = CameraStream()

# -------------------------------
# Inference Queue (Async Processing)
# -------------------------------

inference_queue = queue.Queue(maxsize=2)
result_queue = queue.Queue(maxsize=2)

def predict_gender(face_img):
    """Optimized gender prediction"""
    img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_LINEAR)
    img = Image.fromarray(img)
    
    img_tensor = transform(img).unsqueeze(0).to(device)
    
    with torch.inference_mode():
        outputs = model(img_tensor)
    
    gender_scores = outputs[0, 7:9].cpu().numpy()
    gender = np.argmax(gender_scores)
    
    return "Male" if gender == 0 else "Female"

def inference_worker():
    """Separate thread for ML inference"""
    while True:
        try:
            face_img, frame_id = inference_queue.get(timeout=1)
            if face_img is None:
                break
            
            gender = predict_gender(face_img)
            result_queue.put((gender, frame_id))
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Inference error: {e}")

# Start inference thread
inference_thread = threading.Thread(target=inference_worker, daemon=True)
inference_thread.start()

# -------------------------------
# Detection Variables
# -------------------------------

last_seen = time.time()
detection_start = None
gender_predictions = []
decision_made = False
current_state = "camera"
frame_count = 0
last_gender = None

# -------------------------------
# Frame Generator (Optimized)
# -------------------------------

def generate_frames():
    global last_seen, detection_start
    global gender_predictions, decision_made
    global current_state, frame_count, last_gender

    print("Starting video stream...")
    
    while True:
        ret, frame = camera.read()
        
        if not ret:
            print("Camera read failed")
            time.sleep(0.01)
            continue

        frame_count += 1

        # Process every 3rd frame (performance boost)
        if frame_count % 3 != 0:
            # Still send frames for smooth video
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            continue

        h, w = frame.shape[:2]
        
        # Convert to grayscale for Haar Cascade (faster)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces (MUCH faster than MediaPipe)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80)
        )

        face_detected = False
        gender = last_gender

        if len(faces) > 0:
            # Use largest face
            faces_sorted = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
            x, y, fw, fh = faces_sorted[0]
            
            # Add padding
            padding = 20
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(w, x + fw + padding)
            y2 = min(h, y + fh + padding)
            
            face_img = frame[y1:y2, x1:x2]
            
            if face_img.size > 0:
                face_detected = True
                last_seen = time.time()

                # Predict every 20 frames (balanced performance/accuracy)
                if frame_count % 20 == 0:
                    try:
                        # Get result if available
                        if not result_queue.empty():
                            gender, _ = result_queue.get_nowait()
                            last_gender = gender
                        
                        # Queue new inference
                        if not inference_queue.full():
                            inference_queue.put_nowait((face_img.copy(), frame_count))
                    except:
                        pass

        # Stabilization logic
        if face_detected and not decision_made and gender:
            if detection_start is None:
                detection_start = time.time()

            gender_predictions.append(gender)
            elapsed = time.time() - detection_start

            if elapsed >= 5:
                most_common = Counter(gender_predictions).most_common(1)[0][0]
                current_state = "male" if most_common == "Male" else "female"
                decision_made = True
                print(f"Decision made: {current_state}")

        # Reset when no face
        if not face_detected:
            if time.time() - last_seen > 3:
                if current_state != "camera":
                    print("Resetting to camera mode")
                current_state = "camera"
                decision_made = False
                detection_start = None
                gender_predictions = []
                last_gender = None

        # Encode frame
        ret, buffer = cv2.imencode(
            '.jpg', frame,
            [cv2.IMWRITE_JPEG_QUALITY, 70]
        )

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n'
        )

# -------------------------------
# API Endpoints
# -------------------------------

@app.get("/video")
def video():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/state")
def state():
    return JSONResponse({"state": current_state})

@app.get("/health")
def health():
    return JSONResponse({
        "status": "ok",
        "camera": camera.ret,
        "device": str(device)
    })

@app.on_event("shutdown")
def shutdown_event():
    camera.release()
    inference_queue.put((None, None))

# -------------------------------
# Run with: uvicorn optimized_local:app --reload
# -------------------------------

print("\nServer ready!")
print("Video stream: http://localhost:8000/video")
print("State API: http://localhost:8000/state")
print("Health check: http://localhost:8000/health")
print("\nRun with: uvicorn optimized_local:app --reload\n")