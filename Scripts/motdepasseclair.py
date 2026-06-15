import mysql.connector

db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="magasin_informatique"
)

cursor = db.cursor(dictionary=True)

cursor.execute("SELECT id, nom, prenom, email, password FROM clients")
clients = cursor.fetchall()

print("\n=== AUDIT DES MOTS DE PASSE ===\n")

for client in clients:

    mdp = client["password"]

    if mdp.startswith("scrypt:") or mdp.startswith("pbkdf2:"):
        etat = "Mot de passe haché"
    else:
        etat = "ATTENTION : mot de passe en clair"

    print(f"ID : {client['id']}")
    print(f"Nom : {client['nom']}")
    print(f"Prénom : {client['prenom']}")
    print(f"Email : {client['email']}")
    print(f"Mot de passe stocké : {client['password']}")
    print(f"État : {etat}")
   
    print("-" * 40)

cursor.close()
db.close()