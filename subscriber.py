import socket
import json

class Client:
    def __init__(self, username, udp_port=8888):
        self.username = username
        self.udp_port = udp_port
        self.tcp_server_ip = '127.0.0.1'
        self.tcp_server_port = 65432
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.register()

    def register(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.connect((self.tcp_server_ip, self.tcp_server_port))
            message = {
                "command": "register",
                "username": self.username,
                "udp_port": self.udp_port
            }
            tcp_socket.sendall(json.dumps(message).encode())
            print(f"Registered as {self.username}")

    def request_topics(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.connect((self.tcp_server_ip, self.tcp_server_port))
            message = {"command": "get_topics"}
            tcp_socket.sendall(json.dumps(message).encode())
            data = tcp_socket.recv(1024)
            topics = json.loads(data.decode())
            print("Available Topics:")
            print(topics)

    def get_users_by_topic(self, topic_name):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.connect((self.tcp_server_ip, self.tcp_server_port))
            message = {
                "command": "get_users_by_topic",
                "topic": topic_name
            }
            tcp_socket.sendall(json.dumps(message).encode())
            data = tcp_socket.recv(1024)
            subscribers = json.loads(data.decode())
            print(f"Users subscribed to {topic_name}:")
            print(subscribers)

    def list_users(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.connect((self.tcp_server_ip, self.tcp_server_port))
            message = {"command": "get_users"}
            tcp_socket.sendall(json.dumps(message).encode())
            data = tcp_socket.recv(1024)
            users = json.loads(data.decode())
            print("All Users:")
            print(users)

    def subscribe_topic(self, topic_name):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.connect((self.tcp_server_ip, self.tcp_server_port))
            message = {
                "command": "subscribe",
                "username": self.username,
                "topic": topic_name
            }
            tcp_socket.sendall(json.dumps(message).encode())
            print(f"Subscribed to {topic_name}")

    def create_topic(self, topic_name):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.connect((self.tcp_server_ip, self.tcp_server_port))
            message = {
                "command": "create_topic",
                "topic": topic_name
            }
            tcp_socket.sendall(json.dumps(message).encode())
            print(f"Created topic: {topic_name}")

    def get_user_udp_info(self, target_username):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.connect((self.tcp_server_ip, self.tcp_server_port))
            message = {"command": "get_users"}
            tcp_socket.sendall(json.dumps(message).encode())
            data = tcp_socket.recv(1024)
            user_info = json.loads(data.decode())
            if target_username in user_info:
                udp_info = user_info[target_username]
                print(f"{target_username} UDP info: {udp_info}")
                return udp_info
            else:
                print(f"{target_username} not found.")

    def message_user(self, target_username, message):
        udp_info = self.get_user_udp_info(target_username)
        if udp_info:
            target_ip = udp_info['tcp_ip']
            target_port = udp_info['udp_port']
            self.udp_socket.sendto(message.encode(), (target_ip, target_port))
            print(f"Sent message to {target_username}: {message}")

    def run(self):
        while True:
            print("\nMenu:")
            print("1. Request list of topics")
            print("2. Subscribe to a topic")
            print("3. Create a topic")
            print("4. List users subscribed to a topic")
            print("5. List all users")
            print("6. Message another user")
            print("7. Exit")
            choice = input("Select an option: ")

            if choice == "1":
                self.request_topics()
            elif choice == "2":
                topic_name = input("Enter topic name to subscribe: ")
                self.subscribe_topic(topic_name)
            elif choice == "3":
                topic_name = input("Enter topic name to create: ")
                self.create_topic(topic_name)
            elif choice == "4":
                topic_name = input("Enter topic name to list users: ")
                self.get_users_by_topic(topic_name)
            elif choice == "5":
                self.list_users()
            elif choice == "6":
                target_username = input("Enter the username to message: ")
                message = input("Enter your message: ")
                self.message_user(target_username, message)
            elif choice == "7":
                print("Exiting...")
                break
            else:
                print("Invalid option. Please try again.")

if __name__ == "__main__":
    username = input("Enter your username: ")
    client = Client(username)
    client.run()
