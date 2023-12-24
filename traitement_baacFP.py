import time
import pandas as pd
import geopandas as gpd
from branca.colormap import linear
from branca.colormap import StepColormap
from shapely.geometry import Polygon, LineString, MultiLineString
import plotly.express as px
from branca.colormap import LinearColormap
#from ydata_profiling import ProfileReport
import osmnx as ox
import folium as folium
import numpy as np
import math
from shapely.geometry import Point, LineString
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from folium.plugins import HeatMap
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

accident = pd.read_csv('C:\Users\fanti\M2\data viz\accident.csv')

accident = accident[accident['an']==2021]
accident = accident.drop_duplicates()
accident.drop(columns = 'Unnamed: 0', inplace = True)
accident.long = accident.long.apply(lambda x : x.replace(",", "."))
accident.lat = accident.lat.apply(lambda x : x.replace(",", "."))
accident['age'] = accident['an'] - accident['an_nais']
for col in accident.select_dtypes(include=['float']).columns:
    accident[col] = accident[col].astype(int)
accident = accident.astype(str)
accident.sexe = accident.sexe.apply(lambda x : x.replace("1.0", "homme"))
accident.sexe = accident.sexe.apply(lambda x : x.replace("2.0", "femme"))
columns_to_float = ['lat','long']
for column in columns_to_float:
    accident[column] = accident[column].astype(float)
accident['grav'].replace({"1": 1, "2": 4, "3": 3, "4": 2}, inplace=True)


list_om = ['971','972','974','976', '973', '986','988', '978', '975', '977','987']
accident_metr = accident[~accident['dep'].isin(list_om)]

cntr_dep = gpd.read_file('C:\Users\fanti\M2\data viz\departements.geojson')
cntr_dep.rename(columns = {"code" : "dep", "nom":"Nom_dep","geometry":"geometry_dep"}, inplace = True)

cntr_com_2021 = gpd.read_file('C:\Users\fanti\M2\data viz\commune-frmetdrom-2021\commune-frmetdrom-2021\COMMUNE_FRMETDROM.shp')
cntr_com_2021.rename(columns = {"INSEE_COM" : "com", "NOM":"Nom_com","geometry":"geometry_com"}, inplace = True)

#Nombre d'accidents par département
freq_acc_dep = accident_metr.groupby('dep')['Num_Acc'].nunique().reset_index(name='nb_accident')
accident_nb = freq_acc_dep.merge(cntr_dep, how = "left", on = "dep")
accident_nb = gpd.GeoDataFrame(accident_nb, geometry = "geometry_dep")
accident_nb = accident_nb[accident_nb['geometry_dep'].notna()]

#Nombre d'accidents par commune
freq_acc_com = accident_metr.groupby('com')['Num_Acc'].nunique().reset_index(name='nb_accident')
accident_nb_com = freq_acc_com.merge(cntr_com_2021, how = "left", on = "com")
accident_nb_com = gpd.GeoDataFrame(accident_nb_com, geometry = "geometry_com")
accident_nb_com = accident_nb_com[accident_nb_com['geometry_com'].notna()]


#Moyenne pondérée des gravités par département

freq_grav = accident_metr.groupby(['dep', 'grav']).size().reset_index(name='nombre_accidents')
accident_gravite_ponderee = freq_grav.copy()
accident_gravite_ponderee['grav_ponderee'] = accident_gravite_ponderee['grav'] * accident_gravite_ponderee['nombre_accidents']
somme_ponderee = accident_gravite_ponderee.groupby('dep')['grav_ponderee'].sum()

total_accidents = freq_grav.groupby('dep')['nombre_accidents'].sum()

freq_grav_mp = (somme_ponderee / total_accidents).reset_index(name='moyenne_ponderee_grav')

accident_grav = freq_grav_mp.merge(cntr_dep, how="left", on="dep")
accident_grav = gpd.GeoDataFrame(accident_grav, geometry="geometry_dep")


#ML 
dataMLclass2=accident[accident['obst_fixe']!='IRLVT']
dataMLclass1=accident[accident['obst_mobile']!='IRLVT']
data1=dataMLclass1[['obst_mobile','vitesse_autorisee','sexe','an_nais','grav']]
data2=dataMLclass2[['obst_fixe', 'vitesse_autorisee','sexe','an_nais','grav']]
df3 = pd.concat([data1,data2], ignore_index=True)
df3['obst_mobile'].fillna(0, inplace=True)
df3['obst_fixe'].fillna(0,inplace=True)
df3['obst_mobile']=df3['obst_mobile'].astype(int)
df3['obst_fixe']=df3['obst_fixe'].astype(int)
df3['obst_mobile']=np.where(df3['obst_mobile']>0,2,df3['obst_mobile'])
df3['obst_fixe']=np.where(df3['obst_fixe']>0,1,df3['obst_fixe'])
to_drop=['obst_mobile','obst_fixe']
df3['type_obst']=df3[['obst_mobile','obst_fixe']].max(axis=1)
df3=df3.drop(to_drop,axis=1)
df3['type_obst']=np.where(df3['type_obst']==2,1,0)
df3.sexe = df3.sexe.apply(lambda x : x.replace("homme","1"))
df3.sexe = df3.sexe.apply(lambda x : x.replace("femme","2"))
df3["sexe"]=df3["sexe"].astype('int')
print(df3)
#1: mobile 0: fixe 

x = df3.drop('type_obst', axis='columns')  # X contient les caractéristiques
y = df3['type_obst']  # y contient la variable cible
print(len(x))
X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
print(X_train)
#Cartographie:
    
def map_accident(column, com=None):
    
    longitude, latitude = 2.33190, 48.81701
    m = folium.Map(location=[latitude, longitude], zoom_start=6)
    
    if column=="accident dep":
        intervals = [0, 45, 100, 150, 200, 500, 1000, 3000]
        colors = ['#5fe3c0', '#48c9b0', '#34bf9f', '#21938e', '#10587d', '#0a4572', '#042e58', '#031744', '#010031']

        colormap = StepColormap(
            colors,
            vmin=accident_nb['nb_accident'].min(),
            vmax=accident_nb['nb_accident'].max(),
            index=intervals,
            caption="Nombre d'accident de véhicule par département"
        )


        folium.GeoJson(
            accident_nb,
            style_function=lambda feature: {
                'fillColor': colormap(feature['properties']['nb_accident']),
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.7 
            }
        ).add_to(m)

        for idx, row in accident_nb.iterrows():
            popup = folium.Popup(f"<b>{row['dep']}: {row['Nom_dep']}</b> <br> <b>Nombre d'accidents:</b> {row['nb_accident']}")
            folium.GeoJson(row['geometry_dep'],
                           name=row['Nom_dep'],
                           style_function=lambda x: {
                               'fillOpacity': 0,  
                               'weight': 0
                           }).add_child(popup).add_to(m)


        colormap.add_to(m)


    elif column == "gravite":
        # Définir les couleurs pour la gravité
        colors = ['#5fe3c0', '#48c9b0', '#34bf9f', '#21938e', '#10587d', '#0a4572', '#042e58', '#031744', '#010031']

        # Utiliser LinearColormap au lieu de StepColormap
        colormap = LinearColormap(
            colors,
            vmin=accident_grav['moyenne_ponderee_grav'].min(),  # Mettez ici la valeur minimale de la gravité
            vmax=accident_grav['moyenne_ponderee_grav'].max(),  # Mettez ici la valeur maximale de la gravité
            caption="Moyenne pondérée de la gravité des accidents par département"
        )

        folium.GeoJson(
            accident_grav,
            style_function=lambda feature: {
                'fillColor': colormap(feature['properties']['moyenne_ponderee_grav']),
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.7 
            }
        ).add_to(m)
        
        for idx, row in accident_grav.iterrows():
            popup = folium.Popup(f"Gravité moyenne: {row['moyenne_ponderee_grav']}", parse_html=True)
            folium.GeoJson(row['geometry_dep'],
                           name=row['Nom_dep'],
                           style_function=lambda x: {
                               'fillOpacity': 0,  
                               'weight': 0
                           }).add_child(popup).add_to(m)
        
    if com!=None:
        icon_com = folium.Icon(color='purple', icon='glyphicon glyphicon-flag')
        com_df = accident_metr[accident_metr['com']==com][['long','lat']]
        xc,yc = com_df.iloc[0]
        popup_com = folium.Popup(f"<b>Nombre d'accident:</b> {com_df.drop_duplicates().shape[0]} <br> <b>Nombre de victimes:</b> {com_df.shape[0]}")
        folium.Marker([yc, xc], icon=icon_com, popup=popup_com).add_to(m)
        print('com is not None')
    else:
        print('com is None')
        
    return m


def map_accident_commune(com):
    geom = cntr_com_2021[cntr_com_2021['com']==com].geometry_com
    longitude, latitude = list(geom.iloc[0].exterior.coords)[0]

    map = folium.Map(location=[latitude, longitude], zoom_start=12)
    for _, x, y, j, m, a in accident_metr[accident_metr['com']==com][['long', 'lat', 'jour', 'mois', 'an']].to_records():
        popup = folium.Popup(f"<b>Date:</b> {j}/{m}/{a}")
        icon = folium.Icon(color='purple', icon='glyphicon-warning-sign')
        folium.Marker([y, x], icon=icon, popup=popup).add_to(map)
    return map



# Distribution d'une variable par département:
def plot_distribution(column_name, department=None):
    """
    Function to plot the distribution of a given column in the dataframe as an interactive bar chart using Plotly.
    If 'IRLVT' is a value in the column, it is excluded from the plot.
    The analysis can be narrowed down to a specific department if provided.

    Parameters:
    column_name (str): The name of the column to analyze.
    department (str, optional): The department code for specific analysis. Defaults to None (all of France).
    """
    filtered_data = accident_metr[accident_metr[column_name] != 'IRLVT']

    if department is not None:
        filtered_data = filtered_data[filtered_data['dep'] == department]

    count_data = filtered_data[column_name].value_counts().reset_index()
    count_data.columns = [column_name, 'Count']

    fig = px.bar(count_data, x='Count', y=column_name, orientation='h', 
                 title=f'Distribution of {column_name} in department {department}' if department else f'Distribution of {column_name} (excluding \'IRLVT\')')
    
    fig.update_traces(marker=dict(color='rgba(64, 224, 208, 0.6)', line=dict(color='white', width=1)))

    fig.update_layout(
        xaxis_title='Count', 
        yaxis_title=column_name,
        xaxis=dict(color='white', showgrid=False),
        yaxis=dict(color='white', showgrid=False, dtick=1),
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)', 
        font=dict(color='white')
    )

    # Afficher le graphique
    return fig

# Accidents par date
#Par horaire et jour:
accident_metr['date'] = pd.to_datetime(accident_metr['an'] + '-' + accident_metr['mois'] + '-' + accident_metr['jour'])
accident_metr['datetime'] = pd.to_datetime(accident_metr['date'].astype(str) + ' ' + accident_metr['hrmn'])

accident_count_per_datetime = accident_metr.groupby('datetime')['Num_Acc'].nunique().reset_index()
accident_count_per_datetime.columns = ['DateTime', 'Unique_Accidents_Count']

#Par jour:
accident_count_per_day = accident_count_per_datetime.groupby(accident_count_per_datetime['DateTime'].dt.to_period('D'))['Unique_Accidents_Count'].sum().reset_index()
accident_count_per_day['DateTime'] = accident_count_per_day['DateTime'].dt.to_timestamp()

#Par mois:
accident_count_per_month = accident_count_per_datetime.groupby(accident_count_per_datetime['DateTime'].dt.to_period('M'))['Unique_Accidents_Count'].sum().reset_index()
accident_count_per_month['DateTime'] = accident_count_per_month['DateTime'].dt.to_timestamp()

def graph_datetime(time):
    if time == "month":
        data = accident_count_per_month
    elif time == "day":
        data = accident_count_per_day

    # Créer le graphique avec les modifications de style
    fig = px.line(
        data, 
        x='DateTime', 
        y='Unique_Accidents_Count',
        title='Evolution of Unique Accidents Count Throughout 2021',
        labels={'DateTime': 'Date', 'Unique_Accidents_Count': 'Number of Unique Accidents'},
        line_shape='linear',  # Assure une ligne continue
        markers=True  # Ajoute des points aux données
    )

    # Personnalisation des points et des couleurs
    fig.update_traces(
        line_color='turquoise', 
        marker_color='turquoise', 
        marker=dict(size=6, symbol='square')  # Utilise des carrés pour les points et réduit leur taille
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    return fig

    
def chart_meteo_loc(loc):
    # Votre code existant pour filtrer les données
    if loc in accident_metr['dep'].unique():
        accident_loc = accident_metr[accident_metr['dep'] == loc]
        name = "le département"
    else:
        accident_loc = accident_metr[accident_metr['com'] == loc]
        name = "la commune"

    # Votre code existant pour compter les occurrences
    data = accident_loc['meteo'].value_counts()

    # Mapping des valeurs numériques aux descriptions météorologiques
    meteo_labels = {
        '1': "Normale", '2': "Pluie légère", '3': "Pluie forte",
        '4': "Neige - grêle", '5': "Brouillard - fumée",
        '6': "Vent fort - tempête", '7': "Temps éblouissant",
        '8': "Temps couvert", '9': "Autre"
    }

    # Remplacement des valeurs numériques par des descriptions dans l'index de data
    data.index = [meteo_labels.get(item, item) for item in data.index]

    # Votre code existant pour définir les couleurs
    colors = [
        'deepskyblue', 'blueviolet', 'turquoise', 
        'royalblue', 'darkturquoise', 'dodgerblue', 
        'darkviolet', 'mediumturquoise'
    ]

    # Création du graphique
    fig = px.pie(data, names=data.index, values=data.values, hole=0.3)

    # Mise à jour des traces
    fig.update_traces(marker=dict(colors=colors))

    # Mise à jour de la mise en page pour le texte blanc
    fig.update_layout(
        title_text=f"Distribution de la météo dans {name}: {loc}",
        title_font=dict(color='white'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    return fig

### GRAPHIQUES USAGER ###

#NOMBRE D'ACCIDENT PAR AGE ET PAR SEXE DU CONDUCTEUR
def plot_accidents_by_age_and_sex(loc):
    
    usager_df_1 = accident_metr[accident_metr['type_usager']=="1"][['Num_Acc','sexe','age','dep','com']]
    
    if loc in usager_df_1['dep'].unique():
        usager_df_1_loc = usager_df_1[usager_df_1['dep'] == loc]
        name = "le département"
    else:
        usager_df_1_loc = usager_df_1[usager_df_1['com'] == loc]
        name = "la commune"
    
    grouped_data = usager_df_1_loc.groupby(['age', 'sexe'])['Num_Acc'].count().reset_index()

    color_map = {"1": "darkblue", "2": "purple"} 

    fig = px.bar(grouped_data, x='age', y='Num_Acc', color='sexe', barmode='group',
                 labels={'Num_Acc': 'Nombre d\'accidents', 'sexe': 'Sexe', 'age': 'Âge'},
                 title=f'Nombre d\'accidents par âge et par sexe du conducteur dans {name}: {loc}',
                 color_discrete_map=color_map)

    fig.update_layout(
        title_font=dict(color='white'),
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',  
        font=dict(color='white') 
    )

    fig.update_xaxes(tickfont=dict(color='white'))
    fig.update_yaxes(tickfont=dict(color='white'))

    return fig

#GRAVITE MOYENNE PAR AGE ET PAR SEXE DU CONDUCTEUR OU PASSAGER
def plot_average_gravity_by_age_and_sex(loc):
    
    usager_df_2 = accident_metr[accident_metr['type_usager']!="3"][['Num_Acc','sexe','age','dep','com','grav']]
    
    if loc in usager_df_2['dep'].unique():
        usager_df_2_loc = usager_df_2[usager_df_2['dep'] == loc]
        name = "le département"
    else:
        usager_df_2_loc = usager_df_2[usager_df_2['com'] == loc]
        name = "la commune"

    average_gravity = usager_df_2_loc.groupby(['age', 'sexe'])['grav'].mean().reset_index()
    
    color_map = {"1": "darkblue", "2": "purple"}
    
    fig = px.bar(average_gravity, x='age', y='grav', color='sexe', barmode='group',
                 labels={'grav': 'Gravité moyenne', 'sexe': 'Sexe', 'age': 'Âge'},
                 title=f'Gravité moyenne des accidents par âge et par sexe dans {name}: {loc}',
                 color_discrete_map=color_map)

    fig.update_layout(
        title_font=dict(color='white'),
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',  
        font=dict(color='white') 
    )

    fig.update_xaxes(tickfont=dict(color='white'))
    fig.update_yaxes(tickfont=dict(color='white'))

    return fig

#GRAVITE DE L'ACCIDENT EN FONCTION DE LA MANOEUVRE DU PIETON ET DE SON SEXE.
def plot_gravity_by_age_sex_manoeuvre(loc):
    usager_df_3 = accident_metr[accident_metr['type_usager'] == "3"][['Num_Acc', 'sexe', 'age', 'dep', 'com', 'manoeuvre_pieton', 'grav']]

    if loc in usager_df_3['dep'].unique():
        usager_df_3_loc = usager_df_3[usager_df_3['dep'] == loc]
        name = "le département"
    else:
        usager_df_3_loc = usager_df_3[usager_df_3['com'] == loc]
        name = "la commune"

    average_gravity = usager_df_3_loc.groupby(['age', 'sexe', 'manoeuvre_pieton'])['grav'].mean().reset_index()
    
    color_map = {"1": "darkblue", "2": "purple"}
    
    fig = px.bar(average_gravity, x='age', y='grav', color='sexe', 
                 animation_frame='manoeuvre_pieton',
                 labels={'grav': 'Gravité moyenne', 'sexe': 'Sexe', 'age': 'Âge', 'manoeuvre_pieton': 'Manœuvre piéton'},
                 title=f'Gravité moyenne des accidents par âge, sexe et manœuvre piéton dans {name}: {loc}',
                 color_discrete_map=color_map)

    fig.update_layout(
        title_font=dict(color='white'),
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',  
        font=dict(color='white') 
    )

    fig.update_xaxes(tickfont=dict(color='white'))
    fig.update_yaxes(tickfont=dict(color='white'))

    return fig



### GRAPHIQUES VEHICULE ###

def plot_accidents_by_obst_fixe(loc):
    
    vehicule_df_1 = accident_metr[['Num_Acc','obst_fixe','dep','com']][accident_metr['obst_fixe']!="IRLVT"]
    
    if loc in vehicule_df_1['dep'].unique():
        vehicule_df_1_loc = vehicule_df_1[vehicule_df_1['dep'] == loc]
        name = "le département"
    else:
        vehicule_df_1_loc = vehicule_df_1[vehicule_df_1['com'] == loc]
        name = "la commune"

    obstacle_counts = vehicule_df_1_loc['obst_fixe'].value_counts().reset_index()
    obstacle_counts.columns = ['obst_fixe', 'count']

    fig = px.pie(obstacle_counts, names='obst_fixe', values='count', hole=0.5,
                 title=f'Nombre d\'accidents par obstacle fixe (hors IRLVT) dans {name}: {loc}')
    colors = [
        'deepskyblue', 'blueviolet', 'turquoise', 
        'royalblue', 'darkturquoise', 'dodgerblue', 
        'darkviolet', 'mediumturquoise'
    ]

    fig.update_traces(marker=dict(colors=colors))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )

    return fig


def plot_accidents_by_obst_mobile(loc):
    
    vehicule_df_1 = accident_metr[['Num_Acc','obst_mobile','dep','com']][accident_metr['obst_mobile']!="IRLVT"]
    
    if loc in vehicule_df_1['dep'].unique():
        vehicule_df_1_loc = vehicule_df_1[vehicule_df_1['dep'] == loc]
        name = "le département"
    else:
        vehicule_df_1_loc = vehicule_df_1[vehicule_df_1['com'] == loc]
        name = "la commune"

    obstacle_counts = vehicule_df_1_loc['obst_mobile'].value_counts().reset_index()
    obstacle_counts.columns = ['obst_mobile', 'count']

    fig = px.pie(obstacle_counts, names='obst_mobile', values='count', hole=0.5,
                 title=f'Nombre d\'accidents par obstacle mobile (hors IRLVT) dans {name}: {loc}')
    colors = [
        'deepskyblue', 'blueviolet', 'turquoise', 
        'royalblue', 'darkturquoise', 'dodgerblue', 
        'darkviolet', 'mediumturquoise'
    ]

    fig.update_traces(marker=dict(colors=colors))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )

    return fig


def plot_accidents_by_type_veh(loc):
    
    vehicule_df_1 = accident_metr[['Num_Acc','type_veh','dep','com']]
    
    if loc in vehicule_df_1['dep'].unique():
        vehicule_df_1_loc = vehicule_df_1[vehicule_df_1['dep'] == loc]
        name = "le département"
    else:
        vehicule_df_1_loc = vehicule_df_1[vehicule_df_1['com'] == loc]
        name = "la commune"

    obstacle_counts = vehicule_df_1_loc['type_veh'].value_counts().reset_index()
    obstacle_counts.columns = ['type_veh', 'count']

    fig = px.pie(obstacle_counts, names='type_veh', values='count', hole=0.5,
                 title=f'Nombre d\'accidents par type de véhicule dans {name}: {loc}')
    colors = [
        'deepskyblue', 'blueviolet', 'turquoise', 
        'royalblue', 'darkturquoise', 'dodgerblue', 
        'darkviolet', 'mediumturquoise'
    ]

    fig.update_traces(marker=dict(colors=colors))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )

    return fig



### GRAPHIQUES LIEUX ###

def plot_accidents_by_type_route(loc):
    
    lieux_df = accident_metr[['Num_Acc', 'type_route', 'dep', 'com']]
    
    if loc in lieux_df['dep'].unique():
        lieux_df_loc = lieux_df[lieux_df['dep'] == loc]
        name = "le département"
    else:
        lieux_df_loc = lieux_df[lieux_df['com'] == loc]
        name = "la commune"

    type_route_counts = lieux_df_loc['type_route'].value_counts().reset_index()
    type_route_counts.columns = ['type_route', 'count']

    # Création d'un graphique en barres horizontal avec couleur turquoise
    fig = px.bar(type_route_counts, x='count', y='type_route', orientation='h',
                 title=f'Nombre d\'accidents par type de route dans {name}: {loc}',
                 color_discrete_sequence=['turquoise'] * len(type_route_counts))

    # Personnalisation des barres
    fig.update_traces(marker=dict(line=dict(color='white', width=1)))

    # Personnalisation des axes
    fig.update_xaxes(showline=True, linewidth=2, linecolor='white', color='white')
    fig.update_yaxes(showline=True, linewidth=2, linecolor='white', color='white')

    # Personnalisation supplémentaire du graphique
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )

    return fig

def plot_accidents_by_surface(loc):
    
    lieux_df = accident_metr[['Num_Acc', 'surface', 'dep', 'com']]
    
    if loc in lieux_df['dep'].unique():
        lieux_df_loc = lieux_df[lieux_df['dep'] == loc]
        name = "le département"
    else:
        lieux_df_loc = lieux_df[lieux_df['com'] == loc]
        name = "la commune"

    type_route_counts = lieux_df_loc['surface'].value_counts().reset_index()
    type_route_counts.columns = ['surface', 'count']

    # Création d'un graphique en barres horizontal avec couleur turquoise
    fig = px.bar(type_route_counts, x='count', y='surface', orientation='h',
                 title=f'Nombre d\'accidents par revêtement dans {name}: {loc}',
                 color_discrete_sequence=['turquoise'] * len(type_route_counts))

    # Personnalisation des barres
    fig.update_traces(marker=dict(line=dict(color='white', width=1)))

    # Personnalisation des axes
    fig.update_xaxes(showline=True, linewidth=2, linecolor='white', color='white')
    fig.update_yaxes(showline=True, linewidth=2, linecolor='white', color='white')

    # Personnalisation supplémentaire du graphique
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )

    return fig

def plot_accidents_by_vitesse(loc):
    
    lieux_df = accident_metr[['Num_Acc', 'vitesse_autorisee', 'dep', 'com']]
    
    if loc in lieux_df['dep'].unique():
        lieux_df_loc = lieux_df[lieux_df['dep'] == loc]
        name = "le département"
    else:
        lieux_df_loc = lieux_df[lieux_df['com'] == loc]
        name = "la commune"

    type_route_counts = lieux_df_loc['vitesse_autorisee'].value_counts().reset_index()
    type_route_counts.columns = ['vitesse_autorisee', 'count']

    # Création d'un graphique en barres horizontal avec couleur turquoise
    fig = px.bar(type_route_counts, x='count', y='vitesse_autorisee', orientation='h',
                 title=f'Nombre d\'accidents par revêtement dans {name}: {loc}',
                 color_discrete_sequence=['turquoise'] * len(type_route_counts))

    # Personnalisation des barres
    fig.update_traces(marker=dict(line=dict(color='white', width=1)))

    # Personnalisation des axes
    fig.update_xaxes(showline=True, linewidth=2, linecolor='white', color='white')
    fig.update_yaxes(showline=True, linewidth=2, linecolor='white', color='white')

    # Personnalisation supplémentaire du graphique
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )

    return fig
def predictionKNN(k,sexe,année_naissance,gravité,vitesse):
    # Classement par K-NN

    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_train, X_train)
    y_pred = knn.predict(X_test)

    # Prédiction de la classe pour les caractéristiques données
    prediction = knn.predict([[sexe, année_naissance, gravité, vitesse]])

    # Calcul de la précision du modèle
    accuracy = accuracy_score(y_test, knn.predict(X_test))

    return accuracy,prediction