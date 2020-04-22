import threading
import socket
import socketserver

userDict = {}
dictLock = threading.Lock()


def addUser(userName, address, port):
    with dictLock:
        userDict[userName] = (address, port)


def removeUser(userName):
    with dictLock:
        del userDict[userName]


def userExists(userName):
    with dictLock:
        if userName in userDict:
            return True
        else:
            return False


def getUser(userName):
    with dictLock:
        return userDict[userName]


def getAllUsers():
    with dictLock:
        return userDict


def getAllAddresses():
    with dictLock:
        return userDict.values()


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = str(self.request.recv(1024))
        if data[0] == "/":
            if data == "/listusers":
                self.request.sendall(bytes(getAllUsers()))
            elif data.startswith("/username"):
                # Fix only unique usernames
                newUserName = data.split(" ")[1]
                (address, port) = self.client_address
                addUser(newUserName, address, port)
            elif data.startswith("/exit"):
                leavingUserName = data.split(" ")[1]
                if userExists(leavingUserName):
                    removeUser(leavingUserName)
            elif data.startswith("/message"):
                inputList = data.split(" ")
                if userExists(inputList[1]):
                    directMessageSocket = socket.create_connection(getUser(inputList[1]))
                    directMessageSocket.sendall(bytes(" ".join(inputList[2:])))
            else:
                self.request.sendall(bytes("Server does not recognize this command"))
        else:
            for address in getAllAddresses():
                allMessageSocket = socket.create_connection(address)
                allMessageSocket.sendall(bytes(data))


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def setupServer():
    while True:
        portNum = input("Port? ")
        try:
            portNum = int(portNum)
        except ValueError:
            print("Port needs to be an integer")
            continue
        try:
            return ThreadedTCPServer(("localhost", portNum), ThreadedTCPRequestHandler)
        except:
            print("Failed to create server, port is likely bad or in use")


server = setupServer()
print(server)
with server:
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = False
    server_thread.start()
print("Server created successfully")
while True:
    try:
        inputText = input("Type `exit` to quit: ").strip()
        if inputText == "exit":
            raise KeyboardInterrupt
    except KeyboardInterrupt:
        print("Shutting down server...")
        for address in getAllAddresses():
            directMessageSocket = socket.create_connection(address)
            directMessageSocket.sendall(bytes("Server is shutting down! Bye!"))
        server.shutdown()
        break
    else:
        print("Sorry there is no support for other commands in the server")
