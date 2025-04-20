import json

from redis.asyncio import Redis

hash_name = "mapped_key_values"


def format_value(value):
    if not value:
        return None

    # noinspection PyBroadException
    try:
        return json.loads(value.decode())
    except Exception:
        return value.decode()


def get_redis_instance():
    from prateek_gupta import configuration_properties
    config = {"host": configuration_properties.get("REDIS_HOST"),
              "port": configuration_properties.get("REDIS_PORT")}

    if configuration_properties.get("REDIS_SSL"):
        config["ssl"] = configuration_properties.get("REDIS_SSL")

    if configuration_properties.get("REDIS_PASSWORD"):
        config["password"] = configuration_properties.get("REDIS_PASSWORD")
    return Redis(**config)


async def get_value(key: str, use_map: bool):
    client = get_redis_instance()
    if use_map:
        # noinspection PyTypeChecker
        value: bytes = await client.hget(hash_name, key)
    else:
        value: bytes = await client.get(key)

    if not value:
        return None

    # noinspection PyBroadException
    try:
        return json.loads(value.decode())
    except Exception:
        return value.decode()


async def upsert(key: str, value: str, use_map: bool):
    client = get_redis_instance()
    if use_map:
        await client.hset(hash_name, key, value)
    else:
        await client.set(key, value)


async def search_keys(pattern):
    client = get_redis_instance()
    cursor = 0
    response = dict()
    while True:
        cursor, keys = await client.scan(cursor=cursor, match=pattern)
        for key in keys:
            if (await client.type(key)).decode() == "hash":
                map_key_values = dict()
                for k, v in (await client.hgetall(key)).items():
                    map_key_values[k.decode()] = format_value(v)
                response[key.decode()] = map_key_values
            else:
                response[key.decode()] = format_value(await client.get(key))
        if cursor == 0:
            break

    return response


async def delete_value(key: str, use_map: bool):
    client = get_redis_instance()
    if use_map:
        await client.hdel(hash_name, key)
    else:
        await client.delete(key)
