import socket
import threading

nickname = input('Info à retenir :\n\t- Ne pas mettre de caractère non compris dans acsii\n\nChoose a Nickname : ')
if nickname == 'admin':
    password = input("Enter the password of admin : ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

stop_thread = False

def receive():
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
                next_message = client.recv(1024).decode('utf-8')
                if next_message == 'PASS':
                    client.send(password.encode('utf-8'))
                    if client.recv(1024).decode('utf-8') == 'REFUSE':
                        print('Connection was refused. Wrong password.')
                        stop_thread = True
                elif next_message == 'BAN':
                    print("You were banned, you cannot connect.")
                    client.close()
                    stop_thread = True
            else:
                print(message)
        except:
            print("An error occurred.")
            client.close()
            break
    
def write():
    while True:
        if stop_thread:
            break
        message = f"{nickname}: {input('')}"
        if message[len(nickname) + 2:].startswith("/"):
            if nickname == 'admin':
                command = message[8:]
                if command.startswith("kick "):
                    client.send(f"KICK {command[5:]}".encode('utf-8'))
                elif command.startswith("ban "):
                    client.send(f"BAN {command[4:]}".encode('utf-8'))
                elif command.startswith("look "):
                    client.send(f"LOOK {command[5:]}".encode('utf-8'))
            else:
                print("You're not able to do this.")
        client.send(message.encode('utf-8'))


receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()