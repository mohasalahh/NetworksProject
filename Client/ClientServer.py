import hashlib
import threading
import logging

from Client.UDPServer import UDPServer
from Client.configurations import port, tcpThreads, db
from Utils import AESEnryptionUtils


# This class is used to process the peer messages sent to registry
# for each peer connected to registry, a new client thread is created
class ClientThread(threading.Thread):
    # initializations for client thread
    def __init__(self, ip, port, tcpClientSocket):
        threading.Thread.__init__(self)
        # ip of the connected peer
        self.ip = ip
        # port number of the connected peer
        self.port = port
        # socket of the peer
        self.tcpClientSocket = tcpClientSocket
        # username, online status and udp server initializations
        self.username = None
        self.isOnline = True
        self.udpServer = None
        print("New thread started for " + ip + ":" + str(port))

    # main of the thread
    def run(self):
        # locks for thread which will be used for thread synchronization
        self.lock = threading.Lock()
        print("Connection from: " + self.ip + ":" + str(port))
        print("IP Connected: " + self.ip)

        while True:
            try:
                # waits for incoming messages from peers
                message = AESEnryptionUtils.AESEncryption().decrypt(self.tcpClientSocket.recv(1024).decode()).split()
                logging.info("Received from " + self.ip + ":" + str(self.port) + " -> " + " ".join(message))
                #   JOIN    #
                if message[0] == "JOIN":
                    # join-exist is sent to peer,
                    # if an account with this username already exists
                    if db.is_account_exist(message[1]):
                        response = "join-exist"
                        print("From-> " + self.ip + ":" + str(self.port) + " " + response)
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.sendEncryptedMessage(response)
                    # join-success is sent to peer,
                    # if an account with this username is not exist, and the account is created
                    else:
                        db.register(message[1], message[2])
                        response = "join-success"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.sendEncryptedMessage(response)
                #   LOGIN    #
                elif message[0] == "LOGIN":
                    # login-account-not-exist is sent to peer,
                    # if an account with the username does not exist
                    if not db.is_account_exist(message[1]):
                        response = "login-account-not-exist"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.sendEncryptedMessage(response)
                    # login-online is sent to peer,
                    # if an account with the username already online
                    # login-success is sent to peer,
                    # if an account with the username exists and not online
                    else:
                        # retrieves the account's password, and checks if the one entered by the user is correct
                        retrievedPass = db.get_password(message[1])
                        hashedPassword = hashlib.md5(message[2].encode()).hexdigest()
                        # if password is correct, then peer's thread is added to threads list
                        # peer is added to db with its username, port number, and ip address
                        if retrievedPass == hashedPassword:
                            self.username = message[1]
                            self.lock.acquire()
                            try:
                                tcpThreads[self.username] = self
                            finally:
                                self.lock.release()

                            db.user_login(message[1], self.ip, message[3])
                            # login-success is sent to peer,
                            # and a udp server thread is created for this peer, and thread is started
                            # timer thread of the udp server is started
                            response = "login-success"
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                            self.sendEncryptedMessage(response)
                            self.udpServer = UDPServer(self.username, self.tcpClientSocket)
                            self.udpServer.start()
                            self.udpServer.timer.start()
                        # if password not matches and then login-wrong-password response is sent
                        else:
                            response = "login-wrong-password"
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                            self.sendEncryptedMessage(response)
                #   LOGOUT  #
                elif message[0] == "LOGOUT":
                    # if user is online,
                    # removes the user from onlinePeers list
                    # and removes the thread for this user from tcpThreads
                    # socket is closed and timer thread of the udp for this
                    # user is cancelled
                    if len(message) > 1 and message[1] is not None and db.is_account_online(message[1]):
                        db.user_logout(message[1])
                        self.lock.acquire()
                        try:
                            if message[1] in tcpThreads:
                                del tcpThreads[message[1]]
                        finally:
                            self.lock.release()
                        print(self.ip + ":" + str(self.port) + " is logged out")
                        self.tcpClientSocket.close()
                        self.udpServer.timer.cancel()
                        break
                    else:
                        self.tcpClientSocket.close()
                        break
                #   SEARCH  #
                elif message[0] == "SEARCH":
                    # checks if an account with the username exists
                    if db.is_account_exist(message[1]):
                        # checks if the account is online
                        # and sends the related response to peer
                        if db.is_account_online(message[1]):
                            peer_info = db.get_peer_ip_port(message[1])
                            response = "search-success " + peer_info[0] + ":" + peer_info[1]
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                            self.sendEncryptedMessage(response)
                        else:
                            response = "search-user-not-online"
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                            self.sendEncryptedMessage(response)
                    # enters if username does not exist
                    else:
                        response = "search-user-not-found"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.sendEncryptedMessage(response)

                elif message[0] == "GETONLINE":
                    response = db.get_online_peers(message[1])
                    logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)

                    if response == "":
                        response = "NOONLINEUSERS"

                    self.sendEncryptedMessage(response)

                elif message[0] == "CREATE-ROOM":
                    room_id = db.create_room(message[1])
                    if room_id == "":
                        self.sendEncryptedMessage("error")
                    else:
                        self.sendEncryptedMessage("success "+room_id)

                elif message[0] == "GETROOMS":
                    all_rooms = db.get_all_rooms()
                    if all_rooms == "":
                        self.sendEncryptedMessage("NOROOMS")
                    else:
                        self.sendEncryptedMessage("success "+all_rooms)

                elif message[0] == "SEND_TO_ROOM":
                    room = db.get_room(message[1])
                    members = room["members"]

                    tcp_message = "SEND_ROOM_MESSAGE "+message[2]+" " + " ".join(message[3:]) # user + message

                    for member in members:
                        if member in tcpThreads:
                            tcpThreads[member].sendEncryptedMessage(tcp_message)

                elif message[0] == "JOIN_ROOM":
                    result = db.join_room(message[1], message[2])

                    if result:
                        self.sendEncryptedMessage("success-joining")

                        room = db.get_room(message[1])
                        members = room["members"]

                        tcp_message = "SEND_ROOM_MESSAGE " + message[2] + " joined the room!"

                        for member in members:
                            if member in tcpThreads:
                                tcpThreads[member].sendEncryptedMessage(tcp_message)
                    else:
                        self.sendEncryptedMessage("error-joining")
                elif message[0] == "LEAVE_ROOM":
                    result = db.leave_room(message[1], message[2])
                    if result:
                        self.sendEncryptedMessage("success-leaving")

                        room = db.get_room(message[1])
                        members = room["members"]

                        tcp_message = "SEND_ROOM_MESSAGE " + message[2] + " left the room!"

                        for member in members:
                            if member in tcpThreads:
                                tcpThreads[member].sendEncryptedMessage(tcp_message)
                    else:
                        self.sendEncryptedMessage("error-leaving")

                elif message[0] == "GETROOMINFO":
                    room = db.get_room(message[1])
                    logging.info("Send to " + self.ip + ":" + str(self.port) + " -> ")

                    if room is None:
                        self.sendEncryptedMessage("NOT_FOUND")
                    else:
                        self.sendEncryptedMessage("FOUND "+room["name"])

            except OSError as oErr:
                logging.error("OSError: {0}".format(oErr))

                # function for resettin the timeout for the udp timer thread

    def resetTimeout(self):
        self.udpServer.resetTimer()

    def sendEncryptedMessage(self, plainmessage):
        print("senddddd", plainmessage)
        self.tcpClientSocket.send(AESEnryptionUtils.AESEncryption().encrypt(plainmessage).encode())
