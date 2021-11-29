
from PyQt5.QtNetwork import QUdpSocket
from robot import *
from abstract_radio import AbstractRadio
from logger import Logger
from transport import Transport


class RadioUDP(QObject, AbstractRadio):
    """
    Radio protobuf over UDP
    """

    def __init__(self, addr, port, logger: Logger, rid="dafi", name="Ana", parent=None):
        super().__init__(logger=logger, parent=parent)
        self.addr = addr
        self.port = port
        self.transport = Transport()
        self.socket = QUdpSocket(self)
        # self.socket.bind(addr, port)
        self.rid = rid
        self.add_rid(rid)
        self.name = name

    def start(self):
        self.socket.readyRead.connect(self.read_datagrams)

    def stop(self):
        self.socket.close()

    def read_datagrams(self):
        while self.socket.hasPendingDatagrams():
            datagram = self.socket.receiveDatagram()
            data = datagram.data().data()
            msg = self.transport.put(data)
            if msg is not None:
                # print(msg, data)
                self.handle_umsg(msg)
                d = self.msg_to_dict(self.rid, msg)
                self.log_dict(self.name, d)

    def handle_umsg(self, msg):
        self.emit_msg(self.rid, msg)

    @staticmethod
    def msg_to_dict(src, msg):
        msg_name = msg.WhichOneof('inner')
        inner = getattr(msg, msg_name)
        d_msg = {msg_name: {}}
        for f in inner.DESCRIPTOR.fields:
            field_name = f.name
            d_msg[msg_name][field_name] = getattr(inner, field_name)
        d = {src: d_msg}
        return d

    def send_msg(self, rid, msg: m.Message):
        data = self.transport.serialize(msg)
        self.socket.writeDatagram(data, self.addr, self.port)
