import threading
import socket

userDict = {}
dictLock = threading.Lock()


def addUser(userName, userSocket):
    with dictLock:
        userDict[userName] = userSocket


def removeUser(userName):
    with dictLock:
        del userDict[userName]


def userExists(userName):
    with dictLock:
        if userName in userDict:
            return True
        else:
            return False


def getUserSocket(userName):
    with dictLock:
        return userDict[userName]


def getAllUsers():
    with dictLock:
        return userDict.keys()


def getAllUserSockets():
    with dictLock:
        return userDict.values()


def handleListen():
    while True:
        # print("Listening for users\n")
        connection, address = listenSocket.accept()
        ip, port = str(address[0]), str(address[1])
        # print("Connected with " + ip + ":" + port)
        try:
            threading.Thread(target=handleConnection, args=(connection,)).start()
        except:
            print("Thread did not start.")


def handleConnection(connectionSocket):
    is_active = True
    currentUser = ""
    while is_active:
        data = str(connectionSocket.recv(1024), encoding="utf8")
        if data == "":
            if userExists(currentUser):
                removeUser(currentUser)
            connectionSocket.close()
            is_active = False
            break
        if data[0] == "/":
            if data == "/listusers":
                connectionSocket.sendall(bytes(str("\n".join(getAllUsers())), encoding="utf8"))
            elif data.startswith("/username"):
                # Fix only unique usernames
                newUserName = data.split(" ")[1]
                if userExists(newUserName):
                    connectionSocket.sendall(bytes("/taken", encoding="utf8"))
                    continue
                addUser(newUserName, connectionSocket)
                currentUser = newUserName
                connectionSocket.sendall(bytes("/registered", encoding="utf8"))
            elif data.startswith("/exit"):
                leavingUserName = data.split(" ")[1]
                if userExists(leavingUserName):
                    removeUser(leavingUserName)
                connectionSocket.close()
                is_active = False
            elif data.startswith("/message"):
                inputList = data.split(" ")
                if userExists(inputList[1]):
                    directMessageSocket = getUserSocket(inputList[1])
                    directMessageSocket.sendall(bytes(currentUser + " (direct message): " + " ".join(inputList[2:]), encoding="utf8"))
            else:
                connectionSocket.sendall(bytes("Server does not recognize this command"))
        else:
            for userSocket in getAllUserSockets():
                userSocket.sendall(bytes(currentUser + ": " + data, encoding="utf8"))


listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    portNum = input("Port? ")
    try:
        portNum = int(portNum)
        listenSocket.bind(("localhost", portNum))
        listenSocket.listen(5)  # queue up to 6 requests
        break
    except ValueError:
        print("Port needs to be an integer")
    except:
        print("Failed to create server, port is likely bad or in use")

listenThread = threading.Thread(target=handleListen)
listenThread.daemon = True
listenThread.start()

while True:
    try:
        inputText = input("Type `exit` to quit: ").strip()
        if inputText == "exit":
            raise KeyboardInterrupt
    except KeyboardInterrupt:
        print("Shutting down server...")
        listenSocket.close()
        for userSocket in getAllUserSockets():
            userSocket.sendall(bytes("/serverQuit", encoding="utf8"))
        break
    else:
        print("Sorry there is no support for other commands in the server")

