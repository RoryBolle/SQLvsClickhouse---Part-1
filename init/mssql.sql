IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'DemoDB')
BEGIN
    CREATE DATABASE DemoDB;
END
GO

USE DemoDB;
GO

IF OBJECT_ID('Orders', 'U') IS NOT NULL
    DROP TABLE Orders;
GO

CREATE TABLE Orders (
    OrderID INT PRIMARY KEY,
    CustomerID INT,
    OrderDate DATETIME,
    Amount DECIMAL(18, 2),
    Region NVARCHAR(50),
    Notes NVARCHAR(MAX)
);

-- Note: PRIMARY KEY in MSSQL creates a CLUSTERED INDEX by default.
