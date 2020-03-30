import sys
import csv
from collections import defaultdict

import exceptions as exp

INPUT_FILE = "request.csv"
GRAY = "GRAY"
WHITE = "WHITE"
BLACK = "BLACK"
INPUT_HEADERS = ["EmployeeID", "buildingFrom", "buildingTo"]


class Graph:
    """
    Class to create graph and detect loop to identify the list of employees whose location can be swaped.
    """
    def __init__(self, vertices):
        """
        constructor for graph class
        :param vertices: list of nodes in the graph
        """
        self.vertices = vertices
        self.graph = defaultdict(list)
        self.parent = [{}]
        self.cycle = 0
        self.edge_to_emp_map = {}
        self.emp_swap_list = []
        self.cycle_vertices = []

    def add_edge(self, emp_id, in_id, out_id):
        """
        add edge in directed graph
        :param emp_id: edge label
        :param in_id: edge originating node id
        :param out_id: edge terminating node id
        :return: None
        """
        self.graph[in_id].append(out_id)
        if not self.edge_to_emp_map.get((in_id, out_id),  False):
            self.edge_to_emp_map[(in_id, out_id)] = {"emp": [emp_id]}
        else:
            self.edge_to_emp_map[(in_id, out_id)]["emp"].append(emp_id)
    
    def reset_counters(self):
        """
        reset the counter values
        :return: None
        """
        self.parent = [{}]
        self.cycle = 0
        self.cycle_vertices.clear()
    
    def detect_loop(self, u, color, child):
        """
        Method to detect loop in the graph by performing DFS ans keeping track of all the ancestor.
        The node are colored to keep track of unvisited(WHITE), partially visited(GRAY) and visited(BLACK)
        :param u: node being traversed
        :param color: colour to mark the state of Node
        :param child: list to store the ancestors of the visited node
        :return: True if loop is detected else False
        """
        color[u] = GRAY
        for v in self.graph[u]:
            child.append(v)
            if color[v] == GRAY:
                return True
            if color[v] == WHITE and self.detect_loop(v, color, child):
                return True
            
        color[u] = BLACK
        return False
    
    def is_cyclic(self):
        """
        High level method called to detect loop.
        This function initialises parameters before calling the detect_loop method
        :return: True if loop is detected else False
        """
        color = {}
        for elem in self.vertices:
            color[elem] = WHITE
        
        for elem in self.vertices:
            if color[elem] == WHITE:
                self.parent[self.cycle].clear()
                self.parent[self.cycle].update({elem: []})
                if self.detect_loop(elem, color, self.parent[self.cycle][elem]):
                    self.cycle += 1
                    break
        self.store_cycle()
        return True if self.cycle > 0 else False
    
    def remove_cyclic_edges(self):
        """
        Prune graph by removing cyclic edges.
        Once done we trigger the detect_loop method to find if more cycles are present
        :return: None
        """
        for x, y in zip(self.cycle_vertices[::1], self.cycle_vertices[1::1]):
            self.graph[x].remove(y)
            self.edge_to_emp_map[(x, y)]["emp"].pop(0)
            if not self.edge_to_emp_map[(x, y)]["emp"]:
                self.edge_to_emp_map.pop((x, y))
        self.reset_counters()

    def get_emp_swap_list(self, cycle):
        """
        Fetch label name from the list of cyclic nodes.
        :param cycle: list of nodes involved in cycle
        :return: employed label list
        """
        def get_cyclic_vertices(cyclic_vertices):
            """
            return actual cyclic vertices from all ancestors vertices traversed while detecting loop
            :param cyclic_vertices: dictionary containing the all ancestor traversed during loop detection
                                    Key is the the start vertex(parent)
            :return: list of cyclic vertices
            """
            temp_list = list(cyclic_vertices.keys())
            temp_list.extend(list(cyclic_vertices.values())[0])
            end_pos = len(temp_list)
            for index in range(len(temp_list)):
                if temp_list[index] == temp_list[end_pos - 1]:
                    return temp_list[index::]
        start_pos = len(self.cycle_vertices)
        self.cycle_vertices.extend(get_cyclic_vertices(cycle))
        swap_list = []
        for i in range(start_pos, len(self.cycle_vertices) - 1):
            swap_list.append(self.edge_to_emp_map[(self.cycle_vertices[i], self.cycle_vertices[i+1])]["emp"][0])
        return swap_list

    def store_cycle(self):
        """
        Method to fetch the label form all the cyclic edges identified.
        :return: None
        """
        tmp_swap_list = [[] for _ in range(self.cycle)]
        for cycle in range(self.cycle):
            # print(self.parent[cycle])
            tmp_swap_list[cycle].extend(self.get_emp_swap_list(self.parent[cycle]))
            # print(tmp_swap_list[cycle])
            # print("==========================")
        self.emp_swap_list.extend(tmp_swap_list)
    
    def print_swap_list(self):
        """
        Print the list of employees who can swap their locations.
        :return: None
        """
        print(self.emp_swap_list)


def validate_input(emp, from_building, to_building):
    """
    validate input
    :param emp: list of employee ID's
    :param from_building: list of source building ID's
    :param to_building: list of destination building ID's
    :return: None
    """
    # 1. Employee ID should not be duplicate
    unique_emp_list = list(set(emp))
    if len(emp) != len(unique_emp_list):
        duplicate_emp_id = []
        for elem in unique_emp_list:
            if emp.count(elem) > 1:
                duplicate_emp_id.append(elem)
        raise exp.InitializationError(exp.DUPLICATE_EMPLOYEE_ID, duplicate_emp_id)

    # 2. check if length of all list is same
    if not len(emp) == len(from_building) == len(to_building):
        raise exp.InitializationError(exp.MISSING_ENTRY)


def read_input_file(file_name):
    """
    read the input form given csv file
    :param file_name: file name to read input from
    :return: list of employee ID, source building ID's, destination building ID's
    """
    emp_id = []
    building_from = []
    building_to = []

    try:
        with open(file_name, "r") as fle:
            csv_reader = csv.DictReader(fle)
            if not csv_reader.fieldnames == INPUT_HEADERS:
                raise exp.InitializationError(exp.PARAM_MISSING, csv_reader.fieldnames, INPUT_HEADERS)

            for row in csv_reader:
                if not row["EmployeeID"] or not row["buildingFrom"] or not row['buildingTo']:
                    raise exp.InitializationError(exp.VALUE_MISSING, row["EmployeeID"], row["buildingFrom"],
                                                  row["buildingTo"])
                emp_id.append(row["EmployeeID"])
                source = int(row["buildingFrom"])
                destination = int(row["buildingTo"])
                if source == destination:
                    raise exp.InitializationError(exp.SOURCE_AND_DESTINATION_MATCHING, row["EmployeeID"], source)
                building_from.append(source)
                building_to.append(destination)
    except FileNotFoundError as _err:
        raise exp.InitializationError(exp.MISSING_INPUT_FILE, file_name)
    except ValueError as _err:
        raise exp.InitializationError(exp.INVALID_DATA, row["EmployeeID"])
    except (IOError, OSError) as e:
        print(str(e))
        sys.exit(1)

    return emp_id, building_from, building_to


def find_unique_id(in_list, out_list):
    """
    function to find unique building ID's to identify the graph vertices/nodes.
    :param in_list: source building ID's
    :param out_list: destination building ID's
    :return: list of unique building ID's
    """
    unique_in_list = list(set(in_list))
    unique_out_list = list(set(out_list))
    unique_ids = []
    for build_id in unique_in_list:
        if build_id in unique_out_list:
            unique_out_list.remove(build_id)
        unique_ids.append(build_id)
    unique_ids.extend(unique_out_list)
    return unique_ids


def main():
    """
    main function which triggers the execution.
    :return: None
    """
    emp_ids, building_from, building_to = read_input_file(INPUT_FILE)
    validate_input(emp_ids, building_from, building_to)
    unique_id_list = find_unique_id(building_from[:], building_to[:])
    g = Graph(unique_id_list)
    for emp, in_build_id, out_build_id in zip(emp_ids, building_from, building_to):
        g.add_edge(emp, in_build_id, out_build_id)

    while True:
        if not g.is_cyclic():
            break
        g.remove_cyclic_edges()

    g.print_swap_list()


if __name__ == "__main__":
    try:
        main()
    except exp.InitializationError as err:
        print(str(err))
        sys.exit(1)
    except KeyboardInterrupt:
        print("Stopping due to use interruption.")
        sys.exit(1)
