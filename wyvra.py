#!/usr/bin/env python3.11
# -* encoding: utf-8 -*-

#  __      __
# /  \    /  \ ___.__.___  _________ _____
# \   \/\/   /<   |  |\  \/ /\_  __ \\__  \
#  \        /  \___  | \   /  |  | \/ / __ \_
#   \__/\  /   / ____|  \_/   |__|   (____  /
#        \/    \/                         \/


from wyvra.database import database
from wyvra.networking import networking
from wyvra.logging import wyvra_log
from wyvra.models import user, session
from wyvra.decorators import wyvra_handler, wyvra_subroutine

import threading
import argparse
import yaml, os, ssl
import re, copy

from _thread import *

#context = ssl.SSLContext()
#context.load_cert_chain(certfile="wyvra/cert.pem", keyfile="wyvra/key.pem")
db = None

@wyvra_handler
def wyvra_say(c, text):
    wyvra_log("debug", text)
    for ip, conn in sessions.items():
        conn.send(b"\nSays: " + bytes(text[1], "utf-8") + b"\n")

@wyvra_handler
def wyvra_logout(c, text):
    pass

@wyvra_handler
def wyvra_delete(c, text):
    pass

wyvra_protocol = {
    "^(say|talk)":    wyvra_say,
    "^(exit|quit)$":  wyvra_logout,
    "^(q|e)$":        wyvra_logout,
    "^delete$":       wyvra_delete
}

@wyvra_subroutine
def wyvra_command(c, command):
    command = command.decode("utf-8")
    command = command.split(" ")
    cmd = command[0]

    wyvra_log("info", "Command %s" %cmd)

    matched = False
    for k in wyvra_protocol.keys():
        if re.compile(k).match(cmd):
            handler = wyvra_protocol.get(k)
            handler(c, command)
            matched = True
            break
    
    if matched is False:
        c.send(b"Unknown command.\n")
     
        
@wyvra_subroutine
def wyvra_handle(c):
    wyvra_log("info", "Handling new connection")
    c.send(bytes(motd, "utf-8"))

    while True:
        c.send(b"Nickname: ")
        nickname = c.recv(128)[:-1].decode("utf-8")
        c.send(b"Password: ")
        password = c.recv(128)[:-1].decode("utf-8")
        wyvra_log("info", "Received username and password (%s)" %(nickname))
    
        ret = db.check_user(nickname, password)
        if ret == 2:
            c.send(b"User identified. You are logged in.\n")
            c.send(b"*"*80 + b"\n")
            break
        elif ret == 1:
            c.send(b"Incorrect password.\n")
        else:
            db.register_user(nickname, password)
            c.send(b"User registered. You are logged in.\n")
            wyvra_log("info", "Registered user %s\n" %nickname)
            c.send(b"*"*80 + b"\n")
            break

    wyvra_log("info", "Receiving data")
    while True:
        c.send(b"[%s] >> " %(bytes(nickname, "utf-8")))
        data = c.recv(4096)
        if not data:
            break
        data = data[:-1]

        wyvra_log("info", "Received data: %s" %data)
        wyvra_log("info", "Got %d bytes" %(len(data)))
        wyvra_command(c, data)
    wyvra_log("info", "Client disconnected")
    #c.shutdown(socket.SHUT_RDWR)
    c.close()

@wyvra_subroutine
def wyvra_startup():
    global db

    host, port = wyvra_config["host"], wyvra_config["port"]
    if args.port: port = int(args.port)
    if args.host: host = args.host

    database_name = wyvra_config["database"]
    
    wyvra_log("info", "Connecting database %s" %database_name)
    db = database(database_name)

    wyvra_log("info", "Starting networking %s:%d" %(host, port))
    net = networking(host, port)
    while True:
        c, addr = net.server.accept()
        #connstream = context.wrap_socket(c, server_side=True)
        sess = copy.deepcopy(session)
        sess["ip_address"] = addr[0]
        sess["remote_port"] = addr[1]
        sess["socket"] = c
        db.db.sessions.insert_one(sess)
        wyvra_log("info", "Connected to: %s : %d" %(addr[0], addr[1]))
        start_new_thread(wyvra_handle, (c,))

    net.server.close()

@wyvra_subroutine
def wyvra_cleanup():
    sys.exit(1)

@wyvra_subroutine
def wyvra_argparse():
    parser = argparse.ArgumentParser("Wyvra")
    parser.add_argument("--port", "-p", help="Listenting port")
    parser.add_argument("--host", help="Listenting host")
    parser.add_argument("--admin", "-a", help="One or more admins")
    return parser.parse_args()

if __name__ == "__main__":
    os.system("clear")
    with open("wyvra/arts/motd", "r") as motd:
        motd = motd.read()
        print(motd)
    with open("wyvra/wyvra.yaml", "r") as wyvra_file:
        wyvra_config = yaml.safe_load(wyvra_file)
   
    args = wyvra_argparse()
    wyvra_startup()
    wyvra_cleanup()
