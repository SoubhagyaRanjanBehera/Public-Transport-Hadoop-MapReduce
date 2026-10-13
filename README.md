# Big Data Analytics Mini-Project: Public Transportation Analysis
**Course:** Big Data Analytics (Activity-Based Learning)  
**Group:** Group 9  
**Technology:** Apache Hadoop / MapReduce (Python Hadoop Streaming)  
**Topic:** Public Transportation Analysis  

---

## 1. Project Overview & Problem Statement
Urban public transit networks (buses, metros, trains) serve millions of daily commuters. Analyzing transit trip logs enables city planners and transit authorities to:
1. Identify high-demand routes that experience heavy commuter crowding.
2. Detect routes with persistent transit delays to optimize scheduling and minimize congestion.
3. Compute key performance indicators (KPIs) like average passengers per trip and average delay per route across massive datasets that exceed single-machine memory.

Using **Apache Hadoop** and the **MapReduce programming paradigm**, this project processes distributed transit event logs to aggregate passenger volumes and punctuality statistics efficiently and reliably.

---

## 2. System Architecture

```
   +------------------------------------+
   | Public Transit Event Logs (CSV)    |
   +------------------------------------+
                    |
                    v
   +------------------------------------+
   | Hadoop Distributed File System     |  hdfs dfs -put transit_data.csv
   | (HDFS Data Blocks & Replication)   |
   +------------------------------------+
                    |
                    v
   +------------------------------------+
   | MAP PHASE (mapper.py)              |  Extracts (Route_ID) -> (Passengers, Delay, 1)
   +------------------------------------+
                    |
                    v
   +------------------------------------+
   | SHUFFLE & SORT PHASE (Hadoop Core) |  Partitions & sorts keys across nodes
   +------------------------------------+
                    |
                    v
   +------------------------------------+
   | REDUCE PHASE (reducer.py)          |  Aggregates trips, passengers, & avg delays
   +------------------------------------+
                    |
                    v
   +------------------------------------+
   | HDFS Output / Analytics Report     |  Route metrics & performance insights
   +------------------------------------+
```

---

## 3. Directory Structure

```text
BDA_Mini_Project/
│
├── data/
│   └── transit_data.csv         # 30-row mock public transit dataset
│
├── src/
│   ├── mapper.py                # Hadoop Streaming Mapper script
│   ├── reducer.py               # Hadoop Streaming Reducer script
│   └── generate_summary.py      # Summary metrics and visual chart generator
│
├── output/
│   ├── results.txt              # MapReduce output (Route aggregations)
│   └── summary_report.md        # Formatted executive findings report
│
├── app.py                       # Interactive Streamlit dashboard
├── requirements.txt             # Python dependencies (streamlit, pandas, plotly)
├── run_local_test.py            # Local MapReduce simulation runner
└── README.md                    # Project documentation and Hadoop instructions
```

---

## 4. Dataset Specification (`data/transit_data.csv`)

| Field Name | Data Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `Trip_ID` | String | Unique trip identifier | `T1001` |
| `Route_ID` | String | Public transit corridor / line | `Route_101` |
| `Source_Station` | String | Starting station | `Central_Station` |
| `Destination_Station` | String | Terminating station | `City_Square` |
| `Travel_Time_Min` | Float | Scheduled travel duration (minutes) | `25` |
| `Delay_Min` | Float | Delay experienced (minutes) | `3` |
| `Passenger_Count` | Integer | Total riders on this trip | `45` |

---

## 5. MapReduce Logic

### 1. Mapper (`src/mapper.py`)
- Reads raw CSV rows from standard input (`sys.stdin`).
- Skips header lines (`Trip_ID`) and malformed records.
- Extracts `Route_ID`, `Passenger_Count`, `Delay_Min`, and emits a trip indicator (`1`).
- **Emits:**  
  ```text
  Route_ID <TAB> Passenger_Count <TAB> Delay_Min <TAB> 1
  ```

### 2. Shuffle & Sort (Hadoop Internal)
- Collects all intermediate pairs emitted by all mappers.
- Sorts records by `Route_ID` so all records for the same route arrive sequentially at the reducer.

### 3. Reducer (`src/reducer.py`)
- Reads consecutive records for each `Route_ID` from standard input (`sys.stdin`).
- Computes:
  - $\text{Total Trips} = \sum 1$
  - Total Passengers = sum(Passenger_Count)
  - $\text{Avg Passengers per Trip} = \frac{\text{Total Passengers}}{\text{Total Trips}}$
  - $\text{Avg Delay (min)} = \frac{\sum \text{Delay\_Min}}{\text{Total Trips}}$
- **Emits:**  
  ```text
  Route_ID <TAB> Total_Trips <TAB> Total_Passengers <TAB> Avg_Passengers_Per_Trip <TAB> Avg_Delay_Min
  ```

---

## 6. How to Test and Run Locally (Without Hadoop)

You do **not** need a multi-node Hadoop cluster to develop and test your MapReduce logic. Test it directly using either of the methods below:

### Method A: Using the Automated Test Runner (Recommended)
Run the Python simulation script that executes the entire pipeline (Mapper -> Sort -> Reducer -> Output):
```bash
python run_local_test.py
```

### Method B: Native Terminal Piping

* **On Windows PowerShell:**
  ```powershell
  Get-Content data\transit_data.csv | python src\mapper.py | Sort-Object | python src\reducer.py
  ```

* **On Linux / macOS / Git Bash:**
  ```bash
  cat data/transit_data.csv | python3 src/mapper.py | sort | python3 src/reducer.py
  ```

### View Summary and ASCII Charts
Run the summary generator script to view terminal charts and produce `output/summary_report.md`:
```bash
python src/generate_summary.py
```

---

## 7. Running on a Hadoop Cluster (Pseudo-Distributed / Multi-Node)

When running on an actual Apache Hadoop cluster (e.g., Ubuntu/WSL/Cloud VM):

### Step 1: Start Hadoop Daemons
```bash
start-dfs.sh
start-yarn.sh
jps  # Ensure NameNode, DataNode, ResourceManager, NodeManager are running
```

### Step 2: Create HDFS Directory & Ingest Dataset
```bash
# Create directory in HDFS
hdfs dfs -mkdir -p /bda/public_transport/input

# Upload dataset to HDFS
hdfs dfs -put data/transit_data.csv /bda/public_transport/input/

# Verify upload
hdfs dfs -ls /bda/public_transport/input/
```

### Step 3: Run Hadoop Streaming MapReduce Job
Locate your cluster's `hadoop-streaming` JAR (typically in `$HADOOP_HOME/share/hadoop/tools/lib/`):
```bash
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -input /bda/public_transport/input/transit_data.csv \
  -output /bda/public_transport/output \
  -mapper "python3 mapper.py" \
  -reducer "python3 reducer.py" \
  -file src/mapper.py \
  -file src/reducer.py
```

### Step 4: Inspect and Download Cluster Results
```bash
# View output directly from HDFS
hdfs dfs -cat /bda/public_transport/output/part-*

# Download output file from HDFS to local output directory
hdfs dfs -get /bda/public_transport/output/part-00000 ./output/hadoop_cluster_results.txt
```

---

## 8. Interactive Streamlit Dashboard

A web dashboard is provided in `app.py` for visual analytics, presentations, and viva demonstrations.

### Launching the Dashboard:
```bash
streamlit run app.py
```

### Dashboard Features:
* **Top-Level KPI Metric Cards:** Total Commuters, Total Trips Analyzed, Busiest Route, and Highest Delay Route.
* **Interactive Visualizations (Plotly & Pandas):**
  - **Bar Charts:** Total Commuter Volume per Route and Average Delay per Route.
  - **Scatter Plot:** Commuter Demand vs. Average Delays (with bubble size representing Average Passengers/Trip and median threshold indicators).
* **Interactive Data Explorer:** Real-time search filter by route name, multi-select route filtering, delay cutoff slider, and one-click CSV export.
* **Hadoop Architecture Tab:** Displays pipeline explanation alongside full source code for `mapper.py` and `reducer.py`.
* **Live Pipeline Re-run:** A button in the sidebar to re-trigger the MapReduce job and update dashboard metrics in real time.

---

## 9. Analytical Findings

| Route ID | Total Trips | Total Passengers | Avg Passengers/Trip | Avg Delay (Min) | Operational Takeaway |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Route_101** | 6 | 294 | 49.00 | 3.17 | Stable feeder line; moderate demand. |
| **Route_102** | 6 | 547 | 91.17 | 6.33 | **Highest commuter volume**; needs additional vehicle frequency. |
| **Route_201** | 6 | 250 | 41.67 | 9.50 | **Highest average delay**; bottleneck along airport corridor. |
| **Route_202** | 6 | 402 | 67.00 | 4.00 | Heavy harbor corridor traffic with good punctuality. |
| **Route_305** | 6 | 165 | 27.50 | 2.83 | **Most reliable route**; lowest delays. |

---

## 10. Viva / Defense Preparation Questions

1. **Why use Hadoop/MapReduce instead of SQL or Python Pandas?**
   - Pandas loads the whole dataset into RAM, which crashes on multi-gigabyte or terabyte transit logs. Hadoop splits files across HDFS data blocks (e.g., 128 MB blocks) and processes them in parallel across cluster nodes.

2. **What does Hadoop Streaming do?**
   - Hadoop Streaming is a utility that allows any executable or script (Python, C++, Perl) that reads from `stdin` and writes to `stdout` to act as a Hadoop Mapper or Reducer.

3. **How does the Reducer know when all records for a route are finished?**
   - Because of Hadoop's **Shuffle & Sort** stage, intermediate keys are sorted alphabetically. All keys with the name `Route_101` arrive sequentially before `Route_102` begins.

4. **What happens if a node fails during Map execution?**
   - Hadoop's YARN ResourceManager and NodeManager detect heartbeat loss and reschedule the map task on another node storing a replica of that HDFS data block.
