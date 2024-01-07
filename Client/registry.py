from Client.RegistryThread import RegistryThread

try:
    registryThread = RegistryThread()
    registryThread.start()
    registryThread.join()
except Exception as error:
    print("Error: {0}".format(error))
