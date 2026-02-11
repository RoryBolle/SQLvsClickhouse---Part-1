CREATE DATABASE IF NOT EXISTS DemoDB;

DROP TABLE IF EXISTS DemoDB.Orders;

CREATE TABLE DemoDB.Orders (
    OrderID Int32,
    CustomerID Int32,
    OrderDate DateTime,
    Amount Decimal(18, 2),
    Region String,
    Notes String
) ENGINE = MergeTree()
ORDER BY OrderID;
