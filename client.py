import socket
import threading
import time


# Listening function ran in a separate thread invoked on line 85
def listenToServer():
    # Continually listen
    while True:
        # Receive data from Server
        readData = str(socketInstance.recv(1024), encoding="utf8")
        # Watch out for Server dying
        if readData == "/serverQuit":
            print("Server Closing")
            print("Enter '/exit' to safely close client")
            break
        # Normally just print whatever the Server sends
        else:
            print(readData)


# Print the help text. Instruction on how to use Client
def helpText():
    print(
        "Type any message and hit enter to send to all user!\n"
        "/help -> Display this message\n"
        "/listusers -> List all activate users\n"
        "/message <USERNAME> <MESSAGE> -> Send a MESSAGE to only USERNAME e.g. `/message ted Hello there`\n"
        "/exit -> Safely close this client"
    )


#
# Entry point for Client
#

# Init a IPv4 TCP socket (overwritten later)
socketInstance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Trap loop for collecting Server Address, Server Port, and Client Username
while True:
    # Get Server Address
    ipAddr = input("Server Address? ")

    # Get Server Port
    portNum = 0
    while True:
        portNum = input("Port? ")
        try:
            portNum = int(portNum)
            break
        except ValueError:
            print("Port needs to be an integer")

    # Get Client Username
    while True:
        userName = input("Username? ").strip()
        if userName == "":
            print("Username can not be blank")
        else:
            break

    # Test connection with given input
    # Note this socket is used for ALL communication with Server
    try:
        # Actually test connection
        socketInstance = socket.create_connection((ipAddr, portNum))
        # Test if Username is unique (required for direct message functionality)
        socketInstance.sendall(bytes("/username" + " " + userName, encoding="utf8"))
        readData = str(socketInstance.recv(1024), encoding="utf8")
        if readData == "/taken":
            print("Username is taken, pick another")
            continue
        break
    except Exception as e:
        print("Failed to connect: ", e)
# Leave input trap loop

#
# Start thread to listen for all messages from Server
# See line 6 for the sole function the thread will be executing
#
listenThread = threading.Thread(target=listenToServer)
listenThread.daemon = True  # Mark this listening thread as a daemon as it be inconsequentially killed
listenThread.start()

# Print help text at launch so user can grok what to do
helpText()

# Trap loop for all regular input
while True:
    # Init inputText for use in the later if block
    inputText = ""
    try:
        # Always sleep for the tiniest amount before asking for input such that messages are rendered first
        time.sleep(.1)
        inputText = input(">>> ").strip()
        # Handle "/exit" here as it is most convenient and it has the same behavior as the exception handler
        if inputText == "/exit":
            raise KeyboardInterrupt

    # Clean up on exit
    except KeyboardInterrupt:
        print("Exiting...")
        # Notify Server that Client is leaving to clean up (such as removing from active user list)
        socketInstance.sendall(bytes("/exit" + " " + userName, encoding="utf8"))
        socketInstance.close()
        break

    # Parse input for any commands
    if inputText != "" and inputText[0] == "/":
        # Forward /listusers command to Server
        if inputText == "/listusers":
            socketInstance.sendall(bytes(inputText, encoding="utf8"))
        # Forward /message command to Server
        elif inputText.startswith("/message"):
            inputList = inputText.split(" ")
            if len(inputList) < 3:
                print("/message <USERNAME> <MESSAGE> -> Send a MESSAGE to USERNAME e.g. `/message ted Hello there`")
            socketInstance.sendall(bytes(inputText, encoding="utf8"))
        # If the command is not recognized or /help, print the help text
        else:
            if inputText != "/help":
                print("Unrecognized Command")
            helpText()
    # If not a command, forward input to Server to be sent to all users
    else:
        socketInstance.sendall(bytes(inputText, 'ascii'))
