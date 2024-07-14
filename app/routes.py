import json
from json2html import *
from flask import request, jsonify, make_response, render_template
import random
import array
import requests
from app import app, db, logger, Config
from app.schema import  deployments_schema
from flask import send_from_directory, render_template
from datetime import datetime, timedelta, date
from pymongo import MongoClient
import MySQLdb
import psycopg2
from os import environ
import base64

from requests.exceptions import HTTPError



# JENKINS="https://jenkins-prod.tajawal.io"
# JENKINS_USER="syed.hassan@seera.sa"
# JENKINS_USER_TOKEN="114d0ca7619ee08306db1f3687d4e293c7"
# JOB="devops/job/slack"

JENKINS=environ.get("JENKINS")
JENKINS_USER=environ.get("JENKINS_USER")
JENKINS_USER_TOKEN=environ.get("JENKINS_USER_TOKEN")
JOB=environ.get("JOB")
JENKINS_URL=f"{JENKINS}/job/{JOB}/buildWithParameters?"
AUTH=(JENKINS_USER,JENKINS_USER_TOKEN)
CHANNEL=environ.get("CHANNEL")


mongo_db_names=[]
mysql_db_names=[]
postgress_db_names=[]


def manage_session(f):
    def inner(*args, **kwargs):

        # MANUAL PRE PING
        try:
            db.session.execute("SELECT 1;")
            db.session.commit()
            print ("Try Called")
        except:
            db.session.rollback()
            print("Except Called")
        finally:
            print("Finally Called")
            db.session.close()

        # SESSION COMMIT, ROLLBACK, CLOSE
        try:
            res = f(*args, **kwargs)
            print("Try2 Called")
            db.session.commit()
            return res
        except Exception as e:
            db.session.rollback()
            print("Except2 Called")
            raise e
            # OR return traceback.format_exc()
        finally:
            print("Finally2 Called")
            db.session.close()
    return inner


def future_expiry_time(expiry_map,expiry):
    dt = date.today()
    new_time = timedelta(days=expiry_map[expiry])
    if expiry == "Never":
        future_time = "Never"
    else:
        future_time = dt + new_time
    return future_time



def password_generator():
    maxlen = 14
    upchars = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'M', 'N', 'O', 'p', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    lowchars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',  'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    dig = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    combo =  dig + upchars + lowchars
    randdigs = random.choice(dig)
    randupchars = random.choice(upchars)
    randlowchars = random.choice(lowchars)
    temp = randdigs + randupchars + randlowchars
    for x in range(maxlen - 3):
        temp = temp + random.choice(combo)

        templist = array.array('u', temp)
        random.shuffle(templist)
        pswd = ""
    for x in templist:
        pswd = pswd + x
    return pswd


def jenkins_trigger(hostname,username,tool,db_names,ssh_key,expiry,password,activity,environment,business_justification,requested_by):
        db_names_string = str(db_names)
        print ("String of Database Names",db_names_string)
        replaced_db_names = db_names_string.replace("[","").replace("]","").replace("'","").replace(" ","")
        print ("Replaced Names:", replaced_db_names)
        JENKINS_PARAMS = {
                            'host': hostname,
                            'tool': tool,
                            'username': username,
                            'password': password,
                            'activity': activity,
                            'database_names': replaced_db_names,
                            'ssh_public_key': ssh_key,
                            'expiry': expiry,
                            'environment': environment,
                            'business_justification': business_justification,
                            'requested_by': requested_by

                        }

        print(JENKINS_PARAMS)

        print(JENKINS_URL)
        response = requests.post(
                    JENKINS_URL,auth=AUTH
                    ,params=JENKINS_PARAMS)
        
       
        if str(response.status_code) == "201":
            print ("Jenkins job is triggered")
            message = f"Please wait for approval message on {CHANNEL} channel."
        else:
            print ("Failed to trigger the Jenkins job")
            message = "Something Went Wrong. Please coordinate with devops team."

        return message


@manage_session
def render_function(tool_name, alias):
    db_lists = []
    
    if tool_name == "mongo":
        print ("Inside mongo block")
        ips_query = f"select hostname from `databases_types` where alias='{alias}';"
        ips_query_session = db.session.execute(ips_query)
        array = deployments_schema.dump(ips_query_session)
        print ("Array is:", array)
        ips = array[0].get('hostname')

        replicaset_query = f"select replicaset from `databases_types` where alias='{alias}';"
        replicaset_query_session = db.session.execute(replicaset_query)
        replica_array = deployments_schema.dump(replicaset_query_session)
        replicaset = replica_array[0].get('replicaset')
        user_name_qyery = f"select username from `databases_types` where alias='{alias}';"
        user_name_query_session = db.session.execute(user_name_qyery)
        user_name_array = deployments_schema.dump(user_name_query_session)
        username = user_name_array[0].get('username')

        password_qyery = f"select password from `databases_types` where alias='{alias}';"
        password_query_session = db.session.execute(password_qyery)
        password_array = deployments_schema.dump(password_query_session)
        username = user_name_array[0].get('username')
        password = password_array[0].get('password')
        connection_string=f"mongodb://{username}:{password}@{ips}/?replicaSet={replicaset}"
        print ("Data is:", ips, replicaset, username, password, alias)
        client = MongoClient(f'{connection_string}')
        mongo_db_names.clear()
        for list_db in client.list_databases():
            mongo_db_names.append(list_db['name'])
        db_lists = mongo_db_names
    
    elif tool_name == "mysql":
        print ("Inside mysql block")
        ips_query = f"select hostname from `databases_types` where alias='{alias}';"
        ips_query_session = db.session.execute(ips_query)
        array = deployments_schema.dump(ips_query_session)
        print ("Mysql Array:",array)
        ips = array[0].get('hostname')

        user_name_qyery = f"select username from `databases_types` where alias='{alias}';"
        user_name_query_session = db.session.execute(user_name_qyery)
        user_name_array = deployments_schema.dump(user_name_query_session)
        username = user_name_array[0].get('username')

        password_qyery = f"select password from `databases_types` where alias='{alias}';"
        password_query_session = db.session.execute(password_qyery)
        password_array = deployments_schema.dump(password_query_session)
        username = user_name_array[0].get('username')
        password = password_array[0].get('password')
        print ("Data Is:", username, password, ips)
        serv = MySQLdb.connect(host = ips, user = username, passwd = password)
        c = serv.cursor()
        c.execute("SHOW DATABASES")
        l = c.fetchall()
        mysql_db_names.clear()
        for list_db in l:
            mysql_db_names.extend(list_db)
        db_lists = mysql_db_names
        
    elif tool_name == "postgress":
        print ("Inside postgress block")
        ips_query = f"select hostname from `databases_types` where alias='{alias}';"
        ips_query_session = db.session.execute(ips_query)
        array = deployments_schema.dump(ips_query_session)
        ips = array[0].get('hostname')

        user_name_qyery = f"select username from `databases_types` where alias='{alias}';"
        user_name_query_session = db.session.execute(user_name_qyery)
        user_name_array = deployments_schema.dump(user_name_query_session)
        username = user_name_array[0].get('username')

        password_qyery = f"select password from `databases_types` where alias='{alias}';"
        password_query_session = db.session.execute(password_qyery)
        password_array = deployments_schema.dump(password_query_session)
        username = user_name_array[0].get('username')
        password = password_array[0].get('password')
        print ("Data Is:", username, password, ips) 
        con = psycopg2.connect(
        database="postgres",
        user=username,
        password=password,
        host=ips,
        port= '5432'
        )
        cursor_obj = con.cursor()
        
        cursor_obj.execute("SELECT datname FROM pg_database WHERE datistemplate = false AND datallowconn = true;")
        result = cursor_obj.fetchall()
        print ("Result Is:", result)
        postgress_db_names.clear()
        for list_db in result:
            postgress_db_names.extend(list_db)
        db_lists = postgress_db_names
    else:
        print ("Something Went Wrong")

    if "All" not in db_lists:  
      db_lists.insert(0,"All")
    return db_lists


@manage_session
@app.route("/", methods=['GET', 'POST'])
def main_route():
    #get email from oidc
    email = None
    oidc_data = request.headers.get('X-Amzn-Oidc-Data')
    if oidc_data:
        parts = oidc_data.split('.')
        encoded_payload = parts[1]
        decoded_payload = base64.urlsafe_b64decode(encoded_payload)
        payload = json.loads(decoded_payload)
        email = payload.get('email', 'Email not found')
        print(f"email is {email}")
    #tools
    tool="select DISTINCT tool from databases_types;"
    tool_name = request.args.get('tool', default='mongo') 
    env_name = request.args.get('environment', default='dev') 
    print ("Tool Name is:", tool_name)
    print ("Environment is:", env_name)
    alias = f"select alias from `databases_types` where tool='{tool_name}' AND environment='{env_name}';"
    data_4 = db.session.execute(tool)
    data_5 = db.session.execute(alias)
    
    result_4 = deployments_schema.dump(data_4) 
    result_5 = deployments_schema.dump(data_5) 
    alias = result_5[0].get('alias')
    print ("New Alias:", alias)

    return_result = render_function(tool_name, alias)
    return_result = list(dict.fromkeys(return_result))
    print ("Main function")
    print ("db list in main", return_result)
    environment_query="select DISTINCT environment from databases_types;"
    environment_execute = db.session.execute(environment_query)
    environment_dump = deployments_schema.dump(environment_execute) 
    print ("Enviroments dump is:", environment_dump)
    expiry = ["One Day", "One Week", "One Month", "One Year", "Never"]
    return render_template("index.html", tool=result_4, aliases=result_5, db_names=return_result, expires=expiry, envs=environment_dump, email=email)
  

########## Health Check ################
@app.route("/healthcheck",methods=["POST","GET"])
def healthcheck():

    check = print("Response is 200")
    return jsonify(check)

@app.route("/pickhost",methods=["POST","GET"])
def pickhost():
    if request.method == 'POST':
        category_id = request.form['category_id'] 
        environment = request.form['environment'] 
        print("category id", category_id)
        print("Environment in pickhost", environment)  
        
        result = f"select alias from `databases_types` where tool='{category_id}' AND environment='{environment}';"
        data_5 = db.session.execute(result)
        db_alias =  deployments_schema.dump(data_5)
    return jsonify(db_alias)


@app.route("/pickdbs",methods=["POST","GET"])
def pickdbs():
    db_alias = []
    if request.method == 'POST':

        category_name = request.form['category_name'] 
        category_tool = request.form['category_tool'] 
        print("name category",category_name)  
        print("name category tool",category_tool)
        db_alias.clear()
        if category_name=="Select": 
         pass
        else:
            db_alias = render_function(category_tool, category_name)
            db_alias = list(dict.fromkeys(db_alias))
        print ("In pickdbs dump", db_alias)
    return jsonify(db_alias)





@app.route("/picktools",methods=["POST","GET"])
def picktools():
    if request.method == 'POST':
        environment = request.form['environment'] 
        print("environment id", environment)
        tool_query="select DISTINCT tool from databases_types;"
        tool_execute = db.session.execute(tool_query)
        tool_dump = deployments_schema.dump(tool_execute) 
        tool =  deployments_schema.dump(tool_dump)
    return jsonify(tool)



@app.route("/load" , methods=['GET', 'POST'])
def load():

    hostname = request.form.get('comp')
    tool =  request.form.get('tool')
    db_names = request.form.getlist('release')
    ssh_key = request.form.get('txtsshKey')
    environment = request.form.get('environment')
    business_justification = request.form.get('justification')
    requested_by = request.form.get('requesteremail')
    if ssh_key:
        ssh_key_check = request.form.get('txtsshKey')
        space_key = ' '.join(ssh_key[i:i+80] for i in range(0, len(ssh_key), 80))
    else:
        ssh_key_check= "NotRequired"
        space_key= "NotRequired"
    expiry =  request.form.get('expiry')
    email =  request.form.get('email')
    username = email.split("@")[0]
    password = password_generator()
    activity = "addition"
    expiry_map={"One Day": 1, "One Week": 7, "One Month": 30, "One Year": 365, "Never": 7300}
    future_time = future_expiry_time(expiry_map,expiry)
 
    print ("Environment is:", environment)
    print ("Hostname is:",hostname)
    print ("Username is:",username)
    print ("Tool is:",tool)
    print ("Database Names are:", db_names)
    print ("Text ssh_key_check is:", ssh_key_check)
    print ("Business Justification is:", business_justification)
    print("Requester Email is:", requested_by)
    print ("Expiry:", expiry)
    print ("Password is:", password)
    print ("Activity is:", activity)
    print ("Expiry Future Time is:", future_time)
    jenkins_message=jenkins_trigger(hostname, username, tool, db_names, ssh_key_check, future_time, password, activity, environment, business_justification, requested_by)
    custom_map={
            "Message": f"{jenkins_message}",
            "Environment": f"{environment}",
            "Name":f"{username}",
            "Host": f"{hostname}",
            "Tool": f"{tool}",
            "Database Names": f"{db_names}",
            "SSH Key": f"{space_key}",
            "Expiry": f"{expiry}",
            "Event": f"{activity}",
            "Business Justification": f"{business_justification}",
            "Requester Email": f"{requested_by}"
         
         }
    map_to_json = json.dumps(custom_map)

    table_data = (json2html.convert(json = map_to_json, table_attributes="id=\"info-table\" class=\"table table-bordered table-hover\""))
    
    print ("Table Data Is:", table_data)
    return render_template("table.html", table_data=table_data)



