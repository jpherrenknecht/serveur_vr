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

def f_isochrone(points, temps_initial_iso):
    ''' Calcule le nouvel isochrone a partir d'un tableau de points pt2cplx tableau numpy de cplx'''
    ''' deltatemps, tig , U, V sont supposees etre des variables globales'''
    ''' Retourne les nouveaux points el le nouveau temps et implemente le tableau general des isochrones'''

    #ancienne version on se sert des complexes mais on s'en servira
    pt_init_cplx=np.array([points[:,0]+points[:,1]*1j])
    # print ('pt_init size',pt_init_cplx.size)
    # print ('version 2',points.shape[0])
    

    global isochrone, intervalles, t_v_ar_h,dico
    numero_iso           = int(isochrone[-1][2] + 1)
    delta_temps          = intervalles[numero_iso]  # Ecart de temps entre anciens points et nouveaux en s
    nouveau_temps = temps_initial_iso + delta_temps
    t_iso_formate        = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(temps_initial_iso + delta_temps))
    numero_dernier_point = int(isochrone[-1][4])                   # dernier point isochrone precedent
    numero_premier_point = int(isochrone[-1][4]) - points.shape[0]   # premier point isochrone precedent
   
    but                  = False
    points_calcul        = []
    caps_x               = []
    tab_t                = []  # tableau des temps vers l arrivee en ligne directe
    trace_iso            = []
    trace_iso_cap            = []
 

    
    
    # on recupere toutes les previsions meteo d'un coup pour l'ensemble des points de depart
    TWS, TWD = prevision_tableau3(tig, GR, temps_initial_iso, points)
   
    # pour chaque point de l'isochrone precedent  donnés en entrée (isochrone précédent)

    points_calcul2=np.array([[0,0,0,0,0,0,0]]) # initialisation pour Numpy du brouillard des points de l'isochrone

    for i in range(points.shape[0]):
        HDG = range_cap(dist_cap4(points[i], A)[1], TWD[i], angle_objectif, angle_twa_pres, angle_twa_ar)  # Calcul des caps a etudier
        VT = polaire2_vect(polaires, TWS[i], TWD[i], HDG)
    
        # Ancienne version
        n_pts_x = deplacement2(pt_init_cplx[0][i], delta_temps, HDG, VT)   #coordonnees des nouveaux points calcules sous forme de complexes
    


        #Version Numpy
        X1,Y1,Da1,Ca1=deplacement_x_y_tab_ar(points[i][0],points[i][1],delta_temps,HDG,VT,A) #coordonnees des nouveaux points calcules sous forme X,Y
        L=len(X1)
        niso1= np.ones(L)*numero_iso   #len(X1) doit pouvoir etre evite 3 fois
        npointsm1=np.ones(L)*i  +numero_premier_point +1    # numero du point mere i= 0 correspond au premier point de l'isochrone precedent
        #print('\n point mere',npointsm1)
        
        npoints1=np.array(range(L)) +1           # numero du point  sans importance sera renumeroté
        #print('\n point ',npoints1)
        X=X1.reshape(-1,1)
        Y=Y1.reshape(-1,1)
        niso=niso1.reshape(-1,1)
        npointsm=npointsm1.reshape(-1,1)
        npoints=npoints1.reshape(-1,1)
        Da=Da1.reshape(-1,1)
        Ca=Ca1.reshape(-1,1)
        # maintenant on forme le tableau correspondant à n_pts_x
        n_pts_x2     = np.concatenate((X,Y,niso,npointsm,npoints,Da,Ca), axis=1)    # tableau des points pour un point de base
        
        # print('\n npts_x2')
        # for k in range (-5,-1,1):
        #     print ('{:6.2f} {:6.2f} {:6.2f} {:6.2f} {:6.2f} {:6.2f} {:6.2f}'.format (n_pts_x2[k][0],n_pts_x2[k][1],n_pts_x2[k][2],n_pts_x2[k][3],n_pts_x2[k][4],n_pts_x2[k][5],n_pts_x2[k][6]))
        # print()
        
        points_calcul2= np.concatenate((points_calcul2,n_pts_x2), axis=0)           # tableau du brouillard des points 
        
        # print('\n points_calcul2')
        # for l in range (-10,-1,1):
        #     print ('{:6.2f} {:6.2f} {:6.2f} {:6.2f} {:6.2f} {:6.2f} {:6.2f}'.format (points_calcul2[l][0],points_calcul2[l][1],points_calcul2[l][2],points_calcul2[l][3],points_calcul2[l][4],points_calcul2[l][5],points_calcul2[l][6]))
        # print()

#Ancienne version
        for j in range(len(n_pts_x)):                     # pour chaque point initial i on a j points finaux 
            cap_arrivee = dist_cap(n_pts_x[j],A)[1]
            distance_arrivee = dist_cap(n_pts_x[j], A)[0]
            points_calcul.append(
            [n_pts_x[j].real, n_pts_x[j].imag, numero_iso, numero_premier_point+i+1 , 33333, distance_arrivee,cap_arrivee])

    #tri de la liste de tous les  points obtenus
    points_calcul=sorted(points_calcul,key=lambda colonnes :colonnes[6])
  #  print('\npoints_calcul 10  L145     ',points_calcul[10])     #ok

#Version Numpy    
    points_calcul2=np.delete(points_calcul2,0,0)                                    # on retire le premier terme de points_calcul2
    points_calcul2= points_calcul2[points_calcul2[:,6].argsort(kind='mergesort')]   # tri stable sur 6eme colonne
    # print('\npoints_calcul2 10 l 150**  ',points_calcul2[10])   #ok identique sauf numero point (normal)
    # print()
# petit test comparaison pour voir"
    # print('----points_calcul 15',points_calcul[15])
    # print('****points_calcul2 15 ',points_calcul[15])


# on recole les 359 et les 1 
# Ancienne version
    k=0
    while ((points_calcul[k][6]-points_calcul[k-1][6])<-357) and (k<len(points_calcul)) :
        #print(' i', i, ' ', points_calcul[i][6])    
        points_calcul[k][6]+=360
        k+=1
    points_calcul=sorted(points_calcul,key=lambda colonnes :colonnes[6])
    capmini=points_calcul[0][6]
    capmaxi=points_calcul[-1][6]
    
    #print ('capmini  - maxi  ',capmini, capmaxi)   # ok pour capmini capmaxi
   
    
     
# Version Numpy
    k=0
    while ((points_calcul2[k][6]-points_calcul2[k-1][6])<-357)and (k<points_calcul2.shape[0]):
        points_calcul2[k][6]+=360
        k+=1
    points_calcul2= points_calcul2[points_calcul2[:,6].argsort(kind='mergesort')]
    capmini2=points_calcul2[0][6]
    capmaxi2=points_calcul2[-1][6]
   
    
    # print ('capmini2 - maxi2 ',capmini, capmaxi)    # test ok
    # print()

      
# pour les 2 versions    
    coeff2 = 49/ (capmaxi-capmini)  # coefficient pour ecremer et garder 50 points
   
    
#ecremage arrondi et tri
#ancienne version

    for j in range(len(points_calcul)):  # partie ecremage
        points_calcul[j][6] = int(coeff2 * points_calcul[j][6])
    pointsx = sorted(points_calcul, key=itemgetter(6, 5))  # tri de la liste de points suivant la direction (indice  " \
    pointsx = np.asarray(pointsx)
    # print (' Apres tri ligne 197 pointsx 7',pointsx[-1])  # test ok les numeros de points ne sont pas les memes c'est normal
    # print ('AV len(points_calcul)',len(points_calcul))
    # print()
    
    
    
# variante numpy
    points_calcul2[:,6]=np.floor(points_calcul2[:,6]*coeff2)   # le calcul est fait sur la colonne sans boucle variante around
    points_calcul2= points_calcul2[points_calcul2[:,5].argsort(kind='mergesort')] #on trie sur les distances 
    points_calcul2= points_calcul2[points_calcul2[:,6].argsort(kind='mergesort')] #on trie sur les caps mais l'ordre des distances est respecté
    #print('points_calcul2 10',points_calcul2[10])
    # print (' apres tri ligne 206 points_calcul2 7',points_calcul2[-1])  # test test ok les numeros de points ne sont pas les memes c'est normal
    # print ('points_calcul2.shape',points_calcul2.shape)
    # print()


# ecremage proprement dit
    # Base
    for i in range(len(pointsx) - 1, 0, -1):  # ecremage
        if (pointsx[i][6]) == (pointsx[i - 1][6]):
            pointsx = np.delete(pointsx, i, 0)
    longueur=len(pointsx)
    # print ('ligne 207 pointsx 7',pointsx[7])       # test ok


    #  variante numpy
    for i in range(points_calcul2.shape[0] - 1, 0, -1):  # ecremage
        if (points_calcul2[i][6]) == (points_calcul2[i - 1][6]):
            points_calcul2 = np.delete(points_calcul2, i, 0)
    # print (' (226) points_calcul2 7',points_calcul2[7])  # test ok parfait
    # print()


    
   
# verification points terre ou mer
    # Base
    for i in range(len(pointsx)-1, 0, -1):  # ecremage proprement dit 
        is_on_land = globe.is_land(-pointsx[i][1], pointsx[i][0])
        if (is_on_land==True):
            pointsx = np.delete(pointsx, i, 0)
    #print ('ligne 238 pointsx 7',pointsx[7])       # la numerotation n'a pas encore ete faite

    #  variante numpy
    for i in range(points_calcul2.shape[0] - 1, 0, -1):  # ecremage 
        is_on_land = globe.is_land(-points_calcul2[i][1], points_calcul2[i][0])   # point de latitude -y et longitude x
        if (is_on_land==True):
            points_calcul2 = np.delete(points_calcul2, i, 0)
    # print ('ligne 245 points_calcul2 7',points_calcul2[7])  # test ok hors numerotation
    # print()


# Restitution des caps initiaux et retri par cap necessaire pour calculer les temps vers l'arrivee
    # Base
    for i in range(len(pointsx)):
         pointsx[i][6] = int(pointsx[i][6] / coeff2)%360  # on retablit le cap en valeur
         
    pointsx= pointsx[pointsx[:,6].argsort(kind='mergesort')] # tri comme un np array(c'en est un )

    for i in range(len(pointsx)): # renumerotation
        pointsx[i][4] = i + numero_dernier_point + 1

        # creation du dictionnaire relation point fille mere
    for i in range(len(pointsx)):    
        dico[pointsx[i][4]] = pointsx[i][3]
        trace_iso.append((-pointsx[i][1], pointsx[i][0]))   #sert pour le tracage



        # on cherche les temps vers l'arrivee des nouveaux points (ancienne verion)
        vit_vent, TWD = prevision(tig, GR, nouveau_temps, pointsx[i][1], pointsx[i][0])
        twa = 180 - abs(((360 - TWD + pointsx[i][6]) % 360) - 180)
        resultat = polaire(polaires, vit_vent, twa)
        # print(' ligne 267 AV, N° point{} vit_vent {:4.2f} TWD {:4.2f} cap {:4.2f} twa {:4.2f} resultat '.format(i,vit_vent,TWD,pointsx[i][6],twa))
        # print(resultat)
        d_a = pointsx[i][5]
        t_a = 60 * d_a / (resultat + 0.000001)  # nb ce temps est en heures
        tab_t.append(t_a)
        # print('temps',t_a)
        if t_a < delta_temps / 3600:
            but = True
    print ('(278) nv trace_iso l : {}  {}'.format(len(trace_iso),trace_iso[10]))


    #print ('\nAV ligne 275 pointsx 15  ',pointsx[15] )   # tout est ok
   
    # indice du temps minimum
    indice = tab_t.index(min(tab_t)) + numero_dernier_point + 1
    t_v_ar_h = min(tab_t)
    #print('\n (286)temps mini {} indice {}'.format(t_v_ar_h,indice)) # tout est ok

    isochrone = np.concatenate((isochrone, pointsx))  # On rajoute ces points a la fin du tableau isochrone



# variante numpy 
    points_calcul2[:,6]=np.floor(points_calcul2[:,6]/coeff2)       # on retablit le cap en valeur a rechanger en around 0 decimale
    points_calcul2= points_calcul2[points_calcul2[:,6].argsort(kind='mergesort')] #on trie sur les caps a voir si necessaire !
    # renumerotation sur la colonne 4  le premier numero est le numero dernier point iso precedent +1  
    N=np.array( range( int(numero_dernier_point) + 1, points_calcul2.shape[0] +int(numero_dernier_point) + 1,1))  # tableau des indices
    points_calcul2[:,4]=N     # renumerotation
    # ca ne sert a rien de creer un dictionnaire on se servira du tableau isochrones
    # ca ne sert a rien de creer le trace on l'extraira du tableau isochrone
    TWS, TWD =prevision_tableau3(tig, GR, nouveau_temps, points_calcul2) # Vitesse vent et direction pour nouveaux points (extraction en double)
    VT = polaire3_vect(polaires, TWS, TWD, points_calcul2[:,6])
    # print('ligne 296 Numpy, caps         ',points_calcul2[:,6])
    # print('ligne 296 Numpy, resultat TWS ',TWS)
    # print('ligne 297 Numpy, resultat TWD ',TWD)
    # print('ligne 298 Numpy, resultat polaires ',VT)
   # print ('\nNumpy ligne 298 points_calcul2 15  ',points_calcul2[15] )  # tout est ok

    # calcul des temps vers l arrivee
    D_a = points_calcul2[:,5]               # Distances vers l'arrivee
    T_a = 60 * D_a / (VT + 0.000001)        # Temps vers l'arrivée nb ce temps est en heures
    temps_mini=(T_a[np.argmin(T_a,0)])      # Valeur du temps minimum
    
    if temps_mini < delta_temps / 3600:
            but = True
    indice2= np.argmin(T_a,0)  + numero_dernier_point + 1     #indice du point de temps minimum
    #print(' (316) temps mini {} indice {}'.format(temps_mini,indice2))        # tout est ok
    #print (' (317)NP points _calcul2 en sortie valeur 15 ',points_calcul2 [15]) # tout est ok
    ptn_np2=points_calcul2[:, 0:2]   #(X,Y)
    #print (' (319)NP ptnp2 en sortie valeur 15 ',ptn_np2[15]) # tout est ok
    trace_iso2=np.concatenate((-points_calcul2[:,1].reshape(-1,1),points_calcul2[:,0].reshape(-1,1)),axis=1)  #(-Y,X)
    print ('(319) nv trace_iso2 l : {}  {}'.format(len(trace_iso2),trace_iso2[10]))


    #ptn_cplx = np.array([pointsx[:, 0] + pointsx[:, 1] * 1j])
    #print('ptn_cplx en sortie ',ptn_cplx)
   # print ('type points x',type(pointsx))
    ptn_np = pointsx[:, 0:2]  # on reforme un tableau numpy x,y pour la sortie en eliminant les autres colonnes
    #print (' (324)AV ptn_np en sortie valeur 15 ',pointsx[15])   # tout est ok
    #print (' (325)AV ptnp en sortie valeur 15 ',ptn_np[15]) # tout est ok
    #print('ptn_np en sortie',ptn_np)
    
    print(' Isochrone calculé N° {}  {}  {} points cap mini  {:4.2f}  cap maxi {:4.2f}  '.format(numero_iso, t_iso_formate,longueur,capmini ,  capmaxi  ))

    return ptn_np2, nouveau_temps, but, indice2,trace_iso2

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
m = folium.Map( location=[lat1,long1],  zoom_start=9)
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