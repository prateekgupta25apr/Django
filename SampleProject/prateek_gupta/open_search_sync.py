from opensearchpy import OpenSearch

from prateek_gupta import configuration_properties


def get_client():
    return OpenSearch(
        hosts=[{'host': configuration_properties.get("OPEN_SEARCH_HOST"),
                'port': configuration_properties.get("OPEN_SEARCH_PORT")}],
        use_ssl=True
    )


def get_index(index_name):
    client = get_client()
    response = client.indices.get(index=index_name)
    return response.get(index_name, {})
