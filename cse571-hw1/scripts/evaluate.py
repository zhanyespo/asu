import problem 
from node import Node
from priority_queue import PriorityQueue
import time

class SearchTimeOutError(Exception):
    pass

def compute_g(algorithm, node, goal_state):
    """
        Evaluates the g() value.

        Parameters
        ===========
            algorithm: str
                The algorithm type based on which the g-value will be computed.
            node: Node
                The node whose g-value is to be computed.
            goal_state: State
                The goal state for the problem.

        Returns
        ========
            int
                The g-value for the node.
    """

    if algorithm == "bfs":
       return node.depth

    if algorithm == "astar":

        return node.path_cost

    elif algorithm == "gbfs":

        return 0

    elif algorithm == "ucs":

        return node.path_cost

    elif algorithm == "custom-astar":

        return node.path_cost

    # Should never reach here.
    assert False
    return float("inf")


def compute_h(algorithm, node, goal_state):
    """
        Evaluates the h() value.

        Parameters
        ===========
            algorithm: str
                The algorithm type based on which the h-value will be computed.
            node: Node
                The node whose h-value is to be computed.
            goal_state: State
                The goal state for the problem.

        Returns
        ========
            int
                The h-value for the node.
    """

    if algorithm == "bfs":
        
        return 0

    if algorithm == "astar":

        return get_manhattan_distance(node.state, goal_state)

    elif algorithm == "gbfs":

        return get_manhattan_distance(node.state, goal_state)

    elif algorithm == "ucs":
        
        return 0

    elif algorithm == "custom-astar":

        return get_custom_heuristic(node.state, goal_state)

    # Should never reach here.
    assert False
    return float("inf")


def get_manhattan_distance(from_state, to_state):
    return abs(from_state.x - to_state.x) + abs(from_state.y - to_state.y)


def get_custom_heuristic(from_state, to_state):
    
    dist = get_manhattan_distance(from_state, to_state)
    if from_state.phi != to_state.phi:
        dist += 2
    return dist

def graph_search(algorithm, time_limit):
    """
        Performs a search using the specified algorithm.
        
        Parameters
        ===========
            algorithm: str
                The algorithm to be used for searching.
            time_limit: int
                The time limit in seconds to run this method for.
                
        Returns
        ========
            tuple(list, int)
                A tuple of the action_list and the total number of nodes
                expanded.
    """
    
    # The helper allows us to access the problem functions.
    helper = problem.Helper()
    
    # Get the initial and the goal states.
    init_state = helper.get_initial_state()
    goal_state = helper.get_goal_state()[0]

    #Initialize the init node of the search tree and compute its f_score
    init_node = Node(init_state, None, 0, None, 0)
    f_score = compute_g(algorithm, init_node, goal_state) \
        + compute_h(algorithm, init_node, goal_state)

       
    # Initialize the fringe as a priority queue.
    priority_queue = PriorityQueue()
    priority_queue.push(f_score, init_node)
    

    # action_list should contain the sequence of actions to execute to reach from init_state to goal_state
    action_list = []

    # total_nodes_expanded maintains the total number of nodes expanded during the search
    total_nodes_expanded = 0
    time_limit = time.time() + time_limit
    
    explored = set()

    while not priority_queue.is_empty():
        if time.time() >= time_limit:
            raise SearchTimeOutError("Search timed out")

        f_score, current = priority_queue.pop()

        if current.state == goal_state:
            # reconstruct plan
            action_list = []
            while current.parent is not None:
                action_list.insert(0, current.action)
                current = current.parent
            return action_list, total_nodes_expanded

        if current.state in explored:
            continue
        explored.add(current.state)

        total_nodes_expanded += 1

        for action, succ_state, cost in helper.get_successors(current.state):
            child = Node(succ_state, current, current.path_cost + cost, action, current.depth + 1)
            g = compute_g(algorithm, child, goal_state)
            h = compute_h(algorithm, child, goal_state)
            f = g + h
            priority_queue.push(f, child)

    if time.time() >= time_limit:
    
        raise SearchTimeOutError("Search timed out after %u secs." % (time_limit))

    return action_list, total_nodes_expanded