# Import required libraries
# Do not install/import any additional libraries
import psycopg2
import psycopg2.extras
import json
import csv
import math 


# Lets define some of the essentials
# We'll define these as global variables to keep it simple
username = "postgres"
password = "postgres"
dbname = "assignment4"
host = "127.0.0.1"


def get_open_connection():
    """
    Connect to the database and return connection object
    
    Returns:
        connection: The database connection object.
    """

    return psycopg2.connect(f"dbname='{dbname}' user='{username}' host='{host}' password='{password}'")



def load_data(table_name, csv_path, connection, header_file):
    """
    Create a table with the given name and load data from the CSV file located at the given path.

    Args:
        table_name (str): The name of the table where data is to be loaded.
        csv_path (str): The path to the CSV file containing the data to be loaded.
        connection: The database connection object.
        header_file (str): The path to where the header file is located
    """

    cursor = connection.cursor()

    # Creating the table
    with open(header_file) as json_data:
        header_dict = json.load(json_data)

    table_rows_formatted = (", ".join(f"{header} {header_type}" for header, header_type in header_dict.items()))
    create_table_query = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            {table_rows_formatted}
            )'''

    cursor.execute(create_table_query)
    connection.commit()


    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)  # Skip header row

        insert_query = f"INSERT INTO {table_name} ({', '.join(headers)}) VALUES ({', '.join(['%s' for _ in headers])})"

        for row in reader:
            sanitized_row = [None if cell == '' else cell for cell in row]
            cursor.execute(insert_query, sanitized_row)


    connection.commit()
    cursor.close()
    print(f" Data loaded successfully into table '{table_name}' from file '{csv_path}'.")


def range_partition(data_table_name, partition_table_name, num_partitions, header_file, column_to_partition, connection):
    """
    Use this function to partition the data in the given table using a range partitioning approach.

    Args:
        data_table_name (str): The name of the table that contains the data loaded during load_data phase.
        partition_table_name (str): The name of the table to be created for partitioning.
        num_partitions (int): The number of partitions to create.
        header_file (str): path to the header file that contains column headers and their data types
        column_to_partition (str): The column based on which we are creating the partition.
        connection: The database connection object.
    """

    cursor = connection.cursor()

    cursor.execute(f"SELECT MIN({column_to_partition}), MAX({column_to_partition}) FROM {data_table_name};")
    min_val, max_val = cursor.fetchone()

    range_size = math.ceil((max_val - min_val + 1) / num_partitions)

    with open(header_file, 'r') as f:
        header_dict = json.load(f)

    columns_definition = ", ".join(f"{col} {dtype}" for col, dtype in header_dict.items())

    for i in range(num_partitions):
        start = min_val + i * range_size
        end = start + range_size

        child_table = f"{partition_table_name}{i}"
        create_query = f"CREATE TABLE IF NOT EXISTS {child_table} ({columns_definition});"
        cursor.execute(create_query)

        if i == num_partitions - 1:
            insert_query = f"""
                INSERT INTO {child_table}
                SELECT * FROM {data_table_name}
                WHERE {column_to_partition} >= {start} AND {column_to_partition} <= {end};
            """
        else:
            insert_query = f"""
                INSERT INTO {child_table}
                SELECT * FROM {data_table_name}
                WHERE {column_to_partition} >= {start} AND {column_to_partition} < {end};
            """
        cursor.execute(insert_query)

    connection.commit()
    cursor.close()

    print(f"Range partitioning completed for table '{data_table_name}' into {num_partitions} partitions.")



def round_robin_partition(data_table_name, partition_table_name, num_partitions, header_file, connection):
    """
    Use this function to partition the data in the given table using a round-robin approach.

    Args:
        data_table_name (str): The name of the table that contains the data loaded during load_data phase.
        partition_table_name (str): The name of the table to be created for partitioning.
        num_partitions (int): The number of partitions to create.
        header_file (str): path to the header file that contains column headers and their data types
        connection: The database connection object.
    """

    cursor = connection.cursor()

    with open(header_file, 'r') as f:
        header_dict = json.load(f)

    columns_definition = ", ".join(f"{col} {dtype}" for col, dtype in header_dict.items())

    for i in range(num_partitions):
        child_table = f"{partition_table_name}{i}"
        create_query = f"CREATE TABLE IF NOT EXISTS {child_table} ({columns_definition});"
        cursor.execute(create_query)

    cursor.execute(f"SELECT * FROM {data_table_name};")
    rows = cursor.fetchall()

    for idx, row in enumerate(rows):
        partition_idx = idx % num_partitions
        child_table = f"{partition_table_name}{partition_idx}"
        placeholders = ", ".join(["%s"] * len(row))
        insert_query = f"INSERT INTO {child_table} VALUES ({placeholders});"
        cursor.execute(insert_query, row)

    connection.commit()
    cursor.close()

    print(f"Round-robin partitioning completed for table '{data_table_name}' into {num_partitions} partitions.")




def delete_partitions(table_name, num_partitions, connection):
    """
    This function in NOT graded and for your own testing convinience.
    Use this function to delete all the partitions that are created by you.

    Args:
        table_name (str): The name of the table containing the partitions to be deleted.
        num_partitions (int): The number of partitions to be deleted.
        connection: The database connection object.
    """

    cursor = connection.cursor()

    for i in range(num_partitions):
        partition_name = f"{table_name}{i}"
        cursor.execute(f"DROP TABLE IF EXISTS {partition_name};")

    connection.commit()
    cursor.close()

    print(f"Deleted all {num_partitions} partitions for '{table_name}'.")

