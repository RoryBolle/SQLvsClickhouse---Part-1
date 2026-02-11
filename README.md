# SQL Server vs. ClickHouse Showdown

This project demonstrates the performance differences between **Row-oriented (OLTP)** and **Column-oriented (OLAP)** database architectures.

## 🏗️ Architecture
- **SQL Server**: Optimized for individual row lookups (Point queries) using B-Tree indexes.
- **ClickHouse**: Optimized for scanning specific columns across millions of rows (Analytical queries) using columnar storage and SIMD.

## 🚀 How to Run

1. **Prerequisites**: Ensure you have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed.
2. **Start the demo**:
   ```bash
   docker-compose up --build
   ```
3. **Wait for Ingestion**: 
   The `streamlit_app` container will automatically:
   - Wait for MSSQL and ClickHouse to be healthy.
   - Generate 1,000,000 rows of synthetic order data.
   - Load the data into both databases.
4. **Access the UI**:
   Open [http://localhost:8501](http://localhost:8501) in your browser.

## 📊 Scenarios
- **Scenario A (Point Lookup)**: Retrieve a single full row by ID. SQL Server should win (usually < 5ms vs 50ms+).
- **Scenario B (Aggregation)**: Calculate sums across the entire dataset. ClickHouse should win (usually < 200ms vs 2s+).

## 🛠️ Tech Stack
- **Databases**: MSSQL 2022, ClickHouse Server.
- **UI**: Streamlit.
- **Data**: Python (Pandas & NumPy).
