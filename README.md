# Spyware
Projet de Spyware à faire pour la matière Scripting Python 

# Etapes du projet

**Spyware** : 
- Récupération des frappes sur le client (Linux & Windows)
- Enregistrement des frappes sur le fichier caché (penser à retirer les caractère que le client supprime => si il appui sur la touche effacer, retirer le dernier caractère)
- envoie sécurisé du fichier vers le serveur
- S’arrêter et supprimer le fichier sur ordre du serveur ou au bout de 10 min


**Socket**:
- Recevoir les fichiers venant du client (avec toutes les frappes dedans)
- Ajouter les données reçues (tout rassembler dans un fichier unique par client) 
- Envoyer au client l’ordre de s'arrêter
- Gérer les arguments sur le serveur.
  - Faire la visualisation des fichiers (-r)
  - Faire l’arrêt des autres instances de serveurs (-k)
