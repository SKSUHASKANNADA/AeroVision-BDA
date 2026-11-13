#!/bin/bash
# ==============================================================================
# AeroVision Streaming Reducer (Bash/AWK)
# Input: Sorted tab-separated pairs (zone \t response_ms)
# Output: Summary lines (zone \t event_count \t avg_response_ms)
# ==============================================================================
awk -F'\t' '{
  s[$1] += $2
  n[$1]++
}
END {
  for (k in s)
    printf "%s\t%d\t%.4f\n", k, n[k], s[k]/n[k]
}'

