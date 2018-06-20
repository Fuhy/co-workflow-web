from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import redirect
import re

from .Manipulation import *
from .Client import *
from .DAG import *
from .NodeInfo import *
from .HashMaker import *

# Create your views here.


def edit_task_details(request, task_ID):
    referrer = request.META['HTTP_REFERER']
    task_name = request.GET.get('task_name', "")
    abstract = request.GET.get('abstract', "")
    status = True if request.GET.get('status', "") == '1' else False
    if abstract:
        update('Node_Details', "'abstract'", "'{}'".format(abstract),
               "task_ID = {}".format(task_ID))
    if task_name:
        update('Node', "'task_name'", "'{}'".format(task_name),
               "task_ID = {}".format(task_ID))
    if status:
        update('Node', "'status'", "'{}'".format(status),
               "task_ID = {}".format(task_ID))

    group_list = request.GET.getlist('group_list', [])
    for user in group_list:
        user_ID = select('user_ID', 'User_Info',
                         "nick_name = '{}'".format(user))[0][0]
        insert('node_group', "({},{})".format(task_ID, user_ID))


    return redirect(referrer)


def create_project(request):
    referrer = request.META['HTTP_REFERER']
    user_ID = re.findall('/users/[0-9]+', referrer)[0][7:]
    graph_name = request.GET.get('graph_name', "")
    abstract = request.GET.get('abstract', "")
    graph = new_project(user_ID)
    new_task(user_ID, graph.graph_ID)
    graph.abstract = abstract
    graph.graph_name = graph_name
    graph.save_state()
    return redirect(referrer)


def edit_project(request, graph_ID):
    referrer = request.META['HTTP_REFERER']
    user_ID = re.findall('/users/[0-9]+', referrer)[0][7:]
    graph_name = request.GET.get('graph_name', "")
    abstract = request.GET.get('abstract', "")
    workmate = request.GET.get('workmate', "")
    graph = DAG(graph_ID)
    if abstract:
        graph.abstract = abstract
    if graph_name:
        graph.graph_name = graph_name
    if HashMaker().check_user_name_exist(workmate):
        graph.add_group_member(select('user_ID','User',"user_name = '{}'".format(workmate))[0])
    graph.save_state()
    return redirect(referrer)


def edit_task_group(request, task_ID):
    referrer = request.META['HTTP_REFERER']
    graph = DAG(re.findall('/projects/[0-9]+', referrer)[0][10:])
    task_name = request.GET.get('task_name', "")
    abstract = request.GET.get('abstract', "")
    workmate = []
    temp = request.GET.getlist('user', [])
    if temp:
        users = temp[0].split(',')
    for i in users:
        temp = select('user_ID', 'User_Info', "nick_name='{}'".format(i))
        if temp is not None:
            workmate.append(temp[0][0])

    temp = new_task(111, graph.graph_ID)
    temp.describe_task(abstract, task_name)
    temp.add_group_member(workmate)

    graph.restore_graph(graph.graph_ID)
    graph.add_edge(task_ID, temp.task_ID)
    return redirect(referrer)

def remove_project(request,graph_ID):
    referrer = request.META['HTTP_REFERER']
    graph = DAG(graph_ID)
    for i in graph.topological_sort():
        graph.delete_node(i)
    delete('DAG_Group',"graph_ID = {}".format(graph_ID))
    delete('DAG',"graph_ID = {}".format(graph_ID))
    return redirect(referrer)


def remove_task(request, task_ID):
    referrer = request.META['HTTP_REFERER']
    graph = DAG(re.findall('/projects/[0-9]+', referrer)[0][10:])
    for node in graph.show_all_downstream(task_ID):
        graph.delete_node(node)
    graph.delete_node(task_ID)
    return redirect(referrer)
