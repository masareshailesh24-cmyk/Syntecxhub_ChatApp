import socket
import threading
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

HOST = "127.0.0.1"
PORT = 9000

KEY = b"12345678901234567890123456789012"

def encrypt(msg):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    padded = padder.update(msg.encode()) + padder.finalize()

    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return iv + ciphertext

def decrypt(data):
    iv = data[:16]
    ciphertext = data[16:]

    cipher = Cipher(algorithms.AES(KEY), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    message = unpadder.update(padded) + unpadder.finalize()
    return message.decode()

def receive(sock):
    while True:
        try:
            data = sock.recv(4096)
            if data:
                print("\nNew:", decrypt(data))
        except:
            break

def start():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    thread = threading.Thread(target=receive, args=(client,))
    thread.daemon = True
    thread.start()

    print("Connected to encrypted chat (port 9000)")
    while True:
        msg = input()
        client.send(encrypt(msg))

start()