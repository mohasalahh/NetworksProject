#
#  RegistryThread.py
#  NetworksProject

#  Created by Mohamed Salah on 07/01/2024.
#  Copyright © 2024 Mohamed Salah. All rights reserved.
#


import logging
import threading
from socket import *

import select

from Client.ClientServer import ClientThread
from Client.configurations import port, portUDP, tcpThreads
from Utils.AESEnryptionUtils import AESEncryption


# This class is used to process the peer messages sent to registry
# for each peer connected to registry, a new client thread is created
class RegistryThread(threading.Thread):
    # initializations for client thread
    def __init__(self):
        threading.Thread.__init__(self)

    # main of the thread
    def run(self):
        # tcp and udp server port initializations
        print("Registy started...")

        # gets the ip address of this peer
        # first checks to get it for windows devices
        # if the device that runs this application is not windows
        # it checks to get it for macos devices
        hostname = gethostname()

        host = gethostbyname(hostname)

        print("Registry IP address: " + host)
        print("Registry port number: " + str(port))

        # tcp and udp socket initializations
        tcpSocket = socket(AF_INET, SOCK_STREAM)
        udpSocket = socket(AF_INET, SOCK_DGRAM)
        tcpSocket.bind((host, port))
        udpSocket.bind((host, portUDP))
        tcpSocket.listen(5)

        # input sockets that are listened
        inputs = [tcpSocket, udpSocket]

        peer_threads = []

        # log file initialization
        #logging.basicConfig(filename="registry.log", level=logging.INFO)

        # as long as at least a socket exists to listen registry runs
        while inputs:
            print("Listening for incoming connections...")
            # monitors for the incoming connections
            readable, writable, exceptional = select.select(inputs, [], [])
            for s in readable:
                # if the message received comes to the tcp socket
                # the connection is accepted and a thread is created for it, and that thread is started
                if s is tcpSocket:
                    tcpClientSocket, addr = tcpSocket.accept()
                    newThread = ClientThread(addr[0], addr[1], tcpClientSocket)
                    newThread.start()
                # if the message received comes to the udp socket
                elif s is udpSocket:
                    # received the incoming udp message and parses it
                    message, clientAddress = s.recvfrom(1024)
                    message = AESEncryption().decrypt(message.decode()).split()
                    # checks if it is a hello message
                    if message[0] == "HELLO":
                        # checks if the account that this hello message
                        # is sent from is online
                        if message[1] in tcpThreads:
                            # resets the timeout for that peer since the hello message is received
                            tcpThreads[message[1]].resetTimeout()
                            # print("Hello is received from " + message[1])
                            # logging.info("Received from " + clientAddress[0] + ":" + str(clientAddress[1]) + " -> " + " ".join(message))

        # registry tcp socket is closed
        tcpSocket.close()

