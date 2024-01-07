from Peer.PeerThread import PeerThread

try:
    main = PeerThread()
    main.start()
    main.join()
except Exception as error:
    print("Error: {0}".format(error))
