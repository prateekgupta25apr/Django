import boto3
from botocore.config import Config

from prateek_gupta import post_construct_method
from prateek_gupta.exceptions import *
from prateek_gupta.schedule_task import ScheduledTask

local_run = prateek_gupta.local

queue_names = []
queue_name_url_map = {}
queue_task_map = {}


def get_sqs_client():
    from prateek_gupta import configuration_properties
    logger.info("Entering get_sqs_client()")
    config = Config(signature_version="s3v4")
    session = boto3.Session()
    sqs_client = session.client('sqs', config=config)
    creds = session.get_credentials()

    if sqs_client is None or local_run:
        if all(configuration_properties[field] for field in
               ['AWS_ACCESS_KEY', 'AWS_SECRET_KEY', 'AWS_REGION_NAME']):
            logger.info("Static : Access Key : " +
                        configuration_properties['AWS_ACCESS_KEY'] +
                        " ; Secret Key " +
                        configuration_properties['AWS_SECRET_KEY'])

            sqs_client = session.client(
                'sqs',
                aws_access_key_id=configuration_properties['AWS_ACCESS_KEY'],
                aws_secret_access_key=configuration_properties['AWS_SECRET_KEY'],
                region_name=configuration_properties['AWS_REGION_NAME'],
            )
        else:
            logger.info("Configs AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY or "
                        "AWS_S3_REGION_NAME are not properly configured")
            sqs_client = None
    else:
        logger.info("Dynamic : Access Key : " + creds.access_key +
                    " ; Secret Key " + creds.secret_key)

    logger.info("Existing get_sqs_client()")
    return sqs_client


def get_queue_url(queue_name):
    logger.info("Entering get_queue_url()")
    queue_url = queue_name_url_map.get(queue_name, None)
    if queue_url is None:
        sqs_client = get_sqs_client()
        queue_url = sqs_client.get_queue_url(QueueName=queue_name)
        queue_url = queue_url["QueueUrl"]
        queue_name_url_map[queue_name] = queue_url
    logger.info("Exiting get_queue_url()")
    return queue_url


def is_queue_exists(queue_name):
    logger.info("Entering is_queue_exists()")
    # noinspection PyBroadException
    try:
        if get_queue_url(queue_name):
            result = True
        else:
            result = False
    except Exception:
        result = False
    logger.info("Exiting is_queue_exists()")
    return result


@post_construct_method()
def setup_sync_sqs():
    from prateek_gupta import configuration_properties
    enable_sqs = configuration_properties.get("SQS_ENABLE", None)
    if enable_sqs and enable_sqs == "S":
        logger.info("Starting Sync SQS Receivers")

        for queue in queue_names:
            schedule_messages_polling(queue, True)

        logger.info("Started Sync SQS Receivers")


def schedule_messages_polling(queue_name, is_added):
    """We are using scheduled future concept for polling message because it provides better
    control for polling messages over while loop as I can cancel the task anytime using
    the method cancel()"""
    if is_added:
        sqs_client = get_sqs_client()

        task = ScheduledTask(
            1, False, poll_messages, sqs_client, queue_name)
        task.start()
        queue_task_map[queue_name] = task
    else:
        task: ScheduledTask = queue_task_map[queue_name]
        task.cancel()
        del queue_task_map[queue_name]


def poll_messages(receiver, queue_name):
    queue_url = get_queue_url(queue_name)
    response = receiver.receive_message(
        QueueUrl=queue_url,
        WaitTimeSeconds=20
    )
    messages = response.get("Messages", [])

    for msg in messages:
        print("Received message :: ", msg["Body"])

        # delete after processing
        receiver.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=msg["ReceiptHandle"]
        )


def send_message(queue_name, message):
    logger.info("Entering send_message()")
    sqs_client = get_sqs_client()
    queue_url = get_queue_url(queue_name)
    response = sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=message
    )
    return response["MessageId"]


def get_all_queues():
    logger.info("Entering get_all_queues()")
    sqs_client = get_sqs_client()
    sqs_queues_raw = sqs_client.list_queues()
    sqs_queues = []
    for queue in sqs_queues_raw['QueueUrls']:
        queue: str = queue.split('/')[-1]
        sqs_queues.append(queue)
    return sqs_queues


def get_queue(queue_name):
    logger.info("Entering get_queue()")
    sqs_client = get_sqs_client()
    queue_url = get_queue_url(queue_name)
    response = sqs_client.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=["All"]
    )

    attributes = response.get("Attributes", {})

    logger.info("Exiting get_queue()")
    return attributes


def create_queue(
        queue_name, visibility_timeout="30", retention_period="86400"):
    logger.info("Entering create_queue()")
    sqs_client = get_sqs_client()
    response = sqs_client.create_queue(
        QueueName=queue_name,
        Attributes={
            "VisibilityTimeout": visibility_timeout,
            "MessageRetentionPeriod": retention_period
        }
    )
    queue_name_url_map[queue_name] = response["QueueUrl"]


def update_queue(queue_name, attribute_name, attribute_value):
    logger.info("Entering update_queue()")
    sqs_client = get_sqs_client()
    queue_url = get_queue_url(queue_name)
    sqs_client.set_queue_attributes(
        QueueUrl=queue_url,
        Attributes={attribute_name: attribute_value}
    )
    logger.info("Exiting update_queue()")


def delete_queue(queue_name):
    logger.info("Entering delete_queue()")
    sqs_client = get_sqs_client()
    queue_url = get_queue_url(queue_name)
    sqs_client.delete_queue(QueueUrl=queue_url)
    logger.info("Exiting delete_queue()")


def update_queues(queue, is_added):
    if is_added:
        queue_names.append(queue)
        schedule_messages_polling(queue, True)
        logger.info(f"Started listening for messages to the queue :  {queue}")
    else:
        queue_names.remove(queue)
        schedule_messages_polling(queue, False)
        logger.info(f"Stopped listening for messages to the queue :  {queue}")


def get_messages(queue_name):
    queue_url = get_queue_url(queue_name)
    receiver = get_sqs_client()
    received_messages = []

    response = receiver.receive_message(
        QueueUrl=queue_url,
        WaitTimeSeconds=20
    )
    while response.get("Messages", []):

        messages = response.get("Messages", [])

        for msg in messages:
            received_messages.append({"message_id": msg["MessageId"], "body": msg["Body"]})

        response = receiver.receive_message(
            QueueUrl=queue_url,
            WaitTimeSeconds=20
        )

    return received_messages
