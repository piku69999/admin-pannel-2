from flask import Flask, request, render_template, redirect, send_file, make_response
import io
import time

app = Flask(__name__)
CLIENT_IMAGES = {}

@app.route('/')
def home():
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    clients = list(CLIENT_IMAGES.keys())
    return render_template('dashboard.html', clients=clients)

@app.route('/stream/<client_name>')
def stream(client_name):
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
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return 'No image', 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
