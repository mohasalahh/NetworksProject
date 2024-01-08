import os

from Client.RegistryThread import RegistryThread

clear = lambda: os.system('cls')
clear()

def start_thread():
    try:
        registryThread = RegistryThread()
        registryThread.start()
        registryThread.join()
    except Exception as error:
        clear()
        print("Error: {0}".format(error))
        print("Restarting Registry...")
        start_thread()


start_thread()
