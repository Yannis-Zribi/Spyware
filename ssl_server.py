import socket
import ssl

# Créer un socket TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Liaison du socket à une adresse et un port
server_socket.bind(('localhost', 8443))

# Mettre le socket en mode écoute
server_socket.listen(1)

print("Attente de la connexion...")

# Accepter une connexion
client_socket, addr = server_socket.accept()

# Créer un contexte SSL avec un certificat auto-signé
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="./ssl2/certificate.pem", keyfile="./ssl2/private.pem")

# Wrapping du socket avec SSL
ssl_socket = context.wrap_socket(client_socket, server_side=True)

# Lire des données du client
data = ssl_socket.recv(1024)
print(f"Reçu: {data.decode('utf-8')}")

# Fermer la connexion SSL
ssl_socket.close()
server_socket.close()
