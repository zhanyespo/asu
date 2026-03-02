# Assignment-2-zyesposs

!!! added .gitignore it order to exclude from commit all unnecessary files from project

Project Structure from VSCode:

![alt text](screenshots/image.png)

Run status of Docker container:

![alt text](screenshots/image-1.png)

Executed script to validate scala script:

spark-submit ./target/scala-2.11/CSE511-assembly-0.1.0.jar result/output rangequery src/resources/arealm10000.csv -93.63173,33.0183,-93.359203,33.219456 rangejoinquery src/resources/arealm10000.csv src/resources/zcta10000.csv distancequery src/resources/arealm10000.csv -88.331492,32.324142 1 distancejoinquery src/resources/arealm10000.csv src/resources/arealm10000.csv 0.1

A lines with Df show was commented out + Main.scala was refactored to printout single line with all results.
// resultDf.show()

Final output:
```root@b8ff149eb94a:~/cse511# spark-submit ./target/scala-2.11/CSE511-assembly-0.1.0.jar result/output rangequery src/resources/arealm10000.csv -93.63173,33.0183,-93.359203,33.219456 rangejoinquery src/resources/arealm10000.csv src/resources/zcta10000.csv distancequery src/resources/arealm10000.csv -88.331492,32.324142 1 distancejoinquery src/resources/arealm10000.csv src/resources/arealm10000.csv 0.1
2025-03-13 07:57:58 WARN  NativeCodeLoader:62 - Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
4 7612 302 12336
```

Additional not graded things I did, but needed files to check all definitions:

A huge file from NYC Taxi was cleaned and only drop off points was extracted.

head -n 5 /root/cse511-data/taxi_dropoff_points_clean_fixed.csv
-73.993803,40.695922000000003
-73.955849999999998,40.768030000000003
-73.869983000000005,40.770225000000003
-73.996557999999993,40.731848999999997
-74.008377999999993,40.720350000000003

was able to check only for rangequery as others definitions requires more args:

```
root@b8ff149eb94a:~/cse511# spark-submit ./target/scala-2.11/CSE511-assembly-0.1.0.jar result/output rangequery /root/cse511-data/taxi_dropoff_points_clean_fixed.csv -74.25,40.50,-73.70,40.90
2025-03-13 08:01:24 WARN  NativeCodeLoader:62 - Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
13834832 0 0 0
```