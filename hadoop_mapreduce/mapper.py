#!/usr/bin/env python3
"""AeroVision Hadoop Streaming Mapper (Python)
Extracts navigation zone (field 2) and response time in ms (field 6) from CSV telemetry.
"""
import sys

for line in sys.stdin:
    line = line.strip()
    if not line or line.startswith("date"):
        continue
    parts = line.split(",")
    if len(parts) >= 6:
        zone = parts[1].strip()
        try:
            response_time = float(parts[5].strip())
            print(f"{zone}\t{response_time}")
        except ValueError:
            continue

