import threading
import socket

#
# A variety of functions to manage caching Usernames and their corresponding socket
#
userDict = {}
dictLock = threading.Lock() # With each client having its own thread, be sure to lock any access to this directory

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

# End Username - Socket Dict methods

# Listening function ran in a separate thread invoked on line 132
def handleListen():
    # Continually listen
    while True:
        # Accept all connections, then pass to thread for handling
        connection, address = listenSocket.accept()
        threading.Thread(target=handleConnection, args=(connection,)).start()

# Handle connections after they have been accepted by listening thread
def handleConnection(connectionSocket):
    # Track what Username is being handled
    currentUser = ""

    # Handle all messages until connection dies
    while True:
        data = str(connectionSocket.recv(1024), encoding="utf8")
        # Handle receiving empty data. This tends to happen if the Client disconnects strangely
        if data == "":
            # Assume Client has disconnected strangely and clean up
            if userExists(currentUser):
                removeUser(currentUser)
            connectionSocket.close()
            break
        # Handle commands being forwarded to Server
        if data[0] == "/":

            # If /listusers, reply with newline seperated list of Usernames
            if data == "/listusers":
                connectionSocket.sendall(bytes(str("\n".join(getAllUsers())), encoding="utf8"))

            # If special command /username is sent, register Username. Only intended to be used when Client first connects
            elif data.startswith("/username"):
                newUserName = data.split(" ")[1]
                if userExists(newUserName):
                    # Reply that Username is taken
                    connectionSocket.sendall(bytes("/taken", encoding="utf8"))
                    continue
                addUser(newUserName, connectionSocket)
                # Cache the Username in case the connection ends unexpectedly
                currentUser = newUserName
                connectionSocket.sendall(bytes("/registered", encoding="utf8"))

            # If Client leaves with /exit, clean up
            elif data.startswith("/exit"):
                leavingUserName = data.split(" ")[1]
                if userExists(leavingUserName):
                    removeUser(leavingUserName)
                connectionSocket.close()
                break

            # If a Client wants to direct message, get the Socket used for communicating with Client with that Username
            elif data.startswith("/message"):
                inputList = data.split(" ")
                if userExists(inputList[1]):
                    directMessageSocket = getUserSocket(inputList[1])
                    directMessageSocket.sendall(bytes(currentUser + " (direct message): " + " ".join(inputList[2:]), encoding="utf8"))
            else:
                connectionSocket.sendall(bytes("Server does not recognize this command"))
        # If not a command, forward Client's message to all other Clients
        else:
            for userSocket in getAllUserSockets():
                userSocket.sendall(bytes(currentUser + ": " + data, encoding="utf8"))

#
# Entry point for Server
#

# Init a IPv4 TCP socket
listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Trap loop for collecting Server Port
while True:
    portNum = input("Port? ")
    try:
        portNum = int(portNum)
        # Bind the port to the above socket, so that all message to the port go to this socket
        listenSocket.bind(("localhost", portNum))
        # Ready socket for accepting connections (Maximum queue of 5)
        listenSocket.listen(5)
        break
    except ValueError:
        print("Port needs to be an integer")
    # Handle in case a Port was not properly released or is being used by a different service
    except:
        print("Failed to create server, port is likely bad or in use")

#
# Start thread to listen to messages from ALL clients
# See line 41 for the sole function the thread will be executing
#
listenThread = threading.Thread(target=handleListen)
listenThread.daemon = True  # Mark this listening thread as a daemon as it be inconsequentially killed
listenThread.start()

# Trap loop for getting input to properly kill server
while True:
    try:
        inputText = input("Type `/exit` to quit: ").strip()
        # Handle "/exit" here as it is most convenient and it has the same behavior as the exception handler
        if inputText == "/exit":
            raise KeyboardInterrupt
    except KeyboardInterrupt:
        print("Shutting down server...")
        # Stop listening to Clients
        listenSocket.close()
        # Tell all Clients that Server is going down
        for userSocket in getAllUserSockets():
            userSocket.sendall(bytes("/serverQuit", encoding="utf8"))
        break
    else:
        print("Sorry there is no support for other commands in the server")

