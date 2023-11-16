import socket
import ssl

# Créer un socket TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Établir une connexion SSL avec un certificat auto-signé
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.load_verify_locations(cafile="./ssl2/certificate.pem")

# Connexion au serveur SSL
ssl_socket = context.wrap_socket(client_socket, server_hostname='localhost')

# Connexion au serveur
ssl_socket.connect(('localhost', 8443))

# Envoyer des données au serveur
ssl_socket.sendall("Hello, serveur SSL avec certificat auto-signé!".encode('utf-8'))

# Fermer la connexion SSL
ssl_socket.close()
