from neo4j import GraphDatabase
import logging

# required to set to remove WARNING message appearing for ID depricated in version.
logging.getLogger("neo4j").setLevel(logging.ERROR)

class Interface:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self._driver.verify_connectivity()

    def close(self):
        self._driver.close()

    def bfs(self, start_node, last_node):
        # TODO: Implement this method
        with self._driver.session() as session:
            query = f"""
            MATCH (start:Location {{name: {start_node}}})
            MATCH (end:Location {{name: {last_node}}})
            WITH id(start) AS source, collect(id(end)) AS targets
            CALL gds.bfs.stream('graph', {{
                sourceNode: source,
                targetNodes: targets
            }})
            YIELD path
            RETURN [node IN nodes(path) | {{name: node.name}}] AS path
            """
            result = session.run(query).data()

            # Filter out trivial self-paths or empty paths
            if not result or len(result[0]['path']) <= 1:
                return [{"path": []}]
            return result



    def pagerank(self, max_iterations, weight_property=None):
        # TODO: Implement this method
        with self._driver.session() as session:
            params = f"""
                maxIterations: {max_iterations}
            """
            if weight_property:
                params += f", relationshipWeightProperty: '{weight_property}'"

            query = f"""
            CALL gds.pageRank.stream('graph', {{
                {params}
            }})
            YIELD nodeId, score
            RETURN gds.util.asNode(nodeId).name AS name, score
            ORDER BY score DESC
            """
            records = list(session.run(query))
            return [
                {"name": record["name"], "score": float(round(record["score"], 5))}
                for record in records
            ]


