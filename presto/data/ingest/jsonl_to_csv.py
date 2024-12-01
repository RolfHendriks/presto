import csv
import json
import os
import pandas as pd
import time

# JSONL TO CSV
# This script converts data from jsonl files into a csv format.
# Our main dataset includes jsonl data that is too large to feasibly handle. Testing has shown that 
# using CSV instead is several times as fast, and that using CSV is key to feasibly being able to load 
# full datasets if needed.

def profile(message, timestamp):
    elapsed = time.perf_counter() - timestamp
    print(f'{elapsed:.3f}:\t{message}')

def append_records(
        records: pd.DataFrame, 
        path: str, 
        index_col = 'id', 
        verbosity = 1
) -> int:
    """
    Given a CSV data file, append new records to the end of the file.
    If no file exists, create a new CSV file with the given records.
    """
    file_exists = os.path.exists(path)
    with open(path, 'a') as outfile:
        records.to_csv(outfile, header = not file_exists)
        if verbosity > 0:
            print(f'appended {len(records)} records to {path}')
    return len(records)
    # possible future iteration as needed: prevent duplicates based on ID

def jsonl_to_csv(
        jsonpath: str, csvpath: str = None, 
        process_json = lambda x: x, 
        index_col = 'id', 
        batch_size = 10_000, 
        verbosity = 1, 
        if_exists = 'append'
):
    """
    Converts potentially large jsonl files to csv.

    Saves results in batches for potentially long operations that can be paused and resumed.
    If the destination file exists, new records will be appended to the end of the file. This allows us to potentially consolidate multiple 
    jsonl files into a single CSV file.
    """
    # to do: how to make a properly documented enum-type string for if_exists?
    csv_filename = csvpath or jsonpath.replace('jsonl', 'csv')    
    if os.path.exists(csv_filename):
        if if_exists == 'overwrite':
            os.remove(csv_filename)
        if if_exists == 'skip':
            return
    t0 = time.perf_counter()
    with open(jsonpath) as file:
        if verbosity > 0:
            print(f'Opened file {jsonpath}')
        batch = []  
        count = 0
        def append_batch() -> int:
            records = pd.DataFrame.from_records(batch)
            return append_records(records, csv_filename, index_col = index_col, verbosity = 0)
        while True:
            line = file.readline()
            if line:
                js = json.loads(line)
                record = process_json(pd.Series(js))
                batch.append(record)  
                if len(batch) == batch_size:
                    count += append_batch()
                    batch = []
                    if verbosity > 0:
                        profile(f'converted {count:,} records', t0)
            else:
                count += append_batch()
                if verbosity > 0:
                    profile(f'Finshed converting {count} records from json to csv.\nSee {csv_filename} for results.', t0)
                break

# to do: add scripting ability