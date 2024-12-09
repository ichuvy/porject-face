from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
import subprocess
import sys
import requests

app = Flask(__name__)

# สร้างโฟลเดอร์สำหรับบันทึกรูปภาพ
BASE_UPLOAD_FOLDER = 'dataset'  # โฟลเดอร์สำหรับเก็บข้อมูล
os.makedirs(BASE_UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def handle_register():
    name = request.form['name']  # ชื่อโฟลเดอร์

    # สร้างโฟลเดอร์ใหม่สำหรับชื่อที่ผู้ใช้ป้อน
    folder_path = os.path.join(BASE_UPLOAD_FOLDER, name)
    os.makedirs(folder_path, exist_ok=True)

    # ตรวจสอบและบันทึกรูปภาพหลายไฟล์
    files = request.files.getlist('image')  # ดึงไฟล์ทั้งหมด

    for file in files:
        # สร้างชื่อไฟล์ใหม่เพื่อป้องกันการทับซ้อน
        filename = file.filename
        image_path = os.path.join(folder_path, filename)
        
        # บันทึกรูปภาพในโฟลเดอร์ที่สร้างขึ้น
        file.save(image_path)

    # เรียกโปรแกรม train_model.py เพื่อเทรนโมเดล
    subprocess.Popen([sys.executable, "train.py"])


    # หลังจากการฝึกโมเดลเสร็จแล้วให้ไปที่หน้า URL ของ server ใหม่
    return jsonify({"status": "success", "message": "Model training started"})




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009, debug=True)

