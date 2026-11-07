# Projet de Recherche d'Information — Phase 1

Application d'administration pour charger un sous-ensemble de Reuters-21578, configurer un pipeline de prétraitement, produire des index et les sauvegarder.

## Prérequis

- Python 3.8 ou supérieur
- NumPy
- scikit-learn
- Tkinter (inclus avec la plupart des installations Python pour Windows)

Installation des dépendances :

```powershell
python -m pip install numpy scikit-learn
```

## Lancement

Depuis le dossier du projet :

```powershell
python main.py
```

## Utilisation

1. Dans **Jeu de données**, choisissez Reuters SGML/XML ou un fichier CSV, puis sélectionnez le dossier ou le fichier.
2. Choisissez un nombre maximal de documents et cliquez sur **Recharger les documents**. Le mode SGML utilise `test_docs` par défaut.
3. Cliquez sur **Aperçu des documents** pour consulter les articles chargés.
4. Activez les étapes souhaitées, réordonnez-les avec les flèches et utilisez **Aperçu étape par étape** pour voir les transformations. Stemming et lemmatisation ne peuvent pas être activés simultanément.
5. Cliquez sur **Générer les Index** pour calculer BoW, F, TF et TF-IDF.
6. La zone Monitoring présente les dimensions, la mémoire totale estimée et le rapport entre les deux matrices et la liste inversée. La zone de recherche permet de consulter les postings TF-IDF d'un mot.
7. Cliquez sur **Exporter les Index (.zip)** et choisissez un format : JSON, texte ou binaire. L'archive contient les index, le vocabulaire et la configuration.
8. **Publier les paramètres** crée un fichier `publication.json` avec le jeu de données, le pipeline actif et une limite de documents pour le futur module utilisateur. L'enregistrement est local : aucun serveur ni compte utilisateur n'est configuré dans cette phase.

### Format CSV pris en charge

Le fichier CSV doit avoir une ligne d'en-têtes et au moins une colonne de texte reconnue : `title`, `headline`, `subject`, `text`, `body`, `content`, `article`, `articletext` ou `description`. Une colonne d'identifiant (`newid`, `documentid`, `docid` ou `id`) est facultative; un identifiant est créé si elle est absente.

### Export et index sauvegardés

- Le format **Binaire** contient `index.pkl`, les formats **JSON** et **Texte** ont des fichiers lisibles.
- Les trois formats incluent le vocabulaire et `config.json`.

Le fichier `.pkl` est binaire; il faut l'extraire et le lire avec le module `stockage`, pas avec un éditeur de texte. Pour recharger une sauvegarde créée par l'ancienne fonction :

```python
import stockage

index, configuration = stockage.charger_index(r"C:\chemin\vers\le\dossier")
print(configuration)
```

## Modèles produits

- **BoW** : 1 si un terme est présent, sinon 0.
- **F** : nombre brut d'occurrences.
- **TF** : fréquence divisée par la fréquence maximale du document.
- **TF-IDF** : `TF × log(N / df)`.

Chaque modèle est enregistré sous forme de deux orientations de matrice et d'une liste inversée.

## Notes

Les étapes stopwords, stemming et lemmatisation utilisent des listes et règles simples codées dans le projet. La lemmatisation est donc pédagogique et approximative. Le comptage vectoriel et les opérations sur les matrices reposent encore sur scikit-learn et NumPy. Le moteur de recherche côté utilisateur appartient à la phase suivante.

## Rapports PDF

Le dossier contient `RAPPORT_FINAL_PHASE1.pdf` (rapport pour l'évaluation) et `GUIDE_PROJET_RI_PHASE1.pdf` (guide de démonstration). Pour les régénérer après une modification du projet, installer ReportLab puis lancer :

```powershell
python -m pip install reportlab
python generer_rapports.py
```

La dépendance ReportLab n'est nécessaire que pour générer les PDF, pas pour lancer l'application.
