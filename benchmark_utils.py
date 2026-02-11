import pyodbc
from clickhouse_driver import Client
import time
import os
import random

MSSQL_CONFIG = {
    'server': os.getenv('MSSQL_HOST', 'localhost'),
    'database': 'DemoDB',
    'user': os.getenv('MSSQL_USER', 'sa'),
    'password': os.getenv('MSSQL_PASSWORD', 'YourStrong!Passw0rd')
}

CH_CONFIG = {
    'host': os.getenv('CLICKHOUSE_HOST', 'localhost'),
    'database': 'DemoDB',
    'user': os.getenv('CLICKHOUSE_USER', 'default'),
    'password': os.getenv('CLICKHOUSE_PASSWORD', 'YourStrong!Passw0rd')
}

def get_mssql_conn():
    conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={MSSQL_CONFIG['server']};DATABASE={MSSQL_CONFIG['database']};UID={MSSQL_CONFIG['user']};PWD={MSSQL_CONFIG['password']};TrustServerCertificate=yes"
    return pyodbc.connect(conn_str)

def get_ch_client():
    return Client(
        host=CH_CONFIG['host'],
        database=CH_CONFIG['database'],
        user=CH_CONFIG['user'],
        password=CH_CONFIG['password']
    )

def run_mssql_point_lookup():
    order_id = random.randint(1, 2000000)
    conn = get_mssql_conn()
    cursor = conn.cursor()
    start = time.perf_counter()
    cursor.execute(f"SELECT * FROM Orders WHERE OrderID = {order_id}")
    _ = cursor.fetchone()
    end = time.perf_counter()
    conn.close()
    return (end - start) * 1000 # Return ms

def run_ch_point_lookup():
    order_id = random.randint(1, 2000000)
    client = get_ch_client()
    start = time.perf_counter()
    _ = client.execute(f"SELECT * FROM Orders WHERE OrderID = {order_id}")
    end = time.perf_counter()
    return (end - start) * 1000 # Return ms

def run_mssql_agg():
    conn = get_mssql_conn()
    cursor = conn.cursor()
    start = time.perf_counter()
    cursor.execute("SELECT Region, SUM(Amount) FROM Orders GROUP BY Region")
    _ = cursor.fetchall()
    end = time.perf_counter()
    conn.close()
    return (end - start) * 1000 # Return ms

def run_ch_agg():
    client = get_ch_client()
    start = time.perf_counter()
    _ = client.execute("SELECT Region, SUM(Amount) FROM Orders GROUP BY Region")
    end = time.perf_counter()
    return (end - start) * 1000 # Return ms

def clear_mssql_cache():
    conn = get_mssql_conn()
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("CHECKPOINT;")
    cursor.execute("DBCC DROPCLEANBUFFERS;")
    cursor.execute("DBCC FREEPROCCACHE;")
    cursor.execute("EXEC sp_updatestats;")
    conn.close()

def clear_ch_cache():
    client = get_ch_client()
    client.execute("SYSTEM DROP MARK CACHE")
    client.execute("SYSTEM DROP UNCOMPRESSED CACHE")
    client.execute("SYSTEM DROP COMPILED EXPRESSION CACHE")
    # Note: ClickHouse also relies on OS page cache, but these internal caches are relevant.
