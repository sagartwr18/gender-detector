import cv2

camera = cv2.VideoCapture(1)

def get_frame():

    success, frame = camera.read()

    if not success:
        return None

    ret, buffer = cv2.imencode('.jpg', frame)

    return buffer.tobytes()