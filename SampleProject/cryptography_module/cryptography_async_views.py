from prateek_gupta.LogManager import logger
from prateek_gupta.cryptography_sync import des_encrypt, des_decrypt
from prateek_gupta.exceptions import module_lock_check, ServiceException
from prateek_gupta.utils import request_mapping
from utils import get_success_response, get_error_response


@request_mapping("POST")
async def des_encrypt_request(request):
    logger.info("Entering des_encrypt_request()")
    # noinspection PyBroadException
    try:
        module_lock_check("CRYPTOGRAPHY_ENABLED", "A")

        plain_text = request.POST.get("plain_text", "")
        encrypted_data = des_encrypt(plain_text)
        response = get_success_response({"message": "Successfully fetched messages",
                                         "Encrypted Data(Hex)": encrypted_data.hex()})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing des_encrypt_request()")
    return response


@request_mapping("POST")
async def des_decrypt_request(request):
    logger.info("Entering des_decrypt_request()")
    # noinspection PyBroadException
    try:
        module_lock_check("CRYPTOGRAPHY_ENABLED", "A")

        encrypted_text = request.POST.get("encrypted_text", "")
        if encrypted_text:
            encrypted_data = bytes.fromhex(encrypted_text)
            decrypted_data = des_decrypt(encrypted_data)
            response = get_success_response({"message": "Successfully fetched messages",
                                             "Decrypted Data": decrypted_data})
        else:
            raise ServiceException(
                exception_type=ServiceException.ExceptionType.MISSING_REQUIRED_PARAMETERS)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing des_decrypt_request()")
    return response
