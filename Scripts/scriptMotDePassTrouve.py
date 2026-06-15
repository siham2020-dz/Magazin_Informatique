import mysql.connector

mots_de_passe_faibles = [
    "123456",
    "azerty",
    "password",
    "admin",
    "admin123",
    "test",
    "bonjour",
    "0000"
]

db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="magasin_informatique"
)

cursor = db.cursor(dictionary=True)

cursor.execute("SELECT id, nom, prenom, email, password FROM clients")
clients = cursor.fetchall()

print("=== AUDIT DES MOTS DE PASSE FAIBLES ===")

for client in clients:
    mdp = client["password"]

    print("--------------------------------")
    print("ID :", client["id"])
    print("Nom :", client["nom"])
    print("Prénom :", client["prenom"])
    print("Email :", client["email"])

    if mdp in mots_de_passe_faibles:
        print("Résultat : MOT DE PASSE FAIBLE TROUVÉ")
    else:
        print("Résultat : mot de passe non trouvé dans la liste faible")

cursor.close()
db.close()