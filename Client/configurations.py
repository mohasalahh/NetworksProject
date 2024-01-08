from rich.console import Console

from Client.db import DB

port = 15600
portUDP = 15500
# onlinePeers list for online account
onlinePeers = {}
# accounts list for accounts
accounts = {}
# tcpThreads list for online client's thread
tcpThreads = {}

# db initialization
db = DB()

console = Console(color_system="windows")
