#!/usr/bin/env python3
"""
Public Transportation Analysis - MapReduce Reducer
Group 9 - BDA Mini-Project

This reducer reads sorted key-value pairs line-by-line from standard input (sys.stdin),
groups records by Route_ID, and computes:
  - Total Trips
  - Total Passenger Count
  - Average Passengers per Trip
  - Average Delay (Minutes) per Trip

Input format (from mapper / sort phase):
Route_ID\tPassenger_Count\tDelay_Min\tTrip_Count

Output format:
Route_ID\tTotal_Trips\tTotal_Passengers\tAvg_Passengers_Per_Trip\tAvg_Delay_Min
"""

import sys

def emit_result(route_id, total_trips, total_passengers, total_delay):
    if total_trips > 0:
        avg_passengers = total_passengers / total_trips
        avg_delay = total_delay / total_trips
        print(f"{route_id}\t{total_trips}\t{total_passengers}\t{avg_passengers:.2f}\t{avg_delay:.2f}")

def main():
    current_route = None
    total_trips = 0
    total_passengers = 0
    total_delay = 0.0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) < 4:
            continue

        try:
            route_id = parts[0].strip()
            passengers = int(parts[1].strip())
            delay = float(parts[2].strip())
            trip_count = int(parts[3].strip())
        except (ValueError, IndexError):
            continue

        # If we encounter the same route, aggregate metrics
        if current_route == route_id:
            total_trips += trip_count
            total_passengers += passengers
            total_delay += delay
        else:
            # New route encountered; emit aggregated result of the previous route
            if current_route is not None:
                emit_result(current_route, total_trips, total_passengers, total_delay)

            # Reset aggregators for the new route
            current_route = route_id
            total_trips = trip_count
            total_passengers = passengers
            total_delay = delay

    # Do not forget to emit the last route after exiting the loop
    if current_route is not None:
        emit_result(current_route, total_trips, total_passengers, total_delay)

if __name__ == "__main__":
    main()
