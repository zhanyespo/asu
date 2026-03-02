import pyarrow.parquet as pq
import pandas as pd
from neo4j import GraphDatabase
import time


class DataLoader:

    def __init__(self, uri, user, password):
        """
        Connect to the Neo4j database and other init steps
        
        Args:
            uri (str): URI of the Neo4j database
            user (str): Username of the Neo4j database
            password (str): Password of the Neo4j database
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self.driver.verify_connectivity()


    def close(self):
        """
        Close the connection to the Neo4j database
        """
        self.driver.close()


    # Define a function to create nodes and relationships in the graph
    def load_transform_file(self, file_path):
        """
        Load the parquet file and transform it into a csv file
        Then load the csv file into neo4j

        Args:
            file_path (str): Path to the parquet file to be loaded
        """

        # Read the parquet file
        trips = pq.read_table(file_path)
        trips = trips.to_pandas()

        # Some data cleaning and filtering
        trips = trips[['tpep_pickup_datetime', 'tpep_dropoff_datetime', 'PULocationID', 'DOLocationID', 'trip_distance', 'fare_amount']]

        # Filter out trips that are not in bronx
        bronx = [3, 18, 20, 31, 32, 46, 47, 51, 58, 59, 60, 69, 78, 81, 94, 119, 126, 136, 147, 159, 167, 168, 169, 174, 182, 183, 184, 185, 199, 200, 208, 212, 213, 220, 235, 240, 241, 242, 247, 248, 250, 254, 259]
        trips = trips[trips.iloc[:, 2].isin(bronx) & trips.iloc[:, 3].isin(bronx)]
        trips = trips[trips['trip_distance'] > 0.1]
        trips = trips[trips['fare_amount'] > 2.5]

        # Convert date-time columns to supported format
        trips['tpep_pickup_datetime'] = trips['tpep_pickup_datetime'].dt.strftime('%Y-%m-%dT%H:%M:%S')
        trips['tpep_dropoff_datetime'] = trips['tpep_dropoff_datetime'].dt.strftime('%Y-%m-%dT%H:%M:%S')

        
        # Convert to csv and store in the current directory
        save_loc = "/var/lib/neo4j/import/" + file_path.split(".")[0] + '.csv'
        trips.to_csv(save_loc, index=False)

        # TODO: Your code here
        session = self.driver.session()
        
        # Creating uniqueness constraint on Location
        session.run("""
            CREATE CONSTRAINT IF NOT EXISTS FOR (l:Location)
            REQUIRE l.name IS UNIQUE
        """)

        # Load Location nodes
        session.run(f"""
            LOAD CSV WITH HEADERS FROM 'file:///{file_path.split(".")[0]}.csv' AS row
            WITH toInteger(row.PULocationID) AS pu, toInteger(row.DOLocationID) AS do
            MERGE (:Location {{name: pu}})
            MERGE (:Location {{name: do}})
        """)

        # Creating TRIP relationships
        session.run(f"""
            LOAD CSV WITH HEADERS FROM 'file:///{file_path.split(".")[0]}.csv' AS row
            MATCH (start:Location {{name: toInteger(row.PULocationID)}})
            MATCH (end:Location {{name: toInteger(row.DOLocationID)}})
            MERGE (start)-[:TRIP {{
                distance: toFloat(row.trip_distance),
                fare: toFloat(row.fare_amount),
                pickup_dt: datetime(row.tpep_pickup_datetime),
                dropoff_dt: datetime(row.tpep_dropoff_datetime)
            }}]->(end)
        """)

        # Reset and project the GDS graph
        try:
            print("Dropping existing GDS graph if it exists...")
            session.run("CALL gds.graph.drop('graph', false) YIELD graphName")
        except Exception as e:
            print("Warning: Could not drop existing graph — maybe it doesn't exist yet.")
            print("Details:", e)

        print("Creating GDS graph projection...")
        projection_result = session.run("""
            CALL gds.graph.project(
                'graph',
                'Location',
                {
                    TRIP: {
                        type: 'TRIP',
                        properties: {
                            distance: {
                                property: 'distance',
                                defaultValue: 1.0
                            }
                        }
                    }
                }
            )
        """).data()

        # Optional: log projection result
        print("Projection completed. Details:")
        for row in projection_result:
            print(row)

        # Confirm that projection succeeded
        exists_check = session.run("CALL gds.graph.exists('graph') YIELD exists RETURN exists").single()
        if exists_check and exists_check["exists"]:
            print("GDS graph 'graph' is ready.")
        else:
            print("GDS graph projection failed.")

        # Close session
        session.close()
        print("Load complete.")



def main():

    total_attempts = 10
    attempt = 0

    # The database takes some time to starup!
    # Try to connect to the database 10 times
    while attempt < total_attempts:
        try:
            data_loader = DataLoader("neo4j://localhost:7687", "neo4j", "project1phase1")
            data_loader.load_transform_file("yellow_tripdata_2022-03.parquet")
            data_loader.close()
            
            attempt = total_attempts

        except Exception as e:
            print(f"(Attempt {attempt+1}/{total_attempts}) Error: ", e)
            attempt += 1
            time.sleep(10)


if __name__ == "__main__":
    main()

