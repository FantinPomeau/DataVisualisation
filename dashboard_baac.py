from matplotlib import pyplot as plt
import streamlit as st
import traitement_baac as tb
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
        background-image: url("C:/Users/hugo.razafindralambo/OneDrive - ADDACTIS GROUP/Bureau/Personnel/Datavis/baac/injury-leave-icon-with-png-and-vector-format-for-free-unlimited-920509.png");
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
            streamlit_folium.folium_static(tb.map_accident(st.sidebar.var_map, st.sidebar.var_com), width=800, height=594)
            if st.sidebar.var_map == 'accident dep':
                with st.expander("Commentaire"):
                    st.markdown(f"<b>Description</b>: La cartographie principale permet de constater ici le nombre d'accidents enregistrés dans la base BAAC par département."
                                + "<br> <b>Analyse:</b> On peut observer que les départements ayant les plus grandes densité de population (et les plus grandes villes comme Paris, Lyon, Marseille) semblent avoir un nombre plus élevé d'accidents en raison d'une population plus élevée et donc d'un plus grand nombre de véhicules en circulation.", unsafe_allow_html=True)
            else:
                with st.expander("Commentaire"):
                    st.markdown(f"<b>Description</b>: La cartographie principale permet de constater ici la gravité moyenne des accidents par département. [Revoir]"
                                + "", unsafe_allow_html=True)
            
    with col2:
        streamlit_folium.folium_static(tb.map_accident_commune(st.sidebar.var_com), width=590, height=300)
        
        dataframe_height = 270
        dataframe_width = 700
        
        option = st.sidebar.radio("Tableau de données:", ('Commune', 'Département'))

        if option == 'Commune':
            # Cas 1
            df_com = tb.accident_metr[tb.accident_metr['com'] == st.sidebar.var_com]
            st.dataframe(df_com, height=dataframe_height, width=dataframe_width)
            
            with st.expander("Commentaire"):
                st.markdown(f"<b>Description</b>: La deuxième carte permet de visualiser la localisation géographique des accidents ayant eu lieu dans la commune n°{st.sidebar.var_com}."
                            + "<br> <b>Analyse:</b> On peut observer que les départements ayant les plus grandes densité de population (et les plus grandes villes comme Paris, Lyon, Marseille) semblent avoir un nombre plus élevé d'accidents en raison d'une population plus élevée et donc d'un plus grand nombre de véhicules en circulation."
                            + "Les accidents semblent avoir souvent lieu près des croisements.", unsafe_allow_html=True)
            

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
                
            with st.expander("Commentaire"):
                st.markdown(f"<b>Description</b>: La cartographie principale permet de constater le nombre d'accidents enregistrés dans la base BAAC par département. La deuxième carte permet de visualiser la localisation des accidents ayant eu lieu dans la commune n°{st.sidebar.var_com}."
                            + "<br> <b>Analyse:</b> On peut observer que les départements ayant les plus grandes densité de population (et les plus grandes villes comme Paris, Lyon, Marseille) semblent avoir un nombre plus élevé d'accidents en raison d'une population plus élevée et donc d'un plus grand nombre de véhicules en circulation.", unsafe_allow_html=True)
            
    
    #Alterner accident et gravité
    
    
    col1, col2 = st.columns([1, 8])
    
    with col1:
        time_option = st.radio(
            "Choisissez la période:",
            ('month', 'day')
        )
        
    with col2:
        st.plotly_chart(tb.graph_datetime(time_option), use_container_width=True)
    
    with st.expander("Commentaire"):
        if time_option == 'month':
            time_graph = 'mois'
        else:
            time_graph = 'jour'
        
        st.markdown(f"<b>Description</b>: Ce graphique donne l'évolution du nombre d'accident par {time_graph} dans l'ensemble de la France métropolitaine."
        + "<br><b>Analyse:</b>  Il y a une tendance générale à la hausse du nombre d'accidents de janvier à juillet, avec un pic en juillet. Cela pourrait correspondre à une augmentation des déplacements pendant les mois d'été, notamment en raison des vacances et des voyages de loisirs. Le trafic plus dense et l'augmentation des longs trajets peuvent contribuer à cette hausse.", unsafe_allow_html=True)
        
    col1, col2 = st.columns([3, 8])
    
    with col1:
        loc = st.text_input("Entrez un commune ou un département:", value = '75110')
    with col2:
        st.plotly_chart(tb.chart_meteo_loc(loc), use_container_width=True)
    with st.expander("Commentaire"):
        st.markdown(f"<b>Description</b>: Ce graphique circulaire donne la répartition des accidents selon la météo enregistrée sur le moment dans la circonscription {loc}."
        + "<br><b>Analyse:</b> Probabilité Statistique : Les conditions de temps normal sont les plus communes dans de nombreuses régions, ce qui signifie simplement qu'il y a plus de véhicules sur la route lorsque le temps est clair. Par conséquent, le nombre absolu d'accidents sera naturellement plus élevé durant ces périodes. Comportements de Conduite : Lorsque le temps est clair, les conducteurs peuvent être enclins à conduire plus vite ou à prêter moins d'attention, sous-estimant les risques associés à la conduite. Cela peut augmenter la probabilité d'accidents malgré les bonnes conditions de visibilité.", unsafe_allow_html=True)
        
elif option_affichage == 'Usager':
    col1, col2 = st.columns([3,2])
    with col1:
        loc1 = st.text_input("Entrez un commune ou un département:", value = '75110')
        st.plotly_chart(tb.plot_accidents_by_age_and_sex(loc1), use_container_width=True)
    with col2:
        st.markdown("<br>" * 1, unsafe_allow_html=True) 
        with st.expander("Commentaire"):
            st.markdown(f"<b>Description</b>: Ce graphique est un diagramme en barre donnant la distribution des accidents dans la circonscription {loc1} en fonction du sexe du conducteur."
            + "<br> <b>Analyse:</b> On observe sans surprise une fréquence plus élevée d'accidents chez les conducteurs masculins. Le nombre est aussi plus élevé chez les personnes de moins de 40 ans que chez les personnes âgées, avec parfois des pics chez les plus jeunes conducteurs."
            + "<br><b>Comportements de Conduite</b> : Des études montrent souvent que les hommes, en particulier les plus jeunes, ont tendance à adopter des comportements de conduite plus risqués, tels que la vitesse excessive, la conduite sous l'influence de l'alcool ou de drogues, et moins d'usage de la ceinture de sécurité. <br><b>Fréquence et Distance de Conduite</b> : Statistiquement, les hommes pourraient conduire plus fréquemment et sur de plus longues distances que les femmes, augmentant ainsi leur exposition au risque d'accident. <br><b>Perception du Risque</b> : Les jeunes conducteurs, en particulier les jeunes hommes, peuvent sous-estimer les risques liés à la conduite et surestimer leurs capacités de conduite, ce qui peut conduire à des décisions dangereuses sur la route. <br><b>Expérience de Conduite</b> : Les conducteurs de moins de 40 ans ont généralement moins d'expérience que les conducteurs plus âgés, ce qui peut se traduire par une capacité réduite à anticiper et à réagir aux situations dangereuses.", unsafe_allow_html=True)
    col1, col2 = st.columns([3,2])
    with col1:
        loc2 = st.text_input("Entrez un commune ou un département:", value = '75111')
        st.plotly_chart(tb.plot_average_gravity_by_age_and_sex(loc2), use_container_width=True)
    with col2:
        st.markdown("<br>" * 1, unsafe_allow_html=True) 
        with st.expander("Commentaire"):
            st.markdown(f"<b>Description</b>: Ce graphique est un diagramme en barre donnant la gravité moyenne du dommage subi par le conducteur ou l'un des passagers à bord du véhicule dans la circonscription {loc1} en fonction de son sexe."
            + "<br> <b>Analyse:</b> On observe souvent un pic chez les personnes agées qui peut être due à leur plus grande vulnérabilité. On n'observe pas de différence significative selon les sexes.", unsafe_allow_html=True)
    col1, col2 = st.columns([3,2])
    with col1:
        loc3 = st.text_input("Entrez un commune ou un département:", value = '75112')
        st.plotly_chart(tb.plot_gravity_by_age_sex_manoeuvre(loc3), use_container_width=True)
    with col2:
        st.markdown("<br>" * 1, unsafe_allow_html=True) 
        with st.expander("Commentaire"):
            st.markdown(f"<b>Description</b>: Ce graphique est un diagramme en barre donnant la gravité moyenne du dommage subi par la victime piétonne dans la circonscription {loc1} en fonction de son sexe et de son comportement précédant l'accident."
            + "<br>Indices des maneouvres du piéton: <br>'1': Se déplaçant au sens du véhicule heurtant, <br>'2': Se déplace au sens inverse du véhicule, <br>'3': Traversant, <br>'4': Masqué, <br>'5': Jouant - courant, <br>'6': Avec animal, <br>'9': Autre, <br>'A': Monte/descend du véhicule, <br>'B': Inconnue, <br>'IRLVT': Non renseigné ou sans objet.", unsafe_allow_html=True)
        
elif option_affichage == 'Véhicule':
    col1, col2 = st.columns([3,2])
    with col1:
        loc1 = st.text_input("Entrez un commune ou un département:", value = '75110')
        st.plotly_chart(tb.plot_accidents_by_obst_fixe(loc1), use_container_width=True)
    with col2:
        st.markdown("<br>" * 1, unsafe_allow_html=True) 
        with st.expander("Commentaire"):
            st.markdown(f"<b>Description</b>: Ce graphique est un diagramme circulaire donnant la répartition des accidents selon l'obstacle fixe rencontré dans la circonscription {loc1}."
            + "<br>Indices des obstacles fixes: <br>'1': Véhicule en stationnement, <br>'2': Arbre, <br>'3'; Glissière métallique, <br>'4': Glissière béton, <br>'5': Autre glissière, <br>'6': Bâtiment, mur, pile de pont, <br>'7': Support de signalisation verticale ou poste d'appel d'urgence, <br>'8': Poteau, <br>'9': Mobilier urbain, <br>'10': Parapet, <br>'11': Ilot, refuge, borne haute, <br>'12': Bordure de trottoir, <br>'13': Fossé, talus, paroi rocheuse, <br>'14': Autre obstacle fixe sur chasusée, <br>'15': Autre obstacle fixe sur trottoir ou accotement, <br>'16': Sortie de chaussée sans obstacle, <br>'17': Buse - tête d'aqueduc, <br>'IRLVT': Non renseigné ou sans objet."
            + "<br><b>Analyse:</b> L'obstacle 'Fossé, talus, paroi rocheuse' semble être celui ayant la plus grande fréquence dans la plupart des départements. Dans les communes urbanisées, les glissères, les poteaux et les véhicules stationnés sont récurrents.", unsafe_allow_html=True)
        
    col1, col2 = st.columns([3,2])
    with col1:
        loc2 = st.text_input("Entrez un commune ou un département:", value = '75111')
        st.plotly_chart(tb.plot_accidents_by_obst_mobile(loc2), use_container_width=True)
    with col2:
        st.markdown("<br>" * 1, unsafe_allow_html=True) 
        with st.expander("Commentaire"):
            st.markdown(f"<b>Description</b>: Ce graphique est un diagramme circulaire donnant la répartition des accidents selon l'obstacle mobile rencontré dans la circonscription {loc1}."
            + "<br>Indices des obstacles mobiles: <br>'1': Piéton, <br>'2': Véhicule, <br>'4': Véhicule sur rail, <br>'5': Animal domestique, <br>'6': Animal sauvage, <br>'9': Autre', <br>'IRLVT': Non renseigné ou aucun."
            + "<br><b>Analyse:</b> L'obstacle mobile le plus fréquemment impliqué dans un accident auto est le véhicule, suivi du piéton, ce qui est logique puisque ce sont les obstacles les plus fréquemment rencontrés dans une route.", unsafe_allow_html=True)
    col1, col2 = st.columns([3,2])
    with col1:
        loc3 = st.text_input("Entrez un commune ou un département:", value = '75112')
        st.plotly_chart(tb.plot_accidents_by_type_veh(loc3), use_container_width=True)
    with col2:
        st.markdown("<br>" * 1, unsafe_allow_html=True) 
        with st.expander("Commentaire"):
            st.markdown(f"<b>Description</b>: Ce graphique est un diagramme circulaire donnant la répartition des accidents selon le type de véhicule, dans la circonscription {loc1}."
            + "<br>Indices des types de véhicule: <br>1: Bicyclette, <br>2: Cyclomoteur < 50cm3, <br>3: Voiturette, <br>7: VL seul, <br>10: VU seul 1.5T <= PTAC <= 3.5T avec ou sans remorque, <br>13: PL seul 3.5T < PTCA <= 7.5T, <br>14: PL seul > 7.5T, <br>15: PL > 3.5T + remorque, <br>16: Tracteur routier seul, <br>17: Tracteur routier + semi remorque, <br>20: Engin spécial, <br>21: Tracteur agricole, <br>30: Scooter < 50 cm3, <br>31: Motocyclette > 50 cm3 et <= 125 cm3, <br>32: Scooter > 50 cm3 et <= 125 cm3, <br>33: Motocyclette > 125 cm3, <br>34: Scooter > 125 cm3, <br>35: Quad léger <= 50 cm3, <br>36: Quad lourd > 50 cm3, <br>37: Autobus, <br>38: Autocar, <br>39: Train, <br>40: Tramway, <br>41: 3RM <= 50 cm3, <br>42: 3RM > 50 cm3 <= 125 cm3, <br>43: 3RM > 125 cm3, <br>50: EDP à moteur, <br>60: EDP sans moteur, <br>80: VAE, 99: Autre véhicule."
            + "<br><b>Analyse:</b> Le type de véhicule le plus impliqué dans un accident est le véhicule léger.", unsafe_allow_html=True)

        
elif option_affichage == 'Lieux':
    col1, col2 = st.columns([3,2])
    with col1:
        loc1 = st.text_input("Entrez un commune ou un département:", value = '75110')
        st.plotly_chart(tb.plot_accidents_by_type_route(loc1), use_container_width=True)
    with col2:
        st.markdown("<br>" * 1, unsafe_allow_html=True) 
        with st.expander("Commentaire"):
            st.markdown(f"<b>Description</b>: Ce graphique est un diagramme en barre donnant la distribution des accidents par type de route dans la circonscription {loc1}."
            + "<br>Indices des types de route: <br>1: Autoroute, <br>2: Route nationale, <br>3: Route départementale, <br>4: Voie Communales, <br>5: Hors réseau public, <br>6: Parc de stationnement ouvert à la circulation publique, <br>7: Routes de métropole urbiane, <br>9: Autre."
            + "<br><b>Analyse:</b>", unsafe_allow_html=True)

    col1, col2 = st.columns([3,2])
    with col1:
        loc2 = st.text_input("Entrez un commune ou un département:", value = '75111')
        st.plotly_chart(tb.plot_accidents_by_surface(loc2), use_container_width=True)
    with col2:
        st.markdown("<br>" * 1, unsafe_allow_html=True) 
        with st.expander("Commentaire"):
            st.markdown(f"<b>Description</b>: Ce graphique est un diagramme en barre donnant la distribution des accidents par état de la surface de la route dans la circonscription {loc1}."
            + "<br>Indices des types de route: <br>1: Normale, <br>2: Mouillée, <br>3: Flaques, <br>4: Inondée, <br>5: Enneigée, <br>6: Boue, <br>7: Verglacée, <br>8: Corps gras - huile, <br>9: Autre."
            + "<br><b>Analyse:</b>", unsafe_allow_html=True)
    col1, col2 = st.columns([3,2])
    with col1:
        loc3 = st.text_input("Entrez un commune ou un département:", value = '75112')
        st.plotly_chart(tb.plot_accidents_by_vitesse(loc3), use_container_width=True)
    with col2:
        st.markdown("<br>" * 1, unsafe_allow_html=True) 
        with st.expander("Commentaire"):
            st.markdown(f"<b>Description</b>: Ce graphique est un diagramme en barre donnant la distribution des accidents par vitesse autorisée dans la route dans la circonscription {loc1}."
            + "<br><b>Analyse:</b>", unsafe_allow_html=True)
        
elif option_affichage == 'Machine Learning':  
    st.write("Prédiction KNN à partir de l'année de naissance , de la vitesse autorisée, de la gravité et du sexe: le type d'obstacle rencontré, 1 pour mobile ,0 pour fixe")
    k = int(st.slider("Choisissez le nombre de voisins (k)", 1, 15, 3))
    vitesse = int(st.slider("vitesse autorisée", 30,110,50))
    sexe = int(st.slider("sexe", 1,2))
    année_naissance = int(st.slider("année de naissance", 1940, 2023, 1980))
    gravité = int(st.slider("gravité", 1, 4, 2))
    accuracy,prediction,y_pred=tb.predictionKNN(k,sexe,année_naissance,gravité,vitesse)
    st.write(f"Précision du modèle : {accuracy:.2f}")
    st.write(f"La classe prédite est : {prediction[0]}")
    # Création d'un graphique de dispersion (scatter plot)
    
    fig, ax = plt.subplots()
    ax.scatter(tb.X_test.iloc[:, 0].values, tb.X_test.iloc[:, 3].values, c=y_pred, cmap='viridis', marker='o', edgecolor='k')
    scatter=ax.scatter(tb.X_test.iloc[:, 0].values, tb.X_test.iloc[:, 3].values, c=y_pred, cmap='viridis', marker='o', edgecolor='k')
    # Légende du graphique
    handles, labels = scatter.legend_elements()
    ax.legend(handles, labels, title="Classes")

    # Axes du graphique
    ax.set_xlabel('vitesse')
    ax.set_ylabel('gravité')
    ax.set_title('Prédictions du modèle K-NN')

    # Affichage du graphique dans Streamlit
    st.pyplot(fig)
    
#streamlit run c:\users\hugo.razafindralambo\.spyder-py3\dashboard_baac.py