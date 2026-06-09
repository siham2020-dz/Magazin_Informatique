# ==========================================================
# TP CYBERSÉCURITÉ - TEST PÉDAGOGIQUE
# Objectif : tester une liste de mots de passe
# et retrouver le mot de passe utilisé
# Usage uniquement en laboratoire / TP
# ==========================================================

# Mot de passe réellement utilisé dans le TP
mot_de_passe_utilise = "1234"

# Liste de mots de passe à tester
liste_mots_de_passe = [
    "admin",
    "password",
    "azerty",
    "test",
    "0000",
    "1111",
    "1234",
    "root",
    "secret"
]

mot_de_passe_trouve = None

print("Début du test des mots de passe...")
print("----------------------------------")

for mdp in liste_mots_de_passe:
    print("Test du mot de passe :", mdp)

    if mdp == mot_de_passe_utilise:
        mot_de_passe_trouve = mdp
        break

print("----------------------------------")

if mot_de_passe_trouve:
    print("Mot de passe trouvé :", mot_de_passe_trouve)
else:
    print("Aucun mot de passe trouvé dans la liste.")