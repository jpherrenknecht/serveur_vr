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
from polaires.polaires_class40 import *
from fonctions_vr import *
from operator import itemgetter
import pickle
from shapely.geometry import Point,Polygon
from shapely import speedups


tic = time.time()
basedir = os.path.abspath(os.path.dirname(__file__))


#autre test

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


def f_isochrone(pt_init_cplx, temps_initial_iso):
    ''' Calcule le nouvel isochrone a partir d'un tableau de points pt2cplx tableau numpy de cplx'''
    ''' deltatemps, tig , U, V sont supposees etre des variables globales'''
    ''' Retourne les nouveaux points el le nouveau temps et implemente le tableau general des isochrones'''

    global isochrone, intervalles, t_v_ar_h,dico
    numero_iso           = int(isochrone[-1][2] + 1)
    delta_temps          = intervalles[numero_iso]  # Ecart de temps entre anciens points et nouveaux en s
    nouveau_temps = temps_initial_iso + delta_temps
    t_iso_formate        = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(temps_initial_iso + delta_temps))
    numero_dernier_point = (isochrone[-1][4])  # dernier point isochrone precedent
    numero_premier_point = isochrone[-1][4] - pt_init_cplx.size
   
    but                  = False
    points_calcul        = []
    caps_x               = []
    tab_t                = []  # tableau des temps vers l arrivee en ligne directe
    trace_iso            = []
    nbhdg=0
  
    
    # on recupere toutes les previsions meteo d'un coup pour l'ensemble des points de depart
    TWS, TWD = prevision_tableau(tig, GR, temps_initial_iso, pt_init_cplx)


    # pour chaque point de l'isochrone precedent  donnés en entrée (isochrone précédent)
    for i in range(pt_init_cplx.size):
       
        HDG = range_cap(dist_cap(pt_init_cplx[0][i], A)[1], TWD[i], angle_objectif, angle_twa_pres, angle_twa_ar)  # Calcul des caps a etudier
        VT = polaire2_vect(polaires, TWS[i], TWD[i], HDG)
        
        VT = polaire2_vect(polaires, TWS[i], TWD[i], HDG)
        n_pts_x = deplacement2(pt_init_cplx[0][i], delta_temps, HDG, VT)   #coordonnees des nouveaux points calcules
       

       
        # if numero_iso ==79 :
        #     print ('nb de points etudies', len (n_pts_x))

        for j in range(len(n_pts_x)):
            cap_arrivee = dist_cap(n_pts_x[j], A)[1]
            distance_arrivee = dist_cap(n_pts_x[j], A)[0]
            points_calcul.append(
            [n_pts_x[j].real, n_pts_x[j].imag, numero_iso, numero_premier_point+i+1 , 1, distance_arrivee,cap_arrivee])

            #caps_x.append(cap_arrivee)

    #tri de la liste des points
    #         
        points_calcul=sorted(points_calcul,key=lambda colonnes :colonnes[6])
   
   

    # if numero_iso ==80 :
    #     i=numero_iso
    #     print()
       
    #     print()
    #     #print('points calculs ( tout) ',points_calcul)
    #     print()
    #     print('nb total de points',len(points_calcul))
    #     print('points calculs cap min ',points_calcul[0][6])
    #     print('points calculs cap max',points_calcul[-1][6])
    #     print()
    #     print('points calculs2 cap min ',points_calcul2[0][6])
    #     print('points calculs2 cap max',points_calcul2[-1][6])
    
    #     for i in range (50):
    #         print(' i', i, ' ', points_calcul[i][6]) 
    #     print()

        i=0
        while (points_calcul[i][6]-points_calcul[i-1][6])<-357 :
            #print(' i', i, ' ', points_calcul[i][6])    
            points_calcul[i][6]+=360
            i+=1

    #     for i in range (50):
    #         print(' i', i, ' ', points_calcul[i][6]) 
    #     print()


        points_calcul=sorted(points_calcul,key=lambda colonnes :colonnes[6])

        # for i in range (50):
        #     print(' i', i, ' ', points_calcul[i][6]) 
        # print()
        # print(' i', i, ' ', points_calcul[-1][6]) 
        # print()
       
        # print()
       
        # print('points calculs nouveau cap min ',points_calcul[0][6])
        # print('points calculs nouveau cap max',points_calcul[-1][6])

        capmini=points_calcul[0][6]
        capmaxi=points_calcul[-1][6]

    #max des caps
    # maxi=(max(points_calcul,key=lambda colonnes :colonnes[6])[6])
    # mini=(min(points_calcul,key=lambda colonnes :colonnes[6])[6])

    # maxi2=(max(points_calcul2,key=lambda colonnes :colonnes[6])[6])
    # mini2=(min(points_calcul2,key=lambda colonnes :colonnes[6])[6])

    #print(type(points_calcul))

    # la tous les nouveaux points sont calcules maintenant on expurge et on stocke


    #coeff2 = 50 / (max(caps_x) - min(caps_x))  # coefficient pour ecremer et garder 50 points
        coeff2 = 50 / (capmaxi-capmini)  # coefficient pour ecremer et garder 50 points

    #if numero_iso ==79 :
    #    print('nb total de points',len(points_calcul))





    for j in range(len(points_calcul)):  # partie ecremage
        points_calcul[j][6] = int(coeff2 * points_calcul[j][6])

    pointsx = sorted(points_calcul, key=itemgetter(6, 5))  # tri de la liste de points suivant la direction (indice  " \
    pointsx = np.asarray(pointsx)
    for i in range(len(pointsx) - 1, 0, -1):  # ecremage
        if (pointsx[i][6]) == (pointsx[i - 1][6]):
            pointsx = np.delete(pointsx, i, 0)

    # todo c'est ici qu'il faut supprimer les point a terre

    # verification points terre ou mer
    longueur=len(pointsx)

    for i in range(len(pointsx)-1, -1, -1):  # ecremage proprement dit 
        is_on_land = globe.is_land(-pointsx[i][1], pointsx[i][0])
        if (is_on_land==True):
            pointsx = np.delete(pointsx, i, 0)



    #print (pointsx)
    #
    # for i in range(len(pointsx) - 1, 0, -1):  # ecremage point a terre
    #     point=Point(pointsx[i][0],-pointsx[i][1])
    #     if point.within(a):
    #         #print("le point est a terre")
    #         pointsx = np.delete(pointsx, i, 0)
    #     # else:
    #     #     print("le point est en mer")


    for i in range(len(pointsx)):  # renumerotation
        pointsx[i][4] = i + numero_dernier_point + 1
        pointsx[i][6] = int(pointsx[i][6] / coeff2)  # on retablit le cap en valeur
        dico[pointsx[i][4]] = pointsx[i][3]
        trace_iso.append((-pointsx[i][1], pointsx[i][0]))




        # a ce moment la on a le catalogue de tous les nouveaux points
        # todo la partie a suivre pourrait etre traitee en vectoriel hors de la boucle

        # on cherche les temps vers l'arrivee des nouveaux points
        vit_vent, TWD = prevision(tig, GR, nouveau_temps, pointsx[i][1], pointsx[i][0])
        twa = 180 - abs(((360 - TWD + pointsx[i][6]) % 360) - 180)

        resultat = polaire(polaires, vit_vent, twa)
        d_a = pointsx[i][5]
        t_a = 60 * d_a / (resultat + 0.000001)  # nb ce temps est en heures
        tab_t.append(t_a)
        # print('temps',t_a)
        if t_a < delta_temps / 3600:
            but = True
        # indice du temps minimum

    indice = tab_t.index(min(tab_t)) + numero_dernier_point + 1
    t_v_ar_h = min(tab_t)
    isochrone = np.concatenate((isochrone, pointsx))  # On rajoute ces points a la fin du tableau isochrone
    ptn_cplx = np.array([pointsx[:, 0] + pointsx[:, 1] * 1j])  # on reforme un tableau numpy de complexes pour la sortie
    print(' Isochrone calculé N° {}  {}  {} points cap mini  {:4.2f}  cap maxi {:4.2f}  '.format(numero_iso, t_iso_formate,longueur,capmini ,  capmaxi  ))

    return ptn_cplx, nouveau_temps, but, indice,trace_iso
#******************************************************************************************************************************************
#******************************************************************************************************************************************
#******************************************************************************************************************************************

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
latitude_a     = '049-10-00-N'
longitude_a    = '006-30-00-W'




d  = chaine_to_dec(latitude_d, longitude_d)  # conversion des latitudes et longitudes en tuple
ar = chaine_to_dec(latitude_a, longitude_a)



D = cplx(d)  # transformation des tuples des points en complexes
A = cplx(ar)

# Initialisation du tableau des points d'isochrones
# 0: x du point (longitude), 1: y du point (latitude) , 2: N° isochrone , 3: N° du pt mere ,
# 4: N° du pt , 5: Distance a l'arrivee , 6: Cap vers l'arrivee
isochrone     = [[D.real, D.imag, 0, 0, 0, dist_cap(D, A)[0], dist_cap(D, A)[1]]]

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
print('Date et Heure du grib  en UTC  :', time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tig)))
print('\nLe {} heure locale Pour latitude {:6.2f} et longitude{:6.2f} '.format(instant_formate, D.real, D.imag))
print('\tVitesse du vent {:6.3f} Noeuds'.format(vit_vent_n))
print('\tAngle du vent   {:6.1f} °'.format(TWD))
print()



# Initialisation carte folium **************************************************************
m = folium.Map( location=[lat1,long1],  zoom_start=9)
folium.LatLngPopup().add_to(m)   # popup lat long
#*******************************************************************************************

# on initialise l'isochrone de depart avec le depart
pt1_cpx = np.array([[D]])
# todo il faudrait stoper si l'on sort des limites de temps du grib
# tant que le but n'est pas atteint on calcule des isochrones





but = False
while but == False:
    pt1_cpx, temps, but, indice,trace_iso = f_isochrone(pt1_cpx, temps)   
    # trace des isochrones
    if isochrone[-1,2]%6==0:
        folium.PolyLine(trace_iso, color="black", weight=2, opacity=0.8).add_to(m)
    else :
        folium.PolyLine(trace_iso, color="red", weight=1, opacity=0.8).add_to(m)




# route à suivre
# Retracage chemin à l'envers
a = int(indice)                 # indice du point de la route la plus courte
n = int(isochrone[-1][2])       # nombre d'isochrones

# on reconstitue la route à suivre en remontant le chemin


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
    #print('\t {}  \t{} \t{:6.3f} \t{:6.3f}\t{:6.2f} \t{:6.1f} \t{:6.2f} \t{:6.1f} \t{:6.3f}'
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

folium.Marker([-d[1], d[0]], popup=popup[0], tooltip=tooltip[0]).add_to(m)
folium.Marker([-ar[1], ar[0]], popup='<i>Arrivee</i>', tooltip=tooltip[len(chem)-1]).add_to(m)

folium.PolyLine(chemin_folium, color="blue", weight=2.5, opacity=0.8).add_to(m)



filecarte='map.html'
filepath = 'templates/'+filecarte
m.save(filepath)
webbrowser.open( filepath)


#   ****************************************Controle du temps d'execution **********************************
tac = time.time()
print('\nDuree d\'execution:  {:4.2f} s'.format(tac - tic))



#if __name__ == '__main__':
