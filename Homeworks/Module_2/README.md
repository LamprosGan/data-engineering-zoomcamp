# Module 2 Homework – Workflow Orchestration with Kestra
Data Engineering Zoomcamp

This repository contains my solution for Module 2 Homework of the Data Engineering Zoomcamp.  
The objective of this homework was to extend an existing Kestra workflow to ingest NYC Taxi data for the year 2021, validate the ingested data, and answer a set of conceptual and practical questions related to workflow orchestration and ETL pipelines.

The pipeline processes both Yellow and Green Taxi datasets and loads the data into Google BigQuery using scheduled Kestra flows.

The data source used throughout the homework is the NYC Taxi dataset provided by DataTalksClub:
https://github.com/DataTalksClub/nyc-tlc-data/releases

The GCP environment created in (`gcp_kv`) and in (`gcp_setup`)
The ETL pipeline is implemented using a single scheduled Kestra flow (`gcp_taxi_scheduled`).  
For each execution, the pipeline downloads the monthly taxi CSV file, decompresses it, uploads it to Google Cloud Storage, creates a BigQuery external table, transforms the data, merges it into a partitioned BigQuery table, and finally cleans up temporary files.  
The pipeline is parameterized by taxi type (yellow or green) and by execution date.

---

Question 1  
What is the uncompressed file size of `yellow_tripdata_2020-12.csv`?

To answer this question, the scheduled Kestra flow was executed for Yellow Taxi data for December 2020.  
During execution, the file was downloaded and decompressed in the `extract` task.  
The uncompressed file size was observed directly in the Kestra execution UI under the output of the extract task.

Answer:  
128.3 MiB

---

Question 2  
What is the rendered value of the variable `file` when taxi is green, year is 2020, and month is 04?

The filename is dynamically generated in the flow using the following variable definition:

file: "{{inputs.taxi}}_tripdata_{{trigger.date | date('yyyy-MM')}}.csv"

When the inputs are set to taxi = green and the execution date corresponds to April 2020, the variable is rendered automatically by Kestra during execution.

Answer:  
green_tripdata_2020-04.csv

---

Question 3  
How many rows are there for the Yellow Taxi data for all CSV files in the year 2020?

After ingesting all Yellow Taxi data for the year 2020, the total number of rows was validated using the final merged BigQuery table.  
The validation was performed by filtering the table on the pickup year.

Query used:

```bash
SELECT COUNT(*)
FROM `kestra-sandbox-486222.zoomcamp.yellow_tripdata`
WHERE filename LIKE 'yellow_tripdata_2020-%';
```

Answer:  
24,648,499 rows

---

Question 4  
How many rows are there for the Green Taxi data for all CSV files in the year 2020?

The same validation approach used for Yellow Taxi data was applied to the Green Taxi dataset.  
The final merged Green Taxi table was filtered by pickup year to obtain the total row count for 2020.

Query used:

```bash
SELECT COUNT(*)
FROM `kestra-sandbox-486222.zoomcamp.green_tripdata`
WHERE filename LIKE 'green_tripdata_2020-%';
```

Answer:  
1,734,051 rows

---

Question 5  
How many rows are there for the Yellow Taxi data for the March 2021 CSV file?

The scheduled flow was backfilled for March 2021 using Kestra’s backfill functionality.  
To obtain the exact number of rows ingested from the March 2021 file, the `filename` column (which is added during ingestion) was used instead of filtering by pickup date.  
This ensures that the count reflects exactly the rows loaded from that specific CSV file.

Query used:

```bash
SELECT COUNT(*)  
FROM `kestra-sandbox-486222.zoomcamp.yellow_tripdata`  
WHERE filename = "yellow_tripdata_2021-03.csv";
```

Answer:  
1,925,152 rows

---

Question 6  
How would you configure the timezone to New York in a Schedule trigger?

Kestra Schedule triggers support timezone configuration using IANA timezone identifiers.  
To ensure that the workflow runs according to New York local time, the timezone property was explicitly set in the Schedule trigger configuration.

Configuration used:

timezone: America/New_York

Answer:  
Add a timezone property set to `America/New_York` in the Schedule trigger configuration.

---

2021 Data Processing

Data for January through July 2021 was processed using Kestra’s Backfill functionality on the scheduled flow.  
This allowed historical data ingestion without manually executing the workflow for each month and for each taxi type.

---

Conclusion

This homework demonstrates:
- Workflow orchestration using Kestra
- Parameterized and scheduled ETL pipelines
- Incremental loading and deduplication in BigQuery
- Backfilling historical data
- SQL-based validation of ingested data
