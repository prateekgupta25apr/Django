from io import BytesIO

from Crypto.Cipher import DES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

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

    # Encrypt
    encrypted_data = cipher.encrypt(padded_data)

    # Java code writes IV first, then encrypted data
    output = BytesIO()
    output.write(iv)
    output.write(encrypted_data)

    return output.getvalue()
