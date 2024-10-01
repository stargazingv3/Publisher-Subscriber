import socket
import json
import threading

class Client:
    def __init__(self, username):
        self.username = username
        self.udp_port = self.get_unique_udp_port()
        self.client_host = socket.gethostbyname(socket.gethostname())
        self.tcp_server_ip = '127.0.0.1'
        self.tcp_server_port = 65432
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(('', self.udp_port))
        self.start_udp_listner()
        self.register()

    def get_unique_udp_port(self):
        return 8888

    def start_udp_listner(self):
        listener_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        listener_thread.start()

    def listen_for_messages(self):
        while True:
            message, addr = self.udp_socket.recvfrom(1024)
            decoded_message = message.decode()
            print(f"Recieved message: {decoded_message} from {addr}")

    def register(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.connect((self.tcp_server_ip, self.tcp_server_port))
            message = {
                "command": "register",
                "username": self.username,
                "udp_port": self.udp_port
            }
            tcp_socket.sendall(json.dumps(message).encode())
            print(f"Registered as {self.username} on client host {self.client_host} on UDP port {self.udp_port}")

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
            users_info = json.loads(data.decode())
            print("All users:")
            for user in users_info:
                print(f"Username: {user['username']}")

    def request_user_attribute(self, command, target_username):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.connect((self.tcp_server_ip, self.tcp_server_port))
            message = {"command": command, "username": target_username}
            tcp_socket.sendall(json.dumps(message).encode())
            data = tcp_socket.recv(1024)
            user_info = json.loads(data.decode())
            if 'error' not in user_info:
                print(f"{command} for {target_username}: {user_info}")
                return user_info
            else:
                print(user_info['error'])

    def get_user_info(self, target_username):
        tcp_ip = self.request_user_attribute("get_tcp_ip", target_username)['tcp_ip']
        udp_port = self.request_user_attribute("get_udp_port", target_username)['udp_port']
        return tcp_ip, udp_port

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

    def message_user(self, target_username, message):
        tcp_ip, udp_port = self.get_user_info(target_username)
        if tcp_ip and udp_port:
            #print("Message to send: ", type(message))
            self.udp_socket.sendto(message.encode(), (tcp_ip, udp_port))
            print(f"Sent message to {target_username}: {message}")
        else:
            print("TCP: ", tcp_ip, "UDP: \n", udp_port)
            print(f"Could not send message to {target_username}, user info not found.")

    def publish_message(self, topic_name):
        message_content = input("Enter the meassage you would like to be published: ")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.connect((self.tcp_server_ip, self.tcp_server_port))
            message = {
                "command": "publish_message",
                "username": self.username,
                "topic": topic_name,
                "content": message_content
            }
            tcp_socket.sendall(json.dumps(message).encode())
            print(f"Published message to {topic_name}: {message_content}")


    def run(self):
        while True:
            print("\nMenu:")
            print("1. LIST TOPICS")
            print("2. LIST USERS")
            print("3. CREATE TOPIC")
            print("4. SUB")
            print("5. PUBLISH")
            print("6. GET DM INFO")
            print("7. DM USER")
            print("8. LIST USER SUBED TO TOPIC")
            print("9. Exit")
            choice = input("Select an option: ")

            if choice == "1":
                self.request_topics()
            elif choice == "2":
                self.list_users()
            elif choice == "3":
                topic_name = input("Enter topic name to create: ")
                self.create_topic(topic_name)
            elif choice == "4":
                topic_name = input("Enter topic name to subscribe: ")
                self.subscribe_topic(topic_name)
            elif choice == "5":
               topic_name = input("Enter the topic you wish to publish about: ")
               self.publish_message(topic_name)
            elif choice == "6":
                target_username_info = input("Enter the username whose info you wish to recieve ")
                self.get_user_info(target_username_info)
            elif choice == "7":
                target_username = input("Enter the username to message: ")
                message = input("Enter your message: ")
                self.message_user(target_username, message)
            elif choice == "8":
                topic_name = input("Enter topic name to list users: ")
                self.get_users_by_topic(topic_name)
            elif choice == "9":
                print("Exiting...")
                break

            else:
                print("Invalid option. Please try again.")

if __name__ == "__main__":
    username = input("Enter your username: ")
    client = Client(username)
    client.run()
