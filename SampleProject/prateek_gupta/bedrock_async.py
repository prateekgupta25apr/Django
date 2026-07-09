import base64
import datetime
import json
import urllib.parse

import aioboto3
import boto3
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

from prateek_gupta.cryptography import (
    hash_sha_256, hmac_sha_256_digest, hmac_sha_256_hex)
from prateek_gupta.exceptions import *
from prateek_gupta.utils import execute_as_async

local_run = prateek_gupta.local
configuration_properties = prateek_gupta.configuration_properties


def _get_aws_credentials():
    access_key = configuration_properties.get('AWS_ACCESS_KEY')
    secret_key = configuration_properties.get('AWS_SECRET_KEY')
    region = configuration_properties.get('AWS_REGION_NAME')
    if not all([access_key, secret_key, region]):
        raise ServiceException(message="Couldn't establish a connection to AWS")
    return access_key, secret_key, region


def _prepare_request_context(
        url, payload, request_method, request_content_type):
    if isinstance(payload, dict):
        payload = json.dumps(payload)

    time_val = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    date_val = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d')
    payload_hash = hash_sha_256(payload)

    host = "host"
    accept = "accept"
    content_length = "content-length"
    content_type = "content-type"
    x_content = "x-amz-content-sha256"
    x_date = "x-amz-date"
    headers_config = {
        accept: "application/json",
        host: urllib.parse.urlparse(url).hostname,
        content_length: str(len(payload.encode("utf-8"))),
        content_type: request_content_type,
        x_content: payload_hash,
        x_date: time_val,
    }
    signed_headers = [accept, host, content_length, content_type, x_content, x_date]
    return (payload, time_val, date_val, payload_hash, headers_config,
            signed_headers, request_content_type, request_method)


async def _execute_api_call(url, headers, payload, request_method):
    if request_method == "POST":
        response = await execute_as_async(requests.post, url, headers=headers, data=payload)
    else:
        response = await execute_as_async(requests.get, url, headers=headers)
    try:
        return response.json()
    except Exception:
        return {"status_code": response.status_code, "text": response.text}


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


async def generate_signed_headers_manually(
        url, payload, request_method="POST", request_content_type="application/json",
        service_name="bedrock", api_call=False):
    logger.info("Entering generate_signed_headers_manually()")

    access_key, secret_key, region = _get_aws_credentials()

    (payload, time_val, date_val, payload_hash, headers_config,
     signed_headers, request_content_type, request_method) = _prepare_request_context(
        url, payload, request_method, request_content_type)

    srg_signed_headers = sorted(signed_headers)

    canonical_str = (f'{request_method}\n'
                     f'{urllib.parse.quote(urllib.parse.urlparse(url).path)}\n\n')

    for header in srg_signed_headers:
        canonical_str += f'{header}:{headers_config[header]}\n'

    canonical_str += f"\n{';'.join(srg_signed_headers)}\n{payload_hash}"
    canonical_hash = hash_sha_256(canonical_str)

    str_to_sign = (
        f'AWS4-HMAC-SHA256\n{time_val}\n{date_val}/{region}/{service_name}/'
        f'aws4_request\n{canonical_hash}'
    )

    def sign(key, msg):
        return hmac_sha_256_digest(key, msg)

    def get_signing_key(arg_secret_key, arg_date, arg_region, arg_service):
        k_date = sign(("AWS4" + arg_secret_key).encode("utf-8"), arg_date)
        k_region = sign(k_date, arg_region)
        k_service = sign(k_region, arg_service)
        k_signing = sign(k_service, "aws4_request")
        return k_signing

    def generate_signature(
            arg_secret_key, arg_date, arg_region, service, string_to_sign):
        signing_key = get_signing_key(arg_secret_key, arg_date, arg_region, service)
        return hmac_sha_256_hex(signing_key, string_to_sign)

    signature = generate_signature(
        secret_key,
        date_val,
        region,
        service_name,
        str_to_sign
    )

    signed_headers_response = {
        "accept": headers_config["accept"],
        "host": headers_config["host"],
        "content-type": request_content_type,
        "content-length": headers_config["content-length"],
        "X-Amz-Content-Sha256": payload_hash,
        "X-Amz-Date": time_val,
        "Authorization": (
            f"AWS4-HMAC-SHA256 "
            f"Credential={access_key}/{date_val}/{region}/{service_name}/aws4_request,"
            f"SignedHeaders={';'.join(srg_signed_headers)},"
            f"Signature={signature}")
    }

    result = {"signed_headers": signed_headers_response}
    if api_call:
        result["api_response"] = await _execute_api_call(
            url, signed_headers_response, payload, request_method)

    logger.info("Existing generate_signed_headers_manually()")
    return result


async def generate_signed_headers_using_built_in(
        url, payload, request_method="POST", request_content_type="application/json",
        service_name="bedrock", api_call=False):
    logger.info("Entering generate_signed_headers_using_built_in()")

    access_key, secret_key, region = _get_aws_credentials()

    (payload, time_val, date_val, payload_hash, headers_config,
     signed_headers, request_content_type, request_method) = _prepare_request_context(
        url, payload, request_method, request_content_type)

    arg_signed_headers = sorted(signed_headers)
    arg_headers = {}
    for header in arg_signed_headers:
        arg_headers[header] = headers_config[header]

    if request_method == "POST":
        request = AWSRequest(
            method=request_method, url=url, headers=arg_headers, data=payload)
    else:
        request = AWSRequest(method=request_method, url=url, headers=arg_headers)

    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key)
    creds = session.get_credentials()
    frozen_creds = creds.get_frozen_credentials()
    SigV4Auth(frozen_creds, service_name, region).add_auth(request)

    signed_headers_response = dict(request.headers)
    result = {"signed_headers": signed_headers_response}
    if api_call:
        result["api_response"] = await _execute_api_call(
            url, signed_headers_response, payload, request_method)

    logger.info("Existing generate_signed_headers_using_built_in()")
    return result
