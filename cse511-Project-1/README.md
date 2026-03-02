# Project-1-zyesposs

# main note

!!! SCRIPTS contains commented out lines, what was used for debuging and running code locally in WSL and DOCKER. Latest version with running in Container is committed to git.

A tree of project:

.
├── Dockerfile
├── README.md
├── data (IGNORED, used just for local debug)
│   ├── Phase-1.zip
│   ├── cmd_history.txt
│   ├── neo4j-graph-data-science-2.15.0.jar
│   ├── neo4j-graph-data-science-2.15.0.zip
│   └── yellow_tripdata_2022-03.parquet
├── docker-compose.yml
├── logs
│   ├── data_loader.log
│   └── tester.log
├── screenshots
│   ├── changed_format.png
│   ├── data_validation.png
│   ├── load_completed.png
│   └── plugin_version.png
└── scripts
    ├── __pycache__
    │   └── interface.cpython-310.pyc
    ├── data_loader.py
    ├── interface.py
    └── tester.py

# additional notes_1:
- to debug locally and test used docker-compose file to mount scripts and sync changes locally
    that was later commited to git repo.
- customized Dockerfile provided as template and added below changes
    1. added new argument(parameter)for GITHUB_TOKEN
    2. app installation of git, as its request to pull repo from git repo.
    3. added pips required for project
    4. workdir app is main where repo will be cloned and downloaded trip data and unzipped and moved to plugin folder.
    5. configuration setups for neo4j server.
    6. cleaning folders of neo4j to run server from scratch with application crediatials.
    7. CMD commands to run whole project in container once its ready to use.
    8. all logs for running python scripts will be stored in logs folder.

# Additional notes_2:

1. .env file need with your token required to build the project and run it
    ```GITHUB_TOKEN=YOURTOKENHERE```
2. logger level in interface set to ERROR to ignore log outputs with warnings that occured due to version change for neo4j and plugin.
    ```logging.getLogger("neo4j").setLevel(logging.ERROR)```
3. Convert date-time columns to supported format in data_loaded script: 
     ```   trips['tpep_pickup_datetime'] = trips['tpep_pickup_datetime'].dt.strftime('%Y-%m-%dT%H:%M:%S')
        trips['tpep_dropoff_datetime'] = trips['tpep_dropoff_datetime'].dt.strftime('%Y-%m-%dT%H:%M:%S') ```
# some debugin screenshots locally:

![alt text](screenshots/load_completed.png)

![alt text](screenshots/data_validation.png)

![alt text](screenshots/plugin_version.png)

![alt text](screenshots/changed_format.png)

added 

# required to set to remove WARNING message appearing for ID depricated in version.
logging.getLogger("neo4j").setLevel(logging.ERROR)

for interface because using version of neo4j and plugin 2.15 having some depricated warning about utils.ID

# LOGS from execution:

data_loaded logs:
```
Dropping existing GDS graph if it exists...
Creating GDS graph projection...
Projection completed. Details:
{'nodeProjection': {'Location': {'label': 'Location', 'properties': {}}}, 'relationshipProjection': {'TRIP': {'aggregation': 'DEFAULT', 'orientation': 'NATURAL', 'indexInverse': False, 'properties': {'distance': {'aggregation': 'DEFAULT', 'property': 'distance', 'defaultValue': 1.0}}, 'type': 'TRIP'}}, 'graphName': 'graph', 'nodeCount': 42, 'relationshipCount': 1530, 'projectMillis': 1903}
GDS graph 'graph' is ready.
Load complete.
```

Tester logs:
```Trying to connect to server 
Server is running

----------------------------------
Testing if data is loaded into the database
	Count of Edges is correct: PASS
	Count of Edges is correct: PASS
Testing if PageRank is working
	PageRank Test 1: PASS
Testing if BFS is working
	BFS Test 2: PASS
----------------------------------

Testing Complete: Note that the test cases are not exhaustive. You should run your own tests to ensure that your code is working correctly.
**************************************************
Testinng BFS for unreachable nodes:
Testing if BFS is working
[{'path': []}]
**************************************************
Testinng page rank without weight parameter:
[{'name': 242, 'score': 1.93613}, {'name': 69, 'score': 1.86786}, {'name': 213, 'score': 1.76427}, {'name': 159, 'score': 1.75887}, {'name': 254, 'score': 1.6964}, {'name': 168, 'score': 1.64942}, {'name': 51, 'score': 1.54531}, {'name': 119, 'score': 1.44891}, {'name': 174, 'score': 1.37937}, {'name': 78, 'score': 1.29267}, {'name': 235, 'score': 1.1947}, {'name': 60, 'score': 1.11528}, {'name': 185, 'score': 1.0901}, {'name': 47, 'score': 1.08533}, {'name': 247, 'score': 1.08209}, {'name': 18, 'score': 1.07299}, {'name': 182, 'score': 1.01577}, {'name': 167, 'score': 0.99805}, {'name': 169, 'score': 0.94258}, {'name': 126, 'score': 0.81751}, {'name': 147, 'score': 0.75952}, {'name': 241, 'score': 0.74616}, {'name': 81, 'score': 0.74525}, {'name': 20, 'score': 0.74495}, {'name': 208, 'score': 0.73868}, {'name': 212, 'score': 0.73421}, {'name': 32, 'score': 0.73235}, {'name': 200, 'score': 0.68868}, {'name': 136, 'score': 0.67322}, {'name': 220, 'score': 0.65286}, {'name': 94, 'score': 0.53538}, {'name': 3, 'score': 0.52134}, {'name': 248, 'score': 0.49325}, {'name': 259, 'score': 0.43301}, {'name': 250, 'score': 0.42803}, {'name': 183, 'score': 0.40799}, {'name': 240, 'score': 0.37238}, {'name': 31, 'score': 0.3165}, {'name': 59, 'score': 0.21477}, {'name': 184, 'score': 0.18998}, {'name': 58, 'score': 0.18655}, {'name': 46, 'score': 0.17796}]
```

If you need any other clarifications, please let me know.