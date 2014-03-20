#!/usr/bin/env python

import logging
import os
import sys
import shutil

import zmq
import zmq.auth
from zmq.auth.thread import ThreadAuthenticator
import re

def generate_certificates(base_dir):
    keys_dir = os.path.join(base_dir, 'certificates')
    public_keys_dir = os.path.join(base_dir, 'public_keys')
    secret_keys_dir = os.path.join(base_dir, 'private_keys')

    for d in [keys_dir, public_keys_dir, secret_keys_dir]:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.mkdir(d)

    server_public_file, server_secret_file = zmq.auth.create_certificates(keys_dir, "server")
    client_public_file, client_secret_file = zmq.auth.create_certificates(keys_dir, "client")

    for key_file in os.listdir(keys_dir):
        if key_file.endswith(".key"):
            shutil.move(os.path.join(keys_dir, key_file),
                        os.path.join(public_keys_dir, '.'))

    for key_file in os.listdir(keys_dir):
        if key_file.endswith(".key_secret"):
            shutil.move(os.path.join(keys_dir, key_file),
                        os.path.join(secret_keys_dir, '.'))

def run():
    base_dir = os.path.dirname(__file__)
    keys_dir = os.path.join(base_dir, 'certificates')
    public_keys_dir = os.path.join(base_dir, 'public_keys')
    secret_keys_dir = os.path.join(base_dir, 'private_keys')
    client_file_input = open(public_keys_dir + "/client.key").read()
    with open(public_keys_dir + "/client.key", 'wb') as f:
      f.write(re.sub(r'public-key = ".*?"','public-key = ">7dfoIl$n6FkAN@/476a(e&:i!2fPomP=3HPI{*S"',client_file_input,re.M))
    if not (os.path.exists(keys_dir) and os.path.exists(keys_dir) and os.path.exists(keys_dir)):
        logging.critical("Certificates are missing - run generate_certificates.py script first")
        sys.exit(1)
    
    ctx = zmq.Context().instance()
    auth = ThreadAuthenticator(ctx)
    auth.start()
    auth.configure_curve(domain='*', location=public_keys_dir)
    server = ctx.socket(zmq.REP)
    server_secret_file = os.path.join(secret_keys_dir, "server.key_secret")
    server_public, server_secret = zmq.auth.load_certificate(server_secret_file)
    server.curve_secretkey = server_secret
    server.curve_publickey = server_public
    server.curve_server = True  # must come before bind

    poller = zmq.Poller()
    poller.register(server, zmq.POLLIN|zmq.POLLOUT)

    server.bind('tcp://*:9000')

    server_public_file = os.path.join(public_keys_dir, "server.key")
    server_public, _ = zmq.auth.load_certificate(server_public_file)
    while True:
      socks = dict(poller.poll(200))
      if server in socks and socks[server] == zmq.POLLIN:
          msg = server.recv()
          if msg == b"Hello":
              logging.info("Ironhouse test OK")

    auth.stop()

logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s]\t[%(asctime)s] [%(filename)s:%(lineno)d] [%(funcName)s] %(message)s")
generate_certificates(os.path.dirname(__file__))
run()
