import time
from typing import TextIO, Optional
from queue import Queue
from threading import Thread
import socket
import json

plotjuggler_udp = ("127.0.0.1", 9870)


class Logger(Thread):

    def __init__(self, filename):
        super().__init__()
        self.fic = open(filename, 'w')     # type: TextIO
        self.queue = Queue()
        self.stop_requested = False
        self.start_time = time.time()
        self.soplot = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def stop(self) -> None:
        self.stop_requested = True
        self.join()
        self.fic.close()

    def log_dict(self, dst, d: dict):
        t = time.time() - self.start_time
        self.queue.put((t, dst, d))

    def run(self):
        while not self.stop_requested:
            if not self.queue.empty():
                t, dst, d = self.queue.get()
                src = next(iter(d))
                d_msg = d[src]  # type: dict
                msg_name = next(iter(d_msg))
                d_values = d_msg[msg_name]
                values = " ".join([f"{val}" for val in d_values.values()])
                msg_txt = f"{msg_name} {values}"
                j = json.dumps(d)
                self.soplot.sendto(j.encode(), plotjuggler_udp)
                txt = f"{t} {src} {dst} {msg_txt}\n"
                self.fic.write(txt)
            time.sleep(0.001)
