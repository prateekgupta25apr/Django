from confluent_kafka import Consumer, Producer, ConsumerGroupTopicPartitions
from confluent_kafka.admin import AdminClient, ConfigResource
from confluent_kafka.cimpl import NewTopic, NewPartitions, TopicPartition

from prateek_gupta import pre_construct_method
from prateek_gupta.LogManager import logger

global_consumer = None

def get_consumer(topics=None, group_id=None):
    from prateek_gupta import configuration_properties
    config = {
        "bootstrap.servers": configuration_properties.get("KAFKA_BROKER"),
        "group.id": (group_id if group_id
                     else configuration_properties.get("KAFKA_CONSUMER_GROUP"))
    }

    if configuration_properties.get("KAFKA_SECURITY_PROTOCOL", ""):
        config["security.protocol"] = configuration_properties.get("KAFKA_SECURITY_PROTOCOL")

    if configuration_properties.get("KAFKA_SASL_MECHANISM", ""):
        config["sasl.mechanism"] = configuration_properties.get("KAFKA_SASL_MECHANISM")

    if configuration_properties.get("KAFKA_SASL_USERNAME", ""):
        config["sasl.username"] = configuration_properties.get("KAFKA_SASL_USERNAME")

    if configuration_properties.get("KAFKA_SASL_PASSWORD", ""):
        config["sasl.password"] = configuration_properties.get("KAFKA_SASL_PASSWORD")

    consumer = Consumer(config)
    if topics:
        consumer.subscribe(topics)
    return consumer


def get_producer():
    from prateek_gupta import configuration_properties
    config = {
        "bootstrap.servers": configuration_properties.get("KAFKA_BROKER")
    }

    if configuration_properties.get("KAFKA_SECURITY_PROTOCOL", ""):
        config["security.protocol"] = configuration_properties.get("KAFKA_SECURITY_PROTOCOL")

    if configuration_properties.get("KAFKA_SASL_MECHANISM", ""):
        config["sasl.mechanism"] = configuration_properties.get("KAFKA_SASL_MECHANISM")

    if configuration_properties.get("KAFKA_SASL_USERNAME", ""):
        config["sasl.username"] = configuration_properties.get("KAFKA_SASL_USERNAME")

    if configuration_properties.get("KAFKA_SASL_PASSWORD", ""):
        config["sasl.password"] = configuration_properties.get("KAFKA_SASL_PASSWORD")

    return Producer(config)


def get_admin_client():
    from prateek_gupta import configuration_properties
    config = {
        "bootstrap.servers": configuration_properties.get("KAFKA_BROKER")
    }

    if configuration_properties.get("KAFKA_SECURITY_PROTOCOL", ""):
        config["security.protocol"] = configuration_properties.get("KAFKA_SECURITY_PROTOCOL")

    if configuration_properties.get("KAFKA_SASL_MECHANISM", ""):
        config["sasl.mechanism"] = configuration_properties.get("KAFKA_SASL_MECHANISM")

    if configuration_properties.get("KAFKA_SASL_USERNAME", ""):
        config["sasl.username"] = configuration_properties.get("KAFKA_SASL_USERNAME")

    if configuration_properties.get("KAFKA_SASL_PASSWORD", ""):
        config["sasl.password"] = configuration_properties.get("KAFKA_SASL_PASSWORD")

    return AdminClient(config)


@pre_construct_method(["test"])
def setup_sync_kafka(topics):
    print("TESTING :: SYNC Kafka")
    from prateek_gupta import configuration_properties
    enable_kafka = configuration_properties.get("KAFKA_ENABLE", None)
    if enable_kafka and enable_kafka=="S":
        logger.info("Setting up sync kafka")
        global global_consumer
        global_consumer = get_consumer(topics=topics)

        while global_consumer is not None:
            msg = global_consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error(msg.error())
                continue
            # noinspection PyArgumentList
            logger.info(f"Received message: {msg.value()}")


def send(topic, message):
    def method_to_be_callback(err, msg):
        if err is not None:
            logger.error(f'Message delivery failed: {err}')
        else:
            logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    producer = get_producer()
    producer.produce(topic, message, callback=method_to_be_callback)
    producer.flush()


def get_all_topics():
    admin_client = get_admin_client()
    metadata = admin_client.list_topics(timeout=10)

    topics = list(metadata.topics.keys())

    return topics


def get_topic(topic_name):
    response = dict()
    response["topicName"] = topic_name
    admin_client = get_admin_client()

    consumer = get_consumer()

    # Get partitions
    metadata = consumer.list_topics(topic=topic_name)
    partitions = metadata.topics[topic_name].partitions.keys()

    partition_details = {}
    topic_partitions = [TopicPartition(topic_name, p) for p in partitions]

    # Get the earliest offsets
    consumer.assign(topic_partitions)

    for tp in topic_partitions:
        low, high = consumer.get_watermark_offsets(tp, timeout=5.0)
        partition_details[tp.partition] = {
            'earliest_offset': low,
            'latest_offset': high,
            'message_count': high - low
        }

    consumer.close()
    response["partitions"] = partition_details

    # Get retention.ms
    config_resource = ConfigResource(ConfigResource.Type.TOPIC, topic_name)
    configs = admin_client.describe_configs([config_resource])

    for res, future in configs.items():
        config = future.result()
        response["retention.ms"] = config.get('retention.ms', None).value

    return response


def create_topic(topic_name, partitions, replication_factor):
    new_topic = NewTopic(topic_name, int(partitions), int(replication_factor))

    admin_client = get_admin_client()
    future = admin_client.create_topics([new_topic])

    for topic, future in future.items():
        try:
            future.result()
        except Exception as e:
            raise e


def update_topic_increase_partition(
        topic_name, new_partition_count):
    admin_client = get_admin_client()

    # Increase partitions
    futures = admin_client.create_partitions(
        [NewPartitions(new_total_count=int(new_partition_count), topic=topic_name)])

    # Handle results
    for topic, future in futures.items():
        try:
            future.result()
        except Exception as e:
            raise e


def update_topic(topic_name, config_key, config_value):
    admin_client = get_admin_client()

    # Create a ConfigResource for the topic
    resource = ConfigResource(ConfigResource.Type.TOPIC, topic_name)

    # Set the new configuration
    resource.set_config(config_key, config_value)

    # Call alter_configs
    futures = admin_client.alter_configs([resource])

    # Handle results
    for topic, future in futures.items():
        try:
            future.result()
        except Exception as e:
            raise e


def delete_topic(topic_name):
    admin_client = get_admin_client()

    # Delete the topic
    futures = admin_client.delete_topics([topic_name])

    # Handle results
    for topic, future in futures.items():
        try:
            future.result()
        except Exception as e:
            raise e


def get_committed_offset(topic, partition_id, group_id):
    admin_client = get_admin_client()

    tp = TopicPartition(topic, int(partition_id))
    cg_tp = ConsumerGroupTopicPartitions(group_id, [tp])

    # Request committed offsets
    group_offsets = admin_client.list_consumer_group_offsets([cg_tp])
    return group_offsets[group_id].result().topic_partitions[0].offset


def get_messages(payload: dict):
    partitions = list()
    partition_limit = {}
    consumer = get_consumer()
    for topic, partitions_details in payload.items():
        for partition in partitions_details:
            partitions.append(TopicPartition(topic, partition.get("partitionId"),
                                             partition.get("offset", 0)))
            topic_key = f'{topic}-{partition.get("partitionId")}'
            partition_limit[topic_key] = partition.get("limit", -1)

            if partition_limit[topic_key] == -1:
                _, limit = consumer.get_watermark_offsets(
                    TopicPartition(topic, partition.get("partitionId")))
                partition_limit[topic_key] = limit

    consumer.assign(partitions)

    partition_message_mapping = {}
    empty_poll_count=0
    max_empty_poll_count=5
    while True:
        if not partition_limit:
            break
        msg = consumer.poll(1.0)

        if not msg:
            empty_poll_count += 1
            if empty_poll_count >= max_empty_poll_count:
                break
            else:
                continue

        topic_key = f'{msg.topic()}-{msg.partition()}'

        if topic_key not in partition_limit:
            continue

        if (len(partition_message_mapping.get(topic_key, list())) <
                partition_limit[topic_key]):
            partition_messages = partition_message_mapping.get(topic_key, list())
            # noinspection PyArgumentList
            partition_messages.append(
                {"offset": msg.offset(), "key": msg.key(),
                 "value": msg.value().decode('utf-8')})
            partition_message_mapping[topic_key] = partition_messages

        if (len(partition_message_mapping.get(topic_key, list())) >=
                partition_limit[topic_key]):
            del partition_limit[topic_key]

    response = {}
    for key, value in partition_message_mapping.items():
        topic, partition = key.split("-")
        topic_messages = response.get(topic, {})
        topic_messages[partition] = value
        response[topic] = topic_messages

    return response
