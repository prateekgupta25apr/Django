import json

from opensearchpy import AsyncOpenSearch, NotFoundError
from opensearchpy._async import helpers

from prateek_gupta import configuration_properties


async def get_client():
    return AsyncOpenSearch(
        hosts=[{'host': configuration_properties.get("OPEN_SEARCH_HOST"),
                'port': int(configuration_properties.get("OPEN_SEARCH_PORT"))}],
        use_ssl=True
    )


async def get_index(index_name):
    client = await get_client()
    if await client.indices.exists(index=index_name):
        response = await client.indices.get(index=index_name)
        response = response.get(index_name, {})
        response = {"aliases": response.get("aliases", {}),
                    "mappings": response.get("mappings", {}).get("properties", {}),
                    "settings": response.get("settings", {}).get("index", {})
                    }
    else:
        response = None
    return response


async def create_index(index_name, body):
    client = await get_client()
    if not await client.indices.exists(index=index_name):
        response = await client.indices.create(index=index_name, body=body)
    else:
        response = None
    return response


async def update_index(index_name, settings=None, add_alias=None,
                       remove_alias=None, mappings=None):
    result = {}
    client = await get_client()

    if client.indices.exists(index=index_name):
        response = None

        if settings:
            response = await client.indices.put_settings(index=index_name, body=settings)

        if add_alias or remove_alias:
            actions = []
            if add_alias:
                actions.append({"add": {"index": index_name, "alias": add_alias}})
            if remove_alias:
                actions.append({"remove": {"index": index_name, "alias": remove_alias}})
            response = await client.indices.update_aliases(body={"actions": actions})

        if mappings:
            response = await client.indices.put_mapping(index=index_name, body=mappings)

        result["message"] = "Index updated successfully" if response \
            else "Nothing to update"
    else:
        result["message"] = "Index doesn't exist"

    return result


async def delete_index(index_name):
    client = await get_client()
    if await client.indices.exists(index=index_name):
        response = await client.indices.delete(index=index_name)
    else:
        response = None
    return response


async def get_record(index_name, record_id):
    client = await get_client()
    response = {}
    if client.indices.exists(index=index_name):
        try:
            response = await client.get(index=index_name, id=record_id)
            if response.get("found"):
                response = response["_source"]
        except NotFoundError:
            response["message"] = "Record not found"
    else:
        response = None
    return response


async def upsert_record(index_name, record_id, data, bulk=False):
    result = {}
    client = await get_client()
    if await client.indices.exists(index=index_name):
        if not bulk:
            response = await client.index(index=index_name, id=record_id, body=data)
            result["result"] = response.get("result")
        else:
            result["result"] = "Async bulk not implemented directly"
    else:
        result["message"] = "Index doesn't exist"
    return result


async def partial_update_record(index_name, record_id, data,
                                bulk=False):
    result = {}
    client = await get_client()
    if await client.indices.exists(index=index_name):
        if not bulk:
            response = await client.update(index=index_name, id=record_id,
                                           body={"doc": json.loads(data)})
            result["result"] = response.get("result")
        else:
            result["result"] = "Async bulk not implemented directly"
    else:
        result["message"] = "Index doesn't exist"
    return result


async def delete_record(index_name, record_id, bulk=False):
    result = {}
    client = await get_client()
    if await client.indices.exists(index=index_name):
        if not bulk:
            response = await client.delete(index=index_name, id=record_id)
            result["result"] = response.get("result")
        else:
            result["result"] = "Async bulk not implemented directly"
    else:
        result["message"] = "Index doesn't exist"
    return result
