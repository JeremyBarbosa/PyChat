import socket
import threading
import time

socketInstance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def read():
    is_active = True
    while is_active:
        readData = str(socketInstance.recv(1024), encoding="utf8")
        if readData == "/serverQuit":
            print("Server Closing")
            print("Enter '/exit' to safely close client")
            break
        else:
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
    userName = input("Username? ").strip()
    if userName == "":
        print("Username can not be blank")
        continue
    # Create a socket with TCP
    try:
        socketInstance = socket.create_connection((ipAddr, portNum))
        socketInstance.sendall(bytes("/username" + " " + userName, encoding="utf8"))
        readData = str(socketInstance.recv(1024), encoding="utf8")
        if readData == "/taken":
            print("Username is taken, pick another")
            continue
        break
    except Exception as e:
        print("Failed to connect: ", e)

listenThread = threading.Thread(target=read)
listenThread.daemon = True
listenThread.start()
while True:
    inputText = ""
    try:
        time.sleep(.1)
        inputText = input(">>> ").strip()
    except KeyboardInterrupt:
        print("Exiting...")
        socketInstance.sendall(bytes("/exit"+" "+userName, encoding="utf8"))
        socketInstance.close()
        break
    if inputText != "" and inputText[0] == "/":
        if inputText == "/exit":
            print("Exiting...")
            socketInstance.sendall(bytes("/exit"+" "+userName, encoding="utf8"))
            socketInstance.close()
            break
        elif inputText == "/listusers":
            socketInstance.sendall(bytes(inputText, encoding="utf8"))
        elif inputText.startswith("/message"):
            inputList = inputText.split(" ")
            if len(inputList) < 3:
                print("/message <USERNAME> <MESSAGE> -> Send a MESSAGE to USERNAME e.g. `/message ted Hello there`")
            socketInstance.sendall(bytes(inputText, encoding="utf8"))
        else:
            if inputText != "/help":
                print("Unrecognized Command")
            print(
                "/help -> Display this message\n"
                "/listusers -> List all activate users\n"
                "/message <USERNAME> <MESSAGE> -> Send a MESSAGE to USERNAME e.g. `/message ted Hello there`\n"
                "/exit -> Safely close this client"
            )
    else:
        socketInstance.sendall(bytes(inputText, 'ascii'))
