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
from sys import platform as _platform

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
def chargement_grib2():
 # ouverture du fichier hdf5
    filenamehdf5='gribs/grib_gfs_20200802-12.hdf5'
    f2 = h5py.File(filenamehdf5, 'r')
    list(f2.keys())
    dset1 = f2['dataset_01']
    GR = dset1[:]
    tig = dset1.attrs['time_grib']
    f2.close()
    return tig, GR







def trace_points_folium (points_cpx):
#on extrait les coordonnes pour tracer
    X=points_cpx.real.reshape(-1,1)
    Y=points_cpx.imag.reshape(-1,1)
    points=np.concatenate((-Y,X),axis=1)
    for point in points :
        folium.CircleMarker(point,color='black', radius=1,fill_color='black',fill_opacity=0.3).add_to(m)
    return None

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
    trace_iso_cap            = []
  
    
    # on recupere toutes les previsions meteo d'un coup pour l'ensemble des points de depart
    TWS, TWD = prevision_tableau(tig, GR, temps_initial_iso, pt_init_cplx)


    # pour chaque point de l'isochrone precedent  donnés en entrée (isochrone précédent)
    for i in range(pt_init_cplx.size):
       
        HDG = range_cap(dist_cap(pt_init_cplx[0][i], A)[1], TWD[i], angle_objectif, angle_twa_pres, angle_twa_ar)  # Calcul des caps a etudier
        VT = polaire2_vect(polaires, TWS[i], TWD[i], HDG)
        n_pts_x = deplacement2(pt_init_cplx[0][i], delta_temps, HDG, VT)   #coordonnees des nouveaux points calcules
       

       
        # if numero_iso ==79 :
        #     print ('nb de points etudies', len (n_pts_x))

        for j in range(len(n_pts_x)):                     # pour chaque point initial i on a j points finaux 
            cap_arrivee = dist_cap(A,n_pts_x[j])[1]
            distance_arrivee = dist_cap(n_pts_x[j], A)[0]
            points_calcul.append(
            [n_pts_x[j].real, n_pts_x[j].imag, numero_iso, numero_premier_point+i+1 , 1, distance_arrivee,cap_arrivee])

            #caps_x.append(cap_arrivee)

    #tri de la liste de tous les  points obtenus
        points_calcul=sorted(points_calcul,key=lambda colonnes :colonnes[6])
   


        k=0
        while (points_calcul[k][6]-points_calcul[k-1][6])<-357 :
            #print(' i', i, ' ', points_calcul[i][6])    
            points_calcul[k][6]+=360
            k+=1
        points_calcul=sorted(points_calcul,key=lambda colonnes :colonnes[6])
        capmini=points_calcul[0][6]
        capmaxi=points_calcul[-1][6]
    
    # test=89   # numero iso teste

    # if numero_iso ==test :
    #     print ('Test 1 isochrone {} \n capmini {} capmaxi {} '.format( numero_iso, capmini,capmaxi ))     
    
    coeff2 = 49/ (capmaxi-capmini)  # coefficient pour ecremer et garder 50 points
   
    # if numero_iso ==test :
    #     print ('Test 1 isochrone {} \n coeff2 {}  '.format( numero_iso, coeff2 ))  


    for j in range(len(points_calcul)):  # partie ecremage
        points_calcul[j][6] = int(coeff2 * points_calcul[j][6])
    pointsx = sorted(points_calcul, key=itemgetter(6, 5))  # tri de la liste de points suivant la direction (indice  " \
    pointsx = np.asarray(pointsx)

    for i in range(len(pointsx) - 1, 0, -1):  # ecremage
        if (pointsx[i][6]) == (pointsx[i - 1][6]):
            pointsx = np.delete(pointsx, i, 0)

    longueur=len(pointsx)
    # if numero_iso ==test :        
    #     print ('Test 1 isochrone {} \n nb de points conserves {}  '.format( numero_iso, longueur ))  

        # else :
        #     pointsx[i][6] = int(pointsx[i][6] / coeff2)%360  # on retablit le cap en valeur   
   
    # verification points terre ou mer
    

    for i in range(len(pointsx)-1, -1, -1):  # ecremage proprement dit 
        is_on_land = globe.is_land(-pointsx[i][1], pointsx[i][0])
        if (is_on_land==True):
            pointsx = np.delete(pointsx, i, 0)

    # on peut restituer les caps initiaux et retrier par cap
    for i in range(len(pointsx)):
         pointsx[i][6] = int(pointsx[i][6] / coeff2)  # on retablit le cap en valeur
    #pointsx=sorted(pointsx,key=lambda colonnes :colonnes[6])
    
    # if numero_iso ==test : 
    #     print('type du tableau et longueur ', type(pointsx), len (pointsx))        
    #     print ('Test 1 isochrone {} \n nouveau cap mini {} et cap maxi {}  '.format( numero_iso,points_calcul[0][6],points_calcul[-1][6] ))      
    # maintenant on trie comme un np.array
    pointsx= pointsx[pointsx[:,6].argsort(kind='mergesort')]


    # if numero_iso ==test : 
    #     print('cap minimum et maximum  pour tracage ', pointsx[0][6],pointsx[-1][6])  
    #     #print ('Liste des points',pointsx)




    for i in range(len(pointsx)):  # renumerotation
        pointsx[i][4] = i + numero_dernier_point + 1
    #    pointsx[i][6] = int(pointsx[i][6] / coeff2)%360  # on retablit le cap en valeur
        dico[pointsx[i][4]] = pointsx[i][3]
        trace_iso.append((-pointsx[i][1], pointsx[i][0]))
        trace_iso_cap.append((-pointsx[i][1], pointsx[i][0],pointsx[i][6]))
    
      
     

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
    

    # # if numero_iso ==test : 
    #         print('trace iso et cap ' ) 
    #         for i in range(len(trace_iso_cap)):
    #             print (trace_iso_cap[i][2])

    # indice du temps minimum
    indice = tab_t.index(min(tab_t)) + numero_dernier_point + 1
    t_v_ar_h = min(tab_t)
    isochrone = np.concatenate((isochrone, pointsx))  # On rajoute ces points a la fin du tableau isochrone
    ptn_cplx = np.array([pointsx[:, 0] + pointsx[:, 1] * 1j])  # on reforme un tableau numpy de complexes pour la sortie
    print(' Isochrone calculé N° {}  {}  {} points cap mini  {:4.2f}  cap maxi {:4.2f}  '.format(numero_iso, t_iso_formate,longueur,capmini ,  capmaxi  ))

    return ptn_cplx, nouveau_temps, but, indice,trace_iso
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

#tig, GR        = chargement_grib()
tig, GR        = chargement_grib2()

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
print(d)
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
    if isochrone[-1,2]==174:
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

folium.Marker([  -d[1], d[0]   ], icon= folium.Icon(color='green', icon='info-sign'), popup=popup[0], tooltip=tooltip[0]).add_to(m)
folium.Marker([ -ar[1], ar[0]  ], icon=folium.Icon(color='red', icon='info-sign'), popup='<i>Arrivee</i>', tooltip=tooltip[len(chem)-1] ).add_to(m)
folium.PolyLine(chemin_folium, color="blue", weight=2.5, opacity=0.8).add_to(m)



filecarte='map.html'
filepath = 'templates/'+filecarte
m.save(filepath)

if (_platform)=='win32':
    chrome_path='C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    webbrowser.get(chrome_path).open( filepath)
else :
    webbrowser.open( filepath)

#   ****************************************Controle du temps d'execution **********************************
tac = time.time()
print('\nDuree d\'execution:  {:4.2f} s'.format(tac - tic))


