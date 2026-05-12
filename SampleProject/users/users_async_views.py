import datetime
import json

from django.db import IntegrityError
from django.utils import timezone

from prateek_gupta.emails_async import send
from prateek_gupta.exceptions import ServiceException, log_error
from prateek_gupta.password_utils import valid_password, encrypt_password
from prateek_gupta.utils import request_mapping, execute_as_async
from utils import get_error_response, validate_user_login, get_success_response
from .models import User


@request_mapping("POST")
async def login(request):
    # noinspection PyBroadException
    try:
        body = json.loads(request.body)
        email = body['email']
        password = body['password']
        remember_me = body.get("remember_me", False)

        # Fetching user by email
        user = await execute_as_async(User.objects.get, email=email)

        # Authenticating provided user details
        is_password_valid = valid_password(password, user.password)

        result = dict()
        user_details = None

        if is_password_valid:
            # Preparing user details for response
            user_details = prepare_user_details(user, remember_me)
            result["status"] = 1
            result['message'] = "Login successful"
            result['user_details'] = user_details
        else:
            result["status"] = 2
            result['message'] = "Invalid password"

        response = get_success_response(result)
        if user_details:
            request.user_context.update_session_for_login(user_details, response)

    except ServiceException as e:
        return get_error_response(e)
    except Exception:
        return get_error_response(ServiceException())
    return response


@request_mapping('POST')
async def sign_up(request):
    # noinspection PyBroadException
    try:
        body = json.loads(request.body)
        first_name = body["first_name"]
        last_name = body["last_name"]
        email = body['email']
        password = body['password']
        remember_me = body.get("remember_me", False)
        user_details = None

        try:
            # Saving user
            added_user = await add_user(
                first_name=first_name, last_name=last_name, email=email, password=password)

            user_details = prepare_user_details(added_user, remember_me)

            # Preparing result
            result = {
                "status": 1,
                "message": "Sign up successful",
                "user_details": user_details
            }
        except IntegrityError:
            result = {"status": 2, "message": "Provided email already exists"}

        response = get_success_response(result)

        # Updating session only if user added successfully
        if user_details:
            request.user_context.update_session_for_login(user_details, response)
        return response
    except ServiceException as e:
        return get_error_response(e)
    except Exception:
        return get_error_response(ServiceException())


@request_mapping('POST')
def logout(request):
    # noinspection PyBroadException
    try:
        request.user_context.update_session_for_logout(request)
        return get_success_response({"message": "Successfully logged out"})
    except ServiceException as e:
        return get_error_response(e)
    except Exception:
        return get_error_response(ServiceException())


@request_mapping('POST')
async def forgot_password(request):
    # noinspection PyBroadException
    try:
        # Retrieving body
        body = json.loads(request.body)
        # Retrieving the email
        email = body["email"]

        # Retrieving resend status
        resend_status = body.get("resend", False)

        # Declaring object for response
        response = dict()

        # Retrieving the User object
        try:
            user = await execute_as_async(User.objects.get, email=email)
        except User.DoesNotExist:
            # If no user account is associated with the provided email then we
            # return status as 2
            response["status"] = 2
            response["email"] = email
            response["message"] = "No account found for the provided email"
            return get_success_response(response)

        # If the user has already requested for the Forgot Password
        if user.forgot_password_request and (not resend_status):
            response["status"] = 3
            response["email"] = email
            response["message"] = ("An email with link to reset the password is "
                                   "sent to your email.")
            return get_success_response(response)

        # Preparing the code
        # First we prepare the JSON object by setting the attribute "id" to user_id
        # in String format. Then we use the encode() method to convert the JSON object
        # in String format to bytes format, and then we store the JSON object in byte
        # format to a list, so we can see the JSON object as an array of numbers then
        # we use the map() method to convert the numbers stored in the List to String
        # format and then the join() method to combine all the numbers in the String
        # format to a single String.
        code = "".join(map(str, list(('{"id":' + str(user.user_id) + '}').encode())))

        # Updating the forgot_password_request
        user.forgot_password_request = True

        await execute_as_async(user.save)

        # Sending email to the user
        email_subject = 'Reset Password link'
        email_content = (
                '<!DOCTYPE html><html><body style="font-family:Arial,sans-serif;'
                'color:#333;line-height:1.6;"><p>Hello</p><p>We received a request '
                'to reset the password for your account.</p><p>If you made this '
                'request, please click the button below to choose a new password:'
                '</p><div><form action="' +
                request.tenant_context.api_url +
                'async/reset_password" method="GET" target="_blank" '
                'style="display:inline-block;"><input type="hidden" name="pg" value="' +
                code +
                '"><input type="submit" value="Reset Password" '
                'style="background-color:#007BFF;'
                'color:white;padding:12px 24px;border:none;border-radius:4px;'
                'font-weight:bold;cursor:pointer;"></form></div><p>If you did '
                'not request a password reset, please ignore this email. Your '
                'account will remain secure.</p><p>Regards<br>Prateek Gupta</p>'
                '</body></html>')
        from prateek_gupta import configuration_properties
        from_email = configuration_properties.get(
            "EMAILS_DEFAULT_EMAIL", "Prateek Gupta<prateek.gupta25apr@gmail.com>")

        await send(
            from_email=from_email, to_email=email, subject=email_subject, content=email_content
        )
        response["status"] = 1
        response["email"] = email
        response["message"] = "Email with link to reset password is sent to your email"
        return get_success_response(response)
    except ServiceException as e:
        return get_error_response(e)
    except Exception:
        return get_error_response(ServiceException())


def decoder(code):
    # Converting the code to a JSON Object
    raw_json = list()
    i = 0
    while len(code) > 0:
        if int(code[0:3]) > 256:
            raw_json.append(int(code[0:2]))
            code = code.replace(code[0:2], "", 1)
            i += 2

        else:
            raw_json.append(int(code[0:3]))
            code = code.replace(code[0:3], "", 1)
            i += 3

    return json.loads(bytes(raw_json).decode())


@request_mapping('POST')
async def reset_password(request):
    # noinspection PyBroadException
    try:
        # Retrieving user's id
        # noinspection PyBroadException
        try:
            pg = request.POST.get('pg', None)

            if not pg:
                raise ServiceException()

            pg_decoded = decoder(pg)

            if pg_decoded and type(pg_decoded) is dict and "id" in pg_decoded:
                user_id = pg_decoded['id']
            else:
                raise ServiceException()

            # Retrieving user by using the id
            user = await execute_as_async(User.objects.get, user_id=user_id)

            if not user.forgot_password_request:
                raise ServiceException()

        except Exception:
            result = dict()
            result["status"] = 2
            result["message"] = "Sorry, this page has expired"
            return get_success_response(result)

        # Extracting password
        password = request.POST.get('password', None)

        # Changing user's password
        user.password = encrypt_password(password)

        # Updating forgot_password_request for the user
        user.forgot_password_request = False

        # Saving user's password
        await execute_as_async(user.save)

        result = dict()
        result["status"] = 1
        result["message"] = "Password reset successfully"

        return get_success_response(result)
    except ServiceException as e:
        return get_error_response(e)
    except Exception:
        return get_error_response(ServiceException())


@request_mapping("DELETE")
async def delete_user(request):
    """Method to delete a user account by using the user_id passed as request
    param in the url or fetching from the session"""
    # noinspection PyBroadException
    try:
        validate_user_login(request)
        result = dict()
        message = ""

        # noinspection PyBroadException
        try:
            user = await execute_as_async(
                User.objects.get, user_id=request.user_context.user_id)
            await execute_as_async(user.delete)

            # Logging out the user
            request.user_context.update_session_for_logout(request)

            if request.user_context.is_mobile_api:
                result["status"] = 1
                result["message"] = "Successfully deleted account with id "
            else:
                message = "Successfully deleted your account"
        except Exception:
            log_error()
            if request.user_context.is_mobile_api:
                result["status"] = 2
                result["message"] = ("An error occurred while deleting account"
                                     "with Id ")
            else:
                message = "An error occurred while deleting your account"

        result = {"message": message}
        return get_success_response(result)
    except ServiceException as e:
        return get_error_response(e)
    except Exception:
        return get_error_response(ServiceException())


@request_mapping('POST')
async def change_password(request):
    # noinspection PyBroadException
    try:
        # Extracting password
        password = request.POST.get('password', None)

        if not password:
            return get_error_response(ServiceException(
                exception_type=ServiceException.ExceptionType.MISSING_REQUIRED_PARAMETERS,
                message="Please enter valid password"))

        # Extracting new password
        new_password = request.POST.get('new_password', None)

        if not new_password:
            return get_error_response(ServiceException(
                exception_type=ServiceException.ExceptionType.MISSING_REQUIRED_PARAMETERS,
                message="Please enter valid new password"))

        if not request.user_context.user_id > 0:
            return get_error_response(ServiceException(
                exception_type=ServiceException.ExceptionType.FORBIDDEN,
                message="Please login and then revisit"))

        # Retrieving user by using the id
        user = await execute_as_async(User.objects.get,
                                      user_id=request.user_context.user_id)

        # Validating provided password
        if not valid_password(password, user.password):
            return get_success_response(
                {"status": 2, "message": "Provided password is incorrect"})

        # Changing user's password
        user.password = encrypt_password(new_password)

        # Updating forgot_password_request for the user
        user.forgot_password_request = False

        # Saving user's password
        await execute_as_async(user.save)

        return get_success_response(
            {"status": 1, "message": "Password changed successfully"})
    except ServiceException as e:
        return get_error_response(e)
    except Exception:
        return get_error_response(ServiceException())


def prepare_user_details(
        user, remember_me=None, user_logout_time=None):
    """This method prepare the user details for cookie from User entity"""
    user_details = {
        "user_id": user.user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "dark_mode": user.dark_mode
    }

    if user_logout_time:
        user_details['user_logout_time'] = user_logout_time

    if remember_me is not None:
        # Calculating logout time for the user and if the user has selected for
        # remember_me then we are setting user_logout_time to -1, which will be validated
        # in the middleware for user's logged in status
        if remember_me:
            user_logout_time = -1
        else:
            user_logout_time = ((timezone.now() + datetime.timedelta(days=1))
                                .timestamp() * 1000)

        user_details['user_logout_time'] = user_logout_time

    return user_details


@request_mapping("GET")
async def get_user_details(request):
    # noinspection PyBroadException
    try:
        if not request.user_context.user_id > 0:
            return get_error_response(ServiceException(
                exception_type=ServiceException.ExceptionType.FORBIDDEN,
                message="Please login and then revisit"))

        # Fetching user by id
        user = await execute_as_async(
            User.objects.get, user_id=request.user_context.user_id)

        result = {
            'message': 'Successfully retrieved user details',
            'user_details': prepare_user_details(user)
        }

        return get_success_response(result)
    except ServiceException as e:
        return get_error_response(e)
    except Exception:
        return get_error_response(ServiceException())


@request_mapping("POST")
async def save_user_details(request):
    # noinspection PyBroadException
    try:
        if not request.user_context.user_id > 0:
            return get_error_response(ServiceException(
                exception_type=ServiceException.ExceptionType.FORBIDDEN,
                message="Please login and then revisit"))

        payload = json.loads(request.body)

        if not payload:
            return get_error_response(ServiceException(
                exception_type=ServiceException.ExceptionType.MISSING_REQUIRED_PARAMETERS))

        user_details = None
        try:
            user, _ = await execute_as_async(
                User.objects.update_or_create,
                user_id=request.user_context.user_id,
                defaults=payload
            )

            # Preparing user details for response
            user_details = prepare_user_details(
                user, user_logout_time=request.user_context.user_logout_time)
            result = {
                "status": 1,
                "message": "User details saved successfully",
                'user_details': user_details
            }
        except IntegrityError:
            result = {"status": 2, "message": "Provided email already exists"}

        response = get_success_response(result)
        if user_details:
            request.user_context.update_session_for_login(user_details, response)
        return response
    except ServiceException as e:
        return get_error_response(e)
    except Exception:
        return get_error_response(ServiceException())


async def add_user(first_name, last_name, email, password):
    """This method takes user details as argument and add user in DB.
    Password is encrypted before saving"""
    return await execute_as_async(
        User.objects.create,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=encrypt_password(password)
    )
