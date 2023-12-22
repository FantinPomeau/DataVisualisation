import streamlit as st
import traitement_baacML as tb
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
        st.markdown(f"<b>Description</b>: La cartographie principale permet de constater le nombre d'accidents enregistrés dans la base BAAC par département. La deuxième carte permet de visualiser la localisation des accidents ayant eu lieu dans la commune n°{st.sidebar.var_com}. <br> <b>Analyse:</b> ", unsafe_allow_html=True)
    
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
        st.markdown("")

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
        st.markdown("")
        
        
        
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
        st.markdown("")
elif option_affichage == 'Machine Learning':  
    st.write("Prédiction")  


#streamlit run C:\Users\fanti\OneDrive\Documents\Actuariat\M2\data viz\dashboard_baacFantin.py