import hashlib
import hmac
from io import BytesIO

from Crypto.Cipher import DES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

from prateek_gupta import configuration_properties


def des_encrypt(plaintext):
    # Getting secret key in bytes
    secret_key = configuration_properties.get("CRYPTOGRAPHY_SECRET_KEY").encode("utf-8")
    # DES requires 8-byte key
    if len(secret_key) != 8:
        raise ValueError("DES key must be exactly 8 bytes")

    # Generating IV
    iv = get_random_bytes(8)

    # Creating Cipher(engine) for encrypting and initializing Cipher with secret key and IV
    cipher = DES.new(secret_key, DES.MODE_CBC, iv)

    # Generating bytes for plain text
    plaintext_bytes = plaintext.encode("utf-8")

    # Padding data similar to PKCS5Padding
    padded_data = pad(plaintext_bytes, DES.block_size)

    # Encrypting the data
    encrypted_data = cipher.encrypt(padded_data)

    # Creating in-memory file using BytesIO, IV first, then encrypted data
    output = BytesIO()
    output.write(iv)
    output.write(encrypted_data)

    # Returning encrypted data in bytes
    return output.getvalue()


def des_decrypt(encrypted_data):
    secret_key = configuration_properties.get("CRYPTOGRAPHY_SECRET_KEY").encode("utf-8")
    if len(secret_key) != 8:
        raise ValueError("DES key must be exactly 8 bytes")

    # Creating in-memory file to hold the bytes
    data = BytesIO(encrypted_data)

    # Reading first 8 bytes of IV
    iv = data.read(8)

    # Creating Cipher(engine) for decrypting and initializing Cipher with secret key and IV
    cipher = DES.new(secret_key, DES.MODE_CBC, iv)

    # Keeping the bytes of encrypted data in new variable
    plaintext_bytes = data.read()

    # Decrypting the data
    padded_data = cipher.decrypt(plaintext_bytes)

    # Removing padding from the data
    plaintext_bytes = unpad(padded_data, DES.block_size)

    # Convert bytes to string
    return plaintext_bytes.decode("utf-8")


def hash_sha_256(plain_text):
    return hashlib.sha256(plain_text.encode("utf-8")).hexdigest()


def hmac_sha_256(plain_text):
    # Getting secret key in bytes
    secret_key = configuration_properties.get("CRYPTOGRAPHY_SECRET_KEY").encode("utf-8")

    # Generating bytes for plain text
    plain_text_bytes = plain_text.encode("utf-8")
    return hmac.new(secret_key, plain_text_bytes, hashlib.sha256).hexdigest()
