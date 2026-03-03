import socket
import threading
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

HOST = "0.0.0.0"
PORT = 9000

KEY = b"12345678901234567890123456789012"  # 32-byte key

clients = []

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

def handle_client(client, addr):
    print(f"[+] Connected: {addr}")
    clients.append(client)

    while True:
        try:
            data = client.recv(4096)
            if not data:
                break

            message = decrypt(data)
            print(f"{addr}: {message}")

            # Log messages
            with open("chat.log", "a") as f:
                f.write(f"{addr}: {message}\n")

            # Broadcast to others
            for c in clients:
                if c != client:
                    c.send(encrypt(message))

        except:
            break

    print(f"[-] Disconnected: {addr}")
    clients.remove(client)
    client.close()

def start():
    open("chat.log", "w").close()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server running on port {PORT}")

    while True:
        client, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.start()

start()