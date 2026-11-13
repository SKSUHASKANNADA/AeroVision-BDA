#!/usr/bin/env python3
"""AeroVision Hadoop Streaming Reducer (Python)
Aggregates navigation events by zone, computing total event count and mean response latency.
"""
import sys

current_zone = None
total_time = 0.0
count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        zone, val_str = line.split("\t")
        val = float(val_str)
    except ValueError:
        continue

    if current_zone == zone:
        total_time += val
        count += 1
    else:
        if current_zone:
            avg_time = total_time / count
            print(f"{current_zone}\t{count}\t{avg_time:.4f}")
        current_zone = zone
        total_time = val
        count = 1

if current_zone:
    avg_time = total_time / count
    print(f"{current_zone}\t{count}\t{avg_time:.4f}")
