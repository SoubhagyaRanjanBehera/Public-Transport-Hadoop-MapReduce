import os
import sys
import subprocess
import streamlit as st
import pandas as pd

# Optional Plotly import with fallback
try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Public Transit Analytics | Group 9",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Helper Functions & Data Loading
# ---------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
RESULTS_FILE = os.path.join(PROJECT_ROOT, "output", "results.txt")
DATASET_FILE = os.path.join(PROJECT_ROOT, "data", "transit_data.csv")
TEST_SCRIPT = os.path.join(PROJECT_ROOT, "run_local_test.py")

def run_mapreduce_pipeline():
    """Executes the local MapReduce pipeline and regenerates results."""
    try:
        proc = subprocess.run(
            [sys.executable, TEST_SCRIPT],
            capture_output=True,
            text=True,
            check=True
        )
        return True, proc.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def load_data():
    """Reads and parses output/results.txt into a Pandas DataFrame."""
    if not os.path.exists(RESULTS_FILE):
        return None

    try:
        df = pd.read_csv(RESULTS_FILE, sep="\t")
        # Ensure correct column naming and types
        expected_cols = [
            "Route_ID", "Total_Trips", "Total_Passengers", 
            "Avg_Passengers_Per_Trip", "Avg_Delay_Min"
        ]
        if list(df.columns) != expected_cols and len(df.columns) == 5:
            df.columns = expected_cols

        df["Total_Trips"] = df["Total_Trips"].astype(int)
        df["Total_Passengers"] = df["Total_Passengers"].astype(int)
        df["Avg_Passengers_Per_Trip"] = df["Avg_Passengers_Per_Trip"].astype(float)
        df["Avg_Delay_Min"] = df["Avg_Delay_Min"].astype(float)
        return df
    except Exception as ex:
        st.error(f"Error loading {RESULTS_FILE}: {ex}")
        return None

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2830/2830305.png", width=70)
st.sidebar.title("Transit Analytics")
st.sidebar.markdown("**Group 9 | BDA Mini-Project**")
st.sidebar.caption("Technology: Apache Hadoop / MapReduce")
st.sidebar.divider()

# Re-run MapReduce trigger button
if st.sidebar.button("🔄 Re-run MapReduce Pipeline", help="Executes Mapper & Reducer scripts locally to refresh output"):
    with st.spinner("Executing MapReduce job..."):
        success, message = run_mapreduce_pipeline()
        if success:
            st.sidebar.success("MapReduce executed successfully!")
        else:
            st.sidebar.error(f"Pipeline failed: {message}")

st.sidebar.subheader("Filter Controls")

# Load current data
df = load_data()

if df is None:
    st.warning("⚠️ Aggregated results not found in `output/results.txt`.")
    if st.button("Generate MapReduce Results Now"):
        with st.spinner("Running MapReduce..."):
            success, message = run_mapreduce_pipeline()
            if success:
                st.success("Results generated successfully! Reloading...")
                st.rerun()
            else:
                st.error(f"Error: {message}")
    st.stop()

# Route multiselect filter
all_routes = sorted(df["Route_ID"].unique().tolist())
selected_routes = st.sidebar.multiselect(
    "Filter by Route:",
    options=all_routes,
    default=all_routes,
    help="Select routes to include in graphs and tables"
)

# Delay Threshold slider
max_allowed_delay = float(df["Avg_Delay_Min"].max())
delay_cutoff = st.sidebar.slider(
    "Max Average Delay (Minutes):",
    min_value=0.0,
    max_value=max(15.0, max_allowed_delay + 2.0),
    value=max(15.0, max_allowed_delay + 2.0),
    step=0.5
)

# Apply Sidebar Filters
filtered_df = df[
    (df["Route_ID"].isin(selected_routes)) & 
    (df["Avg_Delay_Min"] <= delay_cutoff)
].copy()

# ---------------------------------------------------------
# Main Page Header & Top KPI Metrics
# ---------------------------------------------------------
st.markdown('<div class="main-header">🚌 Public Transportation Performance Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Aggregated Big Data insights processed via Apache Hadoop MapReduce (Group 9)</div>', unsafe_allow_html=True)

if filtered_df.empty:
    st.warning("No records match the current sidebar filter criteria. Please adjust your filters.")
    st.stop()

# Calculate top-level KPIs
total_passengers = int(filtered_df["Total_Passengers"].sum())
total_trips = int(filtered_df["Total_Trips"].sum())

busiest_row = filtered_df.loc[filtered_df["Total_Passengers"].idxmax()]
busiest_route = f"{busiest_row['Route_ID']} ({busiest_row['Total_Passengers']:,} riders)"

highest_delay_row = filtered_df.loc[filtered_df["Avg_Delay_Min"].idxmax()]
highest_delay_route = f"{highest_delay_row['Route_ID']} ({highest_delay_row['Avg_Delay_Min']:.2f} mins)"

# Display KPI cards in 4 columns
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="Total Commuters", 
        value=f"{total_passengers:,}", 
        help="Cumulative passenger count aggregated across all filtered routes"
    )
with col2:
    st.metric(
        label="Total Trips Analyzed", 
        value=f"{total_trips:,}",
        help="Number of scheduled transit trips processed by Reducer"
    )
with col3:
    st.metric(
        label="Busiest Route", 
        value=busiest_route,
        help="Transit corridor with the highest total passenger volume"
    )
with col4:
    st.metric(
        label="Highest Delay Route", 
        value=highest_delay_route,
        delta=f"{highest_delay_row['Avg_Delay_Min']:.1f}m avg",
        delta_color="inverse",
        help="Corridor experiencing the greatest average delay per trip"
    )

st.markdown("---")

# ---------------------------------------------------------
# Tabs: Visualizations, Table Explorer & Hadoop Architecture
# ---------------------------------------------------------
tab_analytics, tab_data, tab_architecture = st.tabs([
    "📊 Performance Analytics", 
    "📋 Route Data Explorer & Search", 
    "⚙️ MapReduce Architecture"
])

# ---------------------------------------------------------
# TAB 1: Visual Analytics
# ---------------------------------------------------------
with tab_analytics:
    st.subheader("Route Comparison: Passenger Volumes & Delay Patterns")

    chart_col1, chart_col2 = st.columns(2)

    if HAS_PLOTLY:
        # Chart 1: Passenger Volume Bar Chart
        with chart_col1:
            fig_bar_pass = px.bar(
                filtered_df,
                x="Route_ID",
                y="Total_Passengers",
                color="Total_Passengers",
                color_continuous_scale="Blues",
                text="Total_Passengers",
                title="<b>Total Passenger Volume by Route</b>",
                labels={"Total_Passengers": "Passengers", "Route_ID": "Transit Route"}
            )
            fig_bar_pass.update_traces(textposition="outside")
            fig_bar_pass.update_layout(xaxis_title="", yaxis_title="Passengers", height=380)
            st.plotly_chart(fig_bar_pass, use_container_width=True)

        # Chart 2: Average Delay Bar Chart
        with chart_col2:
            fig_bar_delay = px.bar(
                filtered_df,
                x="Route_ID",
                y="Avg_Delay_Min",
                color="Avg_Delay_Min",
                color_continuous_scale="Reds",
                text=filtered_df["Avg_Delay_Min"].apply(lambda v: f"{v:.2f}m"),
                title="<b>Average Trip Delay (Minutes) by Route</b>",
                labels={"Avg_Delay_Min": "Avg Delay (min)", "Route_ID": "Transit Route"}
            )
            fig_bar_delay.update_traces(textposition="outside")
            fig_bar_delay.update_layout(xaxis_title="", yaxis_title="Minutes", height=380)
            st.plotly_chart(fig_bar_delay, use_container_width=True)

        # Chart 3: Scatter Plot (Volume vs. Delay Trade-off)
        st.subheader("Correlation: Commuter Demand vs. Route Congestion / Delay")
        
        fig_scatter = px.scatter(
            filtered_df,
            x="Total_Passengers",
            y="Avg_Delay_Min",
            size="Avg_Passengers_Per_Trip",
            color="Avg_Delay_Min",
            color_continuous_scale="Temps",
            hover_name="Route_ID",
            hover_data={
                "Total_Trips": True,
                "Total_Passengers": True,
                "Avg_Passengers_Per_Trip": ":.2f",
                "Avg_Delay_Min": ":.2f"
            },
            title="<b>Passenger Volume vs. Average Delay</b> (Bubble Size = Avg Passengers / Trip)",
            labels={
                "Total_Passengers": "Total Passenger Volume",
                "Avg_Delay_Min": "Average Delay (Minutes)"
            }
        )
        
        # Add reference lines for median thresholds
        median_pass = filtered_df["Total_Passengers"].median()
        median_delay = filtered_df["Avg_Delay_Min"].median()
        fig_scatter.add_vline(x=median_pass, line_dash="dash", line_color="gray", annotation_text="Median Commuters")
        fig_scatter.add_hline(y=median_delay, line_dash="dash", line_color="gray", annotation_text="Median Delay")
        
        fig_scatter.update_layout(height=450)
        st.plotly_chart(fig_scatter, use_container_width=True)

    else:
        # Fallback to Streamlit native charts
        with chart_col1:
            st.markdown("**Total Passenger Volume by Route**")
            st.bar_chart(filtered_df.set_index("Route_ID")["Total_Passengers"])
        with chart_col2:
            st.markdown("**Average Delay (Minutes) by Route**")
            st.bar_chart(filtered_df.set_index("Route_ID")["Avg_Delay_Min"])

        st.markdown("**Scatter: Total Passengers vs. Average Delay**")
        st.scatter_chart(
            data=filtered_df,
            x="Total_Passengers",
            y="Avg_Delay_Min",
            size="Avg_Passengers_Per_Trip",
            color="Route_ID"
        )

# ---------------------------------------------------------
# TAB 2: Table Explorer & Search Filter
# ---------------------------------------------------------
with tab_data:
    st.subheader("Aggregated Route Metrics & Search Filter")

    search_query = st.text_input(
        "🔍 Search Routes:", 
        placeholder="Type route name (e.g., Route_101, 201)..."
    )

    table_df = filtered_df.copy()
    if search_query:
        table_df = table_df[table_df["Route_ID"].str.contains(search_query, case=False, na=False)]

    # Format numbers for display
    display_df = table_df.copy()
    display_df["Avg_Passengers_Per_Trip"] = display_df["Avg_Passengers_Per_Trip"].map("{:.2f}".format)
    display_df["Avg_Delay_Min"] = display_df["Avg_Delay_Min"].map("{:.2f}".format)

    st.dataframe(
        display_df,
        use_container_width=True,
        column_config={
            "Route_ID": "Route Identifier",
            "Total_Trips": st.column_config.NumberColumn("Total Trips", format="%d"),
            "Total_Passengers": st.column_config.NumberColumn("Total Commuters", format="%d"),
            "Avg_Passengers_Per_Trip": "Avg Riders / Trip",
            "Avg_Delay_Min": "Avg Delay (Mins)",
        },
        hide_index=True
    )

    # Download button
    csv_bytes = table_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Aggregated Results as CSV",
        data=csv_bytes,
        file_name="transit_mapreduce_results.csv",
        mime="text/csv"
    )

    # Raw Source Dataset Preview
    with st.expander("👀 View Raw Sample Dataset (`data/transit_data.csv`)"):
        if os.path.exists(DATASET_FILE):
            raw_df = pd.read_csv(DATASET_FILE)
            st.dataframe(raw_df.head(15), use_container_width=True)
            st.caption(f"Showing first 15 of {len(raw_df)} total raw trip logs.")
        else:
            st.info("Raw dataset not found.")

# ---------------------------------------------------------
# TAB 3: MapReduce Architecture
# ---------------------------------------------------------
with tab_architecture:
    st.subheader("Distributed Data Processing Pipeline")
    st.markdown("""
    This project uses **Apache Hadoop Streaming** to process high-volume transit trip logs in parallel.
    
    ### Pipeline Stages:
    1. **Data Ingestion (HDFS):** 
       - Large CSV files are uploaded into HDFS blocks (`hdfs dfs -put data/transit_data.csv /bda/input/`).
    2. **Map Phase (`src/mapper.py`):**
       - Streams through records line-by-line via `stdin`.
       - Extracts `Route_ID`, `Passenger_Count`, `Delay_Min`, and emits `(Route_ID, Passenger_Count, Delay_Min, 1)`.
    3. **Shuffle & Sort (Hadoop Internal):**
       - Collects intermediate key-value pairs, partitions them across nodes, and sorts by `Route_ID`.
    4. **Reduce Phase (`src/reducer.py`):**
       - Streams sorted records, accumulates total passengers and delays per route, and computes route averages.
    """)

    col_map, col_red = st.columns(2)
    with col_map:
        st.markdown("**Mapper Implementation (`src/mapper.py`)**")
        with open(os.path.join(PROJECT_ROOT, "src", "mapper.py"), "r", encoding="utf-8") as f:
            st.code(f.read(), language="python")

    with col_red:
        st.markdown("**Reducer Implementation (`src/reducer.py`)**")
        with open(os.path.join(PROJECT_ROOT, "src", "reducer.py"), "r", encoding="utf-8") as f:
            st.code(f.read(), language="python")

# Footer
st.markdown("---")
st.caption("Big Data Analytics Mini-Project | Group 9: Public Transportation Analysis | Powered by Hadoop & Streamlit")
