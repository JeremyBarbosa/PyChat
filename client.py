import socket
import threading

socketLock = threading.Lock()

def read():
    readData = ""
    with socketLock:
        readData = socketInstance.recv(1024)
    # Consider making a printing lock so that you can easily type without new messages crowding you
    print(readData)


while True:
    # Get Server Address
    ipAddr = input("Server Address? ")
    portNum = 0
    while True:
        portNum = input("Port? ")
        try:
            portNum = int(portNum)
            break
        except ValueError:
            print("Port needs to be an integer")
    userName = input("Username? ")
    # Create a socket with TCP
    # try:
    socketInstance = socket.create_connection(("localhost", 1234))
    socketInstance.sendall(bytes("/username"))
        # break
    # except Exception as e:
    #     print("Failed to connect", e)

listenThread = threading.Thread(target=read())
listenThread.daemon = True
listenThread.start()
while True:
    inputText = input("Send Message: ").strip()
    if inputText[0] == "/":
        if inputText == "/exit":
            # quit
            pass
        elif inputText == "/listusers":
            socketInstance.send(inputText)
        elif inputText.startswith("/message"):
            inputList = inputText.split(" ")
            if len(inputList) < 3:
                print("bad")
            socketInstance.send(inputText)
        else:
            if inputText != "/help":
                print("Unrecognized Command\n")
            print(
                "/help -> Display this message\n"
                "/listusers -> List all activate users\n"
                "/message <USERNAME> <MESSAGE> -> Send a MESSAGE to USERNAME e.g. `/message ted Hello there`\n"
            )
    else:
        socketInstance.send(inputText)