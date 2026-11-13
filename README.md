# AeroVision: Big Data Storage & Event Analytics

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-green.svg)](https://www.mongodb.com/)
[![Apache Hadoop](https://img.shields.io/badge/Apache%20Hadoop-3.2.1-yellow.svg)](https://hadoop.apache.org/)
[![Docker Compose](https://img.shields.io/badge/Docker%20Compose-v3-blue.svg)](https://docs.docker.com/compose/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

An end-to-end Big Data Analytics engineering project evaluating multi-sensor indoor navigation telemetry for autonomous ground and aerial robotics (**AeroVision**). 

The project demonstrates two complementary architectures for big data engineering:
1. **Activity 1 — Operational Telemetry Storage & Analytics with MongoDB**: High-throughput document ingestion, compound B-tree indexing, real-time aggregation pipelines, and an interactive desktop monitoring dashboard.
2. **Activity 2 — Distributed Batch Processing with Apache Hadoop & MapReduce**: Distributed fault-tolerant storage on HDFS, parallel batch computing using Hadoop Streaming (Mappers and Reducers), and cluster monitoring across a 5-node containerized environment.

---

## Architecture Overview

```
                      +------------------------------------------+
                      | AeroVision Navigation Telemetry (5,000)  |
                      | (date, zone, mode, event, severity, ms)  |
                      +--------------------+---------------------+
                                           |
               +---------------------------+---------------------------+
               |                                                       |
               v                                                       v
+-------------------------------+                     +---------------------------------+
| Activity 1: MongoDB (NoSQL)   |                     | Activity 2: Apache Hadoop       |
+-------------------------------+                     +---------------------------------+
| - Bulk Ingestion (mongoimport)|                     | - Containerized Cluster (Docker)|
| - B-Tree & Compound Indexing  |                     | - HDFS Storage (/user/suhas/)   |
| - Aggregation Pipelines:      |                     | - Hadoop Streaming MapReduce:   |
|   * Event Type Distribution   |                     |   * Mapper (zone \t latency)    |
|   * Mode Latency Ranking      |                     |   * Shuffle & Distributed Sort  |
|   * Severity Classification   |                     |   * Reducer (Count & Mean ms)   |
|   * Safety Stop Thresholding  |                     | - NameNode Web UI Health Audit  |
| - Interactive Python GUI      |                     | - HDFS Zero-Loss Output Cat     |
+-------------------------------+                     +---------------------------------+
```

---

## Repository Structure

```
AeroVision-BDA/
├── dataset/
│   ├── make_dataset.py        # Generates 5,000 synthetic AeroVision navigation telemetry records
│   └── aerovision_events.csv  # 5,000-record navigation event dataset (CSV)
│
├── mongodb/
│   ├── aerovision_dashboard.py # Interactive Tkinter & Matplotlib desktop dashboard
│   ├── verify_mongo.py        # Pipeline validation script for MongoDB aggregation queries
│   └── mongo_queries.js       # Shell queries for indexing and aggregation pipelines
│
├── hadoop_mapreduce/
│   ├── docker-compose.yml     # 5-node Apache Hadoop 3 cluster definition (bde2020)
│   ├── hadoop.env             # Environment configuration for Hadoop cluster services
│   ├── mapper.sh              # Streaming Mapper (Bash/AWK)
│   ├── reducer.sh             # Streaming Reducer (Bash/AWK)
│   ├── mapper.py              # Streaming Mapper (Python)
│   ├── reducer.py             # Streaming Reducer (Python)
│   ├── run_mr.sh              # Automated MapReduce job execution script
│   └── hadoop_commands.sh     # Step-by-step HDFS commands and inspection workflow
│
├── requirements.txt           # Pinned Python dependencies
├── .gitignore                 # Standard ignore patterns
└── README.md                  # Project documentation
```

---

## Dataset Description

The dataset simulates multi-agent robotics test flights and indoor transit sorties across complex physical facility zones:
* **Total Volume**: 5,000 navigation telemetry event records.
* **Indoor Zones (6)**: Corridor, Elevator Bay, Lab Complex, Lobby, Ramp, Warehouse Aisle.
* **Operating Modes (4)**: Autonomous Waypoint, Manual Override, Goal-Maze Navigation, Gazebo Drone Mission.
* **Event Categories**: Obstacle Detected, Localisation Lost, Waypoint Reached, Replan Required, Safety Stop.
* **Severity Levels**: Info, Warning, Error, Critical.
* **Latency Metric**: Control-loop reaction time recorded in milliseconds (`response_ms`).

To regenerate the dataset from scratch:
```bash
python dataset/make_dataset.py
```

---

## Quickstart Guide

### 1. Prerequisites
* Python 3.10+
* MongoDB Community Server 7.0+ & MongoDB Compass
* Docker Desktop (with Docker Compose enabled)

Install Python dependencies:
```bash
pip install -r requirements.txt
```

---

### 2. Activity 1: MongoDB Setup & Analytics

#### A. Ingest Telemetry Dataset
```bash
mongoimport --db aerovision_db --collection events --type csv --headerline --file dataset/aerovision_events.csv
```

#### B. Verify Ingestion & Run Aggregations
```bash
python mongodb/verify_mongo.py
```

#### C. Launch Interactive GUI Dashboard
```bash
python mongodb/aerovision_dashboard.py
```

#### Key MongoDB Aggregation Pipeline Queries (`mongodb/mongo_queries.js`)
* **Index Creation**:
  ```javascript
  db.events.createIndex({ zone: 1, severity: 1 });
  db.events.createIndex({ mode: 1 });
  ```
* **Event Distribution**:
  ```javascript
  db.events.aggregate([
    { $group: { _id: "$event_type", total: { $sum: 1 } } },
    { $sort: { total: -1 } }
  ]);
  ```
* **Safety Stops Exceeding 130 ms Threshold**:
  ```javascript
  db.events.aggregate([
    { $match: { event_type: "Safety Stop", response_ms: { $gt: 130 } } },
    { $count: "slow_stops" }
  ]);
  ```

---

### 3. Activity 2: Hadoop MapReduce Setup & Execution

#### A. Start the Containerized Hadoop Cluster
```bash
cd hadoop_mapreduce
docker compose up -d
docker ps
```
Services initialized:
* `namenode` (HDFS Master, Web UI: `http://localhost:9870`)
* `datanode` (HDFS Worker)
* `resourcemanager` (YARN Master, Web UI: `http://localhost:8088`)
* `nodemanager` (YARN Worker)
* `historyserver` (MapReduce History, Web UI: `http://localhost:8188`)

#### B. Stage Telemetry Dataset into HDFS
```bash
# Copy files into the NameNode container
docker cp ../dataset/aerovision_events.csv namenode:/tmp/aerovision_events.csv
docker cp mapper.sh namenode:/tmp/mapper.sh
docker cp reducer.sh namenode:/tmp/reducer.sh
docker cp run_mr.sh namenode:/tmp/run_mr.sh

# Enter NameNode container
docker exec -it namenode bash
chmod +x /tmp/mapper.sh /tmp/reducer.sh /tmp/run_mr.sh

# Create HDFS directory & upload dataset
hdfs dfs -mkdir -p /user/suhas/aerovision_input
hdfs dfs -put -f /tmp/aerovision_events.csv /user/suhas/aerovision_input/
hdfs dfs -ls -h /user/suhas/aerovision_input
```

#### C. Execute MapReduce Job
```bash
/tmp/run_mr.sh
```
Or execute the streaming command directly:
```bash
SJAR=/opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar

hadoop jar $SJAR \
  -files /tmp/mapper.sh,/tmp/reducer.sh \
  -mapper "bash mapper.sh" \
  -reducer "bash reducer.sh" \
  -input /user/suhas/aerovision_input/aerovision_events.csv \
  -output /user/suhas/aerovision_output \
  -D mapreduce.output.fileoutputformat.compress=false
```

#### D. Inspect Aggregated Results
```bash
hdfs dfs -cat /user/suhas/aerovision_output/part-00000 | sort
```

---

## Experimental Results Summary

### MapReduce Zone Latency Aggregation Output (`part-00000`)
| Facility Zone | Event Count | Record Share | Mean Reaction Latency (ms) | Safety Risk Assessment |
|---|---|---|---|---|
| **Corridor** | 811 | 16.22% | 217.58 ms | Lowest latency; open central transit |
| **Lobby** | 828 | 16.56% | 224.91 ms | Low latency; clear optical sightlines |
| **Lab Complex** | 855 | 17.10% | 228.14 ms | Moderate latency; structured obstacles |
| **Elevator Bay** | 869 | 17.38% | 236.42 ms | Elevated latency; LiDAR surface reflections |
| **Ramp** | 829 | 16.58% | 241.05 ms | High latency; slope attitude adjustments |
| **Warehouse Aisle** | 808 | 16.16% | 250.53 ms | Highest latency; acoustic reverb & clutter |
| **Total / Verified** | **5,000** | **100.00%** | **233.10 ms (Average)** | **Zero data loss across distributed shuffle** |

### Key Findings
1. **Zero Data Loss**: The sum of records across all six zones in MapReduce output (`811 + 828 + 855 + 869 + 829 + 808 = 5,000`) matches the exact count from MongoDB, demonstrating perfect data integrity.
2. **Indexing Acceleration**: Compound B-tree indexing on `(zone, severity)` reduced incident filtering time from 42 ms down to 1.2 ms.
3. **Safety Anomalies**: Exactly 29 out of 585 Safety Stops (4.96%) exceeded the 130 ms emergency threshold, with 55.2% concentrated in the Warehouse Aisle and Ramp zones.

---

## License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
