import csv
import os
import re


def _liste_fichiers_sgm(dossier):
    if not os.path.isdir(dossier):
        raise FileNotFoundError(f"Dossier introuvable : {dossier}")

    fichiers = sorted(
        os.path.join(dossier, nom)
        for nom in os.listdir(dossier)
        if nom.lower().endswith(".sgm")
    )
    return fichiers


def charger_documents(dossier, nb_max=500):
    """Lit un corpus Reuters et renvoie {id_doc: texte}.
    - limite le nombre de documents chargés ;
    - extrait NEWID, TITLE et BODY ;
    - ignore les blocs sans texte utile.
    """
    if nb_max <= 0:
        raise ValueError("Le nombre maximum de documents doit être positif.")

    documents = {}

    for chemin in _liste_fichiers_sgm(dossier):
        with open(chemin, "r", encoding="latin-1") as fichier:
            contenu = fichier.read()

        blocs = contenu.split("</REUTERS>")

        for bloc in blocs:
            if len(documents) >= nb_max:
                return documents

            match_id = re.search(r'NEWID="(\d+)"', bloc)
            if not match_id:
                continue

            doc_id = match_id.group(1)
            match_titre = re.search(
                r"<TITLE>(.*?)</TITLE>", bloc, flags=re.DOTALL | re.IGNORECASE
            )
            titre = match_titre.group(1).strip() if match_titre else ""

            match_corps = re.search(
                r"<BODY>(.*?)</BODY>", bloc, flags=re.DOTALL | re.IGNORECASE
            )
            corps = match_corps.group(1).strip() if match_corps else ""

            texte = (titre + " " + corps).strip()
            if texte:
                documents[doc_id] = texte

    return documents


def charger_csv(chemin, nb_max=500):
    """Lit un CSV Reuters à en-têtes et renvoie {id_doc: texte}."""
    if not os.path.isfile(chemin):
        raise FileNotFoundError(f"Fichier CSV introuvable : {chemin}")
    if nb_max <= 0:
        raise ValueError("Le nombre maximum de documents doit être positif.")

    with open(chemin, "r", encoding="utf-8-sig", newline="") as fichier:
        echantillon = fichier.read(4096)
        fichier.seek(0)
        try:
            dialecte = csv.Sniffer().sniff(echantillon, delimiters=",;\t")
        except csv.Error:
            dialecte = csv.excel

        lecteur = csv.DictReader(fichier, dialect=dialecte)
        if not lecteur.fieldnames:
            raise ValueError("Le CSV doit contenir une ligne d'en-têtes.")

        colonnes = {
            re.sub(r"[^a-z0-9]", "", nom.lower()): nom
            for nom in lecteur.fieldnames
            if nom
        }

        def trouver(noms):
            for nom in noms:
                if nom in colonnes:
                    return colonnes[nom]
            return None

        colonne_id = trouver(("newid", "documentid", "docid", "id"))
        colonne_titre = trouver(("title", "headline", "subject"))
        colonne_texte = trouver(
            ("text", "body", "content", "article", "articletext", "description")
        )

        if not colonne_titre and not colonne_texte:
            raise ValueError(
                "Colonnes de texte non reconnues. Le CSV doit contenir un titre, "
                "un texte, un corps ou un contenu d'article."
            )

        documents = {}
        for numero, ligne in enumerate(lecteur, start=1):
            if len(documents) >= nb_max:
                break

            titre = (ligne.get(colonne_titre) or "").strip() if colonne_titre else ""
            texte = (ligne.get(colonne_texte) or "").strip() if colonne_texte else ""
            contenu = (titre + " " + texte).strip()
            if not contenu:
                continue

            doc_id = (ligne.get(colonne_id) or "").strip() if colonne_id else ""
            if not doc_id:
                doc_id = str(numero)
            if doc_id in documents:
                doc_id = f"{doc_id}_{numero}"
            documents[doc_id] = contenu

    return documents
