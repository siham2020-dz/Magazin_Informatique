from flask import Flask, render_template, request, redirect
import mysql.connector
from datetime import date

app = Flask(__name__)


def get_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="",
        database="magasin_informatique"
    )


# ACCUEIL : afficher les produits
@app.route("/")
def accueil():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produits")
    produits = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("accueil.html", produits=produits)


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email == "admin" and password == "1234":
            return redirect("/admin")

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM clients WHERE email=%s AND password=%s",
            (email, password)
        )
        client = cursor.fetchone()

        cursor.close()
        db.close()

        if client:
            return redirect(f"/client/{client['id']}")
        else:
            return "Erreur login"

    return render_template("login.html")


# INSCRIPTION
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


# PAGE CLIENT
@app.route("/client/<int:id_client>")
def client(id_client):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM clients WHERE id = %s", (id_client,))
    client = cursor.fetchone()

    cursor.execute("SELECT * FROM produits")
    produits = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "client.html",
        client=client,
        produits=produits,
        id_client=id_client
    )

# ADMIN
@app.route("/admin")
def admin():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produits")
    produits = cursor.fetchall()

    cursor.execute("SELECT * FROM clients")
    clients = cursor.fetchall()

    cursor.execute("""
        SELECT id, id_client, date_commande, total, statut
        FROM commandes
    """)
    commandes = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "admin.html",
        produits=produits,
        clients=clients,
        commandes=commandes
    )


# COMMANDER DIRECTEMENT
@app.route("/client/<int:id_client>/commander", methods=["GET", "POST"])
def commander(id_client):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        id_produit = int(request.form["id_produit"])
        quantite = int(request.form["quantite"])

        cursor.execute("SELECT * FROM produits WHERE id=%s", (id_produit,))
        produit = cursor.fetchone()

        if not produit:
            return "Produit introuvable"

        if produit["stock"] < quantite:
            return "Stock insuffisant"

        total = produit["prix"] * quantite

        cursor.execute("""
            INSERT INTO commandes (id_client, date_commande, total, statut)
            VALUES (%s, %s, %s, %s)
        """, (id_client, date.today(), total, "En attente"))

        id_commande = cursor.lastrowid

        cursor.execute("""
            INSERT INTO details_commandes
            (id_commande, id_produit, quantite, prix_unitaire)
            VALUES (%s, %s, %s, %s)
        """, (id_commande, id_produit, quantite, produit["prix"]))

        cursor.execute("""
            UPDATE produits
            SET stock = stock - %s
            WHERE id = %s
        """, (quantite, id_produit))

        db.commit()
        cursor.close()
        db.close()

        return redirect(f"/client/{id_client}")

    cursor.execute("SELECT id, nom, prix, stock FROM produits")
    produits = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "commander.html",
        produits=produits,
        id_client=id_client
    )


# PANIER
@app.route("/panier/<int:id_client>")
def panier(id_client):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT panier.id,
               produits.nom,
               produits.prix,
               panier.quantite,
               produits.prix * panier.quantite AS total
        FROM panier
        JOIN produits ON produits.id = panier.id_produit
        WHERE panier.id_client = %s
    """, (id_client,))

    produits = cursor.fetchall()
    total_panier = sum(produit["total"] for produit in produits)

    cursor.close()
    db.close()

    return render_template(
        "panier.html",
        produits=produits,
        total_panier=total_panier,
        id_client=id_client
    )


# AJOUTER AU PANIER
@app.route("/ajouter_panier/<int:id_client>/<int:id_produit>")
def ajouter_panier(id_client, id_produit):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT stock FROM produits WHERE id = %s", (id_produit,))
    produit = cursor.fetchone()

    if not produit:
        cursor.close()
        db.close()
        return "Produit introuvable"

    cursor.execute("""
        SELECT * FROM panier
        WHERE id_client = %s AND id_produit = %s
    """, (id_client, id_produit))

    article = cursor.fetchone()

    if article:
        if article["quantite"] >= produit["stock"]:
            cursor.close()
            db.close()
            return "Stock insuffisant"

        cursor.execute("""
            UPDATE panier
            SET quantite = quantite + 1
            WHERE id_client = %s AND id_produit = %s
        """, (id_client, id_produit))
    else:
        if produit["stock"] <= 0:
            cursor.close()
            db.close()
            return "Stock insuffisant"

        cursor.execute("""
            INSERT INTO panier(id_client, id_produit, quantite)
            VALUES(%s, %s, %s)
        """, (id_client, id_produit, 1))

    db.commit()
    cursor.close()
    db.close()

    return redirect(f"/panier/{id_client}")

# PAIEMENT
@app.route("/paiement/<int:id_client>", methods=["GET", "POST"])
def paiement(id_client):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT panier.id_produit,
               produits.nom,
               produits.prix,
               produits.stock,
               panier.quantite,
               produits.prix * panier.quantite AS total
        FROM panier
        JOIN produits ON produits.id = panier.id_produit
        WHERE panier.id_client = %s
    """, (id_client,))
    produits = cursor.fetchall()
    total_panier = sum(produit["total"] for produit in produits)

    if request.method == "POST":
        nom = request.form["nom"].strip()
        numero = request.form["numero"].replace(" ", "").replace("-", "")
        expiration = request.form["expiration"].strip()
        cvv = request.form["cvv"].strip()

        if not produits:
            cursor.close()
            db.close()
            return render_template(
                "paiement.html",
                id_client=id_client,
                produits=produits,
                total_panier=total_panier,
                erreur="Votre panier est vide."
            )

        if not nom or not numero.isdigit() or len(numero) != 16 or not expiration or not cvv.isdigit() or len(cvv) not in (3, 4):
            cursor.close()
            db.close()
            return render_template(
                "paiement.html",
                id_client=id_client,
                produits=produits,
                total_panier=total_panier,
                erreur="Paiement refusé : vérifiez les informations de la carte."
            )

        for produit in produits:
            if produit["stock"] < produit["quantite"]:
                cursor.close()
                db.close()
                return render_template(
                    "paiement.html",
                    id_client=id_client,
                    produits=produits,
                    total_panier=total_panier,
                    erreur=f"Stock insuffisant pour {produit['nom']}."
                )

        cursor.execute("""
            INSERT INTO commandes (id_client, date_commande, total, statut)
            VALUES (%s, %s, %s, %s)
        """, (id_client, date.today(), total_panier, "Validée"))

        id_commande = cursor.lastrowid

        for produit in produits:
            cursor.execute("""
                INSERT INTO details_commandes
                (id_commande, id_produit, quantite, prix_unitaire)
                VALUES (%s, %s, %s, %s)
            """, (
                id_commande,
                produit["id_produit"],
                produit["quantite"],
                produit["prix"]
            ))

            cursor.execute("""
                UPDATE produits
                SET stock = stock - %s
                WHERE id = %s
            """, (produit["quantite"], produit["id_produit"]))

        cursor.execute("DELETE FROM panier WHERE id_client = %s", (id_client,))

        db.commit()
        cursor.close()
        db.close()

        return render_template(
            "confirmation.html",
            nom=nom,
            id_client=id_client,
            id_commande=id_commande,
            total_panier=total_panier,
            carte=numero[-4:]
        )

    cursor.close()
    db.close()

    return render_template(
        "paiement.html",
        id_client=id_client,
        produits=produits,
        total_panier=total_panier
    )

if __name__ == "__main__":
    app.run(debug=True)

