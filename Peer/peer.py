from Peer.PeerThread import PeerThread


def start_thread():
    try:
        main = PeerThread()
        main.start()
        main.join()
    except Exception as error:
        print("Error: {0}".format(error))
        print("Restarting Peer...")
        start_thread()


start_thread()
