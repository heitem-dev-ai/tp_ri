import csv
import os
import random
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import chargement
import pretraitement
import indexation
import stockage


class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Administration - Moteur de Recherche RI (Phase 1)")
        self.root.geometry("1000x850")

        self.documents = {}
        self.resultats = None
        self.chemin_corpus = ""
        self.chemin_sauvegarde = ""
        self.etapes_indexees = None
        self.type_source = tk.StringVar(value="sgm")
        self.chemin_source_var = tk.StringVar(
            value=os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_docs")
        )

        self.etapes = [
            "tag_cleaning",
            "normalisation",
            "stopwords",
            "stemming",
            "lemmatisation",
        ]
        self.etapes_vars = {
            e: tk.BooleanVar(value=e != "lemmatisation")
            for e in self.etapes
        }

        self.creer_zone_chargement()
        self.creer_zone_pipeline()
        self.creer_zone_actions()
        self.creer_zone_monitoring()
        self.creer_zone_apercu()

    def creer_zone_chargement(self):
        frame = ttk.LabelFrame(self.root, text="1. Jeu de données")
        frame.pack(fill="x", padx=10, pady=5)

        choix = ttk.Frame(frame)
        choix.pack(fill="x", padx=5, pady=4)
        ttk.Radiobutton(
            choix, text="Reuters SGML/XML (.sgm)", variable=self.type_source,
            value="sgm", command=self.actualiser_source,
        ).pack(side="left", padx=5)
        ttk.Radiobutton(
            choix, text="Fichier Reuters CSV", variable=self.type_source,
            value="csv", command=self.actualiser_source,
        ).pack(side="left", padx=5)

        chemin = ttk.Frame(frame)
        chemin.pack(fill="x", padx=5, pady=4)
        self.entry_source = ttk.Entry(chemin, textvariable=self.chemin_source_var)
        self.entry_source.pack(side="left", fill="x", expand=True, padx=4)
        self.btn_parcourir = ttk.Button(chemin, text="Parcourir...", command=self.parcourir_source)
        self.btn_parcourir.pack(side="left", padx=4)

        options = ttk.Frame(frame)
        options.pack(fill="x", padx=5, pady=4)
        ttk.Label(options, text="Nombre maximal :").pack(side="left", padx=5)
        self.entry_max = ttk.Combobox(
            options, width=10, values=("10", "100", "500", "1000", "2000", "5000"),
        )
        self.entry_max.set("500")
        self.entry_max.pack(side="left", padx=4)
        ttk.Button(options, text="Recharger les documents", command=self.charger).pack(side="left", padx=5)
        ttk.Button(options, text="Aperçu des documents", command=self.ouvrir_apercu_documents).pack(side="left", padx=5)

        self.label_docs = ttk.Label(options, text="Aucun document chargé", foreground="blue")
        self.label_docs.pack(side="left", padx=12)
        self.label_source = ttk.Label(frame, text="", foreground="darkgreen")
        self.label_source.pack(anchor="w", padx=10, pady=2)

    def actualiser_source(self):
        if self.type_source.get() == "sgm":
            self.chemin_source_var.set(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_docs")
            )
        else:
            self.chemin_source_var.set("")

    def parcourir_source(self):
        if self.type_source.get() == "sgm":
            chemin = filedialog.askdirectory(
                title="Sélectionner le dossier contenant les fichiers .sgm",
                initialdir=self.chemin_source_var.get() or os.path.dirname(os.path.abspath(__file__)),
            )
        else:
            chemin = filedialog.askopenfilename(
                title="Sélectionner le fichier Reuters CSV",
                filetypes=(("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")),
                initialdir=os.path.dirname(self.chemin_source_var.get()) or os.path.dirname(os.path.abspath(__file__)),
            )
        if chemin:
            self.chemin_source_var.set(chemin)

    def creer_zone_pipeline(self):
        frame = ttk.LabelFrame(self.root, text="2. Pipeline de prétraitement")
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(
            frame,
            text="Cochez les étapes et changez leur ordre. Stemming et lemmatisation sont exclusifs.",
        ).pack(anchor="w", padx=8, pady=(5, 0))
        self.frame_etapes = ttk.Frame(frame)
        self.frame_etapes.pack(fill="x", padx=5, pady=5)
        self.afficher_etapes()
        boutons = ttk.Frame(frame)
        boutons.pack(fill="x", padx=5, pady=(0, 5))
        ttk.Button(boutons, text="Réinitialiser", command=self.reinitialiser_pipeline).pack(side="left", padx=3)
        ttk.Button(boutons, text="Aperçu étape par étape", command=self.ouvrir_apercu_pipeline).pack(side="left", padx=3)

    def afficher_etapes(self):
        for widget in self.frame_etapes.winfo_children():
            widget.destroy()

        for idx, etape in enumerate(self.etapes):
            ligne = ttk.Frame(self.frame_etapes)
            ligne.pack(fill="x", pady=2)

            libelles = {
                "tag_cleaning": "Nettoyage des balises",
                "normalisation": "Normalisation",
                "stopwords": "Suppression des mots vides",
                "stemming": "Stemming (racinisation)",
                "lemmatisation": "Lemmatisation",
            }
            chk = ttk.Checkbutton(
                ligne,
                text=f"{idx+1}. {libelles[etape]}",
                variable=self.etapes_vars[etape],
                command=lambda nom=etape: self.changer_etape(nom),
            )
            chk.pack(side="left", padx=5)

            btn_monter = ttk.Button(ligne, text="↑", width=3, command=lambda i=idx: self.monter(i))
            btn_monter.pack(side="right", padx=2)

            btn_descendre = ttk.Button(ligne, text="↓", width=3, command=lambda i=idx: self.descendre(i))
            btn_descendre.pack(side="right", padx=2)

    def changer_etape(self, etape):
        autre = "lemmatisation" if etape == "stemming" else "stemming"
        if etape in ("stemming", "lemmatisation") and self.etapes_vars[etape].get():
            self.etapes_vars[autre].set(False)
            self.afficher_etapes()

    def reinitialiser_pipeline(self):
        self.etapes = [
            "tag_cleaning", "normalisation", "stopwords", "stemming", "lemmatisation",
        ]
        for etape in self.etapes:
            self.etapes_vars[etape].set(etape != "lemmatisation")
        self.afficher_etapes()

    def monter(self, idx):
        if idx > 0:
            self.etapes[idx], self.etapes[idx - 1] = self.etapes[idx - 1], self.etapes[idx]
            self.afficher_etapes()

    def descendre(self, idx):
        if idx < len(self.etapes) - 1:
            self.etapes[idx], self.etapes[idx + 1] = self.etapes[idx + 1], self.etapes[idx]
            self.afficher_etapes()

    def get_etapes_actives(self):
        return [e for e in self.etapes if self.etapes_vars[e].get()]

    def creer_zone_actions(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(frame, text="Générer les Index", command=self.generer).pack(side="left", padx=5)
        ttk.Button(frame, text="Exporter les Index (.zip)", command=self.sauvegarder).pack(side="left", padx=5)
        ttk.Button(frame, text="Publier les paramètres", command=self.publier).pack(side="left", padx=5)

    def creer_zone_monitoring(self):
        frame = ttk.LabelFrame(self.root, text="3. Métriques & Monitoring Mémoire")
        frame.pack(fill="x", padx=10, pady=5)

        self.label_stats = ttk.Label(frame, text="Aucun index généré.", font=("Arial", 9, "bold"))
        self.label_stats.pack(anchor="w", padx=5, pady=3)

        self.label_sauvegarde = ttk.Label(frame, text="Aucune sauvegarde effectuée", foreground="gray")
        self.label_sauvegarde.pack(anchor="w", padx=5, pady=2)

        colonnes = ("modele", "terme_doc", "doc_terme", "liste_inv", "gain")
        self.tree = ttk.Treeview(frame, columns=colonnes, show="headings", height=4)
        self.tree.heading("modele", text="Modèle")
        self.tree.heading("terme_doc", text="Matrice Terme-Doc (Mo)")
        self.tree.heading("doc_terme", text="Matrice Doc-Terme (Mo)")
        self.tree.heading("liste_inv", text="Liste Inversée (Mo)")
        self.tree.heading("gain", text="Matrices / liste")

        for col in colonnes:
            self.tree.column(col, anchor="center")
        self.tree.pack(fill="x", padx=5, pady=5)

    def creer_zone_apercu(self):
        frame = ttk.LabelFrame(self.root, text="4. Aperçu de l'Index Inversé (TF-IDF)")
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        ligne = ttk.Frame(frame)
        ligne.pack(fill="x", padx=5, pady=3)

        ttk.Label(ligne, text="Mot à chercher :").pack(side="left", padx=5)
        self.entry_mot = ttk.Entry(ligne, width=20)
        self.entry_mot.pack(side="left", padx=5)

        ttk.Button(ligne, text="Chercher", command=self.chercher).pack(side="left", padx=5)

        self.zone_texte = tk.Text(frame, height=8)
        self.zone_texte.pack(fill="both", expand=True, padx=5, pady=5)

    def charger(self):
        try:
            nb_max = int(self.entry_max.get())
        except ValueError:
            messagebox.showerror("Valeur incorrecte", "Le nombre maximum doit être un entier positif.")
            return
        if nb_max <= 0:
            messagebox.showerror("Valeur incorrecte", "Le nombre maximum doit être supérieur à zéro.")
            return

        source = self.chemin_source_var.get().strip()
        if not source:
            self.parcourir_source()
            source = self.chemin_source_var.get().strip()
        if not source:
            return

        try:
            if self.type_source.get() == "sgm":
                documents = chargement.charger_documents(source, nb_max=nb_max)
            else:
                documents = chargement.charger_csv(source, nb_max=nb_max)
        except (OSError, ValueError, UnicodeError, csv.Error) as erreur:
            messagebox.showerror("Erreur de chargement", f"Impossible de lire ce dossier :\n{erreur}")
            return

        self.chemin_corpus = source
        self.documents = documents
        source_nom = "Reuters SGML/XML" if self.type_source.get() == "sgm" else "Reuters CSV"
        self.label_docs.config(text=f"{len(self.documents)} document(s) chargé(s)")
        self.label_source.config(text=f"{source_nom} : {source}")
        self.resultats = None
        self.etapes_indexees = None
        self.label_stats.config(text="Documents chargés — générez les index.")
        self.label_sauvegarde.config(text="Index non générés", foreground="gray")
        for item in self.tree.get_children():
            self.tree.delete(item)

        if len(self.documents) == 0:
            messagebox.showwarning("Attention", "Aucun document exploitable n'a été trouvé.")
        else:
            messagebox.showinfo("Chargement terminé", f"{len(self.documents)} document(s) chargé(s).")

    def ouvrir_apercu_documents(self):
        if not self.documents:
            messagebox.showwarning("Attention", "Chargez d'abord un jeu de données.")
            return

        fenetre = tk.Toplevel(self.root)
        fenetre.title("Aperçu des documents chargés")
        fenetre.geometry("900x650")

        colonnes = ("id", "titre", "mots")
        liste = ttk.Treeview(fenetre, columns=colonnes, show="headings", height=12)
        liste.heading("id", text="Identifiant")
        liste.heading("titre", text="Début du document")
        liste.heading("mots", text="Mots")
        liste.column("id", width=90, anchor="center")
        liste.column("titre", width=650)
        liste.column("mots", width=80, anchor="center")
        liste.pack(fill="both", expand=True, padx=8, pady=8)

        for doc_id, texte in list(self.documents.items())[:100]:
            mots = texte.split()
            titre = " ".join(mots[:18])
            liste.insert("", "end", iid=str(doc_id), values=(doc_id, titre, len(mots)))

        zone = tk.Text(fenetre, height=10, wrap="word")
        zone.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        def afficher_document(_event=None):
            selection = liste.selection()
            if not selection:
                return
            doc_id = selection[0]
            zone.delete("1.0", "end")
            zone.insert("1.0", self.documents[doc_id])

        liste.bind("<<TreeviewSelect>>", afficher_document)
        premier = liste.get_children()
        if premier:
            liste.selection_set(premier[0])
            afficher_document()

    def ouvrir_apercu_pipeline(self):
        if not self.documents:
            messagebox.showwarning("Attention", "Chargez d'abord des documents.")
            return

        fenetre = tk.Toplevel(self.root)
        fenetre.title("Aperçu du pipeline de prétraitement")
        fenetre.geometry("1000x760")

        choix = ttk.Frame(fenetre)
        choix.pack(fill="x", padx=10, pady=8)
        ttk.Label(choix, text="Document :").pack(side="left")
        selection_doc = ttk.Combobox(choix, state="readonly", values=list(self.documents.keys()))
        selection_doc.pack(side="left", padx=6)
        if self.documents:
            selection_doc.current(0)
        ttk.Button(choix, text="Exécuter l'aperçu", command=lambda: afficher_pipeline()).pack(side="left", padx=6)

        zone = tk.Text(fenetre, wrap="word")
        zone.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        def afficher_pipeline():
            doc_id = selection_doc.get()
            if not doc_id:
                return
            texte = self.documents[doc_id]
            zone.delete("1.0", "end")
            zone.insert("end", f"Document {doc_id} — texte brut\n")
            zone.insert("end", f"{len(texte.split())} mots\n{'-' * 70}\n")
            zone.insert("end", texte[:2500] + ("\n[Texte tronqué pour l'aperçu]\n" if len(texte) > 2500 else ""))
            zone.insert("end", "\n\n")

            for etape in self.get_etapes_actives():
                texte = pretraitement.FONCTIONS[etape](texte)
                zone.insert("end", f"{etape} — {len(texte.split())} mots\n")
                zone.insert("end", f"{texte[:2500]}\n")
                if len(texte) > 2500:
                    zone.insert("end", "[Résultat tronqué pour l'aperçu]\n")
                zone.insert("end", "\n" + "-" * 70 + "\n")

            tokens = pretraitement.appliquer_pipeline(
                self.documents[doc_id], self.get_etapes_actives()
            )
            zone.insert("end", f"\nTokens finaux : {len(tokens)}\n")
            zone.insert("end", " ".join(tokens[:200]))

        ttk.Button(choix, text="Document aléatoire", command=lambda: choisir_aleatoire()).pack(side="left", padx=6)

        def choisir_aleatoire():
            selection_doc.set(random.choice(list(self.documents.keys())))
            afficher_pipeline()

        afficher_pipeline()

    def generer(self):
        if not self.documents:
            messagebox.showwarning("Attention", "Veuillez d'abord charger des documents.")
            return

        etapes_actives = self.get_etapes_actives()
        t0 = time.time()

        docs_tokens = {}
        ids_docs = list(self.documents.keys())

        for doc_id, texte in self.documents.items():
            tokens = pretraitement.appliquer_pipeline(texte, etapes_actives)
            docs_tokens[doc_id] = tokens

        try:
            self.resultats = indexation.construire_index(docs_tokens, ids_docs)
        except ValueError:
            messagebox.showerror("Erreur", "Le vocabulaire est vide après prétraitement.")
            return

        self.etapes_indexees = etapes_actives.copy()
        self.label_sauvegarde.config(text="Index modifiés : sauvegardez-les à nouveau.", foreground="darkorange")
        stats = indexation.calculer_statistiques(self.resultats)
        t_total = time.time() - t0

        self.label_stats.config(
            text=(
                f"Documents : {stats['documents']} | "
                f"Vocabulaire : {stats['vocabulaire']} mots | "
                f"Mémoire totale : {stats['memoire_totale_mo']:.3f} Mo | "
                f"Temps de calcul : {t_total:.2f} s"
            )
        )

        for item in self.tree.get_children():
            self.tree.delete(item)

        for nom in ["bow", "f", "tf", "tfidf"]:
            modele = stats["modeles"][nom]
            self.tree.insert(
                "",
                "end",
                values=(
                    nom.upper(),
                    f"{modele['matrice_terme_doc_mo']:.3f}",
                    f"{modele['matrice_doc_terme_mo']:.3f}",
                    f"{modele['liste_inversee_mo']:.3f}",
                    f"{modele['gain_memoire']:.2f}x",
                ),
            )

        messagebox.showinfo("Succès", f"Index générés avec succès en {t_total:.2f} s !")

    def sauvegarder(self):
        if not self.resultats:
            messagebox.showwarning("Attention", "Veuillez d'abord générer les index.")
            return

        fenetre = tk.Toplevel(self.root)
        fenetre.title("Exporter les index")
        fenetre.geometry("410x190")
        fenetre.resizable(False, False)
        ttk.Label(fenetre, text="Choisir le format de l'archive :").pack(anchor="w", padx=14, pady=(14, 5))

        choix_format = ttk.Combobox(
            fenetre,
            state="readonly",
            values=("JSON — lisible", "Texte — matrices et postings", "Binaire — compact"),
        )
        choix_format.current(2)
        choix_format.pack(fill="x", padx=14, pady=5)
        ttk.Label(
            fenetre,
            text="L'archive ZIP contiendra les index, le vocabulaire et la configuration.",
            wraplength=375,
        ).pack(anchor="w", padx=14, pady=5)

        def choisir_fichier():
            formats = {
                "JSON — lisible": "json",
                "Texte — matrices et postings": "texte",
                "Binaire — compact": "binaire",
            }
            chemin = filedialog.asksaveasfilename(
                title="Enregistrer l'archive d'index",
                initialdir=self.chemin_sauvegarde or os.path.dirname(os.path.abspath(__file__)),
                initialfile="index_reuters.zip",
                defaultextension=".zip",
                filetypes=(("Archive ZIP", "*.zip"),),
            )
            if not chemin:
                return

            try:
                stockage.exporter_index_zip(
                    self.resultats,
                    chemin,
                    self.etapes_indexees or [],
                    formats[choix_format.get()],
                    {
                        "type": self.type_source.get(),
                        "nom": os.path.basename(self.chemin_corpus),
                    },
                )
            except (OSError, ValueError, TypeError) as erreur:
                messagebox.showerror("Erreur d'export", f"Impossible d'exporter les index :\n{erreur}")
                return

            self.chemin_sauvegarde = os.path.dirname(chemin)
            self.label_sauvegarde.config(text=f"Archive créée : {chemin}", foreground="darkgreen")
            fenetre.destroy()
            messagebox.showinfo("Export terminé", f"Archive créée avec succès :\n{chemin}")

        boutons = ttk.Frame(fenetre)
        boutons.pack(fill="x", padx=14, pady=10)
        ttk.Button(boutons, text="Annuler", command=fenetre.destroy).pack(side="right", padx=4)
        ttk.Button(boutons, text="Enregistrer le ZIP", command=choisir_fichier).pack(side="right", padx=4)

    def publier(self):
        if not self.documents:
            messagebox.showwarning("Attention", "Chargez un jeu de données avant de publier les paramètres.")
            return

        fenetre = tk.Toplevel(self.root)
        fenetre.title("Publier la configuration")
        fenetre.geometry("440x200")
        fenetre.resizable(False, False)
        ttk.Label(
            fenetre,
            text="Définissez la limite maximale de documents pour le futur module utilisateur.",
            wraplength=400,
        ).pack(anchor="w", padx=14, pady=(14, 8))

        ligne = ttk.Frame(fenetre)
        ligne.pack(fill="x", padx=14, pady=5)
        ttk.Label(ligne, text="Maximum autorisé :").pack(side="left")
        limite = ttk.Combobox(ligne, width=12, values=("10", "100", "500", "1000"))
        limite.set("1000")
        limite.pack(side="left", padx=8)

        ttk.Label(
            fenetre,
            text="Cette action enregistre publication.json localement. Elle ne publie pas sur un serveur.",
            wraplength=400,
        ).pack(anchor="w", padx=14, pady=5)

        def enregistrer_publication():
            try:
                maximum = int(limite.get())
            except ValueError:
                messagebox.showerror("Valeur incorrecte", "La limite doit être un nombre entier.")
                return
            if maximum <= 0 or maximum > 1000:
                messagebox.showerror("Valeur incorrecte", "La limite doit être comprise entre 1 et 1000.")
                return

            chemin = filedialog.asksaveasfilename(
                title="Enregistrer la configuration publiée",
                initialdir=self.chemin_sauvegarde or os.path.dirname(os.path.abspath(__file__)),
                initialfile="publication.json",
                defaultextension=".json",
                filetypes=(("Fichier JSON", "*.json"),),
            )
            if not chemin:
                return

            try:
                stockage.publier_configuration(
                    chemin,
                    self.type_source.get(),
                    os.path.basename(self.chemin_corpus),
                    self.get_etapes_actives(),
                    maximum,
                )
            except (OSError, ValueError) as erreur:
                messagebox.showerror("Erreur de publication", str(erreur))
                return

            fenetre.destroy()
            messagebox.showinfo(
                "Paramètres enregistrés",
                f"Configuration enregistrée localement :\n{chemin}\n\n"
                "Elle pourra servir de paramètres par défaut au module de recherche de la phase 2.",
            )

        boutons = ttk.Frame(fenetre)
        boutons.pack(fill="x", padx=14, pady=10)
        ttk.Button(boutons, text="Annuler", command=fenetre.destroy).pack(side="right", padx=4)
        ttk.Button(boutons, text="Enregistrer", command=enregistrer_publication).pack(side="right", padx=4)

    def chercher(self):
        if not self.resultats:
            messagebox.showwarning("Attention", "Veuillez d'abord générer les index.")
            return

        mot_brut = self.entry_mot.get().strip()
        if not mot_brut:
            return

        etapes = self.etapes_indexees if self.etapes_indexees is not None else self.get_etapes_actives()
        tokens = pretraitement.appliquer_pipeline(mot_brut, etapes)
        if not tokens:
            self.zone_texte.delete("1.0", "end")
            self.zone_texte.insert("1.0", "Le mot a été éliminé par le pipeline.")
            return

        mot = tokens[0]
        liste_inv = self.resultats["tfidf"]["liste_inversee"]

        self.zone_texte.delete("1.0", "end")
        if mot in liste_inv:
            postings = liste_inv[mot]
            self.zone_texte.insert("end", f"Mot retenu : '{mot}' ({len(postings)} documents)\n\n")
            for doc_id, poids in postings[:20]:
                self.zone_texte.insert("end", f"  Doc ID {doc_id} -> Poids TF-IDF : {poids:.4f}\n")
        else:
            self.zone_texte.insert("end", f"Le mot '{mot}' n'apparaît dans aucun document.")

    def demarrer(self):
        self.root.mainloop()
