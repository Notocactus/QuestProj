import datetime

from sqlalchemy import text


def enclose(v):
    return f"'{v}'"


def select(engine, tab_name, *columns, **options):
    connection = engine.connect()
    columns = ", ".join(columns)
    if len(columns) == 0:
        columns = "*"
    query = f"SELECT {columns} FROM {tab_name}"
    if len(options) > 0:
        opts = " AND ".join([f"{k} = {enclose(v)}"
                             for k, v in options.items()
                             if v is not None])
        if len(opts) > 0:
            query = query + " WHERE " + opts

    # raise Exception(f"{query}")
    data = connection.execute(text(query))
    connection.close()
    data = [dict(row._mapping) for row in data]
    return data


def insert(engine, tab_name, columns, values):
    connection = engine.connect()
    trans = connection.begin()
    query = f"INSERT INTO {tab_name}({','.join(list(map(str, columns)))}) VALUES ({','.join(list(map(enclose, values)))})"
    connection.execute(text(query))
    trans.commit()
    connection.close()


def delete(engine, tab_name, **options):
    connection = engine.connect()
    query = f"DELETE FROM {tab_name}"
    if len(options) > 0:
        opts = " AND ".join([f"{k} = '{v}'"
                             for k, v in options.items()])
        query += " WHERE " + opts
    connection.execute(text(query))
    connection.close()


def update(engine, tab_name, set_kwargs, where_kwargs=None):
    connection = engine.connect()
    trans = connection.begin()
    query = f"UPDATE {tab_name} SET "
    query += ', '.join([f"{k}='{v}'" for k, v in set_kwargs.items()])
    if where_kwargs is not None and len(where_kwargs) > 0:
        opts = " AND ".join([f"{k} = '{v}'"
                             for k, v in where_kwargs.items()])
        query += " WHERE " + opts

    connection.execute(text(query))
    trans.commit()
    connection.close()

