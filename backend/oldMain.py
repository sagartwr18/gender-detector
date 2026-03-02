import cv2
import time
from collections import Counter

# Load models
faceModel = "models/res10_300x300_ssd_iter_140000.caffemodel"
faceProto = "models/deploy.prototxt"

genderModel = "models/gender_net.caffemodel"
genderProto = "models/gender_deploy.prototxt"

faceNet = cv2.dnn.readNet(faceModel, faceProto)
genderNet = cv2.dnn.readNet(genderModel, genderProto)

genderList = ['Male', 'Female']

male_content = cv2.imread("content/male.JPG")
female_content = cv2.imread("content/female.JPG")

cap = cv2.VideoCapture(1)

last_seen = time.time()

detection_start = None
gender_predictions = []
decision_made = False
current_state = "camera"

while True:

    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]

    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300),
                                 (104.0, 177.0, 123.0))

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

            # cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
            # cv2.putText(frame,gender,(x1,y1-10),
            #             cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,0),2)

    # --------------------------------
    # GENDER STABILIZATION
    # --------------------------------

    if face_detected and not decision_made:

        if detection_start is None:
            detection_start = time.time()

        gender_predictions.append(gender)

        elapsed = time.time() - detection_start

        cv2.putText(frame,
                    f"Analyzing... {int(3-elapsed)}s",
                    (30,50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,(0,0,255),2)

        if elapsed >= 3:

            most_common = Counter(gender_predictions).most_common(1)[0][0]

            if most_common == "Male":
                current_state = "male"
            else:
                current_state = "female"

            decision_made = True

    # --------------------------------
    # PERSON LEFT RESET
    # --------------------------------

    if not face_detected:

        if time.time() - last_seen > 3:

            current_state = "camera"
            decision_made = False
            detection_start = None
            gender_predictions = []

    # --------------------------------
    # DISPLAY OUTPUT
    # --------------------------------

    if current_state == "male":

        screen = cv2.resize(male_content,(w,h))
        cv2.imshow("Screen",screen)

    elif current_state == "female":

        screen = cv2.resize(female_content,(w,h))
        cv2.imshow("Screen",screen)

    else:

        cv2.imshow("Screen",frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()