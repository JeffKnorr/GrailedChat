# Basic RESTful Chat server
# Jeffrey Knorr - 1/30/2018

from http.server import HTTPServer, BaseHTTPRequestHandler
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json, re
import urllib.parse
import argparse

# Setup the Datastore
# Create the message table to store all user messages.
Base = declarative_base()
class message(Base):
    __tablename__ = "message"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    timestamp = Column('timestamp', DateTime, default=datetime.utcnow)
    fromUser = Column('fromUser', String)
    toUser = Column('toUser', String)
    messageBody = Column('messageBody', String)

# SQLAlchemy code to store our data inside a SQLite database
# Leveraging a DB Abstraction layer so that this can be easily swapped out.
engine = create_engine('sqlite:///chat.db', echo=False)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()
    
# Helper function to convert our message object into JSON.  
# Future Enhancement opportunity to leverage a Serializer for this task.
def msgs_to_json(msgs):
    listOfDicts = []
    for msg in msgs:
        json = { 'id': msg.id,
                 'timestamp': str(msg.timestamp),
                 'fromUser': msg.fromUser,
                 'toUser': msg.toUser,
                 'messageBody': msg.messageBody
                }
        listOfDicts.append(json)
    return listOfDicts

# Returns JSON representation of a user's inbox
def get_messages(handler):
    path = urllib.parse.unquote(handler.path)
    path = path.split('/')
    inbox = str(path[4])
    msgs = session.query(message).filter((message.toUser==inbox) | (message.fromUser==inbox)).order_by(message.timestamp)
    return msgs_to_json(msgs)

# Adds a new message to the database
def add_message(handler):
    payload = handler.get_payload()
    msg1 = message()
    msg1.fromUser = payload['fromUser']
    msg1.toUser = payload['toUser']
    msg1.messageBody = payload['messageBody']
    session.add(msg1)
    session.commit()
    return "Message Sent Successfully."

# Delete an existing message if it exists
def delete_message(handler):
    global session
    path = urllib.parse.unquote(handler.path)
    path = path.split('/')
    id = str(path[4])
    msg = session.query(message).filter(message.id==id).one()
    session.delete(msg)
    session.commit()
    return True

class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.routes = {
                r'^/chat/v1/inbox/': {'GET': get_messages, 'POST': add_message, 'DELETE': delete_message, 'media_type': 'application/json'}}
        return BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
    
    def get_route(self):
        for path, route in self.routes.items():
            if re.match(path, self.path):
                return route
        return None

    def get_payload(self):
        payload_len = int(self.headers['content-length'],0)
        payload = self.rfile.read(payload_len)
        payload = json.loads(payload)
        return payload

    def do_HEAD(self):
        self.handle_method('HEAD')
    
    def do_GET(self):
        self.handle_method('GET')

    def do_POST(self):
        self.handle_method('POST')

    def do_PUT(self):
        self.handle_method('PUT')

    def do_DELETE(self):
        self.handle_method('DELETE')

    def handle_method(self, method):
        route = self.get_route()
        if route is None:
            self.send_response(404)            
            self.end_headers()
            self.wfile.write('Route not found\n'.encode('utf-8'))
        else:
            if method == 'HEAD':
                self.send_response(200)
                if 'media_type' in route:
                    self.send_header('Content-type', route['media_type'])
                self.end_headers()
            else:
                if method in route:
                    content = route[method](self)
                    if content is not None:
                        self.send_response(200)
                        if 'media_type' in route:
                            self.send_header('Content-type', route['media_type'])
                        self.end_headers()
                        if method != 'DELETE':
                            self.wfile.write(json.dumps(content).encode('utf-8'))
                    else:
                        # Not Found
                        self.send_response(404)
                        self.end_headers()
                        self.wfile.write('Not found\n'.encode('utf-8'))
                else:
                    # Not Supported
                    self.send_response(405)
                    self.end_headers()
                    self.wfile.write((str(method) + ' is not supported\n').encode('utf-8'))

def main():
    # Start the Chat Serer
    port = 8080
    print('Starting Chat Server on localhost port: ' + str(port))
    server = HTTPServer(('', port), RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    print('Stopping Chat Server')

    server.server_close() # Stop the Chat Server
    session.close() # Close the Database Connection

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Creates a RESTful chat server instance.")
    # parser.add_argument('--debug', action='store_true') # Can be leveraged for debugging purposes.
    args = parser.parse_args()
    main()
