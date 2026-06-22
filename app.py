from flask import Flask, render_template, request, redirect
import mysql.connector
from datetime import date

app = Flask(__name__)

# Connexion BDD
import mysql.connector

def get_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="",
        database="magasin_informatique"
    )
# ACCUEIL
@app.route("/")
def accueil():
    return render_template("accueil.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        db = get_db()         
        cursor = db.cursor(dictionary=True, buffered=True)

        # ADMIN
        if email == "admin" and password == "1234":
            return redirect("/admin")

        # CLIENT
        cursor.execute(
            "SELECT * FROM clients WHERE email=%s AND password=%s",
            (email, password)
        )
        client = cursor.fetchone()

        if client:
            return redirect(f"/client/{client['id']}")
        else:
            return "Erreur login"

    return render_template("login.html")


# PAGE CLIENT
@app.route("/client/<int:id_client>")
def client(id_client):
    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)

    cursor.execute("""
        SELECT produits.nom, produits.prix, details_commandes.quantite
        FROM commandes
        JOIN details_commandes ON details_commandes.id_commande = commandes.id
        JOIN produits ON produits.id = details_commandes.id_produit
        WHERE commandes.id_client = %s
    """, (id_client,))

    produits = cursor.fetchall()

    return render_template("client.html", produits=produits, id_client=id_client)


# PAGE ADMIN
@app.route("/admin")
def admin():
    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)

    cursor.execute("SELECT * FROM produits")
    produits = cursor.fetchall()

    cursor.execute("SELECT * FROM clients")
    clients = cursor.fetchall()

    cursor.execute("""
        SELECT commandes.id, commandes.id_client, commandes.date_commande,
               commandes.total, commandes.statut
        FROM commandes
    """)
    commandes = cursor.fetchall()

    return render_template(
        "admin.html",
        produits=produits,
        clients=clients,
        commandes=commandes
    )

@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    if request.method == "POST":
        nom = request.form["nom"]
        prenom = request.form["prenom"]
        email = request.form["email"]
        password = request.form["password"]
        adresse = request.form["adresse"]
        

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO clients (nom, prenom, email, password, adresse)
            VALUES (%s, %s, %s, %s, %s)
        """, (nom, prenom, email, password, adresse))

        db.commit()
        cursor.close()
        db.close()

        return redirect("/login")

    return render_template("inscription.html")
# PAGE COMMANDER
@app.route("/client/<int:id_client>/commander", methods=["GET", "POST"])
def commander(id_client):
    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)

    if request.method == "POST":
        id_produit = int(request.form["id_produit"])
        quantite = int(request.form["quantite"])

        # Récupérer le produit
        cursor.execute("SELECT * FROM produits WHERE id=%s", (id_produit,))
        produit = cursor.fetchone()

        if not produit:
            return "Produit introuvable"

        if produit["stock"] < quantite:
            return "Stock insuffisant"

        total = produit["prix"] * quantite

        # Créer la commande
        cursor.execute("""
            INSERT INTO commandes (id_client, date_commande, total, statut)
            VALUES (%s, %s, %s, %s)
        """, (id_client, date.today(), total, "En attente"))

        id_commande = cursor.lastrowid

        # Ajouter le détail
        cursor.execute("""
            INSERT INTO details_commandes
            (id_commande, id_produit, quantite, prix_unitaire)
            VALUES (%s, %s, %s, %s)
        """, (id_commande, id_produit, quantite, produit["prix"]))

        # Diminuer le stock
        cursor.execute("""
            UPDATE produits
            SET stock = stock - %s
            WHERE id = %s
        """, (quantite, id_produit))

        db.commit()

        return redirect(f"/client/{id_client}")

    cursor.execute("SELECT id, nom, prix FROM produits")
    produits = cursor.fetchall()

    return render_template(
        "commander.html",
        produits=produits,
        id_client=id_client
    )


if __name__ == "__main__":
    app.run(debug=True)