# coding: utf-8
import os
import time
from datetime import timedelta
import math
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
import folium
import webbrowser
from uploadgrib import *
from fonctions_vr import *
from polaires.polaires_figaro2 import *
from global_land_mask import globe
import pickle
from flask import Flask, redirect, url_for,render_template, request , session , flash
from flask_sqlalchemy import SQLAlchemy

tic=time.time()

def polylinetest():
    polyline=[[45,2],[44,3],[46,4]]
    return polyline    


def f_isochrone(l, temps_initial_iso):
    ''' Calcule le nouvel isochrone a partir d'un tableau de points pt2cplx tableau numpy de cplx'''
    ''' deltatemps, tig , U, V sont supposees etre des variables globales'''
    ''' Retourne les nouveaux points el le nouveau temps et implemente le tableau general des isochrones'''
    global isochrone,TWS,TWD
    points=(isochrone[-l:,0:2])
    numero_iso           = int(isochrone[-1][2] + 1)
    delta_temps          = intervalles[numero_iso]  # Ecart de temps entre anciens points et nouveaux en s
    nouveau_temps        = temps_initial_iso + delta_temps
    t_iso_formate        = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(temps_initial_iso + delta_temps))
    numero_dernier_point = int(isochrone[-1][4])                   # dernier point isochrone precedent
    numero_premier_point = int(isochrone[-1][4]) - points.shape[0]   # premier point isochrone precedent
    but                  = False 
    # on recupere toutes les previsions meteo d'un coup pour l'ensemble des points de depart
    # TWS, TWD = prevision_tableau3(tig, GR, temps_initial_iso, points)
    points_calcul2=np.array([[0,0,0,0,0,0,0]]) # initialisation pour Numpy du brouillard des points calcules
# pour chacun des points de l'isochrone 
    for i in range(points.shape[0]):
        HDG = range_cap(dist_cap4(points[i], A)[1], TWD[i], angle_objectif, angle_twa_pres, angle_twa_ar)  # Calcul des caps a etudier
        VT  = polaire2_vect(polaires, TWS[i], TWD[i], HDG)                                                  # Vitesses polaires sur ces caps
        X1,Y1,Da1,Ca1=deplacement_x_y_tab_ar(points[i][0],points[i][1],delta_temps,HDG,VT,A) #Coordonnees des nouveaux points calcules sous forme X,Y
        L=len(X1)                                                                            # nombre de ( caps ) points etudies  
        niso1     = np.ones(L)*numero_iso                                                         # numero isochrone
        npointsm1 = np.ones(L)*i  +numero_premier_point +1    # numero du point mere i = 0 correspond au premier point de l'isochrone precedent
        npoints1  = np.array(range(L)) +1                      # numero du point  sans importance sera renumeroté
        X         = X1.reshape(-1,1)
        Y         = Y1.reshape(-1,1)
        niso      = niso1.reshape(-1,1)
        npointsm  = npointsm1.reshape(-1,1)
        npoints   = npoints1.reshape(-1,1)
        Da        = Da1.reshape(-1,1)
        Ca        = Ca1.reshape(-1,1)
        # maintenant on forme le tableau correspondant à n_pts_x
        n_pts_x2       = np.concatenate((X,Y,niso,npointsm,npoints,Da,Ca), axis = 1)    # tableau des points pour un point de base
        points_calcul2 = np.concatenate((points_calcul2,n_pts_x2), axis         = 0)           # tableau du brouillard pour tous les points de base 
#Version Numpy    
    points_calcul2 = np.delete(points_calcul2,0,0)                                    # on retire le premier terme de points_calcul2
    points_calcul2 = points_calcul2[points_calcul2[: ,6].argsort(kind = 'mergesort')]   # tri stable sur 6eme colonne (caps vers arrivee)
    k=0                                                                             # on regroupe les  caps 359 et 1
    while (((points_calcul2[k][6]-points_calcul2[k-1][6])<-357)and (k<points_calcul2.shape[0]-1)):
        points_calcul2[k][6]+=360
        k+=1
    points_calcul2= points_calcul2[points_calcul2[:,6].argsort(kind='mergesort')]   # les caps en 361 sont replaces a la fin 
    capmini2 = points_calcul2[0][6]
    capmaxi2 = points_calcul2[-1][6]
    coeff2   = 49/ (capmaxi2-capmini2)  # coefficient pour ecremer et garder 50 points
#ecremage arrondi et tri
    points_calcul2[:,6]=np.around(points_calcul2[:,6]*coeff2,0)                   # La colonne 6 est arrondie  
    points_calcul2     = points_calcul2[points_calcul2[:,5].argsort(kind='mergesort')] # On trie sur les distances 
    points_calcul2     = points_calcul2[points_calcul2[:,6].argsort(kind='mergesort')] # On trie sur les caps mais l'ordre des distances est respecté
# ecremage proprement dit
    for i in range(points_calcul2.shape[0] - 1, 0, -1):  # ecremage
        if (points_calcul2[i][6]) == (points_calcul2[i - 1][6]):
            points_calcul2 = np.delete(points_calcul2, i, 0)
    longueur= points_calcul2.shape[0] 
# verification points terre ou mer
    for i in range(points_calcul2.shape[0] - 1, 0, -1):  # ecremage 
        is_on_land = globe.is_land(-points_calcul2[i][1], points_calcul2[i][0])   # point de latitude -y et longitude x
        if (is_on_land==True):
            points_calcul2 = np.delete(points_calcul2, i, 0)
    points_calcul2[:,6]= np.floor(points_calcul2[:,6]/coeff2)       # on retablit le cap en valeur a rechanger en around 0 decimale
    points_calcul2     = points_calcul2[points_calcul2[:,6].argsort(kind='mergesort')] #on trie sur les caps a voir si necessaire !
# renumerotation sur la colonne 4  le premier numero est le numero dernier point iso precedent +1  
    N=np.array( range( int(numero_dernier_point) + 1, points_calcul2.shape[0] +int(numero_dernier_point) + 1,1))  # tableau des indices
    points_calcul2[:,4]=N     # renumerotation
    TWS, TWD =prevision_tableau3(tig, GR, nouveau_temps, points_calcul2) # Vitesse vent et direction pour nouveaux points (extraction en double)
# on minore TWS à  2 pour règle VR
    TWS[TWS <2] = 2
    VT = polaire3_vect(polaires, TWS, TWD, points_calcul2[:,6])
# calcul des temps vers l arrivee
    D_a       = points_calcul2[: ,5]               # Distances vers l'arrivee
    T_a       = 60 * D_a / (VT + 0.000001)        # Temps vers l'arrivée nb ce temps est en heures
    temps_mini=(T_a[np.argmin(T_a,0)])      # Valeur du temps minimum
# Verification si le but est atteignable dans le temps d'un isochrone    
    if temps_mini < delta_temps / 3600:
            but = True
    indice2= np.argmin(T_a,0)  + numero_dernier_point + 1     #indice du point de temps minimum
#    ptn_np2=points_calcul2[:, 0:2]   #(X,Y)# Constitution du tableau des points retournes en sortie    
    lf=points_calcul2.shape[0]
# Ajout des points calcules au tableau global des isochrones
    isochrone = np.concatenate((isochrone, points_calcul2[:,0:5]))  # On rajoute ces points a la fin du tableau isochrone 
# Utilisation pour trace folium  
    #trace_iso2=np.concatenate((-points_calcul2[:,1].reshape(-1,1),points_calcul2[:,0].reshape(-1,1)),axis=1)  #(-Y,X)
    print(' Isochrone  N° {}  {}  {} points  '.format(numero_iso, t_iso_formate,longueur  ))
    return lf, nouveau_temps, but, indice2
# ************************************   Fin de la fonction       **********************************************************




def fonction_routeur(xn,yn,x1,y1,t0=time.time()):
    '''x0,y0,x1,y1 depart et arrivee '''
    ''' Le but de la fonction frouteur est a partir de x0 y0 x1 y1 
    de retourner une multipolyline des isochrones'''
    global isochrone,intervalles,TWS,TWD,tig,GR,angle_objectif,temps_mini,A
# Definition des variables pour le routage
    tig, GR        = chargement_grib()
    A= x1+y1*1j                         # Arrivee sous forme complexe
    pt1_np=np.array([[xn,yn]])          # isochrone de depart (1 point)
    l=pt1_np.shape[0]                   # longueur de l'isochrone de depart (1)
    temps=t0                            # Definition du temps à l'isochrone de depart par defaut time.time()
    angle_objectif = 90                 # amplitude des angle balayes vers l'objectif 
    temps_mini = 0                      # temps entre le dernier isochrone et l'objectif 
# definition des temps des isochrones
    dt1           = np.ones(72) * 600  # intervalles de temps toutes les 10mn pendant une heure puis toutes les heures
    dt2           = np.ones(370) * 3600
    intervalles   = np.concatenate(([t0 - tig], dt1, dt2))
    temps_cumules = np.cumsum(intervalles)
    but = False
    isochrone = np.array([[x0, y0, 0, 0, 0]])# on initialise le tableau isochrone et TWS TWD
    TWS, TWD = prevision_tableau3(tig, GR, t0, pt1_np)  
    print ('(137  premier TWS',TWS) 
# on imprime les donnees de depart    
    print()
    print('Depart :      Latitude {:6.4f}     \tLongitude {:6.4f}'.format(y0, x0))
    print('Arrivee:      Latitude {:6.4f}     \tLongitude {:6.4f}'.format(y1, x1))
    tig_formate_utc = time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tig))
    tic_formate_local = time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(tic))
    print('Heure UTC du dernier Grib             ',tig_formate_utc)
    print('Heure Locale de depart de la prevision',tic_formate_local)
    print ('Ecart en heures ( = ecart - ecartUTC ) ', (tic-tig)/3600)
    print() 
# on calcule tous les isochrones
    while but == False:
        l,temps, but, indice = f_isochrone(l,temps) 
# Reconstitution de la route a emprunter  indice  est l'indice de temps minimum du dernier point 
    a = int(indice)                 # indice du point de la route la plus courte
    n = int(isochrone[-1][2])       # nombre d'isochrones
    dico=dict(zip(isochrone[:,4],isochrone[:,3]))   #dictionnaire des points et points meres
    route = [a]
    for i in range(n):
        a = int(dico[a])
        route.append(a)  # route contient les indices successifs des points a emprunter a l'envers
    route.reverse()
    chemin = np.zeros(len(route) + 1, dtype=complex)  # on initialise le np array de complexes qui va recevoir les donnees
    i = 0
    for n in (route):
        chemin[i] = isochrone[n][0] + isochrone[n][1] * 1j
        i += 1
    chemin[i] = A
    # maintenant on reconstitue le chemin avec les caps les TWA et les previsions
    l = len(chemin)
    temps_cum = temps_cumules[:l]
    temps_cum[-1] = temps_cum[-2] + temps_mini * 3600  # le dernier terme est le temps entre le dernier isochrone et l'arrive
    TWS_ch, TWD_ch = prevision_tableau2(GR, temps_cum, chemin)# previsions meteo aux differents points pour reconstitution 
    distance, cap1 = dist_cap3(chemin[0:-1], chemin[1:])    # distance et angle de chaque point au suivant
    #dist = np.append(distance, [0])                         # on rajoute un 0 pour la distance arrivee et l angle arrivee
    HDG_ch = np.append(cap1, [0])                           # tableau des caps aux differents points
    TWA_ch = twa(HDG_ch, TWD_ch)                            # calculs twa sous forme de tableau pour les differents points
    POL_ch = polaire3_vect(polaires, TWS_ch, TWD_ch, HDG_ch)# calcul des polaires aux differents points du chemin
    temps_cum += tig
    # mise en forme pour concatener
    chx =       chemin.real.reshape((1, -1))
    chy =       chemin.imag.reshape((1, -1))
    temps_pts = temps_cum.reshape((1, -1))
    vitesse =   TWS_ch.reshape((1, -1))
    TWD =       TWD_ch.reshape((1, -1))
    cap =       HDG_ch.reshape((1, -1))
    twat =       TWA_ch.reshape((1, -1))
    pol =       POL_ch.reshape((1, -1))
    # tabchemin : x,y,vit vent ,TWD,cap vers point suivant twa vers point suivant
    chem = np.concatenate((chx.T, chy.T, temps_pts.T, vitesse.T, TWD.T, cap.T, twat.T, pol.T), axis=1)
# confection de la route à suivre avec les tooltips
    route3=[]
    comment=[]
    for i in range (0,len(chem),1):
        temps=time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(chem[i, 2]))
        # heures=str(((chem[i, 2])- t0)//3600)
        # long=str(-round(chem[i, 0], 2))
        # lat=str(-round(chem[i, 1], 2))
        # tws = str(round(chem[i, 3], 1))
        # twd = str(round(chem[i, 4], 0))
        cap = str(round(chem[i, 5], 0))
        # twaroute = str(round(chem[i, 6], 0))
        # Vt  = str(round(chem[i, 7], 2))
        route3.append([-chem[i, 1],chem[i, 0]])   # dans la version leaflet on a le temps en trois
        comment.append([-chem[i, 1],chem[i, 0],chem[i, 2],chem[i, 3],chem[i, 4],chem[i, 5],chem[i, 6],chem[i, 7]])
    #Confection de la multipolyline pour le trace des isochrones 
    X=isochrone[:,0].reshape(-1,1)
    Y=isochrone[:,1].reshape(-1,1)
    N=isochrone[:,2].reshape(-1,1)
    points=np.concatenate((-Y,X,N),1)
    polyline=np.split(points[:,0:2],np.where(np.diff(points[1:,2])==1)[0]+2)
    multipolyline=[arr.tolist() for arr in polyline]
    del multipolyline[0][0]
    return multipolyline,route3,comment




if __name__ == '__main__':
    # Initialisation  **********************************************************************************
    #Depart
    latitude_d     = '043-28-20-N'
    longitude_d    = '009-28-58-E'
    #Point Arrivee 
    latitude_a     = '043-01-00-N'
    longitude_a    = '009-24-00-E'
    


    
    t0=time.time() 
    x0,y0=chaine_to_dec(latitude_d, longitude_d)  # conversion des latitudes et longitudes en tuple
    x1,y1=chaine_to_dec(latitude_a, longitude_a)
  


#*******************************************************************************************
#*******************************************************************************************
# Fonction_routeur  elle retourne les isochrones (multipolyline) et la route ,
    multipolyline,route,comment=fonction_routeur(x0,y0,x1,y1)
#*******************************************************************************************
#*******************************************************************************************
#*******************************************************************************************




# Exportation en pandas et en csv
indexiso=np.arange(len(comment))
df = pd.DataFrame(comment, index = indexiso, columns = ['x', 'y', 't', 'vit_vent','angle_vent','cap','twa', 'polaire'])

print()
print(df.head(12))
print()
df.to_csv('fichier_route2.csv')

#*******************************************************************************************
#*******************************************************************************************

# pour des raisons de mise au point on va l'afficher directement dans folium
# Initialisation carte folium **************************************************************
lat1=  -(y0+y1)/2
lng1=   (x0+x1)/2  
m = folium.Map( location=[lat1,lng1],  zoom_start=9)
folium.LatLngPopup().add_to(m)   # popup lat long
#*******************************************************************************************
#trace de la multipolyline des isochrones
red=[]
black=[]
for i in range(len(multipolyline)):
    if i%6==0:
            black.append(multipolyline[i])
    else:
            red.append(multipolyline[i]) 
#trace des isochrones           
folium.PolyLine(black,color='black',weight=1 , popup='Isochrone %6 ').add_to(m) 
folium.PolyLine(red,color='red',weight=1 , popup='Isochrone ').add_to(m)     
#trace de la route
folium.PolyLine(route, color="blue", weight=2.5, popup='Route calculée ',opacity=0.8).add_to(m)

# Creation de points sur la route avec tooltips pour folium
tooltip=[]
popup=[]

#print ('\ncomment \n',comment)

for i in range (0,len(comment),1):
    temps=time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(comment[i][2]))
    delta_t   = comment[i][2]- t0 +30   #(les 30s sont pour le temps dexecution du programme)
    delta_t_h = delta_t//3600
    delta_t_mn=(delta_t-delta_t_h*3600)//60
    heures=str(delta_t_h)+'H '+str(delta_t_mn)+'mn'
    lng= str(-round(comment[i][0], 2))
    lat = str(-round(comment[i][1], 2))
    tws = str(round(comment[i][3], 1))
    twd = str(round(comment[i][4], 0))
    cap = str(round(comment[i][5], 0))
    twa = str(round(comment[i][6], 0))
    Vt  = str(round(comment[i][7], 2))
    tooltip.append('<b>'+temps+'<br> +'+heures+'<br> Lat :'+lat+'° - Long :'+lng+'°<br>TWD :' +twd+'°-  TWS :'
                   + tws +'N<br> Cap :' + cap + '° TWA :' +twa +'°<br>Vt :' +Vt+'N</b>')
    popup.append( folium.Popup(folium.Html(tooltip[i], script=True), max_width=200,min_width=150))
for i in range( len(comment)):
    folium.Circle([comment[i][0],comment[i][1]],color='black', radius=200,tooltip=tooltip[i], popup=popup[i],fill=True).add_to(m)

#*******************************************************************************************
# Sauvegarde carte et affichage dans browser
filecarte='map.html'
filepath = 'templates/'+filecarte
m.save(filepath)
webbrowser.open( filepath)

    #   ****************************************Controle du temps d'execution **********************************
tac = time.time()
print('\nDuree d\'execution:  {:4.2f} s'.format(tac - tic))
