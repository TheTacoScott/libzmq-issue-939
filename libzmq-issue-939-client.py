#!/usr/bin/env python

import logging
import os
import sys

import zmq
import zmq.auth
import time

def run():
    base_dir = os.path.dirname(__file__)
    keys_dir = os.path.join(base_dir, 'certificates')
    public_keys_dir = os.path.join(base_dir, 'public_keys')
    secret_keys_dir = os.path.join(base_dir, 'private_keys')

    if not (os.path.exists(keys_dir) and os.path.exists(keys_dir) and os.path.exists(keys_dir)):
        logging.critical("Certificates are missing - run generate_certificates.py script first")
        sys.exit(1)

    ctx = zmq.Context().instance()
    client = {}
    num_clients = 100
    client_secret_file = os.path.join(secret_keys_dir, "client.key_secret")
    client_public, client_secret = zmq.auth.load_certificate(client_secret_file)
    server_secret_file = os.path.join(secret_keys_dir, "server.key_secret")
    server_public, server_secret = zmq.auth.load_certificate(server_secret_file)
    while True:
      logging.info("Starting Clients")
      for i in range(num_clients):
        client[i] = ctx.socket(zmq.DEALER)
        client[i].curve_secretkey = client_secret
        client[i].curve_publickey = client_public
        client[i].curve_serverkey = server_public
        client[i].connect('tcp://127.0.0.1:9000')
        client[i].send_multipart(['',b'Hello'])

      logging.info("Sleeping for 3 Seconds")
      time.sleep(3.0)

      logging.info("Killing Clients")
      for i in range(num_clients):
        client[i].close(0)
        del client[i]
      
      logging.info("Sleeping for 3 Seconds")
      time.sleep(3.0)
      
    auth.stop()

logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s]\t[%(asctime)s] [%(filename)s:%(lineno)d] [%(funcName)s] %(message)s")
run()
