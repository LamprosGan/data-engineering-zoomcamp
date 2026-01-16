# Module 1 Homework: Docker, SQL & Terraform
This homework covers environment setup, data ingestion, SQL queries, and infrastructure management with Terraform, following the course exercises.


## Question 1: Understanding Docker images

**Task:** Run Docker with the `python:3.13` image. Use an entrypoint `bash` to interact with the container.

**Question:** What's the version of pip in the image?

Options:
- 25.3
- 24.3.1
- 24.2.1
- 23.3.1

**Steps to solve:**

```bash
$ docker run -it --rm --entrypoint=bash python:3.13 

$ pip -V
```
**Answer:** 25.3


## Question 2: Understanding Docker networking and docker-compose

**Task:** Given the docker-compose.yaml, determine the hostname and port that pgAdmin should use to connect to the Postgres database.

**Answer:**  
- **Hostname:** db  
- **Port:** 5432  

**Explanation:**  
Within Docker Compose, all services are on the same default network and can reach each other using their **service names** as hostnames.  
PgAdmin communicates with Postgres using the **container’s internal port (5432)**, not the host port.  


## Environment Setup

For this homework, we leverage the environment and tools we built during the learning process:


- **PostgreSQL database** is already running via Docker Compose.  
  - Compose file location: [Docker-SQL-Terraform/terrademo/docker-compose.yaml](https://github.com/LamprosGan/data-engineering-zoomcamp/blob/main/Docker-SQL-Terraform/pipeline/docker-compose.yaml)
  - Postgres image: `postgres:16`  
  - pgAdmin image: `dpage/pgadmin4`  
  - Port mappings:  
    - Postgres: `5432:5432`  
    - pgAdmin: `8085:80`  
  - Volumes:  
    - `ny_taxi_postgres_data` for Postgres data  
    - `pgadmin_data` for pgAdmin configuration  

- You can inspect and manage the database via **pgAdmin** at:  http://localhost:8085

- Default email: `admin@admin.com`  
- Password: `root`  

- The database **already contains the zones dataset**, which was uploaded in a previous step.  

**Zones dataset source:** [TLC taxi zone lookup CSV](https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv)  
**Uploaded table:** `zones`  

---

Next, we needed to upload the **green taxi trips data for November 2025** to the database.  

- **Dataset source (Parquet):**  
[green_tripdata_2025-11.parquet](https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet)  
- **Target table in Postgres:** `green_trips_2025_11`  
- **Script used:** `green_trip_data.py`  
- **Virtual environment:** `.venv` in `pipeline` folder  

---

### Steps to upload:

1. **Activate the virtual environment**

```bash
$ source Docker-SQL-Terraform/pipeline/.venv/bin/activate

$ docker-compose up
```

2. **Run the script from the root folder using uv**
```bash
$ uv run Homeworks/Module_1_Docker_SQL_Terraform/green_trip_data.py -- \
    --pg-user root \
    --pg-pass root \
    --pg-host localhost \
    --pg-port 5432 \
    --pg-db ny_taxi \
    --target-table green_trips_2025_11 \
    --parquet-url https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet
```

The script will:

Download the Parquet file from the URL.

Convert columns to correct types (dtypes and datetime).

Upload all rows to the Postgres database table green_trips_2025_11.

Result: 46,912 rows uploaded successfully.


## Question 3: Short Trips in November 2025

**Task:** For the trips in November 2025 (`lpep_pickup_datetime` between `'2025-11-01'` and `'2025-12-01'`, exclusive of the upper bound), how many trips had a `trip_distance` of less than or equal to 1 mile?

**SQL Query:**

```sql
SELECT COUNT(*) AS Short_Trips
FROM public.green_trips_2025_11
WHERE DATE(lpep_pickup_datetime) >= '2025-11-01'
  AND DATE(lpep_pickup_datetime) < '2025-12-01'
  AND trip_distance <= 1;
```
**Answer:** 8007


## Question 4: Pick-up Day with Longest Trip

**Task:** Which pick-up day had the longest trip distance? Only consider trips with `trip_distance < 100` miles (to exclude data errors).  

**SQL Query:**

```sql
SELECT DATE(lpep_pickup_datetime) AS pickup_day,
       MAX(trip_distance) AS max_distance
FROM public.green_trips_2025_11
WHERE trip_distance < 100
GROUP BY pickup_day
ORDER BY max_distance DESC
LIMIT 1;
```

**Answer:** 2025-11-14 with 88.03 miles trip distance.


## Question 5: Pickup Zone with Largest Total Amount on November 18, 2025

**Task:** Which pickup zone had the largest total amount (`sum(total_amount)`) on November 18, 2025? Only trips from that specific day are considered.

**SQL Query:**

```sql
SELECT z."Zone" AS pickup_zone,
       SUM(g."total_amount") AS total_revenue
FROM public.green_trips_2025_11 g
JOIN public.zones z
  ON g."PULocationID" = z."LocationID"
WHERE DATE(g."lpep_pickup_datetime") = '2025-11-18'
GROUP BY z."Zone"
ORDER BY total_revenue DESC
LIMIT 1;
```
**Answer:** East Harlem North with total revenue of 9281.92$.

## Question 6: Dropoff Zone with Largest Tip from East Harlem North in November 2025

**Task:** For passengers picked up in the zone named "East Harlem North" in November 2025, which dropoff zone had the largest total tip?  

**SQL Query:**

```sql
SELECT zdrop."Zone" as dropoff_zone, max(g."tip_amount") as largest_tip
FROM public.green_trips_2025_11 g
JOIN public.zones zpick
ON g."PULocationID" = zpick."LocationID"
JOIN public.zones zdrop
ON g."DOLocationID" = zdrop."LocationID"
WHERE zpick."Zone" = 'East Harlem North'
AND g."lpep_pickup_datetime" >= '2025-11-01'
AND g."lpep_pickup_datetime" < '2025-12-01'
GROUP BY dropoff_zone
ORDER BY largest_tip DESC
LIMIT 1;
```
**Answer:** Yorkville West with the largest amount of tip at 81.89$.

**To Stop the Environment**

```bash
$ docker-compose down 
```

Now that we finished the Docker and SQL section, we are now ready to move on **Terraform exercises**.


## Question 7. Terraform Workflow


## Terraform Homework: Creating Resources in GCP

In this section of the homework, we prepared the environment and created resources in Google Cloud Platform (GCP) using Terraform.

Following the procedure described in the course, we:

1. Created the Terraform configuration files:
   - `main.tf` → defines the GCP resources (e.g., a Cloud Storage bucket, BigQuery dataset)  
   - `variables.tf` → stores configurable variables for our resources  

2. Used Terraform commands to manage our infrastructure:

### Quick Terraform Commands

- **Initialize Terraform** (downloads provider plugins, sets up backend):

```bash
$ cd /workspaces/data-engineering-zoomcamp/Docker-SQL-Terraform/terrademo

$ terraform init
$ terraform plan
$ terraform apply
$ terraform destroy
```

Following this workflow, we successfully created a GCP bucket and BigQuery dataset, verified them, and then destroyed the resources to ensure no leftover infrastructure.

**Answer:** terraform init, terraform apply -auto-approve, terraform destroy
