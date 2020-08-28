#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 08:52:41 2019
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
import copy
from global_land_mask import globe

from uploadgrib import *
from polaires.polaires_ultime import *
from fonctions_vr import *
from operator import itemgetter
import pickle
from shapely.geometry import Point,Polygon
from shapely import speedups


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



# def f_isochrone2 (pt_ws_wd,temps_initial_iso2):
#     ''' Calcule le nouvel isochrone a partir d'un tableau de points  numpy   X,Y, TWS,TWD '''
#     ''' deltatemps, tig , U, V sont supposees etre des variables globales'''
#     ''' Retourne les nouveaux points el le nouveau temps et implemente le tableau general des isochrones'''   
    
#     global isochrone2, intervalles, t_v_ar_h,dico
#     numero_iso2          = int(isochrone2[-1][2] + 1)
#     delta_temps          = intervalles[numero_iso2]  # Ecart de temps entre anciens points et nouveaux en s
#     nouveau_temps        = temps_initial_iso2 + delta_temps
#     t_iso_formate        = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(temps_initial_iso2 + delta_temps))
#     numero_dernier_point = int(isochrone2[-1][4])                   # dernier point isochrone precedent
#     numero_premier_point = int(isochrone2[-1][4]) - points.shape[0]   # premier point isochrone precedent
#     but                  = False
    
#     points_calcules2=np.array([[0,0,0,0,0,0,0]]) # initialisation pour Numpy du brouillard des points calcules
#     longueur2= pt_ws_wd.shape[0] 
       
#     points=pt_ws_wd[:,0:2]   #points est l'equivalent de points dans l'ancienne version
#     TWS=pt_ws_wd[:,2:3]
#     TWD=pt_ws_wd[:,3:4]

#     # ici on evite de recalculer TWS et TWD 
#     for i in range(points.shape[0]):
#         HDG = range_cap(dist_cap4(points[i], A)[1], TWD[i], angle_objectif, angle_twa_pres, angle_twa_ar)  # Calcul des caps a etudier
#         VT = polaire2_vect(polaires, TWS[i], TWD[i], HDG)
    
#         X1,Y1,Da1,Ca1=deplacement_x_y_tab_ar(points[i][0],points[i][1],delta_temps,HDG,VT,A) #coordonnees des nouveaux points calcules sous forme X,Y
#         L=len(X1)  
#         # on forme le tableau des points calcules pour chaque ppoint initial
#         niso1= np.ones(L)*numero_iso   #len(X1) doit pouvoir etre evite 3 fois
#         npointsm1=np.ones(L)*i  +numero_premier_point +1    # numero du point mere i= 0 correspond au premier point de l'isochrone precedent
#         npoints1=np.array(range(L)) +1           # numero du point  sans importance sera renumeroté
#         X=X1.reshape(-1,1)
#         Y=Y1.reshape(-1,1)
#         niso=niso1.reshape(-1,1)
#         npointsm=npointsm1.reshape(-1,1)
#         npoints=npoints1.reshape(-1,1)
#         Da=Da1.reshape(-1,1)
#         Ca=Ca1.reshape(-1,1)

#         # maintenant on forme le tableau correspondant à n_pts_x
#         n_pts_x2     = np.concatenate((X,Y,niso,npointsm,npoints,Da,Ca), axis=1)    # tableau des points pour un point de base
#         points_calcules= np.concatenate((points_calcules,n_pts_x2), axis=0)           # tableau du brouillard des points 
       


#     # print(' NV Isochrone calculé N° {}  {}  {} points  '.format(numero_iso, t_iso_formate,longueur  ))
#     return None




def f_isochrone(pt_ws_wd, temps_initial_iso):
    ''' Calcule le nouvel isochrone a partir d'un tableau de points pt2cplx tableau numpy de cplx'''
    ''' deltatemps, tig , U, V sont supposees etre des variables globales'''
    ''' Retourne les nouveaux points el le nouveau temps et implemente le tableau general des isochrones'''

    global isochrone, intervalles, t_v_ar_h,dico
    numero_iso           = int(isochrone[-1][2] + 1)
    delta_temps          = intervalles[numero_iso]  # Ecart de temps entre anciens points et nouveaux en s
    nouveau_temps        = temps_initial_iso + delta_temps
    t_iso_formate        = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(temps_initial_iso + delta_temps))
    numero_dernier_point = int(isochrone[-1][4])                   # dernier point isochrone precedent
    numero_premier_point = int(isochrone[-1][4]) - pt_ws_wd.shape[0]   # premier point isochrone precedent
    but                  = False
    
    points_calcules=np.array([[0,0,0,0,0,0,0]]) # initialisation pour Numpy du brouillard des points calcules
    

    
    
    # on recupere toutes les previsions meteo d'un coup pour l'ensemble des points de depart
#ancienne version 
    # TWS, TWD = prevision_tableau3(tig, GR, temps_initial_iso, points)
    # print('\n(136) Ancien TWS calcule en debut ', TWS)
    # print('\n(137) Ancien TWD calcule en debut', TWD)
#version 2
    points=pt_ws_wd[:,0:2]   #points est l'equivalent de points dans l'ancienne version
    TWS=pt_ws_wd[:,2:3]
    TWD=pt_ws_wd[:,3:4]

    # print('\n(142) TWS recupere en debut ', TWS)
    # print('\n(143) TWD recupere en debut', TWD)


    # pour chaque point de l'isochrone precedent  donnés en entrée (isochrone précédent)
    for i in range(points.shape[0]):
        HDG = range_cap(dist_cap4(points[i], A)[1], TWD[i], angle_objectif, angle_twa_pres, angle_twa_ar)  # Calcul des caps a etudier
        VT = polaire2_vect(polaires, TWS[i], TWD[i], HDG)
    
    
        X1,Y1,Da1,Ca1=deplacement_x_y_tab_ar(points[i][0],points[i][1],delta_temps,HDG,VT,A) #coordonnees des nouveaux points calcules sous forme X,Y
        L=len(X1)  
        # on forme le tableau des points calcules pour chaque ppoint initial
        niso1= np.ones(L)*numero_iso   #len(X1) doit pouvoir etre evite 3 fois
        npointsm1=np.ones(L)*i  +numero_premier_point +1    # numero du point mere i= 0 correspond au premier point de l'isochrone precedent
        npoints1=np.array(range(L)) +1           # numero du point  sans importance sera renumeroté
        X=X1.reshape(-1,1)
        Y=Y1.reshape(-1,1)
        niso=niso1.reshape(-1,1)
        npointsm=npointsm1.reshape(-1,1)
        npoints=npoints1.reshape(-1,1)
        Da=Da1.reshape(-1,1)
        Ca=Ca1.reshape(-1,1)

        # maintenant on forme le tableau correspondant à n_pts_x
        n_pts_x2     = np.concatenate((X,Y,niso,npointsm,npoints,Da,Ca), axis=1)    # tableau des points pour un point de base
        points_calcules= np.concatenate((points_calcules,n_pts_x2), axis=0)           # tableau du brouillard des points 
       

    points_calcules=np.delete(points_calcules,0,0)                                    # on retire le premier terme de points_calcules
    points_calcules= points_calcules[points_calcules[:,6].argsort(kind='mergesort')]   # tri stable sur 6eme colonne


     
# On recole les caps 359 et 1
    k=0
    while (((points_calcules[k][6]-points_calcules[k-1][6])<-357)and (k<points_calcules.shape[0]-1)):
        points_calcules[k][6]+=360
        k+=1
    points_calcules= points_calcules[points_calcules[:,6].argsort(kind='mergesort')]
    capmini=points_calcules[0][6]
    capmaxi=points_calcules[-1][6]
    coeff = 49/ (capmaxi-capmini)  # coefficient pour ecremer et garder 50 points
   
    
#ecremage arrondi et tri

    points_calcules[:,6]=np.floor(points_calcules[:,6]*coeff)   # le calcul est fait sur la colonne sans boucle variante around
    points_calcules= points_calcules[points_calcules[:,5].argsort(kind='mergesort')] #on trie sur les distances 
    points_calcules= points_calcules[points_calcules[:,6].argsort(kind='mergesort')] #on trie sur les caps mais l'ordre des distances est respecté
   
   
    for i in range(points_calcules.shape[0] - 1, 0, -1):  # ecremage
        if (points_calcules[i][6]) == (points_calcules[i - 1][6]):
            points_calcules = np.delete(points_calcules, i, 0)
    longueur= points_calcules.shape[0]      
# A ce moment il ne subsiste que 50 points        
   
# verification points terre ou mer
    
    for i in range(points_calcules.shape[0] - 1, 0, -1):  # ecremage 
        is_on_land = globe.is_land(-points_calcules[i][1], points_calcules[i][0])   # point de latitude -y et longitude x
        if (is_on_land==True):
            points_calcules = np.delete(points_calcules, i, 0)

# on retablit le cap en valeur a rechanger en around 0 decimale   
    points_calcules[:,6]=np.floor(points_calcules[:,6]/coeff)       
    points_calcules= points_calcules[points_calcules[:,6].argsort(kind='mergesort')] #on trie sur les caps a voir si necessaire !

# renumerotation sur la colonne 4  le premier numero est le numero dernier point iso precedent +1  
    N=np.array( range( int(numero_dernier_point) + 1, points_calcules.shape[0] +int(numero_dernier_point) + 1,1))  # tableau des indices
    points_calcules[:,4]=N     # renumerotation
    TWS, TWD =prevision_tableau3(tig, GR, nouveau_temps, points_calcules) # Vitesse vent et direction pour nouveaux points (extraction en double)
    VT = polaire3_vect(polaires, TWS, TWD, points_calcules[:,6])
    # print('(217) TWS extrait en fin d isochrone', TWS)
    # print('(218) TWD extrait en fin ', TWD)



    # calcul des temps vers l arrivee
    D_a = points_calcules[:,5]               # Distances vers l'arrivee
    T_a = 60 * D_a / (VT + 0.000001)        # Temps vers l'arrivée nb ce temps est en heures
    temps_mini=(T_a[np.argmin(T_a,0)])      # Valeur du temps minimum
    
    if temps_mini < delta_temps / 3600:
            but = True
    indice= np.argmin(T_a,0)  + numero_dernier_point + 1     #indice du point de temps minimum
    #ptn_np=points_calcules[:, 0:2]                           # tableau des (X,Y) pour redonner au calcul de  l'isochrone suivant
    #print('231   ptn_np en sortie \n',ptn_np)
# Nouvelle version on reforme pt_ws_wd
    
    pt_ws_wd=np.concatenate((   points_calcules[:, 0:2]       ,TWS.reshape(-1,1),TWD.reshape(-1,1)),axis=1)
    #print('231   pt_ws_wd en sortie \n',pt_ws_wd)

    trace_iso=np.concatenate((-points_calcules[:,1].reshape(-1,1),points_calcules[:,0].reshape(-1,1)),axis=1)  #(-Y,X)
    isochrone = np.concatenate((isochrone, points_calcules))  # On rajoute ces points a la fin du tableau isochrone
      
    print(' Isochrone calculé N° {}  {}  {} points cap mini  {:4.2f}  cap maxi {:4.2f}  '.format(numero_iso, t_iso_formate,longueur,capmini ,  capmaxi  ))

    return  pt_ws_wd,nouveau_temps, but, indice,trace_iso

#***********************************************************************************************************************
#***********************************************************************************************************************
#***********************************************************************************************************************
# ************************************   Initialisations      **********************************************************

angle_objectif = 90
dico           = {}
indice         = 0
t_v_ar_h       = 0
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
isochrone     = [[D.real, D.imag, 0, 0, 0, dist_cap(D, A)[0], dist_cap(D, A)[1]]]
#v2
isochrone2     = [[D.real, D.imag, 0, 0, 0, dist_cap(D, A)[0], dist_cap(D, A)[1]]]

dt1           = np.ones(72) * 600  # intervalles de temps toutes les 10mn pendant une heure puis toutes les heures
dt2           = np.ones(370) * 3600
intervalles   = np.concatenate(([instant - tig], dt1, dt2))
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
m = folium.Map( location=[lat1,long1],  zoom_start=6)
folium.LatLngPopup().add_to(m)   # popup lat long
#*******************************************************************************************

# on initialise l'isochrone de depart avec le depart
pt1_cpx = np.array([[D]])

#print ('pt1_ cpx anterieur', pt1_cpx)
# todo il faudrait stoper si l'on sort des limites de temps du grib

x0=d[0]
y0=d[1]
pt1_np=np.array([[x0,y0]])

TWS, TWD = prevision(tig, GR, instant, y0, x0)
pt_ws_wd=np.array([[x0,y0,TWS,TWD]])
#print('(337) pt_ws_wd',pt_ws_wd)

# tant que le but n'est pas atteint on calcule des isochrones
but = False
while but == False:
# i=0
# while i<2 :    
    pt_ws_wd,temps, but, indice,trace_iso = f_isochrone(pt_ws_wd, temps)
    #f_isochrone2 (pt_ws_wd,temps)  # sert a impimer les resultats 
    # trace des isochrones
    if isochrone[-1,2]==120:
        X=pt1_cpx.real.reshape(-1,1)
        Y=pt1_cpx.imag.reshape(-1,1)
        points=np.concatenate((-Y,X),axis=1)
        for point in points :
            folium.CircleMarker(point,color='black', radius=1,fill_color='black',fill_opacity=0.3).add_to(m)


        trace_points_folium (pt1_cpx)
    if isochrone[-1,2]%6==0:
        folium.PolyLine(trace_iso, color="black", weight=2, opacity=0.8).add_to(m)
    else :
        folium.PolyLine(trace_iso, color="red", weight=1, opacity=0.8).add_to(m)

    #i+=1




# route à suivre
# Retracage chemin à l'envers
a = int(indice)                 # indice du point de la route la plus courte
n = int(isochrone[-1][2])       # nombre d'isochrones

# on reconstitue la route à suivre en remontant le chemin
# fabrication du dictionnaire a partir du tableau isochrone


#print ('(447)  Extrait de dico',dico[139])


# reconstitution de dico par extrait du tableau isochrone
dico2=dict(zip(isochrone[:,4],isochrone[:,3]))
#print ('(452) Extrait de dico',dico2[139])

route = [a]
for i in range(n):
    a = int(dico2[a])
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

# print ('tabchemin \n',chem)

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