package cse511

import org.apache.log4j.{Level, Logger}
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions.udf
import org.apache.spark.sql.functions._

object HotcellAnalysis {
  Logger.getLogger("org.spark_project").setLevel(Level.WARN)
  Logger.getLogger("org.apache").setLevel(Level.WARN)
  Logger.getLogger("akka").setLevel(Level.WARN)
  Logger.getLogger("com").setLevel(Level.WARN)

    def runHotcellAnalysis(spark: SparkSession, pointPath: String): DataFrame =
    {
    // Load the original data from a data source
    var pickupInfo = spark.read.format("com.databricks.spark.csv").option("delimiter",";").option("header","false").load(pointPath);
    pickupInfo.createOrReplaceTempView("nyctaxitrips")
    pickupInfo.show()

    // Assign cell coordinates based on pickup points
    spark.udf.register("CalculateX",(pickupPoint: String)=>((
      HotcellUtils.CalculateCoordinate(pickupPoint, 0)
      )))
    spark.udf.register("CalculateY",(pickupPoint: String)=>((
      HotcellUtils.CalculateCoordinate(pickupPoint, 1)
      )))
    spark.udf.register("CalculateZ",(pickupTime: String)=>((
      HotcellUtils.CalculateCoordinate(pickupTime, 2)
      )))
    pickupInfo = spark.sql("select CalculateX(nyctaxitrips._c5),CalculateY(nyctaxitrips._c5), CalculateZ(nyctaxitrips._c1) from nyctaxitrips")
    var newCoordinateName = Seq("x", "y", "z")
    pickupInfo = pickupInfo.toDF(newCoordinateName:_*)
    pickupInfo.show()

    // Define the min and max of x, y, z
    val minX = -74.50/HotcellUtils.coordinateStep
    val maxX = -73.70/HotcellUtils.coordinateStep
    val minY = 40.50/HotcellUtils.coordinateStep
    val maxY = 40.90/HotcellUtils.coordinateStep
    val minZ = 1
    val maxZ = 31
    val numCells = (maxX - minX + 1)*(maxY - minY + 1)*(maxZ - minZ + 1)

    // YOU NEED TO CHANGE THIS PART
    pickupInfo.createOrReplaceTempView("cells")
    val cellCounts = spark.sql(s"""
      SELECT x, y, z, COUNT(*) as count
      FROM cells
      WHERE x >= $minX AND x <= $maxX AND
            y >= $minY AND y <= $maxY AND
            z >= $minZ AND z <= $maxZ
      GROUP BY x, y, z
    """)
    cellCounts.createOrReplaceTempView("cell_counts")

    val stats = spark.sql("SELECT AVG(count) as mean, STDDEV(count) as stddev FROM cell_counts").first()
    val mean = stats.getDouble(0)
    val stddev = stats.getDouble(1)

    // Register UDF for G-score
    spark.udf.register("calculateGScore", 
      (sum: Double, weight: Int) => 
        HotcellUtils.calculateGScore(sum, weight, mean, stddev, numCells)
    )

    val neighbors = spark.sql(s"""
      SELECT a.x, a.y, a.z,
             SUM(b.count) as neighbor_sum,
             COUNT(b.count) as neighbor_count
      FROM cell_counts a, cell_counts b
      WHERE ABS(a.x - b.x) <= 1 AND
            ABS(a.y - b.y) <= 1 AND
            ABS(a.z - b.z) <= 1
      GROUP BY a.x, a.y, a.z
    """)

    val result = neighbors.withColumn("g_score",
      expr("calculateGScore(neighbor_sum, neighbor_count)")
    )

    val sortedResult = result
      .orderBy(desc("g_score"))
      .select("x", "y", "z")

    return sortedResult

    }
}
