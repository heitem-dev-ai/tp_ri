import sys
import numpy
from sklearn.feature_extraction.text import CountVectorizer


def _memoire_matrice(matrice):
    if matrice is None:
        return 0.0
    return matrice.nbytes / (1024 * 1024)


def _memoire_liste_inversee(liste_inversee):
    if not liste_inversee:
        return 0.0
    taille = sys.getsizeof(liste_inversee)
    for mot, postings in liste_inversee.items():
        taille += sys.getsizeof(mot) + sys.getsizeof(postings)
        for item in postings:
            taille += sys.getsizeof(item)
    return taille / (1024 * 1024)


def construire_index(docs_tokens, ids_docs):
    """Construit les 4 modèles d'indexation et leurs 3 formats de sortie."""
    textes = [" ".join(docs_tokens[doc_id]) for doc_id in ids_docs]

    vectorizer = CountVectorizer(token_pattern=r"\S+", lowercase=False)
    F = vectorizer.fit_transform(textes).toarray().astype(numpy.float32)
    vocabulaire = vectorizer.get_feature_names_out().tolist()

    nb_docs = len(ids_docs)
    nb_mots = len(vocabulaire)

    BOW = (F > 0).astype(numpy.float32)

    max_par_doc = F.max(axis=1, keepdims=True)
    max_par_doc[max_par_doc == 0] = 1.0
    TF = (F / max_par_doc).astype(numpy.float32)

    df = (F > 0).sum(axis=0)
    idf = numpy.log(nb_docs / df)
    TFIDF = (TF * idf).astype(numpy.float32)

    resultats = {
        "vocabulaire": vocabulaire,
        "ids_docs": ids_docs,
    }

    modeles = {
        "bow": BOW,
        "f": F,
        "tf": TF,
        "tfidf": TFIDF,
    }

    for nom, mat in modeles.items():
        matrice_terme_doc = mat
        matrice_doc_terme = mat.T.copy()

        liste_inversee = {}
        for j in range(nb_mots):
            mot = vocabulaire[j]
            indices_docs = numpy.nonzero(mat[:, j])[0]
            if len(indices_docs) == 0:
                continue
            postings = []
            for i in indices_docs:
                doc_id = ids_docs[i]
                poids = float(mat[i, j])
                postings.append((doc_id, poids))
            liste_inversee[mot] = postings

        resultats[nom] = {
            "matrice_terme_doc": matrice_terme_doc,
            "matrice_doc_terme": matrice_doc_terme,
            "liste_inversee": liste_inversee,
        }

    return resultats


def calculer_statistiques(resultats):
    """Retourne un résumé simple et exploitable pour l'interface."""
    if not resultats:
        return {}

    stats = {
        "documents": len(resultats["ids_docs"]),
        "vocabulaire": len(resultats["vocabulaire"]),
        "modeles": {},
        "memoire_totale_mo": 0.0,
    }

    for nom in ["bow", "f", "tf", "tfidf"]:
        modele = resultats[nom]
        stats["modeles"][nom] = {
            "matrice_terme_doc_mo": round(_memoire_matrice(modele["matrice_terme_doc"]), 3),
            "matrice_doc_terme_mo": round(_memoire_matrice(modele["matrice_doc_terme"]), 3),
            "liste_inversee_mo": round(_memoire_liste_inversee(modele["liste_inversee"]), 3),
        }
        memoire_matrices = (
            stats["modeles"][nom]["matrice_terme_doc_mo"]
            + stats["modeles"][nom]["matrice_doc_terme_mo"]
        )
        memoire_liste = stats["modeles"][nom]["liste_inversee_mo"]
        stats["modeles"][nom]["gain_memoire"] = (
            round(memoire_matrices / memoire_liste, 2)
            if memoire_liste > 0
            else 0.0
        )
        stats["memoire_totale_mo"] += memoire_matrices + memoire_liste

    stats["memoire_totale_mo"] = round(stats["memoire_totale_mo"], 3)

    return stats


def taille_liste(inverse):
    return _memoire_liste_inversee(inverse) * (1024 * 1024)
