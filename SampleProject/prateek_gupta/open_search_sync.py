import json

from opensearchpy import OpenSearch, NotFoundError, helpers

from prateek_gupta import configuration_properties


def get_client():
    return OpenSearch(
        hosts=[{'host': configuration_properties.get("OPEN_SEARCH_HOST"),
                'port': configuration_properties.get("OPEN_SEARCH_PORT")}],
        use_ssl=True
    )


def get_index(index_name):
    client = get_client()
    if client.indices.exists(index=index_name):
        response = client.indices.get(index=index_name)
        response = response.get(index_name, {})
        response = {"aliases": response.get("aliases", {}),
                    "mappings": response.get("mappings", {}).get("properties", {}),
                    "settings": response.get("settings", {}).get("index", {})
                    }
    else:
        response = None
    return response


def create_index(index_name, body):
    client = get_client()
    if not client.indices.exists(index=index_name):
        response = client.indices.create(index=index_name, body=body)
    else:
        response = None
    return response


def update_index(index_name, settings=None, add_alias=None,
                 remove_alias=None, mappings=None):
    result = {}
    client = get_client()

    if client.indices.exists(index=index_name):
        response = None

        if settings:
            response = client.indices.put_settings(index=index_name, body=settings)

        if add_alias or remove_alias:
            actions = []
            if add_alias:
                actions.append({"add": {"index": index_name, "alias": add_alias}})
            if remove_alias:
                actions.append({"remove": {"index": index_name, "alias": remove_alias}})
            response = client.indices.update_aliases(body={"actions": actions})

        if mappings:
            response = client.indices.put_mapping(index=index_name, body=mappings)

        result["message"] = "Index updated successfully" if response \
            else "Nothing to update"
    else:
        result["message"] = "Index doesn't exist"

    return result


def delete_index(index_name):
    client = get_client()
    if client.indices.exists(index=index_name):
        response = client.indices.delete(index=index_name)
    else:
        response = None
    return response


def get_record(index_name, record_id):
    client = get_client()
    response = {}
    if client.indices.exists(index=index_name):
        try:
            response = client.get(index=index_name, id=record_id)
            if response.get("found"):
                response = response["_source"]
        except NotFoundError:
            response["message"] = "Record not found"
    else:
        response = None
    return response


def upsert_record(index_name, record_id, data, bulk=False):
    result = {}
    client = get_client()
    if client.indices.exists(index=index_name):
        if not bulk:
            response = client.index(index=index_name, id=record_id, body=data)
            result["result"] = response.get("result")
        else:
            actions = [{
                "_op_type": "index",
                "_index": index_name,
                "_id": record_id,
                "_source": data
            }]
            result["result"] = "bulk index success"
            result["details"] = helpers.bulk(client, actions)
    else:
        result["message"] = "Index doesn't exist"
    return result


def partial_update_record(index_name, record_id, data,
                          bulk=False):
    result = {}
    client = get_client()
    if client.indices.exists(index=index_name):
        if not bulk:
            response = client.update(index=index_name, id=record_id,
                                     body={"doc": json.loads(data)})
            result["result"] = response.get("result")
        else:
            actions = [{
                "_op_type": "update",
                "_index": index_name,
                "_id": record_id,
                "doc": json.loads(data)
            }]
            result["result"] = "bulk update success"
            result["details"] = helpers.bulk(client, actions)
    else:
        result["message"] = "Index doesn't exist"
    return result


def delete_record(index_name, record_id, bulk=False):
    result = {}
    client = get_client()
    if client.indices.exists(index=index_name):
        if not bulk:
            response = client.delete(index=index_name, id=record_id)
            result["result"] = response.get("result")
        else:
            actions = [{
                "_op_type": "delete",
                "_index": index_name,
                "_id": record_id
            }]
            result["result"] = "bulk delete success"
            result["details"] = helpers.bulk(client, actions)
    else:
        result["message"] = "Index doesn't exist"
    return result


def search_record(index_name, search_json):
    client = get_client()
    response = client.search(index=index_name, body=json.loads(search_json))
    return response


def count_record(index_name, search_json):
    client = get_client()
    response = client.count(index=index_name, body=json.loads(search_json))
    return response


def delete_by_query_record(index_name, search_json):
    client = get_client()
    response = client.delete_by_query(index=index_name, body=json.loads(search_json))
    return response
