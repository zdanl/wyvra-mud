#  __      __
# /  \    /  \ ___.__.___  _________ _____
# \   \/\/   /<   |  |\  \/ /\_  __ \\__  \
#  \        /  \___  | \   /  |  | \/ / __ \_
#   \__/\  /   / ____|  \_/   |__|   (____  /
#        \/    \/                         \/

from wyvra.database import database
from wyvra.networking import networking
from wyvra.logging import wyvra_log

import argparse
from _thread import *
import threading

import yaml, os

print_lock = threading.Lock()

def wyvra_handle(c):
    wyvra_log("info", "Handling new connection")
    wyvra_log("info", "Receiving data")
    while True:
        data = c.recv(4096)
        if not data:
            print_lock.release()
            break
        data = data[:-1]
        wyvra_log("info", "Received data: %s" %data)
        wyvra_log("info", "Got %d bytes" %(len(data)))
    wyvra_log("info", "Client disconnected")
    c.close()

def wyvra_init():
    with open("arts/motd", "r") as motd:
        motd = motd.read()
        print(motd)

    host, port = wyvra_config["host"], wyvra_config["port"]
    if args.port: port = int(args.port)
    if args.host: host = args.host

    database_name = wyvra_config["database"]
    
    wyvra_log("info", "Connecting database %s" %database_name)
    db = database(database_name).connection

    wyvra_log("info", "Starting networking %s:%d" %(host, port))
    net = networking(host, port)
    while True:
        c, addr = net.server.accept()
        print_lock.acquire()
        wyvra_log("info", "Connected to: %s : %d" %(addr[0], addr[1]))
        start_new_thread(wyvra_handle, (c,))
    net.server.close()

def wyvra_cleanup():
    pass

def wyvra_argparse():
    parser = argparse.ArgumentParser("Wyvra")
    parser.add_argument("--port", "-p", help="Listenting port")
    parser.add_argument("--host", help="Listenting host")
    parser.add_argument("--admin", "-a", help="One or more admins")
    return parser.parse_args()


if __name__ == "__main__":
    os.system("clear")
    with open("wyvra.yaml", "r") as wyvra_file:
        wyvra_config = yaml.safe_load(wyvra_file)
   
    args = wyvra_argparse()
    wyvra_log("info", "Initiating Wyvra")
    wyvra_init()
    wyvra_log("info", "Preparing for quit")
    wyvra_cleanup()
    wyvra_log("info", "Wyvra terminated")
