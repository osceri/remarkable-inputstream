"""
This script is used to forward the touch screen events from the reMarkable to the host computer.

Prerequisites:
1. The reMarkable and the host computer are connected to the same network.
2. The reMarkable is connected to the host computer via USB.
3. You have uploaded an authorized ssh key to the reMarkable.
4. You have either xdotool or another mouse-interaction tool installed on the host computer.
"""
import socket
import struct
import subprocess
import os
from threading import Thread
from time import time, sleep
from itertools import count
from typing import Iterable
from user_select import UserSelect, BoundingBox
from mouse_interacter import MouseInteracter, get_mouse_interacter


class State:
    """
    A class to manage the state of the touch screen.
    """

    def __init__(self):
        self.x_rm = 0
        self.y_rm = 0
        self.touch = False
        self.press = False

    def unpack(self, data: bytes):
        event_type, event_code, value = struct.unpack("H H I", data[8:16])

        if event_type == 3:
            if event_code == 0:
                self.x_rm = value
            elif event_code == 1:
                self.y_rm = value
            elif event_code == 24:
                self.touch = (value / 4096) > 0.25
                self.press = (value / 4096) > 0.75


class Interval:
    """
    A class to manage time intervals.
    """

    def __init__(self, interval_length_ms: float):
        self.interval_length_ms = interval_length_ms
        self.interval_start = time()

    def has_elapsed(self):
        time_now = time()
        if (time_now - self.interval_start) < (self.interval_length_ms / 1000):
            return False
        self.interval_start = time_now
        return True

def rm_T_wm(
    x_rm: int, y_rm: int, rm: BoundingBox, wm: BoundingBox, flip: bool
) -> tuple[int, int]:
    """
    Convert between the remote and window coordinates.
    """
    if flip:
        x_wm = int(
            wm.x_min + (y_rm - rm.y_min) * (wm.x_max - wm.x_min) / (rm.y_max - rm.y_min)
        )
        y_wm = int(
            wm.y_min + (rm.x_max - x_rm) * (wm.y_max - wm.y_min) / (rm.x_max - rm.x_min)
        )
    else:
        x_wm = int(
            wm.x_min + (x_rm - rm.x_min) * (wm.x_max - wm.x_min) / (rm.x_max - rm.x_min)
        )
        y_wm = int(
            wm.y_min + (y_rm - rm.y_min) * (wm.y_max - wm.y_min) / (rm.y_max - rm.y_min)
        )
    return x_wm, y_wm


def remarkable_datastream(host: str, remote: str, port: str | int) -> None:
    """
    Run the command to forward the touch screen events to the host.
    """
    sleep(0.5)
    command = f"ssh root@{remote} 'cat /dev/input/touchscreen0 | nc {host} {port}'"
    subprocess.Popen(command, shell=True)


def connect_to_port(
    preconn: socket.socket, host: str, remote: str, port_iterator: Iterable[int]
) -> socket.socket:
    """
    Connect to the port and return the connection.
    """
    for port in port_iterator:
        try:
            preconn.bind(("0.0.0.0", port))
            break
        except OSError:
            pass

    thread = Thread(target=remarkable_datastream, args=(host, remote, port))
    thread.start()

    preconn.listen(1)
    conn, addr = preconn.accept()
    print(f"Connected by {addr}")
    return conn

def app(host: str, remote: str, portrait_mode: bool = False):
    """
    The main application function.
    """
    port_iter = count(12345)  # start from 12345 and increment by 1

    rm = BoundingBox(x_min=0, y_min=0, x_max=20966, y_max=15725)
    wm: BoundingBox = UserSelect()

    mouse_interacter: MouseInteracter = get_mouse_interacter()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as preconn:
        state = State()
        conn = connect_to_port(preconn, host, remote, port_iter)

        interval = Interval(interval_length_ms=16)

        while True:
            data = conn.recv(16)  # Read 16-byte event packets
            if not data:
                break

            state.unpack(data)

            if not interval.has_elapsed():
                continue

            if state.touch:
                x_wm, y_wm = rm_T_wm(
                    state.x_rm, state.y_rm, rm=rm, wm=wm, flip=portrait_mode
                )
                mouse_interacter.move(x_wm, y_wm)
            if state.press:
                mouse_interacter.mouse_down()
            else:
                mouse_interacter.mouse_up()


if __name__ == "__main__":
    app(
        host="10.11.99.8", 
        remote="10.11.99.1", 
        portrait_mode=True
    )
