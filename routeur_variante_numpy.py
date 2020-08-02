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
from global_land_mask import globe
from uploadgrib import *
from polaires.polaires_class40 import *
from fonctions_vr import *
from operator import itemgetter
import pickle
from shapely.geometry import Point,Polygon
from shapely import speedups


tic = time.time()
basedir = os.path.abspath(os.path.dirname(__file__))




# ****************************************   Donnees   ****************************************************************
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






def f_isochrone(pt_init_cplx, temps_initial_iso):
    ''' Calcule le nouvel isochrone a partir d'un tableau de points pt2cplx tableau numpy de cplx'''
    ''' deltatemps, tig , U, V sont supposees etre des variables globales'''
    ''' Retourne les nouveaux points el le nouveau temps et implemente le tableau general des isochrones'''

    global isochrone, intervalles, t_v_ar_h,dico
    numero_iso           = int(isochrone[-1][2] + 1)
    delta_temps          = intervalles[numero_iso]  # Ecart de temps entre anciens points et nouveaux en s
    nouveau_temps       = temps_initial_iso + delta_temps
    t_iso_formate        = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(temps_initial_iso + delta_temps))
    numero_dernier_point = (isochrone[-1][4])                    # dernier point isochrone precedent
    numero_premier_point = isochrone[-1][4] - pt_init_cplx.size  # premier point isochrone precedent
   
    but                  = False
    points_calcul        = []
    caps_x               = []
    tab_t                = []  # tableau des temps vers l arrivee en ligne directe
    trace_iso            = []
   
   
   
    # on recupere toutes les previsions meteo d'un coup pour l'ensemble des points de depart
    TWS, TWD = prevision_tableau(tig, GR, temps_initial_iso, pt_init_cplx)
   
    #tableau=np.array([[0,0,0,0,0,0,0]])
    # pour chaque point de l'isochrone precedent  donnés en entrée (isochrone précédent)
    for i in range(pt_init_cplx.size): # on parcourt les points de l'isochrone precedent
        n=0
        HDG = range_cap(dist_cap(pt_init_cplx[0][i], A)[1], TWD[i], angle_objectif, angle_twa_pres, angle_twa_ar)  # Calcul des caps a etudier
        VT = polaire2_vect(polaires, TWS[i], TWD[i], HDG)               # calcul des vitesses polaires suivant ces caps
        n_pts = deplacement2(pt_init_cplx[0][i], delta_temps, HDG, VT)  #coordonnees des nouveaux points calcules
        
        
        tableau=np.ones((len(HDG),7))                                   # on reserve un tableau numpy pour stocker
       
       

       # on stocke les nouveaux points dans le np.array réservé pour ce point en particulier
        tableau[:,0]=n_pts.real
        tableau[:,1]=n_pts.imag
        tableau[:,2]=numero_iso
        tableau[:,3]=numero_premier_point+i                         # numero du point mere
        tableau[:,4]=i                                             # numero du point  , sera renumeroté après purge
        tableau[:,5]=dist_cap3(pt_init_cplx[0][i],A)[0]             # distance a l'arrivee
        tableau[:,6]=dist_cap3(pt_init_cplx[0][i],A)[1]             # cap vers l'arrivee
        if n>0: 
            tableau=np.concatenate((tableau,tableau),axis=0)

   
    for i in range (tableau.shape[0]):
        print ('\t{:6.4f} \t {:6.4f} \t {} \t {} \t {:4.2f} \t {:4.2f} \t {:4.2f}' .format(tableau[i][0],tableau[i][1],tableau[i][2],tableau[i][3],tableau[i][4],tableau[i][5],tableau[i][6]))

    #print(' Isochrone N° {}  {}'.format(numero_iso, t_iso_formate))
    #isochrone = np.concatenate((isochrone, tableau))  # On rajoute ces points a la fin du tableau isochrone
    ptn_cplx = np.array([tableau[:, 0] + tableau[:, 1] * 1j])  # on reforme un tableau numpy de complexes pour la sortie
    return ptn_cplx,nouveau_temps









angle_objectif = 90
dico = {}
indice = 0
t_v_ar_h = 0
nouveau_temps = 0
t = time.localtime()
instant = time.time()
tig, GR =chargement_grib()
temps = instant
#todo ###############################################################"
# Depart ou position actuelle ###########################################################"
# latitude_d = '052-04-00-N'
# longitude_d = '006-28-00-W'

# #Point Arrivee 
# latitude_a = '051-50-00-N'
# longitude_a = '006-44-00-W'

latitude_d = '047-39-09-N'
longitude_d = '003-53-09-W'
#Point Arrivee 
latitude_a = '049-00-00-N'
longitude_a = '006-30-00-W'




d = chaine_to_dec(latitude_d, longitude_d)  # conversion des latitudes et longitudes en tuple
ar = chaine_to_dec(latitude_a, longitude_a)

ar=(-4.09,-47.64)
d=(-3.89,-47.65)
D = cplx(d)  # transformation des tuples des points en complexes
A = cplx(ar)

# Initialisation du tableau des points d'isochrones
# 0: x du point (longitude), 1: y du point (latitude) , 2: N° isochrone , 3: N° du pt mere ,
# 4: N° du pt , 5: Distance a l'arrivee , 6: Cap vers l'arrivee
isochrone = [[D.real, D.imag, 0, 0, 0, dist_cap(D, A)[0], dist_cap(D, A)[1]]]

dt1 = np.ones(72) * 600  # intervalles de temps toutes les 10mn pendant une heure puis toutes les heures
dt2 = np.ones(370) * 3600
intervalles = np.concatenate(([instant - tig], dt1, dt2))
temps_cumules = np.cumsum(intervalles)

lat1=-(d[1]+ar[1])/2                    # Point pour centrer la carte folium
long1= (d[0]+ ar[0])/2


# ************************************* Grib   *************************************************************************
instant_formate = time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(instant))
vit_vent_n, TWD = prevision(tig, GR, instant, D.imag, D.real)

# Impression des resultats au depart

print('Depart : Latitude {:6.4f}  Longitude {:6.4f}'.format(d[1], d[0]))
print('Arrivee: Latitude {:4.2f}  Longitude {:4.2f}'.format(ar[1], ar[0]))
print('Date et Heure du grib  en UTC  :', time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tig)))
print('\nLe {} heure locale Pour latitude {:6.2f} et longitude{:6.2f} '.format(instant_formate, D.real, D.imag))
print('\tVitesse du vent {:6.3f} Noeuds'.format(vit_vent_n))
print('\tAngle du vent   {:6.1f} °'.format(TWD))
print()




# on initialise l'isochrone de depart avec le depart
pt1_cpx = np.array([[D]])
# todo il faudrait stoper si l'on sort des limites de temps du grib
# tant que le but n'est pas atteint on calcule des isochrones





# but = False
# while but == False:
#     # i=0
#     # while i<1:  pour test
#     #todo *********************************************************************
#     pt1_cpx, temps, but, indice,trace_iso = f_isochrone(pt1_cpx, temps)
  
  
#     # trace des isochrones
#     if isochrone[-1,2]%6==0:
#         folium.PolyLine(trace_iso, color="black", weight=2, opacity=0.8).add_to(m)
#     else :
#         folium.PolyLine(trace_iso, color="red", weight=1, opacity=0.8).add_to(m)


# # Retracage chemin à l'envers
# a = int(indice)                 # indice du point de la route la plus courte
# n = int(isochrone[-1][2])       # nombre d'isochrones

# # on reconstitue la route à suivre en remontant le chemin
# route = []
# for i in range(n):
#     a = int(dico[a])
#     route.append(a)  # route contient les indices successifs des points a emprunter a l'envers
# route.reverse()

# # on stocke les valeurs des points dans chemin
# chemin = np.zeros(len(route) + 1, dtype=complex)  # on initialise le np array de complexes qui va recevoir les donnees
# i = 0
# for n in (route):
#     chemin[i] = isochrone[n][0] + isochrone[n][1] * 1j
#     i += 1
# chemin[i] = A

# # maintenant on reconstitue le chemin avec les caps les TWA et les previsions
# l = len(chemin)
# temps_cum = temps_cumules[:l]
# temps_cum[-1] = temps_cum[-2] + t_v_ar_h * 3600  # le dernier terme est le temps entre le dernier isochrone et l'arrivee

# # previsions meteo aux differents points
# TWS_ch, TWD_ch = prevision_tableau2(GR, temps_cum, chemin)

# # distance et angle d un point au suivant
# distance, cap1 = dist_cap(chemin[0:-1], chemin[1:])

# # on rajoute un 0 pour la distance arrrivee et l angle arrivee
# dist = np.append(distance, [0])
# HDG_ch = np.append(cap1, [0])  # tableau des caps aux differents points

# # calculs twa sous forme de tableau pour les differents points
# TWA_ch = twa(HDG_ch, TWD_ch)
# # calcul des polaires aux differents points du chemin
# POL_ch = polaire3_vect(polaires, TWS_ch, TWD_ch, HDG_ch)

# temps_cum += tig
# # mise en forme pour concatener
# chx =       chemin.real.reshape((1, -1))
# chy =       chemin.imag.reshape((1, -1))
# temps_pts = temps_cum.reshape((1, -1))
# vitesse =   TWS_ch.reshape((1, -1))
# TWD =       TWD_ch.reshape((1, -1))
# cap =       HDG_ch.reshape((1, -1))
# twa =       TWA_ch.reshape((1, -1))
# pol =       POL_ch.reshape((1, -1))



# # tabchemin : x,y,vit vent ,TWD,cap vers point suivant twa vers point suivant
# chem = np.concatenate((chx.T, chy.T, temps_pts.T, vitesse.T, TWD.T, cap.T, twa.T, pol.T), axis=1)
# # print ('tabchemin \n',chem)
# # Exportation en pandas
# indexiso=np.arange(l)
# df = pd.DataFrame(chem, index = indexiso, columns = ['x', 'y', 't', 'vitesse_v','angle_v','cap','twa', 'polaire'])
# print(df.head(5))
# df.to_csv('fichier_route.csv')
# # print ('tabchemin.shape',chem.shape)
# print('\t n \t\t\t Date \t\t\t\t  X \t\t\tY  \tV_vent \tA_Vent \t Cap  \t TWA\t Polaire')
# chemin_folium=[]
# np.around(chem, decimals=2)
# for i in range(len(chem)):
#     chemin_folium.append((-chem[i, 1],chem[i, 0]))
#     print('\t {}  \t{} \t{:6.3f} \t{:6.3f}\t{:6.2f} \t{:6.1f} \t{:6.2f} \t{:6.1f} \t{:6.3f}'
#           .format(i,time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(chem[i, 2])),
#         chem[i, 0],chem[i, 1],chem[i, 3],chem[i, 4],chem[i, 5],chem[i, 6],chem[i, 7]))

# duree = (temps_cum[-1] - instant)
# print('temps total en s ', duree)
# h=duree/3600
# print('temps total en h {:6.2f}' .format(h))
# j = duree // (3600 * 24)
# h = duree // 3600-(j*24)
# mn = (duree - (j * 3600 * 24) - h * 3600) // 60

# #print('temps total  {}h {}mn'.format(duree/3600,(duree-duree//3600))/60)


# print('temps total {}j {}h {}mn'.format(j, h, mn))


# # Creation de tooltips pour folium
# tooltip=[]
# popup=[]
# for i in range (0,len(chem),1):
#     temps=time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(chem[i, 2]))
#     heures=str(((chem[i, 2])- instant)//3600)
#     long=str(-round(chem[i, 0], 2))
#     lat=str(-round(chem[i, 1], 2))
#     tws = str(round(chem[i, 3], 1))
#     twd = str(round(chem[i, 4], 0))
#     cap = str(round(chem[i, 5], 0))
#     twa = str(round(chem[i, 6], 0))
#     Vt  = str(round(chem[i, 7], 2))
#     tooltip.append('<b> H+'+heures+'<br>'+temps+'<br> Lat :'+lat+'° - Long :'+long+'°<br>TWD :' +twd+'°-  TWS :'
#                    + tws +'N<br> Cap :' + cap + '° TWA :' +twa +'°<br>Vt :' +Vt+'N</b>')
#     popup.append( folium.Popup(folium.Html(tooltip[i], script=True), max_width=200,min_width=150))
# for i in range(1, len(chem), 1):
#     folium.Circle([-chem[i,1],chem[i,0]],color='black', radius=200,tooltip=tooltip[i], popup=popup[i],fill=True).add_to(m)

# #tooltip[0]='<b>'+temps+' <br> Lat :'+lat+'° - Long :'+long+'°<br>TWD :' + twd + '°  TWS :' + tws + 'N<br> Cap ' + cap + '°<br>TWA ' +twa +'°</b>'
# # test = folium.Html(tooltip[0], script=True)
# # popupdepart = folium.Popup(test, max_width=200,min_width=150)



# folium.Marker([-d[1], d[0]], popup=popup[0], tooltip=tooltip[0]).add_to(m)
# folium.Marker([-ar[1], ar[0]], popup='<i>Arrivee</i>', tooltip=tooltip[len(chem)-1]).add_to(m)
# folium.PolyLine(chemin_folium, color="blue", weight=2.5, opacity=0.8).add_to(m)

# filecarte='map.html'

# filepath = 'templates/'+filecarte
# m.save(filepath)
# webbrowser.open( filepath)

def trace_points_folium (points_cpx):
#on extrait les coordonnes pour tracer
    X=points_cpx.real.reshape(-1,1)
    Y=points_cpx.imag.reshape(-1,1)
    points=np.concatenate((-Y,X),axis=1)
    for point in points :
        folium.CircleMarker(point,color='black', radius=1,fill_color='black',fill_opacity=0.3).add_to(carte)
    return None





if __name__ == '__main__':

    #initialisation Depart Arrivee ***********************************************************
    ar=(-4.09,-47.64)
    d=(-3.89,-47.65)
    temps = time.time()    # pour le premier calcul
    D = cplx(d)  # transformation des tuples des points en complexes
    A = cplx(ar)
    #*******************************************************************************************


    #initialisation du tableau des isochrones *************************************************
    isochrone = [[D.real, D.imag, 0, 0, 0, dist_cap(D, A)[0], dist_cap(D, A)[1]]]


    #initialisation des ecarts de temps entre les isochrones **********************************
    dt1           = np.ones(72) * 600  # intervalles de temps toutes les 10mn pendant une heure puis toutes les heures
    dt2           = np.ones(370) * 3600
    intervalles   = np.concatenate(([instant - tig], dt1, dt2))
    temps_cumules = np.cumsum(intervalles)
    #*******************************************************************************************

    # Initialisation carte folium **************************************************************
    lat1  = -(d[1]+ar[1])/2                    # Point pour centrer la carte folium
    long1 = (d[0]+ ar[0])/2
    carte = folium.Map( location = [lat1,long1],  zoom_start = 9)
    folium.LatLngPopup().add_to(carte)   # popup lat long
    folium.Marker([  -d[1], d[0]   ], icon= folium.Icon(color='green', icon='info-sign') ).add_to(carte)
    folium.Marker([ -ar[1], ar[0]  ], icon=folium.Icon(color='red', icon='info-sign') ).add_to(carte)
    #*******************************************************************************************

    
    # test de la fonction 
    
    points_cpx = np.array([[D]])
    points_cpx, temps= f_isochrone(points_cpx, temps)
    # print ('Tableau de points', points_cpx)
    # i=0
    # print ('premier point',points_cpx[0][i])

    #trace_points_folium (points_cpx)




    # on fait une deuxime fois
    points_cpx, temps= f_isochrone(points_cpx, temps)
    #trace_points_folium (points_cpx)
    # #on extrait les coordonness pour tracer
    # X=points_cpx.real.reshape(-1,1)
    # Y=points_cpx.imag.reshape(-1,1)
    # points=np.concatenate((-Y,X),axis=1)
    # for point in points :
    #     folium.CircleMarker(point,color='black', radius=1,fill_color='black',fill_opacity=0.3).add_to(carte)


    
    #  print (tableau)
    #     # on extrait les coordonnees pour tracer l'isochrone
    #     coords= np.fliplr(np.delete(tableau,[2,3,4,5,6],1))
    #     coords[:,0]=-coords[:,0]   # changement de signe des latitudes
    #     # on trace les points
    #     print (coords)
    #     for point in coords:
    #         folium.CircleMarker(point,color='black', radius=1,fill_color='black',fill_opacity=0.3).add_to(carte)
    
    
    
    # on l'applique une deuxieme fois


   # si on veut tracer a partir de tableau
   # coords=np.fliplr(np.delete(tableau,[2,3,4,5,6],1))




    #affichage de la carte
    
    
    
    # trace des points de la route
    # for point in coords :
    #     folium.CircleMarker(point,color='black', fill_color='black',fill_opacity=0.3).add_to(carte)

    # enregistrement et ouverture de la carte
    filecarte='map.html'
    filepath = 'templates/'+filecarte
    carte.save(filepath)
    webbrowser.open( filepath)

    #   ****************************************Controle du temps d'execution **********************************
    tac = time.time()
    print('\nDuree d\'execution:  {:4.2f} s'.format(tac - tic))