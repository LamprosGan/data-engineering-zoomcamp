#!/usr/bin/env python3
import sys
import click
import pandas as pd
from sqlalchemy import create_engine

dtype = {
    "LocationID": "Int64",
    "Borough": "string",
    "Zone": "string",
    "service_zone": "string",
    "store_and_fwd_flag": "string"
}


@click.command()
@click.option(
    '--csv-url',
    default='https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv',
    show_default=True,
    help='URL to the TLC CSV file'
)
@click.option('--pg-user', default='root', show_default=True, help='Postgres user')
@click.option('--pg-pass', default='root', show_default=True, help='Postgres password')
@click.option('--pg-host', default='localhost', show_default=True, help='Postgres host')
@click.option('--pg-port', default=5432, show_default=True, type=int, help='Postgres port')
@click.option('--pg-db', default='ny_taxi', show_default=True, help='Postgres database')
@click.option('--target-table', default='zones', show_default=True, help='Target table name')
def main(csv_url, pg_user, pg_pass, pg_host, pg_port, pg_db, target_table):
    
    try:
        df = pd.read_csv(csv_url, dtype=dtype)
    except Exception as e:
        print(f"Failed to read CSV at '{csv_url}': {e}", file=sys.stderr)
        sys.exit(1)

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
    main()
