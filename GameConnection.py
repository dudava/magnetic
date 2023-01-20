import threading
import time

DISCONNECT_TIMEOUT = 1

from settings import PACKAGE_SIZE


class GameConnectionPull:
    def __init__(self):
        self.ids = {_: False for _ in range(10)}
    
    def refactJSONstring(self, JSONstring):
        return JSONstring.replace("None", "null")

    def prepareData(self):
        data = []
        for _ in self.ids:
            if self.ids[_] != False:
                data.append(f'"{_}": {self.ids[_].data}')
        JSONstring = "{" + ", ".join(data) + "}"
        return self.refactJSONstring(JSONstring)


connections = GameConnectionPull()


class GameConnection(threading.Thread):
    def __init__(self, client_socket, addressInfo):
        super().__init__(target=self)
        global connections
        self.client_socket = client_socket
        self.addressInfo = addressInfo
        self.id = self.setId()
        self.data = None

    def run(self):
        print(self.getAddressInfo())
        self.runPackageCycle()

    def getAddressInfo(self):
        return self.addressInfo
        
    def runPackageCycle(self):
        self.client_socket.send(f"{self.id}".encode())
        while True:
            try:
                package = self.client_socket.recv(PACKAGE_SIZE)
                if package == b"":
                    break
                self.data = package.decode()
                self.client_socket.sendall(connections.prepareData().encode())
            except ConnectionResetError:
                break
            except BrokenPipeError:
                break
            except KeyboardInterrupt:
                break
        self.close()

    def setId(self):
        global connections
        for _ in connections.ids:
            if connections.ids[_] == False:
                connections.ids[_] = self
                return _

    def close(self):
        global connections
        self.client_socket.close()
        self.data = f'"closed"'
        time.sleep(DISCONNECT_TIMEOUT)
        connections.ids[self.id] = False