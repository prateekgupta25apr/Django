import asyncio
from concurrent.futures import Future

from db.models import Table1AttachmentMapping, Table1
from prateek_gupta.thread_manager import executor
from project_utils import execute_query, execute_model_query


def get_data(schema_name, primary_key):
    query = (f"select * from {schema_name}.table_1 where primary_key={primary_key}"
             if primary_key is not None else f"select * from {schema_name}.table_1")
    future: Future = executor.submit(asyncio.run, execute_query(query, 'fetchall'))
    result = future.result()
    result_list = list()
    for record in result:
        data = dict()
        data["primary_key"] = record[0]
        data["col_1"] = record[1]
        data["col_2"] = record[2]
        result_list.append(data)
    return result_list


def save_data(schema_name, data):
    future: Future = executor.submit(
        asyncio.run, execute_model_query(
            schema_name,
            Table1.objects.create,
            primary_key=data.get("primary_key", None),
            col_1=data["col_1"],
            col_2=data["col_2"]
        ))
    future.result()


def update_data(schema_name, primary_key, col_1, col_2):
    future: Future = executor.submit(
        asyncio.run, execute_model_query(
            schema_name, Table1.objects.filter(primary_key=primary_key)
            .update, col_1=col_1, col_2=col_2
        )
    )
    future.result()


def partial_update_data(
        schema_name, primary_key, col_1=None, col_2=None):
    set_cols = ""

    if col_1 is not None:
        set_cols = f"col_1 = '{col_1}'"

    if col_2 is not None:
        if set_cols:
            set_cols += ","
        set_cols += f"col_2={col_2}"

    query = (f"update {schema_name}.table_1 set " + set_cols + f" where primary_key={primary_key}")
    future: Future = executor.submit(asyncio.run, execute_query(query))
    future.result()


def delete_data(schema_name, primary_key):
    future: Future = executor.submit(
        asyncio.run, execute_model_query(
            schema_name, Table1.objects.filter(primary_key=primary_key)
            .delete
        )
    )
    future.result()


def add_attachment(schema_name, table_1_primary_key, attachment):
    future: Future = executor.submit(asyncio.run, execute_model_query(
        schema_name, Table1AttachmentMapping.objects.create,
        table_1_id=table_1_primary_key, attachment_path=attachment
    ))
    future.result()


def get_attachment_path(schema_name, primary_key):
    future: Future = executor.submit(asyncio.run, execute_model_query(
        schema_name, Table1AttachmentMapping.objects.get, primary_key=primary_key
    ))
    result: Table1AttachmentMapping = future.result()
    return str(result.attachment_path)
