#!/usr/bin/env python

import os
import socket
import argparse
import json

def _send_data(args, data):
    send_data = json.dumps(data, ensure_ascii=False)

    sock = socket.create_connection((args.server, args.port))
    sock.send(send_data)
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()

def main(args):
    data = { 'action': 'open',
             'filepath': os.path.abspath(args.filename) }
    if 'hostname' in args:
        data['hostname'] = args.hostname
    if not args.no_data:
        f = open(args.filename, 'r')
        data['file_data'] = f.read()
        f.close()
    _send_data(args, data)

if __name__ == '__main__':
    args = argparse.Namespace()
    if os.getenv('SMATE_HOSTNAME'):
        args.hostname = os.getenv('SMATE_HOSTNAME')
    if os.getenv('SMATE_SERVER'):
        args.server = os.getenv('SMATE_SERVER')
    if os.getenv('SMATE_PORT'):
        args.port = os.getenv('SMATE_PORT')
    if os.getenv('SMATE_NO_DATA'):
        args.no_data = os.getenv('SMATE_NO_DATA')

    parser = argparse.ArgumentParser(description='smate client')
    parser.add_argument('filename', type=str, help='file to load')
    parser.add_argument('-r', dest='reload', action='store_true', default=False, help='if set, file will be reload')
    parser.add_argument('-d', dest='no_data', action='store_true', default=False, help='if set, data won\'t be transferred')
    parser.add_argument('-s', dest='server', type=str, default='localhost:52693', help='server with smate. default is localhost:52693')
    parser.add_argument('-p', dest='port', type=int, default=None, help='port of server. if set, port from -server option will be overvritten')
    parser.add_argument('-hostname', dest='hostname', type=str, help='name of host in sftp')
    args = parser.parse_args(namespace=args)

    if args.port == None:
        if args.server.find(':') == -1:
            args.port = 52693
        args.server, args.port = args.server.split(':')

    if args.server.find(':') != -1:
        args.server = args.server[:args.server.find(':')]

    main(args)
