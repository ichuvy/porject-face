from flask import Flask, request, redirect, url_for, render_template, flash
import threading

# สร้างแอป Flask สำหรับพอร์ต 5000
app1 = Flask(__name__)
app1.secret_key = 'your_secret_key'  # เปลี่ยนเป็น secret key ที่ปลอดภัย

# ข้อมูลผู้ใช้ตัวอย่างสำหรับการเข้าสู่ระบบ
users = {
    "ichuvy": "1234",  # ผู้ใช้ตัวอย่าง
}

@app1.route('/')
def index():
    return render_template('login.html')

@app1.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # ตรวจสอบข้อมูลการเข้าสู่ระบบ
    if username in users and users[username] == password:
        return redirect("http://127.0.0.1:5001/")  # เปลี่ยนเส้นทางไปยังพอร์ต 5001 เมื่อเข้าสู่ระบบสำเร็จ
    else:
        flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง')  # แสดงข้อความแสดงข้อผิดพลาด
        return redirect(url_for('index'))

# สร้างแอป Flask สำหรับพอร์ต 5001
app2 = Flask(__name__)

@app2.route('/')
def video_feed():
    return "นี่คือหน้า Video Feed"  # ตัวอย่างเนื้อหาสำหรับ video feed

# สร้างแอป Flask สำหรับพอร์ต 5002
app3 = Flask(__name__)

@app3.route('/')
def another_page():
    return "นี่คือหน้าอีกหน้า"  # ตัวอย่างเนื้อหาสำหรับแอปที่สาม

# ฟังก์ชันเพื่อรันแอปตัวแรก
def run_app1():
    app1.run(port=5000, debug=True)

# ฟังก์ชันเพื่อรันแอปตัวที่สอง
def run_app2():
    app2.run(port=5001, debug=True)

# ฟังก์ชันเพื่อรันแอปตัวที่สาม
def run_app3():
    app3.run(port=5002, debug=True)

# ฟังก์ชันหลักเพื่อเริ่มต้นแอปทั้งสามตัว
if __name__ == '__main__':
    # สร้างเธรดสำหรับแอปทั้งสามตัว
    thread1 = threading.Thread(target=run_app1)
    thread2 = threading.Thread(target=run_app2)
    thread3 = threading.Thread(target=run_app3)

    # เริ่มต้นเธรดทั้งสามตัว
    thread1.start()
    thread2.start()
    thread3.start()

    # รอให้เธรดทั้งสามตัวเสร็จสิ้น (ซึ่งจะไม่เกิดขึ้น เพราะทั้งสามแอปกำลังรันอยู่)
    thread1.join()
    thread2.join()
    thread3.join()
