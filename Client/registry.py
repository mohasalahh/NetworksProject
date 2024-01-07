from Client.RegistryThread import RegistryThread


def start_thread():
    try:
        registryThread = RegistryThread()
        registryThread.start()
        registryThread.join()
    except Exception as error:
        print("Error: {0}".format(error))
        print("Restarting Registry...")
        start_thread()


start_thread()
