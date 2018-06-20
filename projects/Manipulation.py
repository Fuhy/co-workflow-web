import pymysql
from .HashMaker import *
from .DAG import DAG
from .User import UserInfo
from .NodeInfo import NodeInfo
from .Client import *



def fetch_uid(account):
    predicate = "`user_name` = '{}' ".format(account)
    result = select('user_id', 'User', predicate)[0]
    return result[0]


def fetch_nid(node_name):
    predicate = "`task_name` = '{}' ".format(node_name)
    result = select('task_id', 'Node', predicate)[0]
    return result[0]


def new_project(account, graph_name="New Project"):
    #create a new project
    g_id = HashMaker().hash_graph()
    u_id = account
    # u_id = fetch_uid(account)
    task = DAG(g_id, u_id, graph_name)
    #create the new DAG

    task.rename_graph(graph_name)
    #rename the DAG

    values = "({},{})".format(g_id, u_id)
    insert('DAG_Group', values)
    #insert to DAG_Group

    return task


def new_task(account, graph_id, task_name="New Task"):
    #create a new task
    # u_id = fetch_uid(account)
    u_id = account

    task = DAG(graph_id, u_id)
    n_id = HashMaker().hash_task()

    #insert to DAG_Node

    task.add_node(n_id)
    node_info = NodeInfo(n_id, u_id, task_name)

    #add the first node
    values = "({},{})".format(n_id, u_id)
    insert('Node_Group', values)
    #insert to NodeGroup

    node_info.rename_task(task_name)
    node_info.save_state()

    return node_info



def describe_task(task_ID,abstract,new_title="",due_date=""):
    task = NodeInfo(task_ID)
    return task.describe_task(abstract,new_title,due_date)



    


