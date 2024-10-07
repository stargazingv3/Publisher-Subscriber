import socket
import threading
import json
from dataclasses import dataclass, field
from typing import List, Dict

#creates variables for user
@dataclass
class User:
    username: str
    tcp_ip: str
    udp_port: int
    subscribed_topics: List[str] = field(default_factory=list)

#creates variables for topics
@dataclass
class Topic:
    name: str
    subscribers: List[str] = field(default_factory=list)

#creates class Publisher for handeling logic for users and messages
class Publisher:
    #creates 2 dictionaries one for users one for topics
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.topics: Dict[str, Topic] = {}

    #handles incoming connections from clients, listens for commands sent by client 
    def handle_client(self, conn: socket.socket, addr: tuple):
        print(f"Connection from {addr}")
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                
                #decodes data and gets the command to assign to variable to call which funtion to perform
                message = json.loads(data.decode())
                command = message.get("command")

                #calls a funtion based on the command
                if command == "register":
                    self.register_user(message, conn)
                elif command == "create_topic":
                    self.create_topic(message)
                elif command == "subscribe":
                    self.subscribe_topic(message)
                elif command == "publish_message":
                    self.publish_message(message)
                elif command == "get_topics":
                    self.send_topics(conn)
                elif command == "get_users_by_topic":
                    self.send_users_by_topic(message, conn)
                elif command == "get_users":
                    self.send_all_users(conn)
                elif command == "get_tcp_ip":
                    self.send_tcp_ip(message, conn)
                elif command == "get_udp_port":
                    self.send_udp_port(message, conn)

        print(f"Connection closed for {addr}")

    #registers a new user by extracting username IP and Port num storing ingo in users dictonary
    def register_user(self, message: Dict, conn: socket.socket):
        username = message["username"]
        tcp_ip = conn.getsockname()[0]
        udp_port = message["udp_port"]

        user = User(username=username, tcp_ip=tcp_ip, udp_port=udp_port)
        self.users[username] = user
        print(f"Registered user: {user}")

    #creates a new topic if it doenst already exist and adds it to the topics dictionary 
    def create_topic(self, message: Dict):
        topic_name = message["topic"]
        if topic_name not in self.topics:
            self.topics[topic_name] = Topic(name=topic_name)
            print(f"Created topic: {topic_name}")

    #subscribes to a topic chosen by the user, updates both topisc sub list and users subed topics
    def subscribe_topic(self, message: Dict):
        username = message["username"]
        topic_name = message["topic"]
        if topic_name in self.topics:
            self.topics[topic_name].subscribers.append(username)
            self.users[username].subscribed_topics.append(topic_name)
            print(f"{username} subscribed to {topic_name}")
        else:
            print(f"invalid topic not in list")
        
    #brodcasts a mssg from a user to all other subs of a specified topic
    def publish_message(self, message: Dict):
        username = message["username"]
        topic_name = message["topic"]
        msg_content = message["content"]

        #excludes the user who sent it
        if topic_name in self.topics:
            print(f"Broadcasting message from {username} to topic {topic_name}: {msg_content}")
            subscribers = self.topics[topic_name].subscribers
            for subcriber in subscribers:
                if subcriber != username:
                    self.send_message_to_user(subcriber, msg_content, topic_name)

    #sends a mssg to a specific user of another users choosing using a new socket connection
    def send_message_to_user(self, username: str, msg_content: str, topic_name: str):
        user = self.users.get(username)
        if user:
            try:
                message = json.dumps({topic_name: "broadcast", "content": msg_content}).encode()
                self.send_udp_message(user.tcp_ip, user.udp_port, message) #calls send_udp_message to send the mssg transfering the data to class
            except Exception as e:
                print(f"Error sending message to {username}: {e}")

    #sends the published mssg to all users useing UDP 
    def send_udp_message(self, ip: str, port: int, message: bytes):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:     #sends as UDP
            s.sendto(message, (ip, port))

    #sends list of abailable topics to the client 
    def send_topics(self, conn: socket.socket):
        topics_list = list(self.topics.keys())
        conn.sendall(json.dumps(topics_list).encode())

    #returns list of users subed to a topic
    def send_users_by_topic(self, message: Dict, conn: socket.socket):
        topic_name = message["topic"]
        if topic_name in self.topics:
            subscribers = self.topics[topic_name].subscribers
            conn.sendall(json.dumps(subscribers).encode())
        else:
            conn.sendall(json.dumps([]).encode())

    #sends list of all registered users to the client 
    def send_all_users(self, conn: socket.socket):
        users_info = [
            {
                'username': user.username,
            }
            for user in self.users.values()
        ]
        conn.sendall(json.dumps(users_info).encode())
    
    #sends the TCP IP address of a specified user
    def send_tcp_ip(self, message: Dict, conn: socket.socket):
        target_username = message["username"]
        user = self.users.get(target_username)
        if user:
            conn.sendall(json.dumps({"tcp_ip": user.tcp_ip}).encode())
        else:
            conn.sendall(json.dumps({"error": "User not found"}).encode())

    #sends UDP port num of a specified user
    def send_udp_port(self, message: Dict, conn: socket.socket):
        target_username = message["username"]
        user = self.users.get(target_username)
        if user:
            conn.sendall(json.dumps({"udp_port": user.udp_port}).encode())
        else:
            conn.sendall(json.dumps({"error": "User not found"}).encode())

    #intitalizes TCP server that listens for incoming conections, new conections = new thread
    def start_server(self, host='127.0.0.1', port=65432):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket: #sock_stream means TCP
            server_socket.bind((host, port))
            server_socket.listen()
            print(f"Publisher listening on {host}:{port}")

            while True:
                conn, addr = server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.start()

#the main that creates instance of Publisher and starts the server
if __name__ == "__main__":
    publisher = Publisher()
    publisher.start_server()
