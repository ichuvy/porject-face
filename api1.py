from flask import Flask, Response, render_template, request, jsonify
import face_recognition
import joblib
import cv2
import os
import time
from flask_cors import CORS
import sys
import requests
from gtts import gTTS
import pygame

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# โหลดโมเดลที่ฝึกไว้
model_path = 'model/face_recognition_model.pkl'
if os.path.exists(model_path):
    knn_clf = joblib.load(model_path)
else:
    raise FileNotFoundError(f"ไม่พบไฟล์โมเดลที่ {model_path}. กรุณาตรวจสอบตำแหน่งและชื่อไฟล์ของโมเดล.")

# สร้างตัวแปรสำหรับกล้อง
camera = cv2.VideoCapture(0)
if not camera.isOpened():
    raise IOError("ไม่สามารถเข้าถึงกล้องได้ กรุณาตรวจสอบการเชื่อมต่อกล้อง.")

# Line Notify Token (แก้ไขเป็น Token ของคุณ)
line_token = "1P0AutnCwI5CrwPa4CsM7pXXKW0iGgDTJJBlwoBVUb5"

# ฟังก์ชันส่งภาพไปยัง LINE Notify
def send_to_line(image_path, message, token):
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    payload = {"message": message}
    files = {"imageFile": open(image_path, "rb")}
    response = requests.post(url, headers=headers, data=payload, files=files)
    return response.status_code

# ฟังก์ชันเล่นเสียงแจ้งเตือนเมื่อเจอ Unknown
def play_alert_sound(message):
    filename = 'alert.mp3'
    tts = gTTS(text=message, lang='th')
    tts.save(filename)
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()
    os.remove(filename)

# ฟังก์ชันสำหรับสร้างเฟรมจากกล้อง
def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            print("ไม่สามารถอ่านภาพจากกล้องได้ กำลังพยายามรีสตาร์ท...")
            camera.release()
            time.sleep(2)
            camera.open(0)
            continue

        # ลดขนาดของภาพเพื่อลดภาระการประมวลผล
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # ค้นหาใบหน้าและทำการ encoding
        face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        results = []
        for face_encoding in face_encodings:
            closest_distances = knn_clf.kneighbors([face_encoding], n_neighbors=1)
            is_recognized = closest_distances[0][0][0] < 0.6
            name = knn_clf.predict([face_encoding])[0] if is_recognized else "Unknown"
            results.append((name, is_recognized))

        for (top, right, bottom, left), (name, is_recognized) in zip(face_locations, results):
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2

            if is_recognized:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)  # สีเขียว
            else:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)  # สีแดง
                face_image_path = f"unknown_faces/unknown_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
                os.makedirs("unknown_faces", exist_ok=True)
                cv2.imwrite(face_image_path, frame[top:bottom, left:right])
                send_to_line(face_image_path, "Unknown face detected!", line_token)
                play_alert_sound("เเกมาทำไม จัยฉันมาทำไม!")

            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed', methods=['GET'])
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/restart', methods=['POST'])
def restart():
    if request.json.get('action') == 'restart':
        response = jsonify({"status": "success", "message": "Server restarting"})
        response.status_code = 200
        time.sleep(2)
        os.execv(sys.executable, ['python'] + sys.argv)
        return response
    return jsonify({"status": "error", "message": "Invalid action"}), 400

if __name__ == '__main__':
    os.makedirs("unknown_faces", exist_ok=True)
    os.makedirs("intruder_images", exist_ok=True)
    app.run(host='0.0.0.0', port=5008, debug=True)
