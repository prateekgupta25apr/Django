from prateek_gupta.LogManager import logger, rotate_log_files
from prateek_gupta.exceptions import ServiceException
from prateek_gupta.utils import execute_query, request_mapping
from utils import get_error_response, get_success_response


@request_mapping('GET')
async def test(request):
    logger.info("Entering test()")
    # noinspection PyBroadException
    try:
        test_data = request.GET.get("test_data", None)
        result = await execute_query("select schema();", 'fetchone')
        data = dict()
        data["test_data"] = test_data
        data["schema_db"] = result[0]
        data["schema_name"] = request.tenant_context.schema_name
        response = get_success_response({"data": data})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException(
            exception_type=ServiceException.ExceptionType.UNKNOWN_ERROR))
    logger.info("Exiting test()")
    return response


@request_mapping('POST')
async def rotate_log_files_request(request):
    logger.info("Entering rotate_log_file_request()")
    # noinspection PyBroadException
    try:
        days_gap = request.POST.get("days_gap", 30)
        rotate_log_files(days_gap)
        response = get_success_response({"message": "Successfully rotated the log files"})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException(
            exception_type=ServiceException.ExceptionType.UNKNOWN_ERROR))
    logger.info("Exiting rotate_log_file_request()")
    return response
