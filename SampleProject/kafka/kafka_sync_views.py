import json

from prateek_gupta.LogManager import logger
from prateek_gupta.exceptions import ServiceException
from prateek_gupta.kafka_sync import (send, create_topic, get_all_topics, get_topic,
                                      update_topic_increase_partition, update_topic,
                                      delete_topic, get_committed_offset, get_messages)
from prateek_gupta.utils import request_mapping
from utils import get_success_response, get_error_response, get_api_response


@request_mapping("POST")
def send_message_request(request):
    logger.info("Entering send_message_request()")
    # noinspection PyBroadException
    try:
        from prateek_gupta import configuration_properties,module_lock_message
        enable_kafka = configuration_properties.get("KAFKA_ENABLE", None)
        if enable_kafka and enable_kafka == "S":
            topic = request.POST.get("topic", "")
            message = request.POST.get("message", "")
            send(topic, message)
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
def get_all_topics_request(request):
    logger.info("Entering get_all_topic_request()")
    # noinspection PyBroadException
    try:
        from prateek_gupta import configuration_properties, module_lock_message
        enable_kafka = configuration_properties.get("KAFKA_ENABLE", None)
        if enable_kafka and enable_kafka == "S":
            topics = get_all_topics()
            response = get_success_response({
                "message": "Topics fetched successfully", "topics": topics})
        else:
            response=get_api_response({"message":module_lock_message},403)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing get_all_topic_request()")
    return response


@request_mapping("GET")
def get_topic_request(request):
    logger.info("Entering get_topic_request()")
    # noinspection PyBroadException
    try:
        from prateek_gupta import configuration_properties, module_lock_message
        enable_kafka = configuration_properties.get("KAFKA_ENABLE", None)
        if enable_kafka and enable_kafka == "S":
            topic_name = request.GET.get("topic")
            topic = get_topic(topic_name)
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


@request_mapping("POST")
def create_topic_request(request):
    logger.info("Entering create_topic()")
    # noinspection PyBroadException
    try:
        from prateek_gupta import configuration_properties, module_lock_message
        enable_kafka = configuration_properties.get("KAFKA_ENABLE", None)
        if enable_kafka and enable_kafka == "S":
            topic_name = request.POST.get("topic_name", "")
            partitions = request.POST.get("partitions", "")
            replication_factor = request.POST.get("replication_factor", "")
            create_topic(topic_name, partitions, replication_factor)
            response = get_success_response({"message": "Topic created successfully"})
        else:
            response=get_api_response({"message":module_lock_message},403)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing create_topic()")
    return response


@request_mapping("POST")
def update_topic_increase_partition_request(request):
    logger.info("Entering update_topic_increase_partition_request()")
    # noinspection PyBroadException
    try:
        from prateek_gupta import configuration_properties, module_lock_message
        enable_kafka = configuration_properties.get("KAFKA_ENABLE", None)
        if enable_kafka and enable_kafka == "S":
            topic_name = request.POST.get("topic_name", "")
            partitions = request.POST.get("partitions", "")
            update_topic_increase_partition(topic_name, partitions)
            response = get_success_response({"message": "Updated partitions successfully"})
        else:
            response=get_api_response({"message":module_lock_message},403)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing update_topic_increase_partition_request()")
    return response


@request_mapping("POST")
def update_topic_request(request):
    logger.info("Entering update_topic_request()")
    # noinspection PyBroadException
    try:
        from prateek_gupta import configuration_properties, module_lock_message
        enable_kafka = configuration_properties.get("KAFKA_ENABLE", None)
        if enable_kafka and enable_kafka == "S":
            topic_name = request.POST.get("topic_name", "")
            config_name = request.POST.get("config_name", "")
            config_value = request.POST.get("config_value", "")
            update_topic(topic_name, config_name, config_value)
            response = get_success_response({"message": "Updated topic config successfully"})
        else:
            response=get_api_response({"message":module_lock_message},403)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing update_topic_request()")
    return response


@request_mapping("DELETE")
def delete_topic_request(request):
    logger.info("Entering delete_topic_request()")
    # noinspection PyBroadException
    try:
        from prateek_gupta import configuration_properties, module_lock_message
        enable_kafka = configuration_properties.get("KAFKA_ENABLE", None)
        if enable_kafka and enable_kafka == "S":
            topic_name = request.GET.get("topic")
            delete_topic(topic_name)
            response = get_success_response({"message": "Topics deleted successfully"})
        else:
            response=get_api_response({"message":module_lock_message},403)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing delete_topic_request()")
    return response


@request_mapping("GET")
def get_committed_offset_request(request):
    logger.info("Entering get_committed_offset_request()")
    # noinspection PyBroadException
    try:
        from prateek_gupta import configuration_properties, module_lock_message
        enable_kafka = configuration_properties.get("KAFKA_ENABLE", None)
        if enable_kafka and enable_kafka == "S":
            topic_name = request.GET.get("topic")
            partition = request.GET.get("partition")
            group = request.GET.get("group")
            committed_offset = get_committed_offset(topic_name, partition, group)
            response = get_success_response({
                "message": f"Successfully fetched commited offset as {committed_offset}"
                if committed_offset != -1001 else "No committed offset for group"})
        else:
            response=get_api_response({"message":module_lock_message},403)
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing get_committed_offset_request()")
    return response


@request_mapping("POST")
def get_messages_request(request):
    logger.info("Entering get_messages_request()")
    # noinspection PyBroadException
    try:
        from prateek_gupta import configuration_properties, module_lock_message
        enable_kafka = configuration_properties.get("KAFKA_ENABLE", None)
        if enable_kafka and enable_kafka == "S":
            data = request.POST.get("data", "")
            data = json.loads(data)
            messages = get_messages(data)
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
