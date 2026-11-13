#!/bin/bash
# ==============================================================================
# Executes Hadoop Streaming MapReduce Job for AeroVision Navigation Analytics
# ==============================================================================

SJAR=/opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar

# Remove existing output directory if present to allow fresh execution
hdfs dfs -rm -r -skipTrash /user/suhas/aerovision_output 2>/dev/null

echo "Launching Hadoop Streaming MapReduce Job..."
hadoop jar "$SJAR" \
  -files /tmp/mapper.sh,/tmp/reducer.sh \
  -mapper "bash mapper.sh" \
  -reducer "bash reducer.sh" \
  -input /user/suhas/aerovision_input/aerovision_events.csv \
  -output /user/suhas/aerovision_output \
  -D mapreduce.output.fileoutputformat.compress=false

echo ""
echo "=== MapReduce Job Finished ==="
echo "Output Directory Contents:"
hdfs dfs -ls /user/suhas/aerovision_output

echo ""
echo "=== Aggregated Zone Telemetry Results (part-00000) ==="
hdfs dfs -cat /user/suhas/aerovision_output/part-00000 | sort
