from matplotlib import pyplot as plt
import streamlit as st
import traitement_baacFP as tb
import streamlit_folium

st.set_page_config(page_title="Application BAAC", page_icon="🚗", layout="wide")

st.title("Dashboard BAAC 2021")
    
with st.sidebar:
    st.header("Sélection pages")
    
    option_affichage = st.sidebar.radio(
        "Choisissez l'affichage",
        ('Général', 'Usager', 'Véhicule','Lieux','Machine Learning')
    )   
    
    

# Style for containers
st.markdown(
    """
    <style>
    .data-container {
        border: 1px solid #e1e4e8;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        background-color: #f6f8fa;
    }
    
    .head-data-container {
        color: #ffffff;
        background-color: #0078D4;
        padding: 20px 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        background-size: cover;
        background-position: center;
        }
    
    .data-value {
        font-size: 1.5em;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

nb_acc = len(set(tb.accident_metr['Num_Acc']))
nb_veh = len(set(tb.accident_metr.id_vehicule))
nb_victime = tb.accident_metr[tb.accident_metr['grav']!='4'].shape[0]

with col1:
    st.markdown(f"<div class='head-data-container'>Nombre d'accidents 💥<div class='data-value'>{nb_acc}</div></div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='head-data-container'>Nombre de véhicules impliqués 🚗<div class='data-value'>{nb_veh}</div></div>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<div class='head-data-container'>Nombre de victimes blessées 👤<div class='data-value'>{nb_victime}</div></div>", unsafe_allow_html=True)


if option_affichage == 'Général':
    col1, col2 = st.columns([2, 1.5])
    
    st.sidebar.var_map = st.sidebar.selectbox(
        "Sélectionnez le type de données à afficher sur la carte",
        ('accident dep', 'gravite')
    )
    
    st.sidebar.var_com = st.sidebar.text_input("Entrez un numéro de commune:", value = '75110')
        
    with col1:
        with st.spinner('Chargement de la carte...'):
            streamlit_folium.folium_static(tb.map_accident(st.sidebar.var_map, st.sidebar.var_com), width=800, height=590)
            
    with col2:
        streamlit_folium.folium_static(tb.map_accident_commune(st.sidebar.var_com), width=590, height=300)
        
        dataframe_height = 270
        dataframe_width = 700
        
        option = st.sidebar.radio("Tableau de données:", ('Commune', 'Département'))

        if option == 'Commune':
            # Cas 1
            df_com = tb.accident_metr[tb.accident_metr['com'] == st.sidebar.var_com]
            st.dataframe(df_com, height=dataframe_height, width=dataframe_width)

        elif option == 'Département':
            # Cas 2
            if st.sidebar.var_map == "accident dep":
                df_to_display_full = tb.accident_nb.copy()
                if 'geometry_dep' in df_to_display_full.columns:
                    df_to_display_full['geometry_dep'] = df_to_display_full['geometry_dep'].astype(str)
                st.dataframe(df_to_display_full, height=dataframe_height, width=dataframe_width)
            elif st.sidebar.var_map == "gravite":
                df_to_display_full = tb.accident_grav.copy()
                if 'geometry_dep' in df_to_display_full.columns:
                    df_to_display_full['geometry_dep'] = df_to_display_full['geometry_dep'].astype(str)
                st.dataframe(df_to_display_full, height=dataframe_height, width=dataframe_width)
    
    #Alterner accident et gravité
    with st.expander("Commentaire"):
        st.markdown(f"<b>Description</b>: La cartographie principale permet de constater le nombre d'accidents enregistrés dans la base BAAC par département. La deuxième carte permet de visualiser la localisation des accidents ayant eu lieu dans la commune n°{st.sidebar.var_com}. <br> <b>Analyse: Les accidents ont lieu en majorité sur des grands axes: Boulevard Magenta et Rue de Lafayette dans le 10ème,Voltaire 11ème ou Quai de Bercy et Périphérique dans le 12ème. L'apport de cette zone de périphérique limité à 70 km/h va être intéressante par rapport aux 10ème et 11ème  qui on plus de zones limités à 30km/h par exemple. En regardant la France entière, on a plus d'accidents au 2ème semestre de l'année (ne pas oublier l'effet confinement en début 2021),à 75% avec une météo normale. On a plus d'accidents dans les grandes agglomérations, mais la gravité est plus forte dans des départements plus ruraux </b> ", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 8])
    
    with col1:
        time_option = st.radio(
            "Choisissez la période:",
            ('month', 'day')
        )
        
    with col2:
        st.plotly_chart(tb.graph_datetime(time_option), use_container_width=True)
    
    col1, col2 = st.columns([3, 8])
    
    with col1:
        loc = st.text_input("Entrez une commune ou un département:", value = '75110')
    with col2:
        st.plotly_chart(tb.chart_meteo_loc(loc), use_container_width=True)
        
        
elif option_affichage == 'Usager':
    col1, col2 = st.columns([3,2])
    with col1:
        loc1 = st.text_input("Entrez une commune ou un département:", value = '75110')
        st.plotly_chart(tb.plot_accidents_by_age_and_sex(loc1), use_container_width=True)
        loc2 = st.text_input("Entrez une commune ou un département:", value = '75111')
        st.plotly_chart(tb.plot_average_gravity_by_age_and_sex(loc2), use_container_width=True)
        loc3 = st.text_input("Entrez une commune ou un département:", value = '75112')
        st.plotly_chart(tb.plot_gravity_by_age_sex_manoeuvre(loc3), use_container_width=True)
    with col2:
        st.markdown(f"<b>Description</b>:Intéressons nous maintenant au profil des conducteurs(âge et sexe) causant un accident </b> <br> <b>Analyse: On retrouve pour chaque arrondissemnt beaucoup plus d'accidents causés par les hommes (sexe1) et le nombre décroit avec l'âge. Pour la gravité, on la retrouve plus sur des femmes, et surtout aux âges petits et grands. Le type de manouevre qui cause l'accident  est difficilement analysable avec un échantillon trop petit par type </b> ", unsafe_allow_html=True)

elif option_affichage == 'Véhicule':
    col1, col2 = st.columns([3,2])
    with col1:
        loc1 = st.text_input("Entrez un commune ou un département:", value = '75110')
        st.plotly_chart(tb.plot_accidents_by_obst_fixe(loc1), use_container_width=True)
        loc2 = st.text_input("Entrez un commune ou un département:", value = '75111')
        st.plotly_chart(tb.plot_accidents_by_obst_mobile(loc2), use_container_width=True)
        loc3 = st.text_input("Entrez un commune ou un département:", value = '75112')
        st.plotly_chart(tb.plot_accidents_by_type_veh(loc3), use_container_width=True)
    with col2:
        st.markdown(f"<b>Description</b>:Regardons les accidents selon le type d'obstable et les types de véhicules impliqués </b> <br> <b>Analyse: Pour le 10ème et 11 ème , on a à 70% des obstacles mobiles qui sont des véhicules(types 2)  et 85% dans le 12ème (effet périférique?), le reste est principalement des piétons (type 1). Pour les obstacles fixes, c'est beaucoup plus dispersé avec une majorité de piéton 40% dans le 11 et 12 et 25% dans le 10ème,le type d'obstacle est beaucoup plus disparate dans cet arrondissment, surement car il est plus dense, avec zones à risques. Concernant le type de véhicule, on a en grande majorité du 7, puis du 1 et 10  </b> ", unsafe_allow_html=True)
        
        
        
elif option_affichage == 'Lieux':
    col1, col2 = st.columns([3,2])
    with col1:
        loc1 = st.text_input("Entrez un commune ou un département:", value = '75110')
        st.plotly_chart(tb.plot_accidents_by_type_route(loc1), use_container_width=True)
        loc2 = st.text_input("Entrez un commune ou un département:", value = '75111')
        st.plotly_chart(tb.plot_accidents_by_surface(loc2), use_container_width=True)
        loc3 = st.text_input("Entrez un commune ou un département:", value = '75112')
        st.plotly_chart(tb.plot_accidents_by_vitesse(loc3), use_container_width=True)
    with col2:
        st.markdown(f"<b>Description</b>:Cette Partie s'intéresse aux accidents par rapport à l'état de la route et aux vitesses autorisés </b> <br> <b>Analyse:On remarque que dans le 12ème, le type de route 1 à moins d'accidents, le 10 ème et 11ème n'ont que du type 4. On a nettement plus d'accidents partout sur la surface 1. Pour la vitesse, dans le 11ème et 10 ème il y a des zones à 30km avec beaucoup de traffic de piétons. On remarque que les zones 30 ont plus d'accidents que les 50. Pour le 12ème, avec le périphérique à 70, on ne voit pas forcément beacoup plus de sinistres qu'aux zones 30, sûrement dans le bois de Vincennes, peut être un non-respect des limites de vitesse.   </b> ", unsafe_allow_html=True)
elif option_affichage == 'Machine Learning':  
    st.write("Prédiction KNN à partir de l'année de naissance , de la vitesse autorisée, de la gravité et du sexe")
    k = int(st.slider("Choisissez le nombre de voisins (k)", 1, 15, 3))
    vitesse = int(st.slider("vitesse autorisée", 30,110,50))
    sexe = int(st.slider("sexe", 1,2))
    année_naissance = int(st.slider("année de naissance", 1940, 2023, 1980))
    gravité = int(st.slider("gravité", 1, 4, 2))
    accuracy,prediction=tb.predictionKNN(k,sexe,année_naissance,gravité,vitesse)
    st.write(f"Précision du modèle : {accuracy:.2f}")
    st.write(f"La classe prédite est : {prediction[0]}")
    # Création d'un graphique de dispersion (scatter plot)
    
    fig, ax = plt.subplots()
    ax.scatter(tb.X_test.iloc[:, 0].values, tb.X_test.iloc[:, 3].values, c=tb.y_pred, cmap='viridis', marker='o', edgecolor='k')

    # Légende du graphique
    legend = ax.legend(*plt.scatter.legend_elements(), title="Classes")
    ax.add_artist(legend)

    # Axes du graphique
    ax.set_xlabel('vitesse')
    ax.set_ylabel('gravité')
    ax.set_title('Prédictions du modèle K-NN')

    # Affichage du graphique dans Streamlit
    st.pyplot(fig)
#streamlit run c:\users\hugo.razafindralambo\.spyder-py3\dashboard_baac.py

# Résumé du streamlit:
# 2 pages: Cartographie et données départementales.
# Page Cartographie:
    # Visualisation géographique: On peut voir nb d'accident par département ou gravité (ou par commune mais bug).
    # Visualisation temporelle: On peut voir la distribution des accidents par jour ou mois.
# Page Graphiques sur les données départementales:
    # On peut voir la distribution de chaque variable par département choisi.
    # Rajouter graphique circulaire ?

# Rajouter textes 

