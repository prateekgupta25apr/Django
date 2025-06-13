from prateek_gupta import post_construct_method
from prateek_gupta.LogManager import logger, rotate_log_files
from prateek_gupta.exceptions import ServiceException
from prateek_gupta.utils import execute_query, request_mapping
from utils import get_error_response, get_success_response, get_api_response


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
        from prateek_gupta import configuration_properties
        data["configuration_properties"] = configuration_properties
        response = get_success_response({"data": data})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException(
            exception_type=ServiceException.ExceptionType.UNKNOWN_ERROR))
    logger.info("Exiting test()")
    return response


@request_mapping('GET')
async def health_check(request):
    from prateek_gupta import configuration_properties
    logger.info("Entering " +
                request.path.replace(f"/{configuration_properties.get('context_path', '')}/",
                                     "")+ "()")
    # noinspection PyBroadException
    try:
        query = "SELECT DATABASE();"

        result = await execute_query(query, 'fetchone')
        logger.info("Health check for schema : " + str(result))

        response = get_success_response({"message": 'Healthy'})
    except Exception:
        response = get_api_response({"message": 'Unhealthy'}, 500)
    logger.info("Exiting health_check()")
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


@request_mapping('GET')
async def load_config_values(request):
    """
    The idea for this api is to reload only the configs and not to recreate the beans,
    if configs are updated such that beans need to be created then it's better to restart
    the service.
    """
    from prateek_gupta import configuration_properties, load_config_properties_fom_file
    logger.info(
        "Entering " +
        request.path.replace(f"/{configuration_properties.get('context_path', '')}/", "")
        + "()")
    # noinspection PyBroadException
    try:
        await load_config_value_from_db()
        await load_config_properties_fom_file()
        response = get_success_response({"message": 'Successfully loaded the config values'})
    except ServiceException as e:
        response = get_error_response(e)
    except Exception as e:
        response = get_error_response(ServiceException(
            exception_type=ServiceException.ExceptionType.UNKNOWN_ERROR))
    logger.info("Exiting test()")
    return response


@post_construct_method()
async def load_config_value_from_db():
    from prateek_gupta import configuration_properties
    result = await execute_query("select `key`,value from configurations;", "fetchall")
    for row in result:
        configuration_properties[row[0]] = row[1]
