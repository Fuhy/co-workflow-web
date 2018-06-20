from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .Client import *
from .DAG import *
from .NodeInfo import *



def details(request, user_ID):

    projects = get_projects(user_ID)
    user_info = get_user_info(user_ID)
    context = {}
    context['projects'] = projects
    context['user'] = user_info
    return render(request, 'users/UserView.html', context)




###########################  Tools  ################################## 
def get_projects(user_ID):
    all_graph = []
    result = []
    for graph in [
            i[0] for i in select('graph_id', 'DAG_Group',
                                 "user_id = {}".format(user_ID))
    ]:
        all_graph.append(DAG(graph))
    for graph in all_graph:
        temp = {}
        temp['graph_ID'] = graph.graph_ID
        temp['graph_name'] = graph.graph_name
        temp['abstract'] = graph.abstract
        temp['owner_name'] = select('user_name', 'User', "user_ID = {}".format(
            graph.owner_ID))[0][0]
        result.append(temp)
    return result


def get_user_info(user_ID):
    result = {}
    result['user_ID'] =  user_ID
    result['nick_name'], result['about'] = select(
        'nick_name,about', 'User_info', "user_id = {}".format(user_ID))[0]
    result['account'] = select('user_name', 'User',
                               "user_id = {}".format(user_ID))[0][0]
    result['count'] = len(
        select('*', 'DAG_Group', "user_id = {}".format(user_ID)))
    return result

