package cse511

object HotzoneUtils {

  def ST_Contains(queryRectangle: String, pointString: String ): Boolean = {

    val rect = queryRectangle.split(",").map(_.toDouble)
    val point = pointString.split(",").map(_.replace("(", "").replace(")", "").toDouble)

    val x1 = math.min(rect(0), rect(2))
    val x2 = math.max(rect(0), rect(2))
    val y1 = math.min(rect(1), rect(3))
    val y2 = math.max(rect(1), rect(3))

    val x = point(0)
    val y = point(1)

    x >= x1 && x <= x2 && y >= y1 && y <= y2
  }
}
