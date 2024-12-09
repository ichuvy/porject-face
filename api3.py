from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # เพิ่มการ import CORS

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for CORS

# Example user data for login
users = {
    "ichuvy": "1234",  # Example user
}

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])  # ต้องรับ POST request
def login():
    if request.is_json:  # หากเป็น JSON request (สำหรับ Android)
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
    else:  # หากเป็นฟอร์มข้อมูล (สำหรับเว็บ)
        username = request.form['username']
        password = request.form['password']

    # ตรวจสอบข้อมูลผู้ใช้
    if username in users and users[username] == password:
        response = jsonify({'status': 'success', 'message': 'Login successful'})
        response.status_code = 200
        return response
    else:
        response = jsonify({'status': 'failure', 'message': 'Invalid username or password'})
        response.status_code = 401
        return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5007, debug=True)

