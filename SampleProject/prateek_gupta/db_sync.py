from utils import execute_query, execute_query_sync


def get_data(primary_key):
    query = (f"select * from table_1 where primary_key={primary_key}"
             if primary_key is not None else "select * from table_1")
    result =  execute_query_sync(query, 'fetchall')
    result_list = list()
    for record in result:
        data = dict()
        data["primary_key"] = record[0]
        data["col_1"] = record[1]
        data["col_2"] = record[2]
        result_list.append(data)
    return result_list


async def save_data(data):
    query = (f"insert into table_1 values "
             f"({data['primary_key']},'{data['col_1']}',{data['col_2']})")
    await execute_query(query)


async def update_data(primary_key, col_1, col_2):
    query = (f"update table_1 set col_1='{col_1}',col_2={col_2} where "
             f"primary_key={primary_key}")
    await execute_query(query)


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
    query = f"delete from table_1 where primary_key={primary_key}"
    await execute_query(query)
