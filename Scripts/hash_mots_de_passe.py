# ==========================================================
# TP CYBERSÉCURITÉ
# Script : hachage des mots de passe clients
# Objectif : ne plus stocker les mots de passe en clair
# ==========================================================

import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

# Connexion à la base MySQL
db = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="",   # adapter si vous avez un mot de passe MySQL
    database="magasin_informatique"
)

cursor = db.cursor(dictionary=True)

# Liste des clients avec mot de passe en clair au départ
clients = [
    ("Dupont", "Marie", "marie@gmail.com", "1234", "Paris"),
    ("Martin", "Paul", "paul@gmail.com", "1234", "Evry"),
    ("Benali", "Sofia", "sofia@gmail.com", "1234", "Corbeil"),
    ("Durand", "Lucas", "lucas@gmail.com", "1234", "Massy"),
    ("Bernard", "Emma", "emma@gmail.com", "1234", "Melun")
]

# Supprimer les anciens clients pour éviter les doublons
cursor.execute("DELETE FROM clients")

# Réinsérer les clients avec mot de passe haché
for nom, prenom, email, password, adresse in clients:
    password_hash = generate_password_hash(password)

    cursor.execute("""
        INSERT INTO clients (nom, prenom, email, password, adresse)
        VALUES (%s, %s, %s, %s, %s)
    """, (nom, prenom, email, password_hash, adresse))

db.commit()

print("Les mots de passe ont été hachés et enregistrés dans MySQL.")

# Test de vérification
email_test = "marie@gmail.com"
mot_de_passe_saisi = "1234"

cursor.execute("SELECT * FROM clients WHERE email=%s", (email_test,))
client = cursor.fetchone()

if client and check_password_hash(client["password"], mot_de_passe_saisi):
    print("Test connexion : réussie")
else:
    print("Test connexion : échouée")

cursor.close()
db.close()