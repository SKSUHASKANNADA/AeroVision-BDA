#!/bin/bash
# ==============================================================================
# AeroVision Streaming Mapper (Bash/AWK)
# Input: CSV lines (date, zone, mode, event_type, severity, response_ms)
# Output: Tab-separated key-value pairs (zone \t response_ms)
# ==============================================================================
awk -F, '$1!="date" && NF==6 {
  gsub(/\r/,"",$6)
  print $2 "\t" $6
}'

