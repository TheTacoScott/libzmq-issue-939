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
    for i in range(400):
      logging.info("Starting Client #" + str(i))
      client[i] = ctx.socket(zmq.DEALER)

      client_secret_file = os.path.join(secret_keys_dir, "client.key_secret")
      client_public, client_secret = zmq.auth.load_certificate(client_secret_file)
      server_secret_file = os.path.join(secret_keys_dir, "server.key_secret")
      server_public, server_secret = zmq.auth.load_certificate(server_secret_file)

      client[i].curve_secretkey = client_secret
      client[i].curve_publickey = client_public
      client[i].curve_serverkey = server_public
      client[i].connect('tcp://127.0.0.1:9000')
      client[i].send_multipart(['',b'Hello'])
    logging.info("Waiting for crash to happen server side.")
    time.sleep(1000000)
    auth.stop()

logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s]\t[%(asctime)s] [%(filename)s:%(lineno)d] [%(funcName)s] %(message)s")
run()
