"""Génère le rapport académique et le guide utilisateur de la phase 1."""

import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = os.path.dirname(os.path.abspath(__file__))
BLUE = colors.HexColor("#183B5B")
GREEN = colors.HexColor("#2D6A4F")
PALE = colors.HexColor("#EAF1F6")
TEXT = colors.HexColor("#263442")
MUTED = colors.HexColor("#526273")


def register_fonts():
    fonts_dir = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
    regular = os.path.join(fonts_dir, "arial.ttf")
    bold = os.path.join(fonts_dir, "arialbd.ttf")
    if os.path.exists(regular) and os.path.exists(bold):
        pdfmetrics.registerFont(TTFont("ProjectArial", regular))
        pdfmetrics.registerFont(TTFont("ProjectArial-Bold", bold))
        return "ProjectArial", "ProjectArial-Bold"
    return "Helvetica", "Helvetica-Bold"


def make_styles():
    regular, bold = register_fonts()
    base = getSampleStyleSheet()
    return {
        "kicker": ParagraphStyle(
            "Kicker", parent=base["Normal"], fontName=bold, fontSize=10,
            leading=14, textColor=GREEN, alignment=TA_CENTER, spaceAfter=8,
        ),
        "title": ParagraphStyle(
            "TitleProject", parent=base["Title"], fontName=bold,
            fontSize=24, leading=30, textColor=BLUE,
            alignment=TA_CENTER, spaceAfter=10,
        ),
        "subtitle": ParagraphStyle(
            "SubtitleProject", parent=base["Normal"], fontName=regular,
            fontSize=13, leading=19, textColor=MUTED, alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "HeadingProject1", parent=base["Heading1"], fontName=bold,
            fontSize=15, leading=19, textColor=BLUE,
            spaceBefore=12, spaceAfter=7, keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "HeadingProject2", parent=base["Heading2"], fontName=bold,
            fontSize=11, leading=14, textColor=GREEN,
            spaceBefore=8, spaceAfter=4, keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "BodyProject", parent=base["BodyText"], fontName=regular,
            fontSize=9.2, leading=13.2, textColor=TEXT,
            alignment=TA_JUSTIFY, spaceAfter=6,
        ),
        "small": ParagraphStyle(
            "SmallProject", parent=base["BodyText"], fontName=regular,
            fontSize=8, leading=10.5, textColor=MUTED, spaceAfter=4,
        ),
        "cell": ParagraphStyle(
            "CellProject", parent=base["BodyText"], fontName=regular,
            fontSize=8, leading=10.5, textColor=TEXT,
        ),
        "headcell": ParagraphStyle(
            "HeadCellProject", parent=base["BodyText"], fontName=bold,
            fontSize=8, leading=10.5, textColor=colors.white,
        ),
        "callout": ParagraphStyle(
            "CalloutProject", parent=base["BodyText"], fontName=regular,
            fontSize=8.8, leading=12.5, textColor=TEXT,
            backColor=PALE, borderPadding=7, spaceBefore=3, spaceAfter=7,
        ),
        "center": ParagraphStyle(
            "CenterProject", parent=base["Normal"], fontName=regular,
            fontSize=9, leading=13, textColor=MUTED, alignment=TA_CENTER,
        ),
    }


def para(text, style):
    return Paragraph(text, style)


def make_table(rows, widths, styles, header=True):
    values = []
    for row_index, row in enumerate(rows):
        cell_style = styles["headcell"] if header and row_index == 0 else styles["cell"]
        values.append([Paragraph(str(value), cell_style) for value in row])

    table = Table(values, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    if header:
        commands.extend([
            ("BACKGROUND", (0, 0), (-1, 0), BLUE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#F5F8FA")]),
        ])
    else:
        commands.append(("ROWBACKGROUNDS", (0, 0), (-1, -1),
                         [colors.white, colors.HexColor("#F5F8FA")]))
    table.setStyle(TableStyle(commands))
    return table


def page_decorations(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#D5DEE6"))
    canvas.setLineWidth(0.5)
    canvas.line(20 * mm, 16 * mm, width - 20 * mm, 16 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(20 * mm, 10.5 * mm, "Projet de Recherche d'Information — Phase 1")
    canvas.drawRightString(width - 20 * mm, 10.5 * mm, f"Page {doc.page}")
    if doc.page > 1:
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(BLUE)
        canvas.drawString(20 * mm, height - 12 * mm, "DOCUMENT DE PROJET")
    canvas.restoreState()


def document(path, title):
    return SimpleDocTemplate(
        path,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=22 * mm,
        bottomMargin=22 * mm,
        title=title,
        author="Équipe projet — informations à compléter",
    )


def cover(st, styles, subtitle):
    st.extend([
        Spacer(1, 26 * mm),
        para("PROJET DE RECHERCHE D'INFORMATION", styles["kicker"]),
        Spacer(1, 8 * mm),
        para("PHASE 1", styles["title"]),
        para("Interface administrateur<br/>d'indexation dynamique", styles["title"]),
        Spacer(1, 5 * mm),
        para(subtitle, styles["subtitle"]),
        Spacer(1, 7 * mm),
        Table([[""]], colWidths=[45 * mm], rowHeights=[2], style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), GREEN),
        ]), hAlign="CENTER"),
        Spacer(1, 16 * mm),
        Spacer(1, 16 * mm),
        para("Version mise à jour — novembre 2026", styles["center"]),
        PageBreak(),
    ])


def build_report(styles):
    st = []
    cover(st, styles, "Rapport technique et fonctionnel destiné à l'évaluation")
    st.extend([
        para("Résumé", styles["h1"]),
        para(
            "Ce rapport décrit un outil d'administration de première phase pour préparer un corpus "
            "de recherche d'information. L'application charge Reuters sous forme de fichiers SGML/XML "
            "ou de CSV, permet de choisir et d'ordonner les étapes de prétraitement, construit quatre "
            "modèles d'indexation et fournit des mesures de mémoire et des exports réutilisables.",
            styles["body"],
        ),
        para(
            "<b>Périmètre exact :</b> l'option « Publier les paramètres » écrit un fichier JSON local. "
            "Elle ne déploie pas l'application sur un serveur et ne crée pas de comptes utilisateurs. "
            "La recherche côté client et le classement Top-K relèvent de la phase suivante.",
            styles["callout"],
        ),
        para("1. Objectifs et conformité au cahier des charges", styles["h1"]),
        make_table([
            ["Attendu Phase 1", "Réalisation"],
            ["Charger des données Reuters", "Sélection d'un dossier .sgm ou d'un fichier CSV avec colonnes texte reconnues."],
            ["Configurer le prétraitement", "Étapes activables, ordre modifiable, réinitialisation et aperçu sur un document."],
            ["Générer plusieurs modèles", "BoW, F, TF et TF-IDF avec deux matrices et une liste inversée par modèle."],
            ["Mesurer les résultats", "Documents, vocabulaire, durée, taille mémoire des formats et comparaison de structures."],
            ["Sauvegarder et transmettre", "Export ZIP configurable en JSON, texte ou binaire, avec vocabulaire, IDs et configuration."],
        ], [52 * mm, 108 * mm], styles),
        para("2. Architecture du programme", styles["h1"]),
        make_table([
            ["Module", "Responsabilité"],
            ["main.py", "Démarre l'application."],
            ["gui.py", "Interface Tkinter, validation des entrées, coordination des fonctions et affichage."],
            ["chargement.py", "Lecture Reuters SGML et CSV, extraction des identifiants et textes."],
            ["pretraitement.py", "Nettoyage, normalisation, stopwords, stemming et lemmatisation manuels."],
            ["indexation.py", "Comptage des fréquences, calcul des modèles, matrices, postings et métriques."],
            ["stockage.py", "Export ZIP multi-format et écriture des paramètres de publication locale."],
        ], [38 * mm, 122 * mm], styles),
        para(
            "Le flux est : source → documents identifiés → pipeline NLP → tokens → index → "
            "statistiques et export. La séparation en petits modules permet de distinguer l'interface "
            "des transformations et des calculs.",
            styles["body"],
        ),
        PageBreak(),
        para("3. Chargement et aperçu des documents", styles["h1"]),
        para(
            "L'administrateur choisit soit un dossier de fichiers Reuters .sgm, soit un fichier CSV. "
            "Le chargeur SGML extrait NEWID, TITLE et BODY. Le chargeur CSV reconnaît une colonne "
            "d'identifiant facultative et des colonnes de texte telles que title, headline, text, "
            "body, content, article ou description. Si aucun identifiant n'est fourni, un numéro de "
            "ligne sert d'identifiant. Un maximum de documents peut être fixé avant le chargement.",
            styles["body"],
        ),
        para(
            "La fenêtre « Aperçu des documents » affiche jusqu'à 100 articles chargés; sélectionner "
            "une ligne montre le texte associé. Le bouton de rechargement relit la source avec la "
            "limite courante.",
            styles["body"],
        ),
        para("4. Pipeline de prétraitement", styles["h1"]),
        make_table([
            ["Étape", "Description et choix de réalisation"],
            ["Nettoyage des balises", "Supprime les balises SGML/XML à l'aide d'une expression régulière."],
            ["Normalisation", "Minuscules, ponctuation et chiffres remplacés par des espaces."],
            ["Stopwords", "Liste anglaise définie directement dans le code; retrait des mots de fonction fréquents."],
            ["Stemming", "Règles pédagogiques de suffixes pour réduire certaines formes à une racine."],
            ["Lemmatisation", "Règles de suffixes et petit dictionnaire d'exceptions; résultat approximatif."],
        ], [39 * mm, 121 * mm], styles),
        para(
            "Stemming et lemmatisation sont exclusifs dans l'interface, car ce sont deux traitements "
            "alternatifs des formes des mots. L'aperçu étape par étape applique les étapes actives "
            "à un document choisi et affiche le nombre de mots et un extrait après chaque transformation.",
            styles["body"],
        ),
        para(
            "<b>Limite linguistique :</b> le stemming et la lemmatisation sont des implémentations "
            "manuelles simplifiées. Elles sont faciles à expliquer mais ne reproduisent pas un "
            "lemmatiseur fondé sur un dictionnaire grammatical complet.",
            styles["callout"],
        ),
        para("5. Modèles et structures d'index", styles["h1"]),
        make_table([
            ["Modèle", "Formule / règle", "Sens"],
            ["BoW", "1 si F(t,d) > 0, sinon 0.", "Présence ou absence."],
            ["F", "Nombre d'occurrences F(t,d).", "Fréquence brute."],
            ["TF", "F(t,d) / fréquence maximale du document.", "Fréquence relative au document."],
            ["TF-IDF", "TF(t,d) × log(N / df(t)).", "Diminue le poids des termes fréquents dans le corpus."],
        ], [24 * mm, 72 * mm, 64 * mm], styles),
        para(
            "N désigne le nombre de documents et df(t) le nombre de documents contenant le terme. "
            "CountVectorizer construit le vocabulaire et le tableau de fréquences; NumPy réalise les "
            "transformations numériques. La formule TF-IDF est appliquée explicitement avec le "
            "logarithme non lissé.",
            styles["body"],
        ),
        make_table([
            ["Structure", "Orientation ou contenu"],
            ["matrice_terme_doc", "N lignes de documents × M colonnes de termes."],
            ["matrice_doc_terme", "M lignes de termes × N colonnes de documents (transposée)."],
            ["liste_inversee", "terme → [(identifiant document, poids)]; seules les valeurs non nulles sont retenues."],
        ], [44 * mm, 116 * mm], styles),
        PageBreak(),
        para("6. Métriques, export et paramètres de publication", styles["h1"]),
        para(
            "Les matrices sont stockées en float32. La taille affichée d'une matrice utilise son "
            "attribut nbytes. La taille de la liste inversée est estimée en additionnant les tailles "
            "rapportées par sys.getsizeof pour le dictionnaire, les termes, les listes et les tuples. "
            "La mémoire totale additionne les structures comptabilisées pour les quatre modèles.",
            styles["body"],
        ),
        para(
            "L'estimation Python n'est pas une mesure complète du processus : tous les objets "
            "référencés ne sont pas comptés individuellement. Les valeurs sont utiles pour comparer "
            "les structures dans les mêmes conditions; elles ne doivent pas être interprétées comme "
            "une mesure exacte de la RAM du système.",
            styles["small"],
        ),
        make_table([
            ["Format d'export", "Contenu de l'archive ZIP"],
            ["JSON", "index.json avec les deux matrices et les postings, config.json, vocabulaire.txt, ids_documents.txt."],
            ["Texte", "Matrices TSV et listes inversées TSV, plus configuration, vocabulaire et IDs."],
            ["Binaire", "index.pkl, plus configuration, vocabulaire et IDs."],
        ], [37 * mm, 123 * mm], styles),
        para(
            "Le format binaire est compact et doit être lu par Python; le JSON et les fichiers texte "
            "sont inspectables. Pour un corpus volumineux, l'export JSON peut produire une archive "
            "plus grande que l'export binaire.",
            styles["body"],
        ),
        para(
            "« Publier les paramètres » enregistre publication.json avec le type/nom de source, le "
            "pipeline courant et une limite maximale, choisie entre 1 et 1000 documents. C'est une "
            "publication locale de configuration destinée à préparer une phase client; il n'existe "
            "pas encore de serveur, d'authentification ou de déploiement distant.",
            styles["body"],
        ),
        para("7. Vérifications et limites", styles["h1"]),
        make_table([
            ["Vérification", "Résultat"],
            ["Compilation", "Les modules Python de l'application se compilent sans erreur."],
            ["Chargement Reuters fourni", "Le fichier d'exemple .sgm est lu et fournit 5 documents."],
            ["CSV de test", "Lecture des en-têtes, séparateurs, limite de documents et indexation testées sur un CSV temporaire."],
            ["Exports", "Archives JSON, texte et binaire vérifiées; présence des paramètres, vocabulaire et IDs contrôlée."],
            ["Publication locale", "Le JSON des paramètres et la limite sont vérifiés après écriture."],
        ], [43 * mm, 117 * mm], styles),
        para("Limites restantes", styles["h2"]),
        para(
            "Les matrices sont denses et peuvent consommer beaucoup de mémoire sur tout le corpus; "
            "l'indexation s'exécute dans le thread de l'interface et peut donc la bloquer pendant un "
            "calcul long. Le CSV attendu doit avoir des en-têtes reconnus. La publication ne configure "
            "pas réellement un serveur. Il n'y a pas de bouton GUI pour réimporter un index, ni de "
            "recherche utilisateur par similarité cosinus dans cette phase.",
            styles["body"],
        ),
        para("8. Installation et démonstration", styles["h1"]),
        para(
            "Installer NumPy et scikit-learn, puis lancer python main.py depuis le dossier du projet. "
            "Pour une démonstration reproductible, charger test_docs, consulter un article, montrer "
            "le pipeline étape par étape, générer les index, rechercher oil, puis exporter une archive "
            "dans chacun des formats proposés.",
            styles["body"],
        ),
        para("Conclusion", styles["h1"]),
        para(
            "La phase livrée couvre le cycle d'administration demandé : acquisition des documents, "
            "paramétrage du prétraitement, génération de modèles, observation de métriques et "
            "sauvegarde. Les fonctionnalités ajoutées rendent l'expérimentation plus visible, tandis "
            "que les limites indiquent clairement ce qui reste à développer pour une phase de recherche "
            "utilisateur.",
            styles["body"],
        ),
        para("Captures d'écran à insérer avant remise finale si elles sont exigées par l'enseignant.", styles["small"]),
    ])
    path = os.path.join(ROOT, "RAPPORT_FINAL_PHASE1.pdf")
    document(path, "Rapport final — Projet RI Phase 1").build(
        st, onFirstPage=page_decorations, onLaterPages=page_decorations
    )
    return path


def build_guide(styles):
    st = []
    cover(st, styles, "Guide d'utilisation et de démonstration")
    st.extend([
        para("Objectif du guide", styles["h1"]),
        para(
            "Ce document accompagne le rapport technique et explique comment exécuter une "
            "démonstration de l'application. Il décrit les contrôles de l'interface et le contenu "
            "des fichiers exportés.",
            styles["body"],
        ),
        para("1. Préparer l'environnement", styles["h1"]),
        para("Depuis PowerShell, dans le dossier du projet :", styles["body"]),
        para("python -m pip install numpy scikit-learn<br/>python main.py", styles["callout"]),
        para(
            "Tkinter est fourni avec la plupart des installations Python pour Windows. Si le "
            "terminal signale qu'une bibliothèque est absente, installer les dépendances dans le "
            "même environnement Python que celui utilisé pour démarrer main.py.",
            styles["body"],
        ),
        para("2. Charger les documents", styles["h1"]),
        make_table([
            ["Choix", "Action"],
            ["Reuters SGML/XML", "Sélectionner un dossier qui contient les fichiers .sgm. test_docs est fourni pour l'essai."],
            ["Reuters CSV", "Sélectionner un seul fichier CSV; il doit contenir une ligne d'en-têtes et une colonne de texte reconnue."],
            ["Nombre maximal", "Choisir une valeur puis cliquer sur Recharger les documents."],
            ["Aperçu", "Ouvrir Aperçu des documents; sélectionner une ligne pour voir l'article complet."],
        ], [40 * mm, 120 * mm], styles),
        para("3. Configurer le pipeline", styles["h1"]),
        para(
            "Cocher les traitements souhaités. Les flèches changent l'ordre; Réinitialiser rétablit "
            "la configuration initiale. Stemming et lemmatisation ne peuvent pas être cochés ensemble. "
            "Aperçu étape par étape montre le texte brut puis le résultat de chaque étape active.",
            styles["body"],
        ),
        para(
            "Pour illustrer la normalisation, indexer avec cette seule étape, puis chercher OIL! "
            "dans l'aperçu des postings : la requête est transformée en oil. Toute modification du "
            "pipeline nécessite de générer les index à nouveau.",
            styles["callout"],
        ),
        para("4. Générer et interpréter les index", styles["h1"]),
        para(
            "Cliquer sur Générer les Index. Le résumé affiche le nombre de documents, la taille du "
            "vocabulaire, le temps et la mémoire estimée. Le tableau compare BoW, F, TF et TF-IDF sous "
            "forme de deux matrices et de listes inversées. Le rapport matrices/liste donne un aperçu "
            "comparatif, pas une mesure complète de RAM système.",
            styles["body"],
        ),
        make_table([
            ["Modèle", "Interprétation simple"],
            ["BoW", "Le terme est présent (1) ou absent (0)."],
            ["F", "Nombre d'occurrences du terme dans chaque document."],
            ["TF", "Fréquence brute divisée par la fréquence la plus élevée du document."],
            ["TF-IDF", "Fréquence TF pondérée par la rareté du terme dans tout le corpus."],
        ], [28 * mm, 132 * mm], styles),
        PageBreak(),
        para("5. Exporter les résultats", styles["h1"]),
        para(
            "Cliquer sur Exporter les Index (.zip), choisir un format et sélectionner l'emplacement "
            "du fichier ZIP. Les trois formats incluent config.json, vocabulaire.txt et "
            "ids_documents.txt; ils contiennent aussi les structures d'index dans leur format propre.",
            styles["body"],
        ),
        make_table([
            ["Format", "Quand le choisir"],
            ["JSON — lisible", "Pour inspecter les valeurs et échanger avec un programme qui lit JSON."],
            ["Texte — matrices et postings", "Pour examiner les lignes de matrices et les listes inversées dans un éditeur."],
            ["Binaire — compact", "Pour conserver les structures Python/NumPy et les recharger plus rapidement."],
        ], [45 * mm, 115 * mm], styles),
        para(
            "Un fichier index.pkl est binaire : ne pas l'ouvrir avec le Bloc-notes. Pour le format "
            "binaire, extraire l'archive et charger le dossier qui contient le pickle avec le code "
            "Python correspondant. Ne jamais charger un pickle d'une source inconnue.",
            styles["callout"],
        ),
        para("6. Enregistrer les paramètres pour la phase suivante", styles["h1"]),
        para(
            "Le bouton Publier les paramètres demande une limite maximale et enregistre localement "
            "publication.json. Le fichier mémorise le type et le nom de la source, le pipeline actif "
            "et la limite. Il ne rend pas les paramètres accessibles sur Internet et n'ajoute pas "
            "d'authentification.",
            styles["body"],
        ),
        para("7. Déroulé conseillé devant l'enseignant", styles["h1"]),
        make_table([
            ["Temps", "Démonstration"],
            ["1 min", "Présenter la séparation des modules et charger le jeu test_docs."],
            ["1 min", "Ouvrir un document et expliquer l'ordre du pipeline."],
            ["1 min", "Montrer l'aperçu étape par étape et comparer les tokens avant/après."],
            ["1 min", "Générer les quatre modèles et expliquer une ligne du tableau mémoire."],
            ["1 min", "Rechercher oil, exporter un ZIP et montrer config.json."],
        ], [27 * mm, 133 * mm], styles),
        para("Questions courantes", styles["h1"]),
        para(
            "<b>Pourquoi la liste inversée?</b> Elle associe chaque terme aux documents où il apparaît, "
            "ce qui évite de parcourir tous les zéros d'une matrice pour ce type d'accès.<br/>"
            "<b>Pourquoi deux matrices?</b> Ce sont les mêmes poids avec les axes transposés.<br/>"
            "<b>La publication est-elle en ligne?</b> Non, elle écrit seulement un fichier JSON local.<br/>"
            "<b>La recherche est-elle déjà la phase 2?</b> Non, la zone de mot vérifie seulement les "
            "postings TF-IDF; elle ne classe pas une requête complète par similarité.",
            styles["body"],
        ),
        para("Ce guide correspond aux fonctions présentes dans la version actuelle du projet.", styles["small"]),
    ])
    path = os.path.join(ROOT, "GUIDE_PROJET_RI_PHASE1.pdf")
    document(path, "Guide d'utilisation — Projet RI Phase 1").build(
        st, onFirstPage=page_decorations, onLaterPages=page_decorations
    )
    return path


if __name__ == "__main__":
    styles = make_styles()
    print("Générés :")
    print(build_report(styles))
    print(build_guide(styles))
    print(f"Date de génération : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
