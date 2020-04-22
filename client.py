import socket
import threading

socketInstance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketLock = threading.Lock()


def read():
    print("Waiting for new messages\n")
    is_active = True
    while is_active:
        with socketLock:
            readData = str(socketInstance.recv(1024), encoding="utf8")
            print(readData)
    # Consider making a printing lock so that you can easily type without new messages crowding you


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
    try:
        socketInstance = socket.create_connection((ipAddr, portNum))
        socketInstance.sendall(bytes("/username" + " " + userName, encoding="utf8"))
        break
    except Exception as e:
        print("Failed to connect", e)

listenThread = threading.Thread(target=read)
listenThread.daemon = True
listenThread.start()
while True:
    inputText = input("Send Message: ").strip()
    if inputText[0] == "/":
        if inputText == "/exit":
            # quit
            pass
        elif inputText == "/listusers":
            socketInstance.sendall(bytes(inputText, 'ascii'))
        elif inputText.startswith("/message"):
            inputList = inputText.split(" ")
            if len(inputList) < 3:
                print("bad")
            socketInstance.sendall(bytes(inputText, 'ascii'))
        else:
            if inputText != "/help":
                print("Unrecognized Command")
            print(
                "/help -> Display this message\n"
                "/listusers -> List all activate users\n"
                "/message <USERNAME> <MESSAGE> -> Send a MESSAGE to USERNAME e.g. `/message ted Hello there`\n"
            )
    else:
        socketInstance.sendall(bytes(inputText, 'ascii'))
