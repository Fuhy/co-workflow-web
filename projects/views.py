from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import re
from .Client import *
from .DAG import *
from .NodeInfo import *


def projects(request, graph_ID):
    node_details = construct_list(graph_ID)
    group_list = get_group_list(graph_ID)
    context = {}

    # referrer = request.META['HTTP_REFERER']
    # user_page = re.findall('/users/[0-9]+', referrer)[0]

    # user_ID = user_page[7:]
    # context['user'] = get_user_details(user_ID)
    # context['user_page'] = user_page

    context['node_details'] = node_details
    context['group_list'] = group_list

    return render(request, 'projects/MainView.html', context)


###########################  Tools  ##################################
class VeryNode(object):
    def __init__(self, task_ID, task_name="", abstract="", status=""):
        self.task_ID = task_ID
        self.task_name = task_name
        self.abstract = abstract
        self.status = status


def get_user_details(user_ID):
    result = {}
    result['user_ID'] = user_ID
    result['nick_name'], result['about'] = select(
        'nick_name,about', 'User_info', "user_id = {}".format(user_ID))[0]
    result['account'] = select('user_name', 'User',
                               "user_id = {}".format(user_ID))[0][0]
    result['count'] = len(
        select('*', 'DAG_Group', "user_id = {}".format(user_ID)))
    return result


def get_group_list(graph_ID):
    """ return the name of people who join in this project.
    """
    result = []
    for user in [
            i for item in select('user_ID', 'DAG_Group',
                                 "graph_ID = {}".format(graph_ID))
            for i in item
    ]:
        result.append(
            select('nick_name', 'User_Info',
                   "user_ID = {}".format(user))[0][0])
    return result


# def get_join_ones(task_ID):
#     result = []
#     for user in [i for item in select('user_ID','Node_Group',"task_ID = {}".format(task_ID)) for i in item]:
#         temp = {}
#         temp['user_ID'] = user
#         temp['nick_name'] = select('nick_name','User_Info',"user_ID = {}")
#         temp['about'] =


def construct_list(graph_ID):
    graph = DAG(graph_ID)
    order = []
    result = []
    final_result = []
    search = deque()

    # DFS
    for item in graph.ind_nodes():
        search.append(item)
    while search:
        item = search.popleft()
        order.append(item)
        temp = graph.show_downstream(item)
        temp.reverse()
        for i in temp:
            search.appendleft(i)

    # For each layout, marks the end with -1.
    for x, _ in enumerate(order):
        result.append(order[x])
        if x == len(order) - 1:
            continue

        if not graph.show_downstream(order[x]):
            result.append(-1)

        if order[x + 1] in graph.show_downstream(order[x]):
            result.append(-2)

        for node in graph.show_predecessors(order[x]):
            if node in [
                    i for item in [
                        graph.show_downstream(i)
                        for i in graph.show_predecessors(order[x + 1])
                    ] for i in item
            ]:
                result.append(-1)
                result.append(-1)

        # this node
        root = graph.ind_nodes()[0]
        count_this_node = len(graph.show_all_predecessors(order[x]))

        # next node
        root = graph.ind_nodes()[0]
        count_next_node = len(graph.show_all_predecessors(order[x + 1]))

        if count_this_node - count_next_node >= 2:
            times = 2 * (count_this_node - count_next_node)
            while times > 0:
                result.append(-1)
                times -= 1

    # The very end should be marked too.
    result.append(-1)

    for item in result:
        if item == -1 or item == -2:
            final_result.append(VeryNode(item))
        else:
            name = select('task_name', 'Node',
                          "task_ID = {}".format(item))[0][0]
            abstract = select('abstract', 'Node_Details',
                              "task_ID = {}".format(item))[0][0]
            status = select('status', 'Node',
                            "task_ID = {}".format(item))[0][0]
            final_result.append(VeryNode(item, name, abstract, status))

    return final_result
