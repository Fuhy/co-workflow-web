from copy import copy, deepcopy
from collections import OrderedDict, deque
from .HashMaker import *
from .Client import *


class DAG(object):
    """docstring for DAG

    Cautions:
        `owner_ID` must be given when initialize a graph!

    """

    def __init__(self, graph_ID, owner_ID=None, graph_name="New Project"):
        self.graph = OrderedDict()
        self.graph_ID = graph_ID
        self.group = set()
        self.abstract = ""

        if HashMaker().check_graph_exist(graph_ID):
            self.restore_graph(graph_ID)
        else:
            self.init_graph(graph_ID, graph_name, owner_ID)

    def init_graph(self, graph_ID, graph_name, owner_ID):
        self.graph_name = graph_name
        self.owner_ID = owner_ID
        self.save_state()

    def restore_graph(self, graph_ID):
        # Restore Relation
        predicate = "begin_TID = task_ID and graph_ID = '{}' ".format(graph_ID)
        result = select('begin_TID, end_TID', 'DAG_Node, DAG_Edge', predicate)

        all_nodes = set([i for item in result for i in item]) | set([
            i[0] for i in select('task_id', 'DAG_Node', "graph_ID = {}".format(
                graph_ID))
        ])

        for node in all_nodes:
            self.graph[node] = set()
        for item in result:
            self.graph[item[0]].add(item[1])

        # Restore name
        self.graph_name = select('graph_name', 'DAG',
                                 "graph_ID = '{}' ".format(graph_ID))[0][0]
        self.owner_ID = select('owner_ID', 'DAG',
                               "graph_ID = '{}' ".format(graph_ID))[0][0]
        self.group = set([
            i[0] for i in select('user_ID', 'DAG_Group',
                                 'graph_ID = {}'.format(graph_ID))
        ])

        self.abstract = select('abstract', 'DAG',
                               "graph_ID = '{}' ".format(graph_ID))[0][0]

    def save_state(self):
        if HashMaker().check_graph_exist(self.graph_ID):
            # DAG
            attributes = "'graph_name','owner_ID','abstract'"
            values = "'{}','{}','{}".format(self.graph_name, self.owner_ID,self.abstract)
            update('DAG', attributes, values, " graph_id = '{}' ".format(
                self.graph_ID))
        else:
            values = "({},'{}',{},'{}')".format(self.graph_ID, self.graph_name,
                                                self.owner_ID, self.abstract)
            insert('DAG', values)

    def size(self):
        return len(self.graph)

    def ind_nodes(self, graph=None):
        """ Returns a list of all nodes in the graph with no dependencies. """
        if graph is None:
            graph = self.graph

        dependent_nodes = set(
            node for dependents in graph.values() for node in dependents)
        return [node for node in graph.keys() if node not in dependent_nodes]

    def validate(self, graph=None):
        """ Returns (Boolean, message) of whether DAG is valid. """
        graph = graph if graph is not None else self.graph
        if len(self.ind_nodes(graph)) == 0:
            return (False, 'no independent nodes detected')
        try:
            self.topological_sort(graph)
        except ValueError:
            return (False, 'failed topological sort')
        return (True, 'valid')

    def topological_sort(self, graph=None):
        """ Returns a topological ordering of the DAG.
        Raises an error if this is not possible (graph is not valid).
        """
        if graph is None:
            graph = self.graph

        in_degree = {}
        for u in graph:
            in_degree[u] = 0

        for u in graph:
            for v in graph[u]:
                in_degree[v] += 1

        queue = deque()
        for u in in_degree:
            if in_degree[u] == 0:
                queue.appendleft(u)

        l = []
        while queue:
            u = queue.pop()
            l.append(u)
            for v in graph[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.appendleft(v)

        if len(l) == len(graph):
            return l
        else:
            raise ValueError('graph is not acyclic')

    def rename_graph(self, new_graph_name):
        self.graph_name = new_graph_name

    def add_node(self, taskID, graph=None):
        if not graph:
            graph = self.graph
        if insert('DAG_Node', "({},{})".format(taskID, self.graph_ID)):
            graph[taskID] = set()

    def delete_node(self, taskID, graph=None):
        if not graph:
            graph = self.graph

        graph.pop(taskID)

        for node, edges in graph.items():
            if taskID in edges:
                edges.remove(taskID)

        # DATABASE
        delete('DAG_Node', " graph_ID = {} and task_ID = {} ".format(
            self.graph_ID, taskID))
        delete('DAG_Edge', " end_TID = {} ".format(taskID))

    def add_edge(self, ind_node, dep_node, graph=None):
        if not graph:
            graph = self.graph
        if ind_node not in graph or dep_node not in graph:
            raise KeyError('one or more nodes do not exist in graph')
        test_graph = deepcopy(graph)
        test_graph[ind_node].add(dep_node)
        is_valid, message = self.validate(test_graph)
        if is_valid:
            insert('DAG_Edge', "({},{})".format(ind_node, dep_node))
            graph[ind_node].add(dep_node)
        else:
            raise DAGValidationError()

    def delete_edge(self, ind_node, dep_node, graph=None):
        if not graph:
            graph = self.graph
        if dep_node not in graph.get(ind_node, []):
            raise KeyError('this edge does not exist in graph')
        delete('DAG_Edge', "begin_TID = {} and end_TID = {} ".format(
            ind_node, dep_node))
        graph[ind_node].remove(dep_node)

    def show_predecessors(self, node, graph=None):
        if graph is None:
            graph = self.graph

        return [key for key in graph if node in graph[key]]

    def show_all_predecessors(self, node, graph=None):
        if graph is None:
            graph = self.graph
        nodes = [node]
        nodes_seen = set()
        i = 0
        while i < len(nodes):
            predecessors = list(self.show_predecessors(nodes[i], graph))
            for preNode in predecessors:
                if preNode not in nodes_seen:
                    nodes_seen.add(preNode)
                    nodes.append(preNode)
            i += 1
        return list(
            filter(
                lambda node: node in nodes_seen,
                self.topological_sort(graph=graph)))

    def show_downstream(self, node, graph=None):
        """ Returns a list of all nodes this node has edges towards. """
        if graph is None:
            graph = self.graph
        if node not in graph:
            raise KeyError('node %s is not in graph' % node)
        return list(graph[node])

    def show_all_downstream(self, node, graph=None):
        if graph is None:
            graph = self.graph
        nodes = [node]
        nodes_seen = set()
        i = 0
        while i < len(nodes):
            downstreams = self.show_downstream(nodes[i], graph)
            for downstream_node in downstreams:
                if downstream_node not in nodes_seen:
                    nodes_seen.add(downstream_node)
                    nodes.append(downstream_node)
            i += 1
        return list(
            filter(
                lambda node: node in nodes_seen,
                self.topological_sort(graph=graph)))

    def add_group_member(self, member_list):
        for member in member_list:
            if insert('DAG_Group', "({},'{}')".format(self.graph_ID, member)):
                self.group.add(member)

    def delete_group_member(self, member_list):
        for member in member_list:
            if delete('DAG_Group', " graph_id = {} and user_id = {} ".format(
                    self.graph_ID, member)):
                self.group.remove(member)
