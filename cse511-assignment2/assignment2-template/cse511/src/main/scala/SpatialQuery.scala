package cse511

import org.apache.spark.sql.SparkSession

object SpatialQuery extends App{
	
  def runRangeQuery(spark: SparkSession, arg1: String, arg2: String): Long = {

	val pointDf = spark.read.format("com.databricks.spark.csv").option("delimiter","\t").option("header","false").load(arg1);
	pointDf.createOrReplaceTempView("point")

	// YOU NEED TO FILL IN THIS USER DEFINED FUNCTION
	spark.udf.register("ST_Contains", (queryRectangle: String, pointString: String) => {
		val rect = queryRectangle.split(",").map(_.trim.toDouble)
		val point = pointString.split(",").map(_.trim.toDouble)

		val x1 = Math.min(rect(0), rect(2))
		val y1 = Math.min(rect(1), rect(3))
		val x2 = Math.max(rect(0), rect(2))
		val y2 = Math.max(rect(1), rect(3))

		val x = point(0)
		val y = point(1)

		(x >= x1 && x <= x2 && y >= y1 && y <= y2)
	})

	val resultDf = spark.sql("select * from point where ST_Contains('"+arg2+"',point._c0)")
	// resultDf.show()

	return resultDf.count()
  }

  def runRangeJoinQuery(spark: SparkSession, arg1: String, arg2: String): Long = {

	val pointDf = spark.read.format("com.databricks.spark.csv").option("delimiter","\t").option("header","false").load(arg1);
	pointDf.createOrReplaceTempView("point")

	val rectangleDf = spark.read.format("com.databricks.spark.csv").option("delimiter","\t").option("header","false").load(arg2);
	rectangleDf.createOrReplaceTempView("rectangle")

	// YOU NEED TO FILL IN THIS USER DEFINED FUNCTION
	spark.udf.register("ST_Contains", (queryRectangle: String, pointString: String) => {
		val rect = queryRectangle.split(",").map(_.trim.toDouble)
		val point = pointString.split(",").map(_.trim.toDouble)

		val x1 = Math.min(rect(0), rect(2))
		val y1 = Math.min(rect(1), rect(3))
		val x2 = Math.max(rect(0), rect(2))
		val y2 = Math.max(rect(1), rect(3))

		val x = point(0)
		val y = point(1)

		(x >= x1 && x <= x2 && y >= y1 && y <= y2)
	})

	val resultDf = spark.sql("select * from rectangle,point where ST_Contains(rectangle._c0,point._c0)")
	// resultDf.show()

	return resultDf.count()
  }

  def runDistanceQuery(spark: SparkSession, arg1: String, arg2: String, arg3: String): Long = {

	val pointDf = spark.read.format("com.databricks.spark.csv").option("delimiter","\t").option("header","false").load(arg1);
	pointDf.createOrReplaceTempView("point")

	// YOU NEED TO FILL IN THIS USER DEFINED FUNCTION
	spark.udf.register("ST_Within", (pointString1: String, pointString2: String, distance: Double) => {
		val p1 = pointString1.split(",").map(_.trim.toDouble)
		val p2 = pointString2.split(",").map(_.trim.toDouble)

		val dist = Math.sqrt(Math.pow(p1(0) - p2(0), 2) + Math.pow(p1(1) - p2(1), 2))

		dist <= distance
	})

	val resultDf = spark.sql("select * from point where ST_Within(point._c0,'"+arg2+"',"+arg3+")")
	// resultDf.show()

	return resultDf.count()
  }

  def runDistanceJoinQuery(spark: SparkSession, arg1: String, arg2: String, arg3: String): Long = {

	val pointDf = spark.read.format("com.databricks.spark.csv").option("delimiter","\t").option("header","false").load(arg1);
	pointDf.createOrReplaceTempView("point1")

	val pointDf2 = spark.read.format("com.databricks.spark.csv").option("delimiter","\t").option("header","false").load(arg2);
	pointDf2.createOrReplaceTempView("point2")

	// YOU NEED TO FILL IN THIS USER DEFINED FUNCTION
	spark.udf.register("ST_Within", (pointString1: String, pointString2: String, distance: Double) => {
		val p1 = pointString1.split(",").map(_.trim.toDouble)
		val p2 = pointString2.split(",").map(_.trim.toDouble)

		val dist = Math.sqrt(Math.pow(p1(0) - p2(0), 2) + Math.pow(p1(1) - p2(1), 2))

		dist <= distance
	})

	val resultDf = spark.sql("select * from point1 p1, point2 p2 where ST_Within(p1._c0, p2._c0, "+arg3+")")
	// resultDf.show()

	return resultDf.count()
  }
}
