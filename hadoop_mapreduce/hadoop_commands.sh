#!/bin/bash
# ==============================================================================
# AeroVision Hadoop Distributed Processing - Complete Command Workflow
# ==============================================================================

# --- Phase 1: Cluster Initialization (Host Terminal) ---
# docker compose up -d
# docker ps

# --- Phase 2: Copy Files into NameNode Container (Host Terminal) ---
# docker cp ../dataset/aerovision_events.csv namenode:/tmp/aerovision_events.csv
# docker cp mapper.sh namenode:/tmp/mapper.sh
# docker cp reducer.sh namenode:/tmp/reducer.sh
# docker cp run_mr.sh namenode:/tmp/run_mr.sh
# docker exec -it namenode bash

# --- Phase 3: Commands inside NameNode container ---
chmod +x /tmp/mapper.sh /tmp/reducer.sh /tmp/run_mr.sh

# 1. Inspect staged telemetry dataset
ls -l /tmp/aerovision_events.csv
head -n 5 /tmp/aerovision_events.csv
wc -l /tmp/aerovision_events.csv

# 2. Setup HDFS Directory Structure
hdfs dfs -mkdir -p /user/suhas/aerovision_input

# 3. Ingest Dataset into HDFS
hdfs dfs -put -f /tmp/aerovision_events.csv /user/suhas/aerovision_input/

# 4. Verify HDFS Upload & Cluster Health
hdfs dfs -ls -h /user/suhas/aerovision_input
hdfs dfsadmin -report

# 5. Local pipeline dry-run verification
cat /tmp/aerovision_events.csv | /tmp/mapper.sh | sort | /tmp/reducer.sh | sort

# 6. Execute Distributed MapReduce Job
/tmp/run_mr.sh

# 7. Retrieve Summary and Cleanup
hdfs dfs -get /user/suhas/aerovision_output/part-00000 /tmp/zone_summary.txt
cat /tmp/zone_summary.txt

