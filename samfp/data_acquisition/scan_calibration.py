#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import socket
import sys


def send_command(command):
    """
    Send a command to the SAM-FP server plugin at the SAMI's GUI.

    Parameters
    ----------
    command (string) : a command to be sent via TCP/IP.

    Returns
    -------
    message (string) : the response from the plugin.
    """

    HOST = "soarhrc.ctio.noao.edu"
    PORT = 8888

    s = None
    for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, sock_type, proto, cannon_name, sa = res
        try:
            s = socket.socket(af, sock_type, proto)
        except socket.error as msg:
            s = None
            continue
        try:
            s.connect(sa)
        except socket.error as msg:
            s.close()
            s = None
            continue
        break
    if s is None:
        print('could not open socket')
        sys.exit(1)
    s.sendall(command)
    data = s.recv(1024)
    s.close()
    print('Received', repr(data))


if __name__ == "__main__":

    send_command('dhe set image.type object')
    send_command('dhe set image.title Ne-Lamp')
    send_command('dhe set image.comment My Comment')