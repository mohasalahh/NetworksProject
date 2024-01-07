#
#  PeerThread.py
#  NetworksProject

#  Created by Mohamed Salah on 07/01/2024.
#  Copyright © 2024 Mohamed Salah. All rights reserved.
#


from socket import *
import threading
import logging

from Peer.configurations import console
from Utils import AESEnryptionUtils
from Peer.PeerClient import PeerClient
from Peer.PeerServer import PeerServer
import atexit
import signal


# main process of the peer
class PeerThread(threading.Thread):

    def exit_handler(self, *args):
        del self


    # initializations for client thread
    def __init__(self):
        threading.Thread.__init__(self)

        atexit.register(self.exit_handler)
        signal.signal(signal.SIGTERM, self.exit_handler)
        signal.signal(signal.SIGINT, self.exit_handler)

        # ip address of the registry
        self.registryName = "192.168.56.1"
        # port number of the registry
        self.registryPort = 15600
        # tcp socket connection to registry
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        self.tcpClientSocket.connect((self.registryName, self.registryPort))
        # initializes udp socket which is used to send hello messages
        self.udpClientSocket = socket(AF_INET, SOCK_DGRAM)
        # udp port of the registry
        self.registryUDPPort = 15500
        # login info of the peer
        self.loginCredentials = (None, None)
        # online status of the peer
        self.isOnline = False
        # server port number of this peer
        self.peerServerPort = None
        # server of this peer
        self.peerServer = None
        # client of this peer
        self.peerClient = None
        # timer initialization
        self.timer = None
        self.isInsideRoom = False

        # log file initialization
        logging.basicConfig(filename="../peer.log", level=logging.INFO)

    def __del__(self):
        if not self.isOnline:
            return

        self.logout(1)
        self.isOnline = False
        self.loginCredentials = (None, None)
        self.peerServer.isOnline = False
        self.peerServer.tcpServerSocket.close()
        if self.peerClient is not None:
            self.peerClient.tcpClientSocket.close()
        print("Logged out successfully")

    def run(self):

        choice = "0"
        online_text = "[bold cyan]Welcome to p2p chat[/bold cyan]\n" \
                      "[purple]Logout:[/purple] 3\n" \
                      "[yellow]Search:[/yellow] 4\n" \
                      "[magenta]Start a 1-1 chat:[/magenta] 5\n" \
                      "[magenta]Create a chat room:[/magenta] 6\n" \
                      "[magenta]Join a chat room:[/magenta] 7\n"

        offline_text = "[bold cyan]Welcome to p2p chat[/bold cyan]\n" \
                       "[bold cyan]Choose:[/bold cyan]\n" \
                       "[red]Create account:[/red] 1\n" \
                       "[green]Login:[/green] 2\n"

        while choice != "3":
            # menu selection prompt
            choice = console.input(online_text if self.isOnline else offline_text)
            # if choice is 1, creates an account with the username
            # and password entered by the user
            if choice == "1":
                username = console.input("[bold]username: [/bold]")
                password = console.input("[bold]password: [/bold]")

                self.create_account(username, password)
            # if choice is 2 and user is not logged in, asks for the username
            # and the password to login
            elif choice == "2" and not self.isOnline:
                username = console.input("[bold]username: [/bold]")
                password = console.input("[bold]password: [/bold]")
                # asks for the port number for server's tcp socket
                peer_server_port = int(console.input("Enter a port number for peer server: "))

                status = self.login(username, password, peer_server_port)
                # is user logs in successfully, peer variables are set
                if status == 1:
                    self.isOnline = True
                    self.loginCredentials = (username, password)
                    self.peerServerPort = peer_server_port
                    # creates the server thread for this peer, and runs it
                    self.peerServer = PeerServer(self.loginCredentials[0], self.peerServerPort)
                    self.peerServer.start()
                    # hello message is sent to registry
                    self.sendHelloMessage()
            # if choice is 3 and user is logged in, then user is logged out
            # and peer variables are set, and server and client sockets are closed
            elif choice == "3" and self.isOnline:
                self.logout(1)
                self.isOnline = False
                self.loginCredentials = (None, None)
                self.peerServer.isOnline = False
                self.peerServer.tcpServerSocket.close()
                if self.peerClient is not None:
                    self.peerClient.tcpClientSocket.close()
                print("Logged out successfully, Bye")
            # is peer is not logged in and exits the program
            elif choice == "3":
                self.logout(2)
            # if choice is 4 and user is online, then user is asked
            # for a username that is wanted to be searched
            elif choice == "4" and self.isOnline:
                username = console.input("[bold]Username to be searched: [/bold]")
                searchStatus = self.searchUser(username)
                # if user is found its ip address is shown to user
                if searchStatus is not None and searchStatus != 0:
                    print("IP address of " + username + " is " + searchStatus)
            # if choice is 5 and user is online, then user is asked
            # to enter the username of the user that is wanted to be chatted
            elif choice == "5" and self.isOnline:
                online_peers_response = self.request_online_peers()
                if online_peers_response == "NOONLINEUSERS":
                    print("**No Online Peers**")
                else:
                    online_peers = online_peers_response.split(",")
                    print("Online Peers(" + str(len(online_peers)) + "): ")
                    for peer in online_peers:
                        console.print("[green]•" + peer + " is online[/green]")

                    username = console.input("Choose a user and enter his/her username to start chat: ")
                    searchStatus = self.searchUser(username)
                    # if searched user is found, then its ip address and port number is retrieved
                    # and a client thread is created
                    # main process waits for the client thread to finish its chat
                    if searchStatus is not None and searchStatus != 0:
                        searchStatus = searchStatus.split(":")
                        self.peerClient = PeerClient(searchStatus[0], int(searchStatus[1]), self.loginCredentials[0],
                                                     self.peerServer, None)
                        self.peerClient.start()
                        self.peerClient.join()

            elif choice == "6":
                chatroom_name = console.input("[bold]Enter chat room name: [/bold]")
                self.create_new_room(chatroom_name)
            elif choice == "7":
                current_rooms = self.request_all_rooms()
                if current_rooms == "":
                    print("**No Rooms**")
                else:
                    rooms = current_rooms.split(",")
                    print("Opened rooms(" + str(len(rooms)) + "): ")
                    for room in rooms:
                        room_info = room.split(":")
                        console.print(f"[green]• {room_info[1]} ({room_info[2]} online) ({room_info[0]}) [/green]")

                    chatroom_id = console.input("[bold]Enter chat room id: [/bold]")
                    self.enter_room(chatroom_id)

            # if this is the receiver side then it will get the prompt to accept an incoming request during the main loop
            # that's why response is evaluated in main process not the server thread even though the prompt is printed by server
            # if the response is ok then a client is created for this peer with the OK message and that's why it will directly
            # sent an OK message to the requesting side peer server and waits for the user input
            # main process waits for the client thread to finish its chat
            elif self.peerServer.isChatRequested:
                if choice == "OK":
                    okMessage = "OK " + self.loginCredentials[0]
                    logging.info("Send to " + self.peerServer.connectedPeerIP + " -> " + okMessage)
                    self.peerServer.connectedPeerSocket.send(
                        AESEnryptionUtils.AESEncryption().encrypt(okMessage).encode())
                    self.peerClient = PeerClient(self.peerServer.connectedPeerIP, self.peerServer.connectedPeerPort,
                                                 self.loginCredentials[0], self.peerServer, "OK")
                    self.peerClient.start()
                    self.peerClient.join()
                # if user rejects the chat request then reject message is sent to the requester side
                elif choice == "REJECT":
                    self.peerServer.connectedPeerSocket.send(
                        AESEnryptionUtils.AESEncryption().encrypt("REJECT").encode())
                    self.peerServer.isChatRequested = 0
                    logging.info("Send to " + self.peerServer.connectedPeerIP + " -> REJECT")
            # if choice is cancel timer for hello message is cancelled
            elif choice == "CANCEL":
                self.timer.cancel()
                break
        # if main process is not ended with cancel selection
        # socket of the client is closed
        if choice != "CANCEL":
            del self

    # account creation function
    def create_account(self, username, password):
        # join message to create an account is composed and sent to registry
        # if response is success then informs the user for account creation
        # if response is exist then informs the user for account existence
        message = "JOIN " + username + " " + password
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(AESEnryptionUtils.AESEncryption().encrypt(message).encode())
        response = self.recieveEncryptedMessage()
        logging.info("Received from " + self.registryName + " -> " + response)
        if response == "join-success":
            print("Account created...")
            return 1
        elif response == "join-exist":
            print("choose another username or login...")
            return 0

    def request_online_peers(self):
        message = "GETONLINE " + self.loginCredentials[0]
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(AESEnryptionUtils.AESEncryption().encrypt(message).encode())
        response = self.recieveEncryptedMessage()
        logging.info("Received from " + self.registryName + " -> " + " ".join(response))

        return response

    # login function
    def login(self, username, password, peerServerPort):
        # a login message is composed and sent to registry
        # an integer is returned according to each response
        message = "LOGIN " + username + " " + password + " " + str(peerServerPort)
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(AESEnryptionUtils.AESEncryption().encrypt(message).encode())
        response = self.recieveEncryptedMessage()
        logging.info("Received from " + self.registryName + " -> " + response)
        if response == "login-success":
            console.print("[bold green]Logged in successfully[/bold green]")
            return 1
        elif response == "login-account-not-exist":
            console.print("[bold red]Account does not exist[/bold red]")
            return 0
        elif response == "login-online":
            console.print("[bold green]Logged in successfully[/bold green]")
            return 1
        elif response == "login-wrong-password":
            console.print("[bold red]Wrong password[/bold red]")
            return 3

    # logout function
    def logout(self, option):
        # a logout message is composed and sent to registry
        # timer is stopped
        if option == 1:
            message = "LOGOUT " + self.loginCredentials[0]
            self.timer.cancel()
        else:
            message = "LOGOUT"
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(AESEnryptionUtils.AESEncryption().encrypt(message).encode())

    # function for searching an online user
    def searchUser(self, username):
        # a search message is composed and sent to registry
        # custom value is returned according to each response
        # to this search message
        message = "SEARCH " + username
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(AESEnryptionUtils.AESEncryption().encrypt(message).encode())
        response = self.recieveEncryptedMessage().split()
        logging.info("Received from " + self.registryName + " -> " + " ".join(response))
        if response[0] == "search-success":
            print(username + " is found successfully...")
            return response[1]
        elif response[0] == "search-user-not-online":
            print(username + " is not online...")
            return 0
        elif response[0] == "search-user-not-found":
            print(username + " is not found")
            return None

    def request_all_rooms(self):
        message = "GETROOMS"
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(AESEnryptionUtils.AESEncryption().encrypt(message).encode())
        response = self.recieveEncryptedMessage().split()

        if response[0] == "success":
            return response[1]

        return ""

    def create_new_room(self, name):
        message = "CREATE-ROOM " + name
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(AESEnryptionUtils.AESEncryption().encrypt(message).encode())
        response = self.recieveEncryptedMessage().split()

        if response[0] == "success":
            print("Room created")
            self.enter_room(response[1])
        elif response[0] == "error":
            print("Error creating room")

    def get_room_name(self, id):
        message = "GETROOMINFO " + id
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(AESEnryptionUtils.AESEncryption().encrypt(message).encode())
        response = self.recieveEncryptedMessage().split()
        logging.info("Received from " + self.registryName + " -> " + " ".join(response))

        if response[0] == "FOUND":
            return response[1]

        return ""

    def enter_room(self, id):
        room_name = self.get_room_name(id)
        if room_name == "":
            print("Room Not Found!")
            return

        message = "JOIN_ROOM " + id + " " + self.loginCredentials[0]

        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(AESEnryptionUtils.AESEncryption().encrypt(message).encode())
        response = self.recieveEncryptedMessage().split()

        if response[0] != "success-joining":
            print("Error joining room")
            return

        print(f"You are inside room \"{room_name}\", type \\LEAVE to leave the room")

        self.isInsideRoom = True
        self.peerServer.isInsideRoom = True

        receiving_thread = threading.Thread(target=self.inside_room_receiving, args=(id,))
        receiving_thread.start()

        sending_thread = threading.Thread(target=self.inside_room_waiting_to_send, args=(id,))
        sending_thread.start()
        sending_thread.join()

    def leave_room(self, id):
        if not self.isInsideRoom:
            return

        message = "LEAVE_ROOM " + id + " " + self.loginCredentials[0]
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(AESEnryptionUtils.AESEncryption().encrypt(message).encode())

        # i will wait for response in the receiving thread

    def inside_room_waiting_to_send(self, id):
        while self.isInsideRoom:
            message = input("")
            if message == "\\LEAVE":
                self.leave_room(id)
                break
            message = "SEND_TO_ROOM " + id + " " + self.loginCredentials[0] + " " + message
            # logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
            self.tcpClientSocket.send(AESEnryptionUtils.AESEncryption().encrypt(message).encode())

    def inside_room_receiving(self, id):
        while self.isInsideRoom:
            response = self.recieveEncryptedMessage().split()  # SEND_ROOM_MESSAGE roomid username message
            if response[0] == "SEND_ROOM_MESSAGE":
                message_username = response[1]
                message = ' '.join(response[2:])
                if message_username == self.loginCredentials[0]:
                    message_username = "You"

                if message == "joined the room!":
                    console.print(f"[bold green]{message_username} joined the room![/bold green]")
                elif message == "left the room!":
                    console.print(f"[bold red]{message_username} left the room![/bold red]")
                else:
                    console.print(f"[bold cyan]{message_username}:[/bold cyan] {message}")
            elif response[0] == "success-leaving":
                self.isInsideRoom = False
                self.peerServer.isInsideRoom = False
                print("Left room\n")
            elif response[0] == "error-leaving":
                print("Error Leaving\n")

    # function for sending hello message
    # a timer thread is used to send hello messages to udp socket of registry
    def sendHelloMessage(self):
        message = "HELLO " + self.loginCredentials[0]
        self.udpClientSocket.sendto(AESEnryptionUtils.AESEncryption().encrypt(message).encode(),
                                    (self.registryName, self.registryUDPPort))
        self.timer = threading.Timer(1, self.sendHelloMessage)
        self.timer.start()

    def recieveEncryptedMessage(self):
        return AESEnryptionUtils.AESEncryption().decrypt(self.tcpClientSocket.recv(1024).decode())
