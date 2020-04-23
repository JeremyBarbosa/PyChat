A Python Chat Application for Professor Tseng of Boston College

A Python Adaption of https://courses.engr.illinois.edu/cs241/sp2016/chatroom.html

Features:
- Support one-to-one communication -> See server.py:91
- Support one-to-all communication -> See server.py:99
- Support querying a list of active clients:-> See server.py:67

Guide for Running:
- Launch server.py (e.g. `python server.py`)
  - Input desired port when prompted
- Launch arbitrary amounts of client.py (e.g. `python client.py`)
  - Input desired server address (localhost)
  - Input desired server port
  - Input desired username
  - A prompt will be displyed for running a variety of commands, a copy is below:
        
        `Type any message and hit enter to send to all users!
        /help -> Display this message
        /listusers -> List all activate users
        /message <USERNAME> <MESSAGE> -> Send a MESSAGE to only USERNAME e.g. "/message ted Hello there"
        /exit -> Safely close this client`
     
 
 See comments within code for general flow of data
 
 High-Level Overview:
 - Client makes first contact with Server, sending username to be registered in directory
 - Server accepts connection, moving Client to own thread, then caches Client's username and socket used, finally waits for future messages
 - Some time later, Client sends message
 - Server thread parses for special commands such as those described above, executing that necessary behavior
    - The /listusers command responds with all registered usernames
    - The /message command checks the directory for the socket of that username, and then writes to only that socket
    - The /exit command removes the current Client's username from the directory
 - If Server does not find special command, forward message to all other Clients
 -
