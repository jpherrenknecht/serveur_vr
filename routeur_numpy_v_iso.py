#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 18:07:00 2020
# les gribs complets sont disponibles en heure d'ete à
# 13h(gfs06) - 19(gfs12) -  01(gfs18) - 07 h (gfs00)
@author: jph
"""

import os
import time
import math
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
import folium
import webbrowser
import pickle

from global_land_mask import globe
from uploadgrib import *
from polaires.polaires_ultime import *
from fonctions_vr import *




tic = time.time()
basedir = os.path.abspath(os.path.dirname(__file__))



# *****************************************   Donnees   ****************************************************************
'''
Dans tous les calculs la longitude correspondant à l'axe des x est prise en premier
Les points sont définis en longitude (x) latitude (y)
Attention les previsions sont elles faites en latitude longitude
les latitudes sont positives vers le sud et les longitudes positives vers l'est
Les points initiaux sont sous forme de tuple longitude latitude
Les angles sont des angles trigo
Pour le vent on parle de vitesses TWS  et angles TWD et TWA 
Pour le bateau on parle de cap HDG et de vitesse polaire Vt
'''
#******************************************************************************************************************************************
#******************************************************************************************************************************************
#******************************************************************************************************************************************
#******************************************************************************************************************************************
def trace_points_folium (points_cpx):
#on extrait les coordonnes pour tracer
    X=points_cpx.real.reshape(-1,1)
    Y=points_cpx.imag.reshape(-1,1)
    points=np.concatenate((-Y,X),axis=1)
    for point in points :
        folium.CircleMarker(point,color='black', radius=1,fill_color='black',fill_opacity=0.3).add_to(m)
    return None

def f_isochrone(points, temps_initial_iso):
    ''' Calcule le nouvel isochrone a partir d'un tableau de points pt2cplx tableau numpy de cplx'''
    ''' deltatemps, tig , U, V sont supposees etre des variables globales'''
    ''' Retourne les nouveaux points el le nouveau temps et implemente le tableau general des isochrones'''

    global isochrone
    numero_iso           = int(isochrone[-1][2] + 1)
    delta_temps          = intervalles[numero_iso]  # Ecart de temps entre anciens points et nouveaux en s
    nouveau_temps        = temps_initial_iso + delta_temps
    t_iso_formate        = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(temps_initial_iso + delta_temps))
    numero_dernier_point = int(isochrone[-1][4])                   # dernier point isochrone precedent
    numero_premier_point = int(isochrone[-1][4]) - points.shape[0]   # premier point isochrone precedent
    but                  = False   
    
    # on recupere toutes les previsions meteo d'un coup pour l'ensemble des points de depart
    TWS, TWD = prevision_tableau3(tig, GR, temps_initial_iso, points)
    
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
    VT = polaire3_vect(polaires, TWS, TWD, points_calcul2[:,6])
   

# calcul des temps vers l arrivee
    D_a       = points_calcul2[: ,5]               # Distances vers l'arrivee
    T_a       = 60 * D_a / (VT + 0.000001)        # Temps vers l'arrivée nb ce temps est en heures
    temps_mini=(T_a[np.argmin(T_a,0)])      # Valeur du temps minimum

# Verification si le but est atteignable dans le temps d'un isochrone    
    if temps_mini < delta_temps / 3600:
            but = True
    indice2= np.argmin(T_a,0)  + numero_dernier_point + 1     #indice du point de temps minimum

# Constitution du tableau des points retournes en sortie    
    ptn_np2=points_calcul2[:, 0:2]   #(X,Y)

# Ajout des points calcules au tableau global des isochrones
    isochrone = np.concatenate((isochrone, points_calcul2[:,0:5]))  # On rajoute ces points a la fin du tableau isochrone   

# Utilisation pour trace folium  
    trace_iso2=np.concatenate((-points_calcul2[:,1].reshape(-1,1),points_calcul2[:,0].reshape(-1,1)),axis=1)  #(-Y,X)
    
    
    print(' Isochrone  N° {}  {}  {} points  '.format(numero_iso, t_iso_formate,longueur  ))

    return ptn_np2, nouveau_temps, but, indice2,trace_iso2
# ************************************   Fin de la fonction       **********************************************************







#***********************************************************************************************************************
# ************************************   Initialisations      **********************************************************

angle_objectif = 90
indice         = 0
t_v_ar_h       = 0                  #semble utile
nouveau_temps  = 0
t              = time.localtime()
instant        = time.time()
tig, GR        = chargement_grib()
temps          = instant
#Depart
latitude_d     = '047-39-09-N'
longitude_d    = '003-53-09-W'
#Point Arrivee 
latitude_a     = '049-30-00-N'
longitude_a    = '005-06-00-W'




d  = chaine_to_dec(latitude_d, longitude_d)  # conversion des latitudes et longitudes en tuple
ar = chaine_to_dec(latitude_a, longitude_a)
ar=d
d=(-73.62,-40.46)
#print(d)
D = cplx(d)  # transformation des tuples des points en complexes
A = cplx(ar)
#print ('A',A)

# Initialisation du tableau des points d'isochrones
# 0: x du point (longitude), 1: y du point (latitude) , 2: N° isochrone , 3: N° du pt mere ,
# 4: N° du pt , 5: Distance a l'arrivee , 6: Cap vers l'arrivee
#isochrone     = [[D.real, D.imag, 0, 0, 0, dist_cap(D, A)[0], dist_cap(D, A)[1]]]
isochrone     = [[D.real, D.imag, 0, 0, 0]]
print ('isochrone au deaprt',isochrone)


dt1           = np.ones(72) * 600  # intervalles de temps toutes les 10mn pendant une heure puis toutes les heures
dt2           = np.ones(370) * 3600
intervalles   = np.concatenate(([instant - tig], dt1, dt2))
intervalles2   = np.concatenate(([instant - tig], dt1, dt2))
temps_cumules2 = np.cumsum(intervalles2)
temps_cumules = np.cumsum(intervalles)
lat1          = -(d[1]+ar[1])/2                    # Point pour centrer la carte folium
long1         = (d[0]+ ar[0])/2
print('\n\nDepart :  {:6.4f}   {:6.4f}                Arrivee: {:4.2f}   {:4.2f} '.format(d[1], d[0],ar[1], ar[0] ))


# ************************************* Grib   *************************************************************************
instant_formate = time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(instant))
vit_vent_n, TWD = prevision(tig, GR, instant, D.imag, D.real)

# Impression des resultats au depart
print('\nDate et Heure du grib  en UTC  :', time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tig)))
print('\nLe {} heure locale Pour latitude {:6.2f} et longitude{:6.2f} '.format(instant_formate, D.real, D.imag))
print('\tVitesse du vent {:6.3f} Noeuds'.format(vit_vent_n))
print('\tAngle du vent   {:6.1f} °'.format(TWD))
print()



# Initialisation carte folium **************************************************************
m = folium.Map( location=[lat1,long1],  zoom_start=5)
folium.LatLngPopup().add_to(m)   # popup lat long
#*******************************************************************************************

# on initialise l'isochrone de depart avec le depart
pt1_cpx = np.array([[D]])

#print ('pt1_ cpx anterieur', pt1_cpx)
# todo il faudrait stoper si l'on sort des limites de temps du grib

x0=d[0]
y0=d[1]
pt1_np=np.array([[x0,y0]])

# tant que le but n'est pas atteint on calcule des isochrones
but = False
while but == False:
# i=0
# while i<2 :    
    pt1_np, temps, but, indice,trace_iso = f_isochrone(pt1_np, temps)   
    # trace des isochrones
    if isochrone[-1,2]==120:
        X=pt1_cpx.real.reshape(-1,1)
        Y=pt1_cpx.imag.reshape(-1,1)
        points=np.concatenate((-Y,X),axis=1)
        for point in points :
            folium.CircleMarker(point,color='black', radius=1,fill_color='black',fill_opacity=0.3).add_to(m)


        trace_points_folium (pt1_cpx)
    if isochrone[-1,2]%6==0:                             # Le numero de l'isochrone est multiple de 6 on trace en noir
        folium.PolyLine(trace_iso, color="black", weight=2, opacity=0.8).add_to(m)
    else :
        folium.PolyLine(trace_iso, color="red", weight=1, opacity=0.8).add_to(m)

    #i+=1

# print ('isochrone[125]',isochrone[125])
# print ('isochrone2[125]',isochrone2[125])


# route à suivre
# Retracage chemin à l'envers
a = int(indice)                 # indice du point de la route la plus courte
n = int(isochrone[-1][2])       # nombre d'isochrones

# reconstitution de dico par extrait du tableau isochrone
dico=dict(zip(isochrone[:,4],isochrone[:,3]))

route = [a]
for i in range(n):
    a = int(dico[a])
    route.append(a)  # route contient les indices successifs des points a emprunter a l'envers
route.reverse()


# on stocke les valeurs des points dans chemin
chemin = np.zeros(len(route) + 1, dtype=complex)  # on initialise le np array de complexes qui va recevoir les donnees
i = 0
for n in (route):
    chemin[i] = isochrone[n][0] + isochrone[n][1] * 1j
    i += 1
chemin[i] = A

# maintenant on reconstitue le chemin avec les caps les TWA et les previsions
l = len(chemin)
temps_cum = temps_cumules[:l]
temps_cum[-1] = temps_cum[-2] + t_v_ar_h * 3600  # le dernier terme est le temps entre le dernier isochrone et l'arrivee



# previsions meteo aux differents points
TWS_ch, TWD_ch = prevision_tableau2(GR, temps_cum, chemin)

# distance et angle d un point au suivant
distance, cap1 = dist_cap3(chemin[0:-1], chemin[1:])

# on rajoute un 0 pour la distance arrrivee et l angle arrivee
dist = np.append(distance, [0])
HDG_ch = np.append(cap1, [0])  # tableau des caps aux differents points

# calculs twa sous forme de tableau pour les differents points
TWA_ch = twa(HDG_ch, TWD_ch)
# calcul des polaires aux differents points du chemin
POL_ch = polaire3_vect(polaires, TWS_ch, TWD_ch, HDG_ch)

temps_cum += tig
# mise en forme pour concatener
chx =       chemin.real.reshape((1, -1))
chy =       chemin.imag.reshape((1, -1))
temps_pts = temps_cum.reshape((1, -1))
vitesse =   TWS_ch.reshape((1, -1))
TWD =       TWD_ch.reshape((1, -1))
cap =       HDG_ch.reshape((1, -1))
twa =       TWA_ch.reshape((1, -1))
pol =       POL_ch.reshape((1, -1))



# tabchemin : x,y,vit vent ,TWD,cap vers point suivant twa vers point suivant

chem = np.concatenate((chx.T, chy.T, temps_pts.T, vitesse.T, TWD.T, cap.T, twa.T, pol.T), axis=1)


print()
print ('*****************************************Route à suivre ***************************************************')
print('Depart :  {:6.4f}  {:6.4f}       Le {}    Arrivee: {:4.2f}  {:4.2f} '.format(d[1], d[0],instant_formate, ar[1], ar[0] ))
print ('-----------------------------------------------------------------------------------------------------------')

# Exportation en pandas
indexiso=np.arange(l)
df = pd.DataFrame(chem, index = indexiso, columns = ['x', 'y', 't', 'vit_vent','angle_vent','cap','twa', 'polaire'])
print(df.head(12))
print()
df.to_csv('fichier_route.csv')
# print ('tabchemin.shape',chem.shape)
#print('\t n \t\t\t Date \t\t\t\t  X \t\t\tY  \tV_vent \tA_Vent \t Cap  \t TWA\t Polaire')
chemin_folium=[]
np.around(chem, decimals=2)


for i in range(len(chem)):
    chemin_folium.append((-chem[i, 1],chem[i, 0]))
    #print('\t {}  \t{} \t{:6.3f} \t{:6.3f}\t{:6.2f} \t{:6.1f} \t{:6.2f} \t{:6.1f} \t{:6.3f}'
    #      .format(i,time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(chem[i, 2])),
    #    chem[i, 0],chem[i, 1],chem[i, 3],chem[i, 4],chem[i, 5],chem[i, 6],chem[i, 7]))

duree = (temps_cum[-1] - instant)
print('temps total en s ', duree)
h=duree/3600
print('temps total en h {:6.2f}' .format(h))
j = duree // (3600 * 24)
h = duree // 3600-(j*24)
mn = (duree - (j * 3600 * 24) - h * 3600) // 60

#print('temps total  {}h {}mn'.format(duree/3600,(duree-duree//3600))/60)


print('temps total {}j {}h {}mn'.format(j, h, mn))


# Creation de tooltips pour folium
tooltip=[]
popup=[]
for i in range (0,len(chem),1):
    temps=time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(chem[i, 2]))
    heures=str(((chem[i, 2])- instant)//3600)
    long=str(-round(chem[i, 0], 2))
    lat=str(-round(chem[i, 1], 2))
    tws = str(round(chem[i, 3], 1))
    twd = str(round(chem[i, 4], 0))
    cap = str(round(chem[i, 5], 0))
    twa = str(round(chem[i, 6], 0))
    Vt  = str(round(chem[i, 7], 2))
    tooltip.append('<b> H+'+heures+'<br>'+temps+'<br> Lat :'+lat+'° - Long :'+long+'°<br>TWD :' +twd+'°-  TWS :'
                   + tws +'N<br> Cap :' + cap + '° TWA :' +twa +'°<br>Vt :' +Vt+'N</b>')
    popup.append( folium.Popup(folium.Html(tooltip[i], script=True), max_width=200,min_width=150))
for i in range(1, len(chem), 1):
    folium.Circle([-chem[i,1],chem[i,0]],color='black', radius=200,tooltip=tooltip[i], popup=popup[i],fill=True).add_to(m)

#tooltip[0]='<b>'+temps+' <br> Lat :'+lat+'° - Long :'+long+'°<br>TWD :' + twd + '°  TWS :' + tws + 'N<br> Cap ' + cap + '°<br>TWA ' +twa +'°</b>'

folium.Marker([  -d[1], d[0]   ], icon= folium.Icon(color='green', icon='info-sign'), popup=popup[0], tooltip=tooltip[0]).add_to(m)
folium.Marker([ -ar[1], ar[0]  ], icon=folium.Icon(color='red', icon='info-sign'), popup='<i>Arrivee</i>', tooltip=tooltip[len(chem)-1] ).add_to(m)
folium.PolyLine(chemin_folium, color="blue", weight=2.5, opacity=0.8).add_to(m)



filecarte='map.html'
filepath = 'templates/'+filecarte
m.save(filepath)
webbrowser.open( filepath)


#   ****************************************Controle du temps d'execution **********************************
tac = time.time()
print('\nDuree d\'execution:  {:4.2f} s'.format(tac - tic))



#if __name__ == '__main__':