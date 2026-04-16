import boto3
from botocore.config import Config

from prateek_gupta import post_construct_method
from prateek_gupta.exceptions import *
from prateek_gupta.schedule_task import ScheduledTask

local_run = prateek_gupta.local

queue_names = ["test_queue"]
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
    return queue_url


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
        WaitTimeSeconds=20  # long polling
    )
    messages = response.get("Messages", [])

    for msg in messages:
        print("Received message :: ", msg["Body"])

        # delete after processing
        receiver.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=msg["ReceiptHandle"]
        )


def get_all_queues():
    logger.info("Entering get_all_queues()")
    sqs_client = get_sqs_client()
    sqs_queues_raw = sqs_client.list_queues()
    sqs_queues = []
    for queue in sqs_queues_raw['QueueUrls']:
        queue: str = queue.split('/')[-1]
        sqs_queues.append(queue)
    return sqs_queues


def send_message(queue_name, message):
    logger.info("Entering send_message()")
    sqs_client = get_sqs_client()
    queue_url = get_queue_url(queue_name)
    response = sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=message
    )
    return response
