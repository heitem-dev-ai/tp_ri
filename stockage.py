import os
import json
import pickle
from datetime import datetime


def sauvegarder_index(resultats, dossier, etapes):
    if not os.path.exists(dossier):
        os.makedirs(dossier)

    chemin_pickle = os.path.join(dossier, "index.pkl")
    with open(chemin_pickle, "wb") as f:
        pickle.dump(resultats, f)

    chemin_config = os.path.join(dossier, "config.json")
    config = {
        "etapes": etapes,
        "nb_documents": len(resultats["ids_docs"]),
        "taille_vocabulaire": len(resultats["vocabulaire"]),
        "date_creation": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fichiers": {
            "index": "index.pkl",
            "configuration": "config.json",
        },
    }
    with open(chemin_config, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    return {"index": chemin_pickle, "config": chemin_config}


def charger_index(dossier):
    chemin_pickle = os.path.join(dossier, "index.pkl")
    chemin_config = os.path.join(dossier, "config.json")

    if not os.path.exists(chemin_pickle):
        raise FileNotFoundError(f"Fichier introuvable : {chemin_pickle}")
    if not os.path.exists(chemin_config):
        raise FileNotFoundError(f"Fichier introuvable : {chemin_config}")

    with open(chemin_pickle, "rb") as f:
        resultats = pickle.load(f)

    with open(chemin_config, "r", encoding="utf-8") as f:
        config = json.load(f)

    return resultats, config


def exporter_index_zip(resultats, chemin_zip, etapes, format_sortie, source=None):
    """Crée une archive avec index, vocabulaire et paramètres."""
    import csv
    import io
    import zipfile

    formats = {"json", "texte", "binaire"}
    if format_sortie not in formats:
        raise ValueError(f"Format non pris en charge : {format_sortie}")

    configuration = {
        "etapes": etapes,
        "nb_documents": len(resultats["ids_docs"]),
        "taille_vocabulaire": len(resultats["vocabulaire"]),
        "date_creation": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format_index": format_sortie,
        "source": source or {},
    }

    with zipfile.ZipFile(chemin_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "config.json",
            json.dumps(configuration, indent=2, ensure_ascii=False),
        )
        archive.writestr(
            "vocabulaire.txt",
            "\n".join(resultats["vocabulaire"]),
        )
        archive.writestr(
            "ids_documents.txt",
            "\n".join(str(doc_id) for doc_id in resultats["ids_docs"]),
        )

        if format_sortie == "binaire":
            buffer = io.BytesIO()
            pickle.dump(resultats, buffer)
            archive.writestr("index.pkl", buffer.getvalue())
        elif format_sortie == "json":
            contenu = {
                "vocabulaire": resultats["vocabulaire"],
                "ids_docs": resultats["ids_docs"],
                "modeles": {},
            }
            for nom in ("bow", "f", "tf", "tfidf"):
                modele = resultats[nom]
                contenu["modeles"][nom] = {
                    "matrice_terme_doc": modele["matrice_terme_doc"].tolist(),
                    "matrice_doc_terme": modele["matrice_doc_terme"].tolist(),
                    "liste_inversee": modele["liste_inversee"],
                }
            archive.writestr(
                "index.json",
                json.dumps(contenu, ensure_ascii=False),
            )
        else:
            for nom in ("bow", "f", "tf", "tfidf"):
                modele = resultats[nom]
                for cle, nom_fichier in (
                    ("matrice_terme_doc", f"{nom}_matrice_terme_doc.tsv"),
                    ("matrice_doc_terme", f"{nom}_matrice_doc_terme.tsv"),
                ):
                    matrice = modele[cle]
                    lignes = io.StringIO()
                    for ligne in matrice:
                        lignes.write("\t".join(str(float(valeur)) for valeur in ligne))
                        lignes.write("\n")
                    archive.writestr(nom_fichier, lignes.getvalue())

                postings = io.StringIO()
                writer = csv.writer(postings, delimiter="\t", lineterminator="\n")
                writer.writerow(("terme", "id_document", "poids"))
                for terme, elements in modele["liste_inversee"].items():
                    for doc_id, poids in elements:
                        writer.writerow((terme, doc_id, poids))
                archive.writestr(f"{nom}_liste_inversee.tsv", postings.getvalue())

    return chemin_zip


def publier_configuration(chemin, type_source, nom_source, etapes, max_documents):
    """Sauvegarde localement les paramètres destinés au futur module utilisateur."""
    if max_documents <= 0:
        raise ValueError("La limite de documents doit être positive.")

    configuration = {
        "jeu_de_donnees": {
            "type": type_source,
            "nom": nom_source,
        },
        "pipeline": etapes,
        "limite_documents_utilisateur": max_documents,
        "date_publication": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(chemin, "w", encoding="utf-8") as fichier:
        json.dump(configuration, fichier, indent=2, ensure_ascii=False)
    return chemin
