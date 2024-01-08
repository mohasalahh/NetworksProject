#
#  configurations.py
#  NetworksProject

#  Created by Mohamed Salah on 08/01/2024.
#  Copyright © 2024 Mohamed Salah. All rights reserved.
#

import pickle


def waiting_dict():
    try:
        with open('G:/Mixes/NetworksProject/LoadTesting/saved_dictionary.pkl', 'rb') as f:
            return pickle.load(f)
    except Exception:
        return {}


def set_waiting_dict(key, value):
    dict = waiting_dict()
    dict[key] = value
    with open('G:/Mixes/NetworksProject/LoadTesting/saved_dictionary.pkl', 'wb') as f:
        pickle.dump(dict, f)


def delete_from_waiting_dict(key):
    dict = waiting_dict()
    dict.pop(key, None)
    with open('G:/Mixes/NetworksProject/LoadTesting/saved_dictionary.pkl', 'wb') as f:
        pickle.dump(dict, f)
