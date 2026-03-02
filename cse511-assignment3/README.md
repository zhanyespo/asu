# Assignment-3-zyesposs

This is assignment #3 for **CSE511 – Data Processing at Scale**. It implements two spatial analysis tasks using **Apache Spark** and **Scala**:

- **Hotzone Analysis**: Performs a spatial join to count how many pickup points fall into defined rectangular zones.
- **Hotcell Analysis**: Computes the Getis-Ord G statistic to find the top 50 hot grid cells based on spatial and temporal taxi pickup density.

## Project Structure

├── README.md
├── cse511
│   ├── build.sbt
│   ├── logs
│   │   ├── execution_full_data.log
│   │   └── execution_sample100k_data.log
│   ├── project
│   │   ├── build.properties
│   │   ├── plugins.sbt
│   │   ├── project
│   │   └── target
│   ├── result
│   │   ├── output0
│   │   └── output1
│   ├── spark-warehouse
│   ├── src
│   │   ├── main
│   │   └── resources
│   └── target
│       ├── global-logging
│       ├── scala-2.11
│       ├── streams
│       └── task-temp-directory
└── docker-compose.yml

# Core Codes

cse511/src/main/
└── scala
    ├── HotcellAnalysis.scala
    ├── HotcellUtils.scala
    ├── HotzoneAnalysis.scala
    ├── HotzoneUtils.scala
    └── Main.scala

# How to Run:

1. Make sure you have running docker. Go to project dir.
2. Spin up service "docker-compose up -d".
3. Check for status of container "docker ps" with name of container "spark-hotspot".
4. Dive to inside container by command in terminal "docker exec -it spark-hotspot bash".
5. Generate .jar file by running command "sbt assembly".
6. Make sure file "./target/scala-2.11/CSE511-Hotspot-Analysis-assembly-0.1.0.jar" is generated.
7. Make sure a folder src/resources contains csv files.
8. Run command to execute jar file with params:

for sample data:
```
spark-submit ./target/scala-2.11/CSE511-Hotspot-Analysis-assembly-0.1.0.jar result/output hotzoneanalysis src/resources/point-hotzone.csv src/resources/zone-hotzone.csv hotcellanalysis src/resources/yellow_tripdata_2009-01_point.csv > logs/execution_full_data.log 2>&1
```
for full data:
```
spark-submit ./target/scala-2.11/CSE511-Hotspot-Analysis-assembly-0.1.0.jar result/output hotzoneanalysis src/resources/point-hotzone.csv src/resources/zone-hotzone.csv hotcellanalysis src/resources/yellow-trip-sample-100000.csv > logs/execution_sample100k_data.log 2>&1

```

9. Check for outputs logs and data under cse511/result and cse511/logs.

# Additional notes:

1. .gitignore file ingore several folder that is missing from project repo that may require to run project fully
2. docker-compose file is used to spin up docker container and its mounts volumes to project folder.

Any question reach out zyesposs@asu.edu


