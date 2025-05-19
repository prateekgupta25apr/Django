from opensearchpy import AsyncOpenSearch

from prateek_gupta import configuration_properties


async def get_client():
    return AsyncOpenSearch(
        hosts=[{'host': configuration_properties.get("OPEN_SEARCH_HOST"),
                'port': int(configuration_properties.get("OPEN_SEARCH_PORT"))}],
        use_ssl=True
    )


async def get_index(index_name):
    client = await get_client()
    response = await client.indices.get(index=index_name)
    return response.get(index_name, {})
