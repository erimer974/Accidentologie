import streamlit as st
import json
import pandas as pd
#import numpy as np

#from sklearn.decomposition         import PCA
#from sklearn.preprocessing         import StandardScaler

import seaborn as sns
import matplotlib.pyplot as plt

# TODO  activer après compilation de tensorflow
# import tensorflow as tf

import joblib

from st_demo import st_demo

rep_raw = "data/raw/"
rep_processed = "data/processed/"
rep_models = "models/"
rep_figures = "reports/figures/"
rep_ref = "references/"

st.sidebar.title("Sommaire")

pages=["Présentation",      # 0
       "Le jeu de données", # 1
       "Visualizations",    # 2
       "Preprocessing",     # 3
       "Modélisations",     # 4
       "Essai SVC",         # 5
       "Démonstration"]     # 6
page=st.sidebar.radio("Aller vers", pages)                #
st.sidebar.write("Erika Méronville\n&\nEmmanuel Gautier")


##############################################################################
#
# Chargements en mémoire
#
# Ces chargements sont réalisés par des fonction décorées par @st.cache_data
# pour que les lectures soient réalisées une seule fois.
#
##############################################################################

# Lecture des modèles entraînés

@st.cache_data
def read_models():

    SVC, pca, scaler_ml, scaler_DP = None, None, None, None

    try:
        SVC       = joblib.load(rep_models + "SVC.mdl")
        pca       = joblib.load(rep_models + "pca_ml.mdl")
        scaler_ml = joblib.load(rep_models + "acc_scaler.mdl")
        scaler_DP = joblib.load(rep_models + "scaler_DP.joblib")

    except Exception as e:
        st.error(f"Erreur lors du chargement du modèle: {str(e)}")

    return SVC, pca, scaler_ml, scaler_DP

# Lecture du jeu de données avec une observation à zero
# ce jeu de données avec une seule observation est utilisé par la démo.

@st.cache_data
def read_df_zero():

    df_zero = None

    try:
        df_zero = pd.read_csv(rep_processed + "data_zero.csv", sep='\t')

    except Exception as e:
        st.error(f"Erreur lors du chargement du jeu de données vide : {str(e)}")

    return df_zero

# Lecture du jeu de données avec une observation à zero

@st.cache_data
def read_stats_ech():

    df_evol_grav, stats_expl_var = None, None

    try:
        df_evol_grav   = pd.read_csv(rep_processed + "evol_grav.csv", sep='\t')
        stats_expl_var = pd.read_csv(rep_processed + "stats_expl_var.csv", sep='\t')
        ech_dfc = pd.read_csv(rep_raw + "ech_caracteristiques.csv", sep = ',')
        ech_dfl = pd.read_csv(rep_raw + "ech_lieux.csv", sep = ',')
        ech_dfu = pd.read_csv(rep_raw + "ech_usagers.csv", sep = ',')
        ech_dfv = pd.read_csv(rep_raw + "ech_vehicules.csv", sep = ',')

    except Exception as e:
        st.error(f"Erreur lors du chargement du jeu de données : {str(e)}")

    return df_evol_grav, stats_expl_var, ech_dfc, ech_dfl, ech_dfu, ech_dfv

@st.cache_data
def read_info():

    desc_fic_raw, desc_vars = None, None

    try:
        with open(rep_ref + "desc_fic_raw.json", 'r', encoding='utf-8') as fichier:
            desc_fic_raw = json.load(fichier)

        with open(rep_ref + "desc_vars.json", 'r', encoding='utf-8') as fichier:
            desc_vars = json.load(fichier)

    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier d'information : {str(e)}")

    return desc_fic_raw, desc_vars

desc_fic_raw, desc_vars = read_info()

##############################################################################
#
# En-tête : Titre du projet
#
##############################################################################

st.title ("Accidentologie")

##############################################################################
#
# Page : Présentation du projet
#
##############################################################################

if page == pages[0] :
    st.header("Présentation du projet")
    st.subheader("Notre mission")
    st.write(
"""
Nous présentons notre projet de machine learning réalisé lors de notre formation dispensée par DataScientest.

ce projet porte sur le thème des accidents de la route en France au cours de la période de 2005 à 2022.
Les données ainsi que leur description sont disponibles sur le site www.data.gouv.fr.

Ces données concernent 72 dataframes au total, soit 1 dataframe par année et par rubrique.
Un changement de codage de la gravité entre 2018 et 2019 nous contraint de ne retenir que les données de 2019 à 2022, soit les quatre dernières années.

Notre mission consiste à explorer, préparer et modéliser le jeu de données dans le but de prédire
la gravité des accidents routiers en fonction des circonstances qui les entourent.
"""
)
    st.subheader("Notre progression")
    st.write(
"""
    Nous avons déjà réalisé l'exploration, la préparation et la modélisation des données.
    Ce travail doit être accessible à tous, c'est l'objet de cette présentation avec streamlit en cours de réalisation.

    C'est un travail en cours de réalisation; nous développons en ce moment à l'affichage
    de prédictions avec  des valeurs saisies et ramanions le code.

    Avec ce projet nous mettons en pratique les acquis de notre formation en réalisant un projet de data science complet.
"""
)


##############################################################################
#
#  Le jeu de données
#
##############################################################################

if page == pages[1]:
    st.header("Le jeu de données")
    st.markdown(
"""
Ces données concernent 72 dataframes au total, soit 1 dataframe par année et par rubrique.
Un changement de codage de la gravité entre 2018 et 2019 nous contraint
à ne retenir que les données de 2019 à 2022, soit les quatre dernières années.
Les données sont réparties dans les 4 rubriques suivante :

* caracteristiques : qui prend en compte les circonstances générales de l’accident.
* lieux : qui décrit l’endroit de l’accident.
* vehicules : qui énonce les véhicules impliqués dans l’accident.
* usagers : qui relate les usagers impliqués dans l’accident.
"""
    )
    st.image("reports/figures/diagramme.svg", caption = "Diagramme données", width = 1000)

##############################################################################
#
# Page : Visualisation des données
#
##############################################################################

if page == pages[2]:

    df_evol_grav, stats_expl_var, ech_dfc, ech_dfl, ech_dfu, ech_dfv = read_stats_ech()

    st.header("Visualisation du jeu de données")

    st.subheader("Évolution sur 19 ans des nombres d'usagers impliqués")

    df_base100 = df_evol_grav
    df_base100["grav_1"] = 100. * df_base100["grav_1"] / df_base100.loc[0, "grav_1"]
    df_base100["grav_2"] = 100. * df_base100["grav_2"] / df_base100.loc[0, "grav_2"]
    df_base100["grav_3"] = 100. * df_base100["grav_3"] / df_base100.loc[0, "grav_3"]
    df_base100["grav_4"] = 100. * df_base100["grav_4"] / df_base100.loc[0, "grav_4"]
    # st.dataframe(df_base100)
    #st.write(f"Base grav_1 {df_base100.loc[0, 'grav_1']}")
    fig = plt.figure(figsize=(10, 6))
    sns.lineplot(data=df_base100 , x='annee', y='grav_1', label = "Indemmes", color = "green")
    sns.lineplot(data=df_base100 , x='annee', y='grav_2', label = "Tués", color = "red")
    sns.lineplot(data=df_base100 , x='annee', y='grav_3', label = "blessé hospitalisé", color = "orange")
    sns.lineplot(data=df_base100 , x='annee', y='grav_4', label = "blessé léger", color = "blue")
    plt.title("Évolution des nombres de personnes impliquées\ndans un accident de circulation selon la gravité")
    plt.xlabel("Année")
    plt.xticks (df_base100["annee"])
    plt.ylabel("Pourcentage")
    plt.legend(title='Modalités', loc = "upper center")
    plt.axvline(x=2019, color='black', linestyle=(0, (5, 5)), linewidth=2)
    plt.annotate("Changement\nde codification\nde notre var. cible", xy=(2019, 90),
                 xytext = (2019.5, 95),
                 arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.5))

    plt.annotate("Effet COVID",
                 xy=(2020, 65),
                 xytext=(2019, 75),
                 arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.5))

    plt.grid()
    st.pyplot(fig)
    annee = df_evol_grav["annee"].max()
    annee = st.selectbox("Année : ", df_evol_grav["annee"])

    mod_grav_nb = df_evol_grav[df_evol_grav["annee"] == annee][["grav_1", "grav_2", "grav_3", "grav_4"]]

    fig = plt.figure(figsize=(10, 6))
    plt.title("Répartition de la gravité")

    mod_grav_nb = mod_grav_nb.rename(columns = {"grav_1" : "Indemne", "grav_2" : "Tués",
                         "grav_3" : "Blessés hospitalisés", "grav_4" : "Blessés legers"})
    sns.barplot (mod_grav_nb)
    #plt.ylim(0, df_evol_grav[["grav_1", "grav_2", "grav_3", "grav_4"]].max())
    plt.ylim(0, df_evol_grav["grav_1"].max())

    st.pyplot(fig)

    #
    # Affichages pour chaque rubrique d'un échantillon et de quelques statistiques
    #

    lst_rub = {"usagers": {"df" : ech_dfu, "label" : "usagers"},
               "caracteristiques": {"df" : ech_dfc, "label" : "caractéristiques"},
               "lieux": {"df" : ech_dfl, "label" : "lieux"},
               "vehicules": {"df" : ech_dfv, "label" : "véhicules"}}

    for rub_clef, rub_desc in lst_rub.items():
        st.subheader(rub_clef)

        # Affichage de l'échantillon de données de la rubrique
        st.write("Échantillon des données de la rubrique")
        st.dataframe(rub_desc["df"])

        # Affichage d'un graphique de répartition d'une modalité
        variables = stats_expl_var[stats_expl_var["rubrique"] == rub_desc["label"]]["variable"].unique()
        variables_lib = [] # Liste des variables avec les libellés explicites
        for v in variables:
            if desc_vars[v].get("label") is not None:
                variables_lib.append(v + " : " + desc_vars[v].get("label"))
            else:
                variables_lib.append(v + " : ")
        chx_variable = st.selectbox("Variable : ", variables_lib)
        variable_df   = chx_variable.split(" : ")[0]
        variable_expl = chx_variable.split(" : ")[1]

        df1 = stats_expl_var[(stats_expl_var["rubrique"] == rub_desc["label"]) & (stats_expl_var["variable"] == variable_df)]
        df1["count"] = df1["count"].astype("int")
        df1 = df1[["modalite", "count"]]
        # st.dataframe (df1) # pour mise au point, à supprimer

        fig = plt.figure(figsize=(10, 6))
        plt.title(f"Répartition selon {chx_variable}")

        sns.barplot (df1, y = "modalite", x= "count", orient = "h")

        st.pyplot(fig)


##############################################################################
#
# Page : Pré processing
#
##############################################################################

if page == pages[3]:

    # Choix du type de preprocessing
    liste_preprocessing = ['Première Preprocessing', 'Deuxième Preprocessing']
    choix_preprocessing = st.radio('Choix du Preprocessing', liste_preprocessing)

    if choix_preprocessing == liste_preprocessing[0]:
        st.write(liste_preprocessing[0])
        with st.expander("Le premier preprocessing"):
            st.image (rep_figures + "preprocessing_10.png")

    if choix_preprocessing == liste_preprocessing[1]:
        st.write(liste_preprocessing[1])
        st.write("""
    La faible proportion de tués (2,64%) nous incite à regrouper les modalité de la cible
    en deux modalités "grave" et "non grave", la modalité grave correspond alors au Tués et hospitalisés plus de 24h.
    La modalité grave est plus équilibrée et représente alors 18% des observations. 
    Nous décidons d'équilibrer notre jeux de données pour que chaque modalité de la cible soit également représentée
    en échantillonnant (avec RandomUnderSampler()) les observations "non graves".
    Cet équilibrage permet aussi de réduire les temps d'entraînement.
        """)
        with st.expander("Preprocessing") :
            st.image (rep_figures + "preprocessing_21.png")

        with st.expander("Preprocessing") :
            st.image (rep_figures + "preprocessing_22.png")


##############################################################################
#
# Modélisations : LR, SVC et DP
#
##############################################################################

if page == pages[4] :

    st.header("Un problème de classification")
    st.write ("""
    Notre objectif est de déterminer la gravité des accidents de la circulation 
    pour les usagers en fonction des circonstances. 
    Notre variable cible (grav) indique la gravité et comporte 4 les modalités suivantes :
    "Indemne", "Hospitalisé moins de 24h", "hospitalité plus de 24h" et "Tué". 
    De nombreuses variables explicatives sont des variables catégorielles.
    C'est un problème de classification et entreprenons l'entraînement de modèles de classification.
    """)
    st.header("régression logistique : premier essai")
    st.write("""
    Nous réalisons un premier essai avec une régression logistique (LR) et les 4 modalités de notre variable cible.
    Cette modélisation obtient des scores insuffisants avec des scores faibles de 59% seulement.
    """)
    st.header("Machine learning : la recherche de performance ")
    st.write("""
    Nous utilisons le jeu de données issu du deuxième preprocessing avec un cible binaire
    ("grave" ou "non grave") et équilibrée et des variables explicatives dichotomisées.
    Le nombre important de variables explicatives ()
    
    Un premier essai avec lazypredict, pour voir, nous donne quelques indications sur les performances.
    Nous essayons 11 modèles : des modèles découverts dans les cours, LGBM et même dummy proposés par lazypredict,
    dummy est essayé pour comparaisons.
    
    Le jeu de données contient environ 260 variables explicatives, ce nombre est très important
    nous décidons alors d'appliquer une PCA.
    Après avoir appliqué la PCA nous normalisons le jeu de données de dimension réduite.
    Deux graphiques nous aident à choisir le nombre de composantes
    en affichant la variance expliquée par nombre de composantes.
    Nous choisissons 100 composantes afin afin d'avoir au moins 90% de variance expliquée
    pour ne pas diminuer les performances des modèles. 
    """)
    st.image(rep_figures + "choix_PCA.png")

    st.write("""
    Nous entraînons alors les modèles. Le code utilise un dictionnaire des modèles avec les paramètres à essayer
    une boucle d'essais avec GridSearchCV et des affichages de nombreuses métriques. Le dictionnaire a permis
    très simplement d'ajouter des modèles et de faire des essais de paramètres. Nous affichons de nombreuses métriques
    pour les étudier, finalement le graphe des vrais/faux positifs/négatifs nous paraît le plus clair.
    """)
    st.write("""
    Le modèle SVC semble le plus performant pour trouver "le plus sûrement"
    les causes d'accident graves pour les usagers, il a le meilleur recall (82%) la plus faible proportion de
    faux négatifs; il présente toutefois un surapprentissage trop important.
    le modèle LGBM a des score proches et un faible surapprentissage; il a l'avantage d'être très rapide à entraîner
    et d'occuper peu de place sur le disque.
    """)
    st.image(rep_figures + "comparaison_scores.png")
    st.image(rep_figures + "evaluation_performances.png")

    st.write ("""
    Enfin, pour évaluer les modèles et vérifier la cohérence des prédictions avec les variables explicatives
    nous utilisons SHAP pour afficher leurs liens sur un graphique.
    Il apparaît très clairement que le port du casque ou de la ceinture de sécurité
    sont les éléments les plus importants pour éviter les conséquences graves. 
    """)
    st.image(rep_figures + "shap_summary_LGBM.png")

    st.header("Machine learning : un modèle plus efficace")
    st.write("""
    
    """)

    st.image(rep_figures + "feature_importance.png")
    st.image(rep_figures + "shap_summary_plot.png")
    st.image(rep_figures + "training_history.png")

##############################################################################
#
# Page : Démonstration ML
#
# Cette page présente :
#  - des choix de circonstances;
#  - ? ? ? le choix du modèle  ? ? ?;
#  - Les valeurs données au modèle ;
#  - la prédiction de la gravité avec le ou les modèles;
#  - la probabilité de la gravité
#
##############################################################################

if page == pages[5]:
    st.write("### Modélisation par Deep Learning")

    SVC, pca, scaler_ml, scaler_DP = read_models()

    X_zero = read_df_zero()
    X_zero = X_zero.drop("grav_grave", axis = 1)
    #X_zero = X_zero.drop("agg", axis = 1)
    Xp = X_zero.copy()

    choix = {} # Liste des choix de modalités ou circonstances
    choix_inv = {} # Dictionnaires qui permet de retrouver  les noms de variables
                   # à partir des libellés retournés par les st.selectbox()
                   # Cela sera plus rapide que de rechercher les clefs à partir de valeurs

    # La liste des choix des variables est dans le dictionnaire lst_var_pred
    # Ce dictionnaire est complété, avec les informations de desc_var.json
    #  L'ajout ou la suppression de variables se fait en modifiant la liste suivante
    lst_var_pred = {"secu" : {}, "choc" : {}, "obs" : {}, "obsm" : {}, "catv" : {}, "trajet" : {}, "jour" : {}}

    for var in lst_var_pred.keys():
        lst_var_pred[var]["modalites"] = {}
        label_var = desc_vars[var].get("label")
        lst_var_pred[var]["libelle"] = label_var
        choix_inv[label_var] = {"var" : var, "mod" : {}}
        for col in X_zero.columns:
            if col.startswith(var + "_"):
                #lst_var_pred[var]["modalites"].append(desc_vars.get(col).get("label"))
                clef = col.split("_")[0]
                modalite = col.split("_")[1]
                #st.write(f" clef : {clef} modalité {modalite}\n")
                label = desc_vars.get(col).get("label").split(" : ")[1]
                code_label = desc_vars.get(col).get("name")
                lst_var_pred[var]["modalites"][modalite] = label
                choix_inv[label_var]["mod"][label] = code_label

    # st.write(lst_var_pred) # Pour mise au point

    # Création des choix de modalités
    # à partir du dictionnaire des choix
    for clefs, item in lst_var_pred.items():
        libelle = item["libelle"]
        #st.write(f"Choix : {libelle}\n") # Pour mise au point
        #st.write(f"modalités : {item['modalites']}\n") # Pour mise au point
        choix_mod = []
        #choix_mod_clef = []
        for mod, lib_mod in item["modalites"].items():
            choix_mod.append(lib_mod)
            #choix_mod_clef.append(mod)
        choix[libelle] = st.selectbox(libelle, choix_mod, placeholder="Choisissez une option", index = None)

    # Récupération des choix de l'utilisateur
    # Les choix sont dans les menus de type st.selectbox() enregistrés dans choix
    for lib, mod in choix.items():
        #st.write(f"{lib} : {mod}")
        #choix_inv[label_var]["mod"][label] = code_label
        nom_var_sel = choix_inv[lib]['mod'].get(mod)

        #st.write(f"   ----:: {choix_inv[lib]['mod'].get(mod)}")
        #st.write(f"   ----> {nom_var_sel}")
        if nom_var_sel is not None:
            Xp[nom_var_sel] = 1

        # lib et mod contiennent les libellés des variables et les libellés des modalités.
        # il faut retrouver les noms d'origine des
        #st.write(f" Modalité : {mod} {lib}")
        #for
        #desc_vars.valu

    #st.write(f" ---->  {choix_inv}\n")

    st.dataframe(Xp)

    for col in Xp.columns:
        # st.write (f" colonne : {col}")
        if Xp.loc[0, col] != 0:
            st.write (f"{col} : {desc_vars[col].get('label')}")


    st.write(f"Mise à l'échelle")
    Xp = scaler_ml.transform(Xp)
    st.write(f"PCA")
    Xp = pca.transform(Xp)
    st.write(f"Prédiction")
    pred = SVC.predict(Xp)

    st.write(f"Prédiction : {pred}")

    #Xp = scaler_DP.transform(Xp)

    st.write ("Développement en cours")

    # TODO Activer après compilation de tensorflow
    #ypred = DP.predict(Xp)

    #st.write(f"Prédiction : {ypred}")

##############################################################################
#
# Page : Démonstration avec deep learning
#
# Cette page présente :
#  - des choix de circonstances;
#  - ? ? ? le choix du modèle  ? ? ?;
#  - Les valeurs données au modèle ;
#  - la prédiction de la gravité avec le ou les modèles;
#  - la probabilité de la gravité
#
##############################################################################

if page == pages[6]:
   st_demo()
