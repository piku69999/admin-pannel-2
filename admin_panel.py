from flask import Flask, request, render_template, redirect, send_file, make_response
import io
import pyotp
import time
import os

app = Flask(__name__)
TOTP_SECRET = os.getenv('TOTP_SECRET', '3U3RBZ25MJ7D5F2HFUE2WCUOFXJ7RT3L')  # fallback if not set

SESSION = {'authenticated': False}
CLIENT_IMAGES = {}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        code = request.form.get('code')
        totp = pyotp.TOTP(TOTP_SECRET)
        if totp.verify(code):
            SESSION['authenticated'] = True
            return redirect('/dashboard')
        return render_template('login.html', error='Invalid code')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not SESSION.get('authenticated'):
        return redirect('/')
    clients = list(CLIENT_IMAGES.keys())
    return render_template('dashboard.html', clients=clients)

@app.route('/stream/<client_name>')
def stream(client_name):
    if not SESSION.get('authenticated'):
        return redirect('/')
    return render_template('stream.html', client_name=client_name)

@app.route('/upload', methods=['POST'])
def upload():
    client_name = request.form.get('client_name')
    file = request.files.get('screenshot')
    if client_name and file:
        CLIENT_IMAGES[client_name] = {
            'image': file.read(),
            'timestamp': time.time()
        }
        return 'OK'
    return 'Failed', 400

@app.route('/screenshot/<client_name>')
def screenshot(client_name):
    if client_name in CLIENT_IMAGES:
        img_data = CLIENT_IMAGES[client_name]['image']
        response = make_response(send_file(io.BytesIO(img_data), mimetype='image/jpeg'))
        # Prevent caching so the browser always fetches latest image
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return 'No image', 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
