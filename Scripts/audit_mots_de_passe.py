import mysql.connector
from werkzeug.security import generate_password_hash

db = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="",  # mets "root" si besoin
    database="magasin_informatique"
)

cursor = db.cursor(dictionary=True)

cursor.execute("SELECT id, nom, prenom, email, password FROM clients")
clients = cursor.fetchall()

print("=== AUDIT DES MOTS DE PASSE CLIENTS ===")

for client in clients:
    mdp = client["password"]

    # Affichage masqué
    mdp_masque = "*" * len(mdp)

    print("--------------------------------")
    print("ID :", client["id"])
    print("Nom :", client["nom"])
    print("Prénom :", client.get("prenom"))
    print("Email :", client["email"])
    print("Mot de passe stocké :", mdp_masque)

    # Vérifie si le mot de passe semble haché
    if mdp.startswith("scrypt:") or mdp.startswith("pbkdf2:"):
        print("État : mot de passe déjà haché")
    else:
        print("État : ATTENTION mot de passe en clair")

cursor.close()
db.close()