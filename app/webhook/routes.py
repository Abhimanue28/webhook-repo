from flask import Blueprint, json, request
from enum import Enum
from app.extensions import mongo

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

class Action(Enum):
    PUSH = 1
    PULL_REQUEST = 2
    MERGE = 3

@webhook.route('/receiver', methods=["POST"])
def receiver():
    if request.headers['Content-Type'] =='application/json':
        response = request.get_json()   
        
        if request.headers['X-GitHub-Event'] == 'push':
            request_id = (response['commits'][0].get("id")) 
            author = (response['commits'][0].get("author").get("name"))
            action = Action.PUSH.name
            to_branch = (response['ref'])
            timestamp = (response['commits'][0].get("timestamp"))
            print(action)
            mongo.db.events.insert_one({'request_id':request_id, 'author':author, 'action':action, 'to_branch':to_branch,'timestamp':timestamp})
            
        elif request.headers['X-GitHub-Event'] == 'pull_request':
            
            if response['action'] == 'opened':                                      
                request_id = (response['pull_request'].get('id'))
                author = (response['pull_request'].get('user').get('login'))
                action = Action.PULL_REQUEST.name
                from_branch = (response['pull_request'].get('head').get('ref'))
                to_branch = (response['pull_request'].get('base').get('ref'))
                timestamp = (response['pull_request'].get('created_at'))
                print(action)
                mongo.db.events.insert_one({'request_id':request_id, 'author':author, 'action':action,'from_branch':from_branch,
                 'to_branch':to_branch,'timestamp':timestamp})
            
            if response['action'] == 'closed':
                request_id = (response['pull_request'].get('id'))
                author = (response['pull_request'].get('merged_by').get('login'))
                action = Action.MERGE.name
                from_branch = (response['pull_request'].get('head').get('ref'))
                to_branch = (response['pull_request'].get('base').get('ref'))
                timestamp = (response['pull_request'].get('closed_at'))
                print(action)
                mongo.db.events.insert_one({'request_id':request_id, 'author':author, 'action':action,'from_branch':from_branch,
                 'to_branch':to_branch,'timestamp':timestamp})
                 
    return {}, 200


@webhook.route('/info', methods=["GET"])
def info():
    header = '<head><meta http-equiv="refresh" content="15"></head>'
    data = mongo.db.events.find().sort([('_id', -1)]).limit(1).next()
    if data['action'] == "PUSH":
        return (header + '<h2>' + data['author'] + " pushed to " + data['to_branch'] + " on " + data['timestamp'] + '</h2>')  
    elif data['action'] == "PULL_REQUEST":
        return (header + '<h2>' + data['author'] + " submitted a pull request from " + data['from_branch'] + " to " +data['to_branch'] + " on " + data['timestamp']+'</h2>')  
    elif data['action'] == "MERGE":
        return (header + '<h2>' + data['author'] + " merged branch " + data['from_branch'] + " to " +data['to_branch'] + " on " + data['timestamp'] + '</h2>')   

        