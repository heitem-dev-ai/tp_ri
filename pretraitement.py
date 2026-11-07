import re


STOP_WORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any',
    'are', 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between',
    'both', 'but', 'by', 'can', 'cannot', 'could', 'did', 'do', 'does', 'doing', 'down',
    'during', 'each', 'few', 'for', 'from', 'further', 'had', 'has', 'have', 'having',
    'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if',
    'in', 'into', 'is', 'it', 'its', 'itself', 'just', 'me', 'more', 'most', 'my', 'myself',
    'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our', 'ours',
    'ourselves', 'out', 'over', 'own', 'same', 'she', 'should', 'so', 'some', 'such', 'than',
    'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they',
    'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'we',
    'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'with', 'you',
    'your', 'yours', 'yourself', 'yourselves'
}

IRREGULAR_LEMMAS = {
    'am': 'be', 'are': 'be', 'is': 'be', 'was': 'be', 'were': 'be',
    'been': 'be', 'being': 'be',
    'do': 'do', 'does': 'do', 'did': 'do', 'done': 'do',
    'have': 'have', 'has': 'have', 'had': 'have',
    'went': 'go', 'gone': 'go', 'went': 'go',
    'better': 'good', 'best': 'good',
    'men': 'man', 'women': 'woman', 'children': 'child', 'people': 'person',
    'mice': 'mouse', 'teeth': 'tooth', 'feet': 'foot',
}


# Etape 1 : Nettoyage des balises SGML / XML
def tag_cleaning(texte):
    return re.sub(r"<[^>]+>", " ", texte)


# Etape 2 : Minuscules et suppression de la ponctuation / chiffres
def normalisation(texte):
    texte = texte.lower()
    return re.sub(r"[^a-z\s]", " ", texte)


# Etape 3 : Suppression des mots vides anglais
def stopwords_removal(texte):
    mots = texte.split()
    mots_filtres = [m for m in mots if m not in STOP_WORDS]
    return " ".join(mots_filtres)


def _stem_word(mot):
    mot = mot.strip().lower()
    if len(mot) <= 2:
        return mot

    if mot in IRREGULAR_LEMMAS:
        return IRREGULAR_LEMMAS[mot]

    if len(mot) > 5 and mot.endswith("ies"):
        return mot[:-3] + "y"
    if len(mot) > 4 and mot.endswith("sses"):
        return mot[:-2]
    if len(mot) > 4 and mot.endswith("eed"):
        return mot[:-1]
    if len(mot) > 4 and mot.endswith("ing"):
        return mot[:-3]
    if len(mot) > 3 and mot.endswith("ed"):
        return mot[:-2]
    if len(mot) > 3 and mot.endswith("es"):
        return mot[:-2]
    if len(mot) > 3 and mot.endswith("s"):
        return mot[:-1]
    if len(mot) > 3 and mot.endswith("ly"):
        return mot[:-2]
    return mot


# Etape 4 : Racinisation manuelle (Porter simplifie)
def stemming(texte):
    mots = texte.split()
    mots_racines = [_stem_word(m) for m in mots]
    return " ".join(mots_racines)


def _lemmatize_word(mot):
    mot = mot.strip().lower()
    if not mot:
        return mot

    if mot in IRREGULAR_LEMMAS:
        return IRREGULAR_LEMMAS[mot]

    if len(mot) > 5 and mot.endswith("ies"):
        return mot[:-3] + "y"
    if len(mot) > 4 and mot.endswith("sses"):
        return mot[:-2]
    if len(mot) > 4 and mot.endswith("ing"):
        base = mot[:-3]
        return base if len(base) > 2 else base
    if len(mot) > 3 and mot.endswith("ed"):
        return mot[:-2]
    if len(mot) > 3 and mot.endswith("es"):
        return mot[:-2]
    if len(mot) > 3 and mot.endswith("s"):
        return mot[:-1]
    return mot


# Etape 5 : Lemmatisation manuelle (règles simples de suffixes)
def lemmatisation(texte):
    mots = texte.split()
    mots_lemmes = [_lemmatize_word(m) for m in mots]
    return " ".join(mots_lemmes)


# Dictionnaire des fonctions disponibles
FONCTIONS = {
    "tag_cleaning": tag_cleaning,
    "normalisation": normalisation,
    "stopwords": stopwords_removal,
    "stemming": stemming,
    "lemmatisation": lemmatisation,
}


def appliquer_pipeline(texte, liste_etapes):
    for etape in liste_etapes:
        if etape in FONCTIONS:
            texte = FONCTIONS[etape](texte)
    return texte.split()
