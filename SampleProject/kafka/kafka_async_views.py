import json

from prateek_gupta.LogManager import logger
from prateek_gupta.exceptions import ServiceException
from prateek_gupta.kafka_async import (send, get_all_topics, get_topic,
                                       get_committed_offset, get_messages)
from prateek_gupta.utils import request_mapping
from utils import get_success_response, get_error_response, get_api_response


@request_mapping("POST")
async def send_message_request(request):
    logger.info("Entering send_message_request()")
    # noinspection PyBroadException
    try:
        from prateek_gupta import configuration_properties, module_lock_message
        enable_kafka = configuration_properties.get("KAFKA_ENABLE", None)
        if enable_kafka and enable_kafka == "A":
            topic = request.POST.get("topic", "")
            message = request.POST.get("message", "")
            await send(topic, message)
            response = get_success_response({"message": "Sent message"})
        else:
            response=get_api_response({"message":module_lock_message},403)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing send_message_request()")
    return response


@request_mapping("GET")
async def get_all_topics_request(request):
    logger.info("Entering get_all_topics_request()")
    # noinspection PyBroadException
    try:
        from prateek_gupta import configuration_properties, module_lock_message
        enable_kafka = configuration_properties.get("KAFKA_ENABLE", None)
        if enable_kafka and enable_kafka == "A":
            topics = await get_all_topics()
            response = get_success_response({
                "message": "Topics fetched successfully", "topics": topics})
        else:
            response=get_api_response({"message":module_lock_message},403)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing get_all_topics_request()")
    return response


@request_mapping("GET")
async def get_topic_request(request):
    logger.info("Entering get_topic_request()")
    # noinspection PyBroadException
    try:
        from prateek_gupta import configuration_properties, module_lock_message
        enable_kafka = configuration_properties.get("KAFKA_ENABLE", None)
        if enable_kafka and enable_kafka == "A":
            topic_name = request.GET.get("topic")
            topic = await get_topic(topic_name)
            response = get_success_response({
                "message": "Topics fetched successfully", "topic": topic})
        else:
            response=get_api_response({"message":module_lock_message},403)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing get_topic_request()")
    return response


@request_mapping("GET")
async def get_committed_offset_request(request):
    logger.info("Entering get_committed_offset_request()")
    # noinspection PyBroadException
    try:
        from prateek_gupta import configuration_properties, module_lock_message
        enable_kafka = configuration_properties.get("KAFKA_ENABLE", None)
        if enable_kafka and enable_kafka == "A":
            topic_name = request.GET.get("topic")
            partition = request.GET.get("partition")
            group = request.GET.get("group")
            committed_offset = await get_committed_offset(topic_name, partition, group)
            response = get_success_response({
                "message": f"Successfully fetched commited offset as {committed_offset}"
                if committed_offset else "No committed offset for group"})
        else:
            response=get_api_response({"message":module_lock_message},403)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing get_committed_offset_request()")
    return response


@request_mapping("POST")
async def get_messages_request(request):
    logger.info("Entering get_messages_request()")
    # noinspection PyBroadException
    try:
        from prateek_gupta import configuration_properties, module_lock_message
        enable_kafka = configuration_properties.get("KAFKA_ENABLE", None)
        if enable_kafka and enable_kafka == "A":
            data = request.POST.get("data", "")
            data = json.loads(data)
            messages = await get_messages(data)
            response = get_success_response({"message": "Successfully fetched messages",
                                             "messages": messages})
        else:
            response=get_api_response({"message":module_lock_message},403)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing get_messages_request()")
    return response
