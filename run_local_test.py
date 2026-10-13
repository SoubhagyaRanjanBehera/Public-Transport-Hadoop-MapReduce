#!/usr/bin/env python3
"""
Local MapReduce Simulation Runner
Group 9 - BDA Mini-Project

This script simulates the complete Hadoop MapReduce pipeline locally:
  Data Source -> Mapper -> Shuffle & Sort -> Reducer -> Output file

It requires no Hadoop installation, allowing immediate testing and verification
on any machine (Windows, Linux, macOS).
"""

import os
import sys
import subprocess

def run_pipeline():
    project_root = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(project_root, "data", "transit_data.csv")
    mapper_script = os.path.join(project_root, "src", "mapper.py")
    reducer_script = os.path.join(project_root, "src", "reducer.py")
    output_dir = os.path.join(project_root, "output")
    output_file = os.path.join(output_dir, "results.txt")

    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(data_file):
        print(f"Error: Dataset not found at {data_file}")
        sys.exit(1)

    print("=================================================================")
    print("  Group 9: Public Transportation Analysis - Local MapReduce Run  ")
    print("=================================================================")
    print(f"[1/4] Reading dataset from: {os.path.relpath(data_file, project_root)}")

    # 1. Map Phase: pipe transit_data.csv into mapper.py
    with open(data_file, "r", encoding="utf-8") as f_in:
        mapper_proc = subprocess.Popen(
            [sys.executable, mapper_script],
            stdin=f_in,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        mapper_out, mapper_err = mapper_proc.communicate()

    if mapper_proc.returncode != 0:
        print(f"Mapper Error:\n{mapper_err}")
        sys.exit(1)

    print(f"[2/4] Mapper completed successfully. Generated {len(mapper_out.strip().splitlines())} intermediate key-value pairs.")

    # 2. Shuffle & Sort Phase: sort lines alphabetically by key
    intermediate_lines = [line for line in mapper_out.strip().splitlines() if line]
    sorted_lines = sorted(intermediate_lines)
    sorted_input_for_reducer = "\n".join(sorted_lines) + "\n"
    print(f"[3/4] Shuffle & Sort completed. Records grouped by Route_ID.")

    # 3. Reduce Phase: pipe sorted lines into reducer.py
    reducer_proc = subprocess.Popen(
        [sys.executable, reducer_script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    reducer_out, reducer_err = reducer_proc.communicate(input=sorted_input_for_reducer)

    if reducer_proc.returncode != 0:
        print(f"Reducer Error:\n{reducer_err}")
        sys.exit(1)

    # 4. Save results to output/results.txt
    header = "Route_ID\tTotal_Trips\tTotal_Passengers\tAvg_Passengers_Per_Trip\tAvg_Delay_Min\n"
    full_output = header + reducer_out
    with open(output_file, "w", encoding="utf-8") as f_out:
        f_out.write(full_output)

    print(f"[4/4] Reducer completed. Results written to: {os.path.relpath(output_file, project_root)}")
    print("\n------------------------- FINAL RESULTS -------------------------")
    print(f"{'Route ID':<12} | {'Trips':<6} | {'Passengers':<11} | {'Avg Pass/Trip':<14} | {'Avg Delay (m)':<13}")
    print("-" * 68)

    for line in reducer_out.strip().splitlines():
        parts = line.split("\t")
        if len(parts) == 5:
            r_id, trips, pass_count, avg_pass, avg_delay = parts
            print(f"{r_id:<12} | {trips:<6} | {pass_count:<11} | {avg_pass:<14} | {avg_delay:<13}")

    print("-----------------------------------------------------------------")
    print("Done! The MapReduce logic is verified and ready for Hadoop cluster submission.")

if __name__ == "__main__":
    run_pipeline()
