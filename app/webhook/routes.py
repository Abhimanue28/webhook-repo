from flask import Blueprint, request
from enum import Enum
from app.extensions import mongo
import app.ordinals as ords


webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')
recent_events = []
old_size = 0
final_data = ''
display_limit = 5

class Action(Enum):
    PUSH = 1
    PULL_REQUEST = 2
    MERGE = 3


# Fn to store the corresponding action made in github(#pull,#merge,#push)
# And map it to the url:http://127.0.0.1:5000/receiver
@webhook.route('/receiver', methods=["POST"])
def receiver():
    if request.headers['Content-Type'] == 'application/json':
        response = request.get_json()

        if request.headers['X-GitHub-Event'] == 'push':
            request_id = (response['commits'][0].get("id"))
            author = (response['commits'][0].get("author").get("name"))
            action = Action.PUSH.name
            to_branch = (response['ref'])
            branch = to_branch.split("/")
            timestamp = (response['commits'][0].get("timestamp"))
            dt = ords.ordinal_output(timestamp)
            print(action)
            mongo.db.events.insert_one({'request_id': request_id,
                                        'author': author,
                                        'action': action,
                                        'to_branch': branch[-1],
                                        'timestamp': dt})

        elif request.headers['X-GitHub-Event'] == 'pull_request':

            if response['action'] == 'opened':
                request_id = (response['pull_request'].get('id'))
                author = (response['pull_request'].get('user').get('login'))
                action = Action.PULL_REQUEST.name
                from_branch = (response['pull_request'].get('head').get('ref'))
                to_branch = (response['pull_request'].get('base').get('ref'))
                timestamp = (response['pull_request'].get('created_at'))
                print(timestamp)
                dt = ords.ordinal_output2(timestamp)
                print(action)
                mongo.db.events.insert_one({'request_id': request_id,
                                            'author': author,
                                            'action': action,
                                            'from_branch': from_branch,
                                            'to_branch': to_branch,
                                            'timestamp': dt})

            if response['action'] == 'closed':
                request_id = (response['pull_request'].get('id'))
                author = (response
                          ['pull_request'].get('merged_by').get('login'))
                action = Action.MERGE.name
                from_branch = (response['pull_request'].get('head').get('ref'))
                to_branch = (response['pull_request'].get('base').get('ref'))
                timestamp = (response['pull_request'].get('closed_at'))
                dt = ords.ordinal_output2(timestamp)
                print(action)
                mongo.db.events.insert_one({'request_id': request_id,
                                            'author': author,
                                            'action': action,
                                            'from_branch': from_branch,
                                            'to_branch': to_branch,
                                            'timestamp': dt})
    return {}, 200


# Function to display the documents in receiver()
# With a 15 second dealy on the url:http://127.0.0.1:5000/webhook/info
@webhook.route('/info', methods=["GET"])
def info():
    global old_size
    global final_data
    global display_limit
    global recent_events
    header = '<head><meta http-equiv="refresh" content="15"></head>'
    skip_size = 0

    new_size = mongo.db.events.count()
    size_diff = new_size - old_size
    available_new = new_size > old_size

    # when db is deleted and there is no doc
    if new_size < old_size:
        old_size = 0
        final_data = ''
        del recent_events[0:display_limit]
    
    
    # calucate the no.of documents to skip
    if (size_diff > display_limit):
        skip_size = new_size - display_limit
    else:
        skip_size = old_size
    
    # fetch new data
    if (available_new):
        print(old_size)
        data = mongo.db.events.find().skip(skip_size)
        
        recent_events.reverse()
        # deleting old documents from list
        if (size_diff > display_limit):                                     
            del recent_events[0:display_limit]
        elif(len(recent_events)== display_limit):
            del recent_events[0:(size_diff)]   
        elif(len(recent_events) < display_limit):
            del recent_events[0:(len(recent_events) + size_diff - display_limit)]


        # appending new documents to the list
        for value in data:
            recent_events.append(value) 
        recent_events.reverse()

        # generating HTML elements 
        final_data = ''
        for item in recent_events:
            if item['action'] == "PUSH":
                final_data += ('<h2>' + item['author']
                                    + " pushed to "
                                    + item['to_branch']
                                    + " on "
                                    + item['timestamp']
                                    + '</h2>')
            elif item['action'] == "PULL_REQUEST":
                final_data += ('<h2>' + item['author']
                                    + " submitted a pull request from "
                                    + item['from_branch']
                                    + " to " + item['to_branch']
                                    + " on " + item['timestamp']
                                    + '</h2>')
            elif item['action'] == "MERGE":
                final_data += ('<h2>' + item['author']
                                    + " merged branch "
                                    + item['from_branch']
                                    + " to "
                                    + item['to_branch']
                                    + " on "
                                    + item['timestamp'] + '</h2>')

        # updating locally stored document count
        old_size = new_size
        
    return header + final_data