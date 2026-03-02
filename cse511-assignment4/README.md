# Assignment-4-zyesposs

# Project Summary
What I did
-   Loaded the data from the CSV file subreddits.csv into PostgreSQL database.
-   Implemented range partitioning and round robin partitioning as required in the assignment.
-   Used tester code and fixed several issue with helper and tester it self in order all test should pass.
-   After partitioning, I checked and reported how many rows are in: 
     * the main subreddits table
     * each of the partition tables
- Gave a summary of the row counts from all tables after partitioning.

# Project structure

1. I added a .gitignore file to keep the repo clean.
2. I created a docker-compose.yml to:
3. Spin up PostgreSQL server easily.
4. Mount my local project folder into the container so I could code live in VSCode without rebuilding Docker images.

# Issues I faced

0. parameters was messed up several functions with table_names of partitions. Corrected them.
1. while debuging only passed checks was coming, but no output for failures and reason. So, I included.
2. added extra logic for db creation, because if not press d tables would be deleted and that will cause issue.
3. customized read_date function because it's was recognizing in right format true false value

# some extra results view: 

  table_name  | count  
--------------+--------
 range_part0  |   2772
 range_part1  |  17786
 range_part3  |  44009
 range_part2  |  44335
 range_part4  | 805166
 rrobin_part0 | 182814
 rrobin_part3 | 182814
 rrobin_part2 | 182814
 rrobin_part4 | 182814
 subreddits   | 914067
 rrobin_part1 | 182814
(11 rows)

# log details can be found in tester_output.log file. Below is copy.

Database "assignment4" already exists. Dropping all tables inside it...
All tables in "assignment4" dropped successfully.
----------------------------------------------------------------------------
Testing load_data function
 Data loaded successfully into table 'subreddits' from file './subreddits.csv'.
load_data function pass!
----------------------------------------------------------------------------

----------------------------------------------------------------------------
Testing range_partition function
Range partitioning completed for table 'subreddits' into 5 partitions.
range_partition function pass!
----------------------------------------------------------------------------

----------------------------------------------------------------------------
Testing range_insert function
range_insert function pass!
----------------------------------------------------------------------------

----------------------------------------------------------------------------
Testing round_robin_partition function
Round-robin partitioning completed for table 'subreddits' into 5 partitions.
round_robin_partition function pass!
----------------------------------------------------------------------------

----------------------------------------------------------------------------
Testing round_robin_insert function
round_robin_insert function pass!
----------------------------------------------------------------------------

Press d to Delete all tables? 