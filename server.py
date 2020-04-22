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
        return userDict


def getAllUserSockets():
    with dictLock:
        return userDict.values()


def handleConnection(connectionSocket):
    is_active = True
    while is_active:
        data = str(connectionSocket.recv(1024), encoding="utf8")
        print(data)
        if data[0] == "/":
            if data == "/listusers":
                connectionSocket.sendall(bytes(str(getAllUsers()), encoding="utf8"))
            elif data.startswith("/username"):
                # Fix only unique usernames
                newUserName = data.split(" ")[1]
                addUser(newUserName, connectionSocket)
                connectionSocket.sendall(bytes("Registered", encoding="utf8"))
                print("New User Registered")
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
                    directMessageSocket.sendall(bytes(" ".join(inputList[2:]), encoding="utf8"))
            else:
                connectionSocket.sendall(bytes("Server does not recognize this command"))
        else:
            for userSocket in getAllUserSockets():
                userSocket.sendall(bytes(data, encoding="utf8"))


soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    portNum = input("Port? ")
    try:
        portNum = int(portNum)
        soc.bind(("localhost", portNum))
        soc.listen(5)  # queue up to 6 requests
        break
    except ValueError:
        print("Port needs to be an integer")
    except:
        print("Failed to create server, port is likely bad or in use")

while True:
    print("Listening for users")
    connection, address = soc.accept()
    ip, port = str(address[0]), str(address[1])
    print("Connected with " + ip + ":" + port)
    try:
        threading.Thread(target=handleConnection, args=(connection,)).start()
    except:
        print("Thread did not start.")

# while True:
#     try:
#         inputText = input("Type `exit` to quit: ").strip()
#         if inputText == "exit":
#             raise KeyboardInterrupt
#     except KeyboardInterrupt:
#         print("Shutting down server...")
#         for address in getAllAddresses():
#             directMessageSocket = socket.create_connection(address)
#             directMessageSocket.sendall(bytes("Server is shutting down! Bye!"))
#         soc.close()
#         break
#     else:
#         print("Sorry there is no support for other commands in the server")
