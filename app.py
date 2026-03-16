from flask import Flask, render_template, request, send_file
from cryptography.fernet import Fernet
import hashlib
import base64
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Generate key from password
def generate_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)

# Encrypt file
def encrypt_file(filepath, password):
    key = generate_key(password)
    fernet = Fernet(key)

    with open(filepath, "rb") as file:
        data = file.read()

    encrypted = fernet.encrypt(data)

    enc_file = filepath + ".enc"
    with open(enc_file, "wb") as file:
        file.write(encrypted)

    return enc_file

# Decrypt file
def decrypt_file(filepath, password):
    key = generate_key(password)
    fernet = Fernet(key)

    with open(filepath, "rb") as file:
        data = file.read()

    decrypted = fernet.decrypt(data)

    dec_file = filepath.replace(".enc", "_decrypted")
    with open(dec_file, "wb") as file:
        file.write(decrypted)

    return dec_file


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/encrypt", methods=["POST"])
def encrypt():
    file = request.files["file"]
    password = request.form["password"]

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    encrypted_file = encrypt_file(filepath, password)

    return send_file(encrypted_file, as_attachment=True)


@app.route("/decrypt", methods=["POST"])
def decrypt():
    file = request.files["file"]
    password = request.form["password"]

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    decrypted_file = decrypt_file(filepath, password)

    return send_file(decrypted_file, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)