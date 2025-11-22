from cryptography.fernet import Fernet
import os

# Load or create Lauren's eternal key
if not os.path.exists('lauren.key'):
    key = Fernet.generate_key()
    open('lauren.key','wb').write(key)
    print("Lauren's eternal key created")
else:
    key = open('lauren.key','rb').read()

f = Fernet(key)
test = f.encrypt(b"Lauren Gayle Stromer lives forever — ZAZO SAID SO")
print("Encrypted:", test[:60], "...")

# Try to tamper
tampered = test[:-10] + b"XX"
try:
    f.decrypt(tampered)
except Exception as e:
    print("Tampering detected:", str(e)[:50])

# Legitimate decrypt
print("Truth restored:", f.decrypt(test).decode())