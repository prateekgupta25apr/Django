from db.models import Table1AttachmentMapping, Table1
from prateek_gupta.utils import execute_as_async
from project_utils import execute_query


async def get_data(primary_key):
    query = (f"select * from table_1 where primary_key={primary_key}"
             if primary_key is not None else "select * from table_1")
    result = await execute_query(query, 'fetchall')
    result_list = list()
    for record in result:
        data = dict()
        data["primary_key"] = record[0]
        data["col_1"] = record[1]
        data["col_2"] = record[2]
        result_list.append(data)
    return result_list


async def save_data(data):
    await execute_as_async(
        Table1.objects.create,
        primary_key=data.get("primary_key", None),
        col_1=data["col_1"],
        col_2=data["col_2"]
    )


async def update_data(primary_key, col_1, col_2):
    await execute_as_async(Table1.objects.filter(primary_key=primary_key)
                           .update, col_1=col_1, col_2=col_2)


async def partial_update_data(primary_key, col_1=None, col_2=None):
    set_cols = ""

    if col_1 is not None:
        set_cols = f"col_1 = '{col_1}'"

    if col_2 is not None:
        if set_cols:
            set_cols += ","
        set_cols += f"col_2={col_2}"

    query = (f"update table_1 set " + set_cols + f" where primary_key={primary_key}")
    await execute_query(query)


async def delete_data(primary_key):
    await execute_as_async(
        Table1.objects.filter(primary_key=primary_key).delete
    )


async def add_attachment(table_1_primary_key, attachment):
    await execute_as_async(
        Table1AttachmentMapping.objects.create,
        table_1_id=table_1_primary_key, attachment_path=attachment
    )


async def get_attachment_path(primary_key):
    obj = await execute_as_async(Table1AttachmentMapping.objects.get, primary_key=primary_key)
    return str(obj.attachment_path)
