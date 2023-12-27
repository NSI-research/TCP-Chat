import threading
import socket

host = '0.0.0.0'
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))

server.listen()

clients = []
nicknames = []
addresss = []

def broadcast(message):
    var = message.decode('utf-8')
    print(var)

    if "/on" in var:
        message = "\n" + nicknames[0]
        for i in range(1, len(nicknames)):
            message += " ; " + nicknames[i]
        message = message.encode('utf-8')
        print(message.decode('utf-8'))
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            msg = message = client.recv(1024)
            if msg.decode('utf-8').startswith("KICK"):
                name_to_kick = msg.decode('utf-8')[5:]
                kick_user(name_to_kick)
            elif msg.decode('utf-8').startswith("BAN"):
                name_to_ban = msg.decode('utf-8')[4:]
                kick_user(name_to_ban)
                index = nicknames.index(name_to_ban)

                with open('ban.txt', 'a') as f:
                    f.write(f"{addresss[index]}\n")

                print(f"{name_to_ban} as {addresss[index]} was banned.")

            elif msg.decode('utf-8').startswith("LOOK"):
                name_to_look = msg.decode('utf-8')[5:]
                broadcast(addresss[nicknames.index(name_to_look)])
            else:
                broadcast(message)
        except:
            try:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(f"{nickname} has left.".encode('utf-8'))
                nicknames.remove(nickname)
                addresss.pop(index)
            except:
                pass
            break

def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send("NICK".encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')

        with open("ban.txt", "r") as f:
            bans = f.readlines()

        if address[0] + "\n" in bans:
            client.send('BAN'.encode('utf-8'))
            client.close()
            continue


        if nickname == 'admin':
            client.send('PASS'.encode('utf-8'))
            password = client.recv(1024).decode('utf-8')

            if password != "admin123":
                client.send('REFUSE'.encode('utf-8'))
                client.close()
                continue
        
        addresss.append(address)
        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname of client is {nickname}")
        broadcast(f"{nickname} joined.".encode('utf-8'))
        client.send("Connected.".encode('utf-8'))
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

def kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send("You were kick by an admin".encode('utf-8'))
        client_to_kick.close()
        nicknames.remove(name)
        addresss.pop(name_index)
        broadcast(f"{name} was kicked by an admin.".encode('utf-8'))

print("Server is listening...")
receive()


