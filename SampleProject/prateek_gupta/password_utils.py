from prateek_gupta.cryptography import aes_encrypt, aes_decrypt


def encrypt_password(password):
    """Method to accept password as plain text and return encrypted password"""
    return aes_encrypt(password)


def valid_password(user_password, actual_password):
    """Method to accept password as plain text and return true if password is valid"""
    actual_password_str = aes_decrypt(actual_password)
    return actual_password_str == user_password
