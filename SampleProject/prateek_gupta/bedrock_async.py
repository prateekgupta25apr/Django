import base64
import json

import aioboto3
import requests

from prateek_gupta.exceptions import *
from prateek_gupta.utils import execute_as_async

local_run = prateek_gupta.local


async def get_bedrock_client():
    logger.info("Entering get_bedrock_client()")
    session = aioboto3.Session()
    creds = await session.get_credentials()
    creds = await creds.get_frozen_credentials()
    async with session.client('bedrock-runtime') as bedrock_client:
        if bedrock_client is None or local_run:
            if all(prateek_gupta.configuration_properties[field] for field in
                   ['AWS_ACCESS_KEY', 'AWS_SECRET_KEY', 'AWS_REGION_NAME']):
                logger.info("Static : Access Key : " +
                            prateek_gupta.configuration_properties['AWS_ACCESS_KEY'] +
                            " ; Secret Key " +
                            prateek_gupta.configuration_properties['AWS_SECRET_KEY'])

                async with session.client(
                        'bedrock-runtime',
                        aws_access_key_id=prateek_gupta.configuration_properties[
                            'AWS_ACCESS_KEY'],
                        aws_secret_access_key=(
                                prateek_gupta.configuration_properties['AWS_SECRET_KEY']),
                        region_name=prateek_gupta.configuration_properties[
                            'AWS_REGION_NAME'],
                ) as bedrock_client_obj:
                    bedrock_client = bedrock_client_obj
            else:
                logger.info("Configs AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY or "
                            "AWS_REGION_NAME are not properly configured")
                bedrock_client = None
        else:
            logger.info("Dynamic : Access Key : " + creds.access_key +
                        " ; Secret Key " + creds.secret_key)

    logger.info("Existing get_bedrock_client()")
    return bedrock_client


async def generate_embedding_for_image(image_url):
    logger.info("Entering generate_embedding_for_image()")
    bedrock_client = await get_bedrock_client()
    async with bedrock_client as bedrock_client:
        if bedrock_client is None:
            raise ServiceException(message="Couldn't establish a connection to AWS")

        response = await execute_as_async(requests.get, image_url)
        base64_image = base64.b64encode(response.content).decode('utf-8')

        request_body = {"inputImage": base64_image}

        response = await bedrock_client.invoke_model(
            modelId="amazon.titan-embed-image-v1",
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json"
        )

        response_body = json.loads(await response['body'].read())
        embedding = response_body.get("embedding", [])

    logger.info("Existing generate_embedding_for_image()")
    return embedding


async def generate_embedding_for_text(text):
    logger.info("Entering generate_embedding_for_text()")
    bedrock_client = await get_bedrock_client()
    async with bedrock_client as bedrock_client:
        if bedrock_client is None:
            raise ServiceException(message="Couldn't establish a connection to AWS")

        request_body = {"inputText": text}

        response = await bedrock_client.invoke_model(
            modelId="amazon.titan-embed-text-v2:0",
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json"
        )

        response_body = json.loads(await response['body'].read())
        embedding = response_body.get("embedding", [])

    logger.info("Existing generate_embedding_for_text()")
    return embedding
