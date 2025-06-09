import logging
import ssl

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.structs import RecordMetadata, TopicPartition

from prateek_gupta.LogManager import logger

global_consumer=None

def get_consumer(topics=None, group_id=None):
    from prateek_gupta import configuration_properties
    config = {
        "bootstrap_servers": configuration_properties.get("KAFKA_BROKER"),
        "group_id": (group_id if group_id
                     else configuration_properties.get("KAFKA_CONSUMER_GROUP"))
    }

    if configuration_properties.get("KAFKA_SECURITY_PROTOCOL", ""):
        config["security_protocol"] = configuration_properties.get("KAFKA_SECURITY_PROTOCOL")
        ssl_context = ssl.create_default_context(
            cafile=configuration_properties.get("KAFKA_AWS_CA_FILE_PATH")
        )
        config["ssl_context"] = ssl_context

    if configuration_properties.get("KAFKA_SASL_MECHANISM", ""):
        config["sasl_mechanism"] = configuration_properties.get("KAFKA_SASL_MECHANISM")

    if configuration_properties.get("KAFKA_SASL_USERNAME", ""):
        config["sasl_plain_username"] = configuration_properties.get("KAFKA_SASL_USERNAME")

    if configuration_properties.get("KAFKA_SASL_PASSWORD", ""):
        config["sasl_plain_password"] = configuration_properties.get("KAFKA_SASL_PASSWORD")

    if topics:
        return AIOKafkaConsumer(*topics, **config)
    else:
        return AIOKafkaConsumer(**config)


def get_producer():
    from prateek_gupta import configuration_properties
    config = {
        "bootstrap_servers": configuration_properties.get("KAFKA_BROKER")
    }

    if configuration_properties.get("KAFKA_SECURITY_PROTOCOL", ""):
        config["security_protocol"] = configuration_properties.get("KAFKA_SECURITY_PROTOCOL")
        ssl_context = ssl.create_default_context(
            cafile=configuration_properties.get("KAFKA_AWS_CA_FILE_PATH")
        )
        config["ssl_context"] = ssl_context

    if configuration_properties.get("KAFKA_SASL_MECHANISM", ""):
        config["sasl_mechanism"] = configuration_properties.get("KAFKA_SASL_MECHANISM")

    if configuration_properties.get("KAFKA_SASL_USERNAME", ""):
        config["sasl_plain_username"] = configuration_properties.get("KAFKA_SASL_USERNAME")

    if configuration_properties.get("KAFKA_SASL_PASSWORD", ""):
        config["sasl_plain_password"] = configuration_properties.get("KAFKA_SASL_PASSWORD")

    return AIOKafkaProducer(**config)


async def setup_async_kafka(topics):
    logger.info("Setting up async kafka")

    # To log only warnings n errors from aiokafka
    logging.getLogger("aiokafka").setLevel(logging.WARNING)

    global global_consumer
    global_consumer = get_consumer(topics=topics)
    await global_consumer.start()
    try:
        async for msg in global_consumer:
            if global_consumer is None:
                break
            logger.info(f"Received: {msg.value.decode()} from offset {msg.offset}")
    finally:
        await global_consumer.stop()


async def send(topic, message: str):
    producer = get_producer()
    await producer.start()
    try:
        meta_data: RecordMetadata = await producer.send_and_wait(topic, message.encode())
        logger.info("Message sent to topic : " + meta_data.topic)
    finally:
        await producer.stop()


async def get_all_topics():
    consumer = get_consumer()
    await consumer.start()
    try:
        # Fetch the metadata
        # noinspection PyProtectedMember
        metadata = await consumer._client.fetch_all_metadata()
        topics = metadata.topics()
        return list(topics)
    finally:
        await consumer.stop()


async def get_topic(topic_name):
    consumer = get_consumer(topics=[topic_name])
    await consumer.start()
    response = {}
    try:
        # Get partitions for the topic
        partitions = consumer.partitions_for_topic(topic_name)
        if not partitions:
            return f"Topic '{topic_name}' not found or has no partitions."

        response["topicName"] = topic_name

        topic_partitions = [TopicPartition(topic_name, p) for p in partitions]

        # Fetch the earliest offsets
        beginning_offsets = await consumer.beginning_offsets(topic_partitions)
        # Fetch latest offsets
        end_offsets = await consumer.end_offsets(topic_partitions)

        partitions = {}
        for tp in topic_partitions:
            partitions[tp.partition] = {
                "earliest_offset": beginning_offsets.get(tp),
                "latest_offset": end_offsets.get(tp),
                "message_count": end_offsets.get(tp) - beginning_offsets.get(tp)
            }

        response["partitions"] = partitions
        # Note: aiokafka doesn't provide methods to extract config "retention.ms"
        return response
    finally:
        await consumer.stop()


# Kafka doesn't provide methods for following
# Creating a topic
# Increasing the number of partitions of a topic
# Updating topic configurations (like retention.ms)
# Deleting a topic


async def get_committed_offset(
        topic_name, partition_id, group_id):
    consumer = get_consumer(topics=[topic_name], group_id=group_id)
    await consumer.start()
    try:
        return await consumer.committed(TopicPartition(topic_name, int(partition_id)))
    finally:
        await consumer.stop()


async def get_messages(payload: dict):
    partition_mapping = {}
    consumer = get_consumer()
    await consumer.start()
    try:
        for topic, partitions_details in payload.items():
            for partition in partitions_details:
                topic_partition = TopicPartition(topic, partition.get("partitionId"))
                partition_mapping[topic_partition] = [partition.get("offset", 0),
                                                      partition.get("limit", -1)]

                if partition_mapping[topic_partition][1] == -1:
                    partition_mapping[topic_partition][1] = (await consumer.end_offsets(
                        [topic_partition])).get(topic_partition)

        consumer.assign(list(partition_mapping.keys()))

        for topic_partition, values in partition_mapping.items():
            consumer.seek(topic_partition, values[0])

        partition_message_mapping = {}
        while True:
            if not partition_mapping:
                break

            msg = await consumer.getone()

            if not msg:
                continue

            topic_partition = TopicPartition(msg.topic, msg.partition)

            if topic_partition not in partition_mapping:
                continue

            if (len(partition_message_mapping.get(topic_partition, list())) <
                    partition_mapping[topic_partition][1]):
                partition_messages = partition_message_mapping.get(topic_partition, list())
                # noinspection PyArgumentList
                partition_messages.append(
                    {"offset": msg.offset, "key": msg.key,
                     "value": msg.value.decode('utf-8')})
                partition_message_mapping[topic_partition] = partition_messages

            if (len(partition_message_mapping.get(topic_partition, list())) >=
                    partition_mapping[topic_partition][1]):
                del partition_mapping[topic_partition]

        response = {}
        for key, value in partition_message_mapping.items():
            topic_messages = response.get(key.topic, {})
            topic_messages[key.partition] = value
            response[key.topic] = topic_messages

        return response
    finally:
        await consumer.stop()
