#
#  LoadTesting.py
#  NetworksProject
#  Created by Mohamed Salah on 08/01/2024.
#  Copyright © 2024 Mohamed Salah. All rights reserved.
#


from LoadTesting.configurations import waiting_dict, set_waiting_dict, delete_from_waiting_dict
import logging
import threading
import time

logger = logging.getLogger('p2p_chat')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('G:/Mixes/NetworksProject/LoadTesting/load_testing.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

lock = threading.Lock()


def log_send(sender, message):
    with lock:
        set_waiting_dict(message, (sender, time.time()))


def log_receive(receiver, message):
    with lock:
        waiting_dictt = waiting_dict()
        if not waiting_dictt.__contains__(message):
            return

        sender, time_sent = waiting_dictt[message]
        delete_from_waiting_dict(message)
        logger.info(f"{sender}::{receiver}::{message.split()[0]}::{time.time() - time_sent}")
