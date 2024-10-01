import socket
import threading
import json
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class User:
    username: str
    tcp_ip: str
    udp_port: int
    subscribed_topics: List[str] = field(default_factory=list)

@dataclass
class Topic:
    name: str
    subscribers: List[str] = field(default_factory=list)

class Publisher:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.topics: Dict[str, Topic] = {}

    def handle_client(self, conn: socket.socket, addr: tuple):
        print(f"Connection from {addr}")
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                
                message = json.loads(data.decode())
                command = message.get("command")

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

    def register_user(self, message: Dict, conn: socket.socket):
        username = message["username"]
        tcp_ip = conn.getsockname()[0]
        udp_port = message["udp_port"]

        user = User(username=username, tcp_ip=tcp_ip, udp_port=udp_port)
        self.users[username] = user
        print(f"Registered user: {user}")

    def create_topic(self, message: Dict):
        topic_name = message["topic"]
        if topic_name not in self.topics:
            self.topics[topic_name] = Topic(name=topic_name)
            print(f"Created topic: {topic_name}")

    def subscribe_topic(self, message: Dict):
        username = message["username"]
        topic_name = message["topic"]
        if topic_name in self.topics:
            self.topics[topic_name].subscribers.append(username)
            self.users[username].subscribed_topics.append(topic_name)
            print(f"{username} subscribed to {topic_name}")
        
    def publish_message(self, message: Dict):
        username = message["username"]
        topic_name = message["topic"]
        msg_content = message["content"]

        if topic_name in self.topics:
            print(f"Broadcasting message from {username} to topic {topic_name}: {msg_content}")
            subscribers = self.topics[topic_name].subscribers
            for subcriber in subscribers:
                if subcriber != username:
                    self.send_message_to_user(subcriber, msg_content)

    def send_message_to_user(self, username: str, msg_content: str):
        user = self.users.get(username)
        if user:
            try:
                message = json.dumps({"topic": "broadcast", "content": msg_content}).encode()
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((user.tcp_ip, user.udp_port))
                    s.sendall(message)
            except Exception as e:
                print(f"Error sending message to {username}: {e}")

    def send_topics(self, conn: socket.socket):
        topics_list = list(self.topics.keys())
        conn.sendall(json.dumps(topics_list).encode())

    def send_users_by_topic(self, message: Dict, conn: socket.socket):
        topic_name = message["topic"]
        if topic_name in self.topics:
            subscribers = self.topics[topic_name].subscribers
            conn.sendall(json.dumps(subscribers).encode())
        else:
            conn.sendall(json.dumps([]).encode())

    def send_all_users(self, conn: socket.socket):
        users_info = [
            {
                'username': user.username,
            }
            for user in self.users.values()
        ]
        conn.sendall(json.dumps(users_info).encode())
    
    def send_tcp_ip(self, message: Dict, conn: socket.socket):
        target_username = message["username"]
        user = self.users.get(target_username)
        if user:
            conn.sendall(json.dumps({"tcp_ip": user.tcp_ip}).encode())
        else:
            conn.sendall(json.dumps({"error": "User not found"}).encode())

    def send_udp_port(self, message: Dict, conn: socket.socket):
        target_username = message["username"]
        user = self.users.get(target_username)
        if user:
            conn.sendall(json.dumps({"udp_port": user.udp_port}).encode())
        else:
            conn.sendall(json.dumps({"error": "User not found"}).encode())

    def start_server(self, host='127.0.0.1', port=65432):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((host, port))
            server_socket.listen()
            print(f"Publisher listening on {host}:{port}")

            while True:
                conn, addr = server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.start()

if __name__ == "__main__":
    publisher = Publisher()
    publisher.start_server()
