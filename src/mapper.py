#!/usr/bin/env python3
"""
Public Transportation Analysis - MapReduce Mapper
Group 9 - BDA Mini-Project

This mapper reads CSV records line-by-line from standard input (sys.stdin),
skips headers/malformed rows, extracts relevant fields, and emits key-value pairs
to standard output (sys.stdout) for the Hadoop Shuffle & Sort phase.

Input format:
Trip_ID,Route_ID,Source_Station,Destination_Station,Travel_Time_Min,Delay_Min,Passenger_Count

Output format:
Route_ID\tPassenger_Count\tDelay_Min\tTrip_Count(1)
"""

import sys
import csv

def main():
    # Use csv.reader to handle any quoted fields or standard CSV formatting safely
    reader = csv.reader(sys.stdin)
    
    for row in reader:
        # Skip empty rows
        if not row:
            continue
        
        # Check if the line is the CSV header
        if len(row) > 0 and row[0].strip().lower() in ("trip_id", "tripid"):
            continue

        # Expecting at least 7 fields
        if len(row) < 7:
            continue

        try:
            route_id = row[1].strip()
            travel_time = float(row[4].strip())
            delay_min = float(row[5].strip())
            passenger_count = int(row[6].strip())

            # Skip records with missing route identifiers
            if not route_id:
                continue

            # Emit: Key = Route_ID, Value = Passenger_Count, Delay_Min, 1 (trip)
            print(f"{route_id}\t{passenger_count}\t{delay_min}\t1")

        except (ValueError, IndexError):
            # Ignore malformed or corrupted rows safely
            continue

if __name__ == "__main__":
    main()
