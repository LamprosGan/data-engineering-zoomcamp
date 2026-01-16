#!/usr/bin/env python
# coding: utf-8
import sys
import click
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm



# Read a sample of the data


dtypes = {
    "VendorID": "Int64",
    "store_and_fwd_flag": "string",
    "RatecodeID": "Int64",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "payment_type": "Int64",
    "trip_type": "Int64",
    "congestion_surcharge": "float64",
    "cbd_congestion_fee": "float64",
}

parse_dates = [
    "lpep_pickup_datetime",
    "lpep_dropoff_datetime"
]

@click.command()
@click.option(
    '--parquet-url',
    default='https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet',
    show_default=True,
    help='URL to the green taxi Parquet file'
)
@click.option('--pg-user', default='root', show_default=True, help='Postgres user')
@click.option('--pg-pass', default='root', show_default=True, help='Postgres password', hide_input=True)
@click.option('--pg-host', default='localhost', show_default=True, help='Postgres host')
@click.option('--pg-port', default=5432, show_default=True, type=int, help='Postgres port')
@click.option('--pg-db', default='ny_taxi', show_default=True, help='Postgres database')
@click.option('--target-table', default='green_trips_2025_11', show_default=True, help='Target table name')


def run(parquet_url, pg_user, pg_pass, pg_host, pg_port, pg_db, target_table):
    """
    Loads a Parquet file from a URL into a Postgres table.
    Creates the table schema if it doesn't exist, then appends all rows.
    """
    # Read Parquet
    try:
        df = pd.read_parquet(parquet_url, engine="pyarrow")
        for col, dtype in dtypes.items():
            if col in df.columns:
                if dtype.startswith("datetime"):
                    df[col] = pd.to_datetime(df[col])
                else:
                    df[col] = df[col].astype(dtype, errors='ignore')
    except Exception as e:
        print(f"Failed to read Parquet at '{parquet_url}': {e}", file=sys.stderr)
        sys.exit(1)

    # Connect to Postgres and upload
    conn_str = f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}'
    try:
        engine = create_engine(conn_str)
        df.head(0).to_sql(name=target_table, con=engine, if_exists='replace', index=False)
        df.to_sql(name=target_table, con=engine, if_exists='append', index=False)
    except Exception as e:
        print(f"Failed to write to database {pg_db} on {pg_host}:{pg_port}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Uploaded {len(df)} rows to table '{target_table}' in database '{pg_db}' on {pg_host}:{pg_port}")

if __name__ == '__main__':
    run()