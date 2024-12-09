import os
import face_recognition
import pickle
from sklearn import neighbors
import requests

# ฟังก์ชันสำหรับโหลดและเข้ารหัสใบหน้าอัตโนมัติ
def load_and_encode_faces(dataset_path):
    face_encodings = []
    face_labels = []
    
    # วนลูปเพื่อดึงข้อมูลจาก dataset
    for person_name in os.listdir(dataset_path):
        person_folder = os.path.join(dataset_path, person_name)
        
        # ตรวจสอบว่าเป็นโฟลเดอร์หรือไม่
        if not os.path.isdir(person_folder):
            continue
            
        # อ่านภาพในแต่ละโฟลเดอร์
        for image_name in os.listdir(person_folder):
            image_path = os.path.join(person_folder, image_name)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            
            # หากพบใบหน้าในภาพนี้
            if encodings:
                face_encodings.append(encodings[0])  # เก็บการเข้ารหัสใบหน้า
                face_labels.append(person_name)  # เก็บชื่อบุคคล
    
    return face_encodings, face_labels

# กำหนดเส้นทางไปยังโฟลเดอร์ dataset และเส้นทางที่จะบันทึกโมเดล
dataset_path = "dataset"  # เปลี่ยนเป็นที่เก็บข้อมูลของคุณ
model_path = "model/face_recognition_model.pkl"  # ที่เก็บโมเดล
restart_url = "http://172.20.10.2:5008/restart"  # URL สำหรับรีสตาร์ทเซิร์ฟเวอร์

# โหลดข้อมูลการเข้ารหัสใบหน้าและป้ายชื่อจาก dataset ใหม่
new_encodings, new_labels = load_and_encode_faces(dataset_path)

# สร้างและเทรนโมเดล K-Nearest Neighbors (KNN) ใหม่ด้วยข้อมูลที่โหลดจาก dataset
knn_clf = neighbors.KNeighborsClassifier(n_neighbors=5, algorithm='ball_tree', weights='distance')
knn_clf.fit(new_encodings, new_labels)

# บันทึกโมเดลที่เทรนเสร็จแล้ว
with open(model_path, "wb") as f:
    pickle.dump(knn_clf, f)

print("Model trained and saved successfully.")

# ฟังก์ชันสำหรับรีสตาร์ทเซิร์ฟเวอร์
def restart_server(restart_url):
    try:
        response = requests.post(restart_url, json={"action": "restart"}, timeout=10)
        if response.status_code == 200:
            print("Successfully sent restart request to the server.")
        else:
            print(f"Failed to restart server. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error while restarting server: {e}")

# เรียกฟังก์ชันเพื่อรีสตาร์ทเซิร์ฟเวอร์
restart_server(restart_url)
