import pandas as pd
import numpy as np
import pyodbc
from clickhouse_driver import Client
import time
import os

# Configuration
NUM_ROWS = 2000000
CHUNK_SIZE = 100000

# Connection settings
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

def generate_data(n):
    print(f"Generating {n} rows of data...")
    regions = ['North', 'South', 'East', 'West', 'Central']
    data = {
        'OrderID': np.arange(1, n + 1),
        'CustomerID': np.random.randint(1000, 9999, size=n),
        'OrderDate': pd.to_datetime(np.random.randint(1577836800, 1735689600, size=n), unit='s'),
        'Amount': np.random.uniform(10.0, 1000.0, size=n).round(2),
        'Region': np.random.choice(regions, size=n),
        'Notes': [' '.join(['word' for _ in range(10)]) for _ in range(n)] # Bloat row size
    }
    return pd.DataFrame(data)

def load_mssql(df):
    conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={MSSQL_CONFIG['server']};DATABASE=master;UID={MSSQL_CONFIG['user']};PWD={MSSQL_CONFIG['password']};TrustServerCertificate=yes"
    
    # Wait for SQL Server to be ready
    retries = 10
    while retries > 0:
        try:
            conn = pyodbc.connect(conn_str, autocommit=True)
            break
        except Exception as e:
            print(f"Waiting for MSSQL... {e}")
            time.sleep(5)
            retries -= 1
    
    # Create DB and Table if not exists
    cursor = conn.cursor()
    cursor.execute("IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'DemoDB') CREATE DATABASE DemoDB")
    conn.close()
    
    conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={MSSQL_CONFIG['server']};DATABASE={MSSQL_CONFIG['database']};UID={MSSQL_CONFIG['user']};PWD={MSSQL_CONFIG['password']};TrustServerCertificate=yes"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    cursor.execute("IF OBJECT_ID('Orders', 'U') IS NOT NULL DROP TABLE Orders")
    cursor.execute("""
        CREATE TABLE Orders (
            OrderID INT PRIMARY KEY,
            CustomerID INT,
            OrderDate DATETIME,
            Amount DECIMAL(18, 2),
            Region NVARCHAR(50),
            Notes NVARCHAR(MAX)
        )
    """)
    conn.commit()

    print("Loading data into MSSQL...")
    start_time = time.time()
    
    # Use fast_executemany for better performance
    cursor.fast_executemany = True
    sql = "INSERT INTO Orders (OrderID, CustomerID, OrderDate, Amount, Region, Notes) VALUES (?, ?, ?, ?, ?, ?)"
    
    for i in range(0, len(df), CHUNK_SIZE):
        chunk = df.iloc[i:i+CHUNK_SIZE]
        cursor.executemany(sql, chunk.values.tolist())
        conn.commit()
    
    print(f"MSSQL load complete in {time.time() - start_time:.2f}s")
    conn.close()

def load_clickhouse(df):
    client = Client(
        host=CH_CONFIG['host'],
        user=CH_CONFIG['user'],
        password=CH_CONFIG['password']
    )
    
    client.execute('CREATE DATABASE IF NOT EXISTS DemoDB')
    client.execute('DROP TABLE IF EXISTS DemoDB.Orders')
    client.execute("""
        CREATE TABLE DemoDB.Orders (
            OrderID Int32,
            CustomerID Int32,
            OrderDate DateTime,
            Amount Decimal(18, 2),
            Region String,
            Notes String
        ) ENGINE = MergeTree()
        ORDER BY OrderID
    """)

    print("Loading data into ClickHouse...")
    start_time = time.time()
    
    client.execute('INSERT INTO DemoDB.Orders VALUES', df.to_dict('records'))
    
    print(f"ClickHouse load complete in {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    print("-" * 30)
    print("🚀 STARTING AUTOMATED DATA LOAD")
    print("-" * 30)
    df = generate_data(NUM_ROWS)
    load_mssql(df)
    load_clickhouse(df)
    print("-" * 30)
    print("✅ DATA LOAD COMPLETE - STARTING UI")
    print("-" * 30)
    del df
