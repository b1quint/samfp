#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import socket
import sys

HOST = "soarhrc.ctio.noao.edu"
PORT = 8888


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

    global HOST
    global PORT

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
    message = s.recv(1024)
    s.close()

    return message


def set_comment(comment):
    """
    Add a comment to the header. This will be stored in the keyword
     NOTES.

    Parameters
    ----------
    target_name (string) : any comment to be added to the FITS header.

    Returns
    -------
    message (string) : DONE if successful.
    """
    message = send_command('dhe set image.comment {:s}'.format(comment))
    return message


def set_image_type(image_type):
    """
    Set the image type that will be acquired. SAMI accepts several
    arguments but since I do not know then, here I will fix this to
    "object".

    Parameters
    ----------
    image_type (string) : the image type [DARK|DFLAT|OBJECT|SFLAT|ZERO]

    Returns
    -------
    message (string) : DONE if successful.
    """
    message = send_command('dhe set image.comment {:s}'.format(image_type))
    return message


def set_path(path):
    """
    Set the path to where the images will be saved in SAMI's computer.

    Parameters
    ----------
    path (string) : the path

    Returns
    -------
    message (string) : DONE if successful.
    """
    # TODO - Check if remote path exists
    message = send_command('dhe set image.dir {:s}'.format(path))
    return message


def set_target_name(target_name):
    """
    Set the target name on SAMI's GUI. If the target name has any space it
    will be replaced by an underscore (_). This information will be stored
    in the FITS header within the key OBJECT.

    Parameters
    ----------
    target_name (string) : the target name

    Returns
    -------
    message (string) : DONE if successful.
    """
    target_name = target_name.replace(" ", "_")
    message = send_command('dhe set image.title {:s}'.format(target_name))

    return message


if __name__ == "__main__":

    msg = set_path("xxx")
    print(msg)

    msg = set_image_type("object")
    print(msg)

    msg = set_target_name("Ne Lamp")
    print(msg)

    msg = set_comment("Cube for calibration")
    print(msg)

