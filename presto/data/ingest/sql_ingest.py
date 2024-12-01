from collections.abc import Iterable 
import sqlite3 as sql
import time

import numpy as np
import pandas as pd

def check_required_columns(data: pd.DataFrame, columns: list):
    missing_columns = set(columns).difference(set(data.columns))
    if len(missing_columns) > 0:
        raise ValueError(f'Missing column(s): {missing_columns}')

def insert_records(
    data: pd.DataFrame,
    table: str,
    conn: sql.Connection,
    include_index = True,
    batch_size = 500,
    commit_batches = True,
    feedback_batch_size = 100_000
    # potential future option as needed: how to handle duplicates
):    
    """
    Inserts potentially large volumes (millions of records) of Pandas data into an SQL database.
    This is functionally identical to DataFrame.to_sql, except that we get progressive feedback + results.
    Progressive saving and feedback is especially important for very large datasets and for performance tuning.

    Parameters
    ----------
    - data: the Pandas DataFrame holding the records to insert into SQL.
    - table: the name of the SQL table into which to insert records. Record columns must match SQL table name columns. Use rename(columns) and drop(columns) to fit data into your SQL schema before inserting.
    - include_index: whether to include the DataFrame's index as if it were an SQL column or to omit the index
    - batch_size: the numer of records to insert into SQL at once. Tuning this parameter is important for performance. Try experimenting with different values to find what is best for your machine.
    - commit_batches: saves changes to disk after each batch. This is recommended for large datasets. If disabled, you are responsible for committing changes to disk as needed. 
    - feedback_batch_size: the number of records after which to emit progressive feedback for progress. Use None to disable all feedback.

    Performance Notes
    -----------------
    Observed batch size vs records per second for inserting into a table.
    Performance measurements are for in-memory insertions into an empty table without indices. Real-world performance will likely be substantially slower and can vary widely 
    based on table structure and hardware.

    -1      4,000
    -2      8,000
    -5      17,000
    -10:     29,000
    -100:    69,000
    -200:    71,000
    -500:    79,000
    -1000:   78,000
    -5000:   67,000
    """
    count = len(data)
    if feedback_batch_size != None:
        print(f'Inserting {count:,d} records into {table}...')
    columns_str = ','.join(data.columns)
    if include_index:
        columns_str = data.index.name + ',' + columns_str
    placeholder_str = ','.join(['?'] * (data.shape[1] + 1 if include_index else data.shape[1]))
    batch_count = 1 + count // batch_size
    query = f"""
    INSERT INTO {table}({columns_str})
    VALUES({placeholder_str})
    """
    t = time.perf_counter()
    for batch in range(batch_count):
        range_start = batch * batch_size
        range_end = min(range_start + batch_size, count)
        records = data.iloc[range_start : range_end].to_records(index = include_index)
        # Fix: sqlite mangles numpy integers. sqlite documentation states that only Python standard data types are supported for parameterized queries, so this is by design.
        # To resolve, we convert all numpy ints to standard ints:
        records = [[int(value) if isinstance(value, np.int64) else value for value in values] for values in records]
        conn.executemany(query, records)
        if commit_batches:
            conn.commit()

        should_emit_feedback = feedback_batch_size != None and (range_end // feedback_batch_size > range_start // feedback_batch_size or range_end >= count)
        if should_emit_feedback:
            elapsed = time.perf_counter() - t
            progress = range_end / count
            print(f'{elapsed:.2f}: inserted {range_end:,d} of {count:,d} records ({progress * 100:.1f}%) @ {round(range_end / elapsed)} records / sec')
    

def import_reviews(reviews: pd.DataFrame, db_connection: sql.Connection):
    check_required_columns(reviews, ['product_id', 'user_id', 'rating', 'review', 'title', 'upvotes'])
    insert_records(reviews, 'review', db_connection, include_index = False)


def import_products(products: pd.DataFrame, connection: sql.Connection):
    required_columns = ['title', 'title_search', 'description', 'creator', 'creator_search', 'category']
    check_required_columns(products, required_columns)    
    insert_records(products, 'product', conn)

def find_duplicates(
    data: pd.DataFrame,
    table: str,
    conn: sql.Connection,
    sql_index_column = 'id',
    data_index_column = None, # None means use the DataFrame index
) -> pd.DataFrame:
    """ 
    Given a DataFrame and a target SQL table, return the records in the DataFrame that already exist in the target table.

    The purpose of this method is to help insert non-duplicate records and to troubleshoot errors relating to duplicate records.
    """
    result = data.copy()
    if data_index_column != None:
        result = result.set_index(data_index_column)
    sql_ids = pd.read_sql_query(f"SELECT {sql_index_column} FROM {table}", conn)[sql_index_column]
    dataframe_ids = data.index
    duplicate_ids = list(set(sql_ids).intersection(set(dataframe_ids)))
    return result.loc[duplicate_ids]

def get_single_value(iterable_or_string, sep = ', ') -> str:
    """
    Flattens inputs that may or may not be a list or a list string into a single string. 
    
    Examples:
    - "['Value']" or ['Value'] is transformed into 'Value'
    - "[]" or [] is transformed into ''
    - "Value" remains as-is
    - "[1,2]" or [1,2] is transformed into "1, 2" (assuming the default separator)
    """
    if isinstance(iterable_or_string, str):
        # if string represents an array ('[...]'), unpack the array. This happens frequently in our data sets.
        if iterable_or_string.startswith('['):
            try:
                l = eval(iterable_or_string)
                return get_single_value(l)
            except:
                pass
        return iterable_or_string
    if isinstance(iterable_or_string, Iterable):
        return sep.join(map(str, iterable_or_string))
    return str(iterable_or_string)