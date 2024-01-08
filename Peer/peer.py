from Peer.PeerThread import PeerThread

import os

clear = lambda: os.system('cls')
clear()


def start_thread():
    try:
        main = PeerThread()
        main.start()
        main.join()
    except Exception as error:
        clear()
        print("Error: {0}".format(error))
        print("Restarting Peer...")
        start_thread()


start_thread()
