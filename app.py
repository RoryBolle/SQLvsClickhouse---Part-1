import streamlit as st
import benchmark_utils as bench
import pandas as pd
import numpy as np

st.set_page_config(page_title="SQL Server vs ClickHouse Showdown", layout="wide")

st.title("🚀 Row-Store (SQL Server) vs Column-Store (ClickHouse)")
st.markdown("""
This demo compares a traditional transactional database (SQL Server) with an analytical powerhouse (ClickHouse).
Observe how architecture dictates performance for different workloads.
""")

# Initialize session state for history
if 'history' not in st.session_state:
    st.session_state.history = {
        'point': pd.DataFrame(columns=['Run', 'MSSQL', 'ClickHouse']),
        'agg': pd.DataFrame(columns=['Run', 'MSSQL', 'ClickHouse'])
    }

def add_run_data(scenario, mssql_t, ch_t):
    df = st.session_state.history[scenario]
    new_run = len(df) + 1
    new_row = pd.DataFrame({'Run': [new_run], 'MSSQL': [mssql_t], 'ClickHouse': [ch_t]})
    # Removed .tail(5) to allow unlimited historical tracking until page refresh
    st.session_state.history[scenario] = pd.concat([df, new_row], ignore_index=True)

def plot_benchmark(scenario):
    df = st.session_state.history[scenario]
    if not df.empty:
        # Plotting line chart for history tracking
        plot_df = df.set_index('Run')
        st.line_chart(plot_df)

col_main, _ = st.columns([2, 1])

with col_main:
    # --- SCENARIO A ---
    st.header("🎯 Scenario A: Point Lookup")
    st.info("Retrieve 1 specific row. One button runs both to compare timing on the same chart.")
    
    with st.expander("Show Query Logic"):
        st.code("""
# Both Platforms
SELECT * FROM Orders WHERE OrderID = {random_id}
        """, language="sql")

    if st.button("🔥 Run Point Lookup Comparison", type="primary"):
        with st.spinner("Executing queries..."):
            t_mssql = bench.run_mssql_point_lookup()
            t_ch = bench.run_ch_point_lookup()
            add_run_data('point', t_mssql, t_ch)
    
    plot_benchmark('point')

    st.divider()    
      
    if st.button("♻️ Clear All Caches", key="clear_a"):
        with st.spinner("Cleaning..."):
            bench.clear_mssql_cache()
            bench.clear_ch_cache()
            st.success("Caches cleared for both platforms!")

    st.divider()

    # --- SCENARIO B ---
    st.header("📊 Scenario B: Analytical Aggregation")
    st.info("Sum 2M rows grouped by Region. One button runs both to compare timing.")

    with st.expander("Show Query Logic"):
        st.code("""
# Both Platforms
SELECT Region, SUM(Amount) FROM Orders GROUP BY Region
        """, language="sql")

    if st.button("🔥 Run Aggregation Comparison", type="primary"):
        with st.spinner("Executing queries..."):
            t_mssql = bench.run_mssql_agg()
            t_ch = bench.run_ch_agg()
            add_run_data('agg', t_mssql, t_ch)
    
    plot_benchmark('agg')

    st.divider()    
      
    if st.button("♻️ Clear All Caches", key="clear_b"):
        with st.spinner("Cleaning..."):
            bench.clear_mssql_cache()
            bench.clear_ch_cache()
            st.success("Caches cleared for both platforms!")

st.divider()

st.markdown("""
### 💡 Why the difference?
*   **Point Lookup:** SQL Server uses a **Clustered B-Tree index** to jump directly to the exact page on disk. ClickHouse uses **Sparse Indexes** and often has to scan a 'granule' of 8,192 rows even for a single match.
*   **Aggregation:** ClickHouse only reads the `Amount` and `Region` columns, ignoring everything else. It processes data using **SIMD** instructions. SQL Server (unless using Columnstore indexes) must read the entire row to access just two columns, leading to massive I/O overhead.
""")
