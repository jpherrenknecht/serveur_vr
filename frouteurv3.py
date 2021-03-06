# coding: utf-8
import os
import time
from datetime import timedelta
import math
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
import json
import folium
import webbrowser
from uploadgrib import *
from fonctions_vr import *

val='polaires.polaires_figaro2'
exec('from '+val+ ' import *')

from global_land_mask import globe
import pickle
from flask import Flask, redirect, url_for,render_template, request , session , flash
from flask_sqlalchemy import SQLAlchemy

tic=time.time()





def f_isochrone(l, temps_initial_iso):
    ''' Calcule le nouvel isochrone a partir d'un tableau de points pt2cplx tableau numpy de cplx'''
    ''' deltatemps, tig , U, V sont supposees etre des variables globales'''
    ''' Retourne les nouveaux points el le nouveau temps et implemente le tableau general des isochrones'''
    global isochrone,TWS,TWD,isochrone2,TWS2,TWD2,penalite,temps_mini
# il faudrait ajouter aux points l'amure recupere sur l'isochrone
    points=(isochrone[-l:,0:2])
    points2=(isochrone2[-l:,[0,1,5]])  # ici on selectionne -l lignes en partant du bas et les colonnes 0 1 6
    
    numero_iso           = int(isochrone[-1][2] + 1)
    delta_temps          = intervalles[numero_iso]  # Ecart de temps entre anciens points et nouveaux en s
    nouveau_temps        = temps_initial_iso + delta_temps
    t_iso_formate        = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(temps_initial_iso + delta_temps))
    numero_dernier_point = int(isochrone[-1][4])                   # dernier point isochrone precedent
    numero_premier_point = int(isochrone[-1][4]) - points.shape[0]   # premier point isochrone precedent
    but                  = False 
    # on recupere toutes les previsions meteo d'un coup pour l'ensemble des points de depart
    # TWS, TWD = prevision_tableau3(tig, GR, temps_initial_iso, points)

## Ici il faut rajouter une colonne pour la TWA pour arriver au nouveau point    
    points_calcul=np.array([[0,0,0,0,0,0,0]]) # initialisation pour Numpy du brouillard des points calcules
# variante la derniere colonne sert pour la TWA
    points_calcul3=np.array([[0,0,0,0,0,0,0,0]]) # initialisation pour Numpy du brouillard des points calcules  


# pour chacun des points de l'isochrone 
    for i in range(points.shape[0]):

        # attention points[i] doit etre a 2 dimensions et non 3 il doit falloir changer la fonction dist_cap
        HDG = range_cap(dist_cap4(points[i], A)[1], TWD[i], angle_objectif, angle_twa_pres, angle_twa_ar)  # Calcul des caps a etudier
        VT  = polaire2_vect(polaires, TWS[i], TWD[i], HDG) 
        #TWAO1= Twao(HDG,TWD[i])
        
        # utilise pour calculer la penalite
        tws=TWS[i]
        twd=TWD[i]

        #print('(65)', TWS.shape )                                             # Vitesses polaires sur ces caps
# Impressions de controle        
        #print ('(60) HDG',HDG)
        #print ('(61) VT',VT)


        #VRT=  test_virement(HDG,TWD,points2[i][2])       # retourne un tableau des virements correspondant au tableau de points  

#ici il faut calculer les virements pour pouvoir introduire la penalite dans le deplacement

# Il faut changer la fonction de dplacement en introduisant la penalite 
#   
# 
# # ici on recupere la twa du point precedent
    #    twa=points2[i][2]

        #print('(80)twa_pt_precedent',points2[i][1])
        #print('tws, type',tws,type(tws))
# version base

        X1,Y1,Da1,Ca1=deplacement_x_y_tab_ar(points[i][0],points[i][1],delta_temps,HDG,VT,A) #Coordonnees des nouveaux points calcules sous forme X,Y

#version modifiee

# 






        X12,Y12,Da12,Ca12,TWAO12=deplacement (points2[i][0],points2[i][1],delta_temps,points2[i][2],tws,twd,HDG,A, penalite)
                   #Coordonnees des nouveaux points calcules sous forme X,Y
        #print("\n(85) TWAO",TWAO12)
            
# version base
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
        Ca        = Ca1.reshape(-1,1)                       #caps vers arrivee
         
        # maintenant on forme le tableau correspondant à n_pts_x
        n_pts_x2       = np.concatenate((X,Y,niso,npointsm,npoints,Da,Ca), axis = 1)    # tableau des points pour un point de base
        points_calcul = np.concatenate((points_calcul,n_pts_x2), axis         = 0)           # tableau du brouillard pour tous les points de base 

#version modifiee        
        L2=len(X12)                                                                            # nombre de ( caps ) points etudies  
        niso12     = np.ones(L2)*numero_iso                                                         # numero isochrone
        npointsm12 = np.ones(L2)*i  +numero_premier_point +1    # numero du point mere i = 0 correspond au premier point de l'isochrone precedent
        npoints12  = np.array(range(L2)) +1                      # numero du point  sans importance sera renumeroté
        X2         = X12.reshape(-1,1)
        Y2         = Y12.reshape(-1,1)
        niso2      = niso12.reshape(-1,1)
        npointsm2  = npointsm12.reshape(-1,1)
        npoints2   = npoints12.reshape(-1,1)
        Da2        = Da12.reshape(-1,1)
        Ca2        = Ca12.reshape(-1,1)                       #caps vers arrivee
        TWAO      = TWAO12.reshape(-1,1)    

        n_pts_x3       = np.concatenate((X,Y,niso,npointsm,npoints,Da,Ca,TWAO), axis = 1)    # tableau des points pour un point de base
        points_calcul3 = np.concatenate((points_calcul3,n_pts_x3), axis         = 0)           # tableau du brouillard pour tous les points de base 

        # print ('\n((104)n_pts_x2(0à3)',n_pts_x2[0:3])    # a priori les points sont les mêmes hors la twa
        # print ('\¬((105)n_pts_x3(0à3)',n_pts_x3[0:3])
  

#Version de base    
    points_calcul = np.delete(points_calcul,0,0)                                    # on retire le premier terme de points_calcul
    points_calcul = points_calcul[points_calcul[: ,6].argsort(kind = 'mergesort')]   # tri stable sur 6eme colonne (caps vers arrivee)
    k=0                                                                             # on regroupe les  caps 359 et 1
    while (((points_calcul[k][6]-points_calcul[k-1][6])<-330)and (k<points_calcul.shape[0]-1)):
        points_calcul[k][6]+=360
        k+=1
    points_calcul= points_calcul[points_calcul[:,6].argsort(kind='mergesort')]   # les caps en 361 sont replaces a la fin 
    capmini2 = points_calcul[0][6]
    capmaxi2 = points_calcul[-1][6]
    coeff2   = 49/ (capmaxi2-capmini2)  # coefficient pour ecremer et garder 50 points
    #print ('(124)points_calcul[-1]',points_calcul[-1])


# version modifiee 
    points_calcul3 = np.delete(points_calcul3,0,0)                                    # on retire le premier terme de points_calcul
    points_calcul3 = points_calcul3[points_calcul3[: ,6].argsort(kind = 'mergesort')]   # tri stable sur 6eme colonne (caps vers arrivee)
    k=0                                                                             # on regroupe les  caps 359 et 1
    while (((points_calcul3[k][6]-points_calcul3[k-1][6])<-330)and (k<points_calcul.shape[0]-1)):
        points_calcul3[k][6]+=360
        k+=1
    points_calcul3= points_calcul3[points_calcul[:,6].argsort(kind='mergesort')]   # les caps en 361 sont replaces a la fin 
    capmini23 = points_calcul3[0][6]
    capmaxi23 = points_calcul3[-1][6]
    coeff2   = 49/ (capmaxi23-capmini23)  # coefficient pour ecremer et garder 50 points
    #print ('(139) points_calcul3[-1]',points_calcul3[-1])

# version base
#ecremage arrondi et tri
    points_calcul[:,6]=np.around(points_calcul[:,6]*coeff2,0)                   # La colonne 6 est arrondie  
    points_calcul     = points_calcul[points_calcul[:,5].argsort(kind='mergesort')] # On trie sur les distances 
    points_calcul     = points_calcul[points_calcul[:,6].argsort(kind='mergesort')] # On trie sur les caps mais l'ordre des distances est respecté
# ecremage proprement dit
    for i in range(points_calcul.shape[0] - 1, -1, -1):  # ecremage
        if (points_calcul[i][6]) == (points_calcul[i - 1][6]):
            points_calcul = np.delete(points_calcul, i, 0)
    longueur= points_calcul.shape[0] 
# verification points terre ou mer
    for i in range(points_calcul.shape[0]- 1, -1, -1):  # ecremage 
        is_on_land = globe.is_land(-points_calcul[i][1], points_calcul[i][0])   # point de latitude -y et longitude x
        if (is_on_land==True):
            points_calcul = np.delete(points_calcul, i, 0)
    points_calcul[:,6]= np.floor(points_calcul[:,6]/coeff2)       # on retablit le cap en valeur a rechanger en around 0 decimale
    points_calcul     = points_calcul[points_calcul[:,6].argsort(kind='mergesort')] #on trie sur les caps a voir si necessaire !
    print('len(points calcul)',len(points_calcul))
    #print ('(177)points_calcul[-1]',points_calcul[-1]) # a priori ok
   


# Version modifiee
#ecremage arrondi et tri
    points_calcul3[:,6]= np.around(points_calcul3[:,6]*coeff2,0)                   # La colonne 6 est arrondie  
    points_calcul3     = points_calcul3[points_calcul3[:,5].argsort(kind='mergesort')] # On trie sur les distances 
    points_calcul3     = points_calcul3[points_calcul3[:,6].argsort(kind='mergesort')] # On trie sur les caps mais l'ordre des distances est respecté
# ecremage proprement dit
    for i in range(points_calcul3.shape[0] - 1, -1, -1):  # ecremage
        if (points_calcul3[i][6]) == (points_calcul3[i - 1][6]):
            points_calcul3 = np.delete(points_calcul3, i, 0)
    longueur= points_calcul3.shape[0] 
# verification points terre ou mer
    for i in range(points_calcul3.shape[0]- 1, -1, -1):  # ecremage 
        is_on_land = globe.is_land(-points_calcul3[i][1], points_calcul3[i][0])   # point de latitude -y et longitude x
        if (is_on_land==True):
            points_calcul3 = np.delete(points_calcul3, i, 0)
    points_calcul3[:,6]= np.floor(points_calcul3[:,6]/coeff2)       # on retablit le cap en valeur a rechanger en around 0 decimale
    points_calcul3     = points_calcul3[points_calcul3[:,6].argsort(kind='mergesort')] #on trie sur les caps a voir si necessaire !
    # print ('(196)points_calcul3[-1]',points_calcul3[-1])  # ok même resultat que 177
    # print()



#version base
# renumerotation sur la colonne 4  le premier numero est le numero dernier point iso precedent +1  
    N=np.array( range( int(numero_dernier_point) + 1, points_calcul.shape[0] +int(numero_dernier_point) + 1,1))  # tableau des indices
    points_calcul[:,4]=N     # renumerotation
    TWS, TWD =prevision_tableau3(tig, GR, nouveau_temps, points_calcul) # Vitesse vent et direction pour nouveaux points (extraction en double)
# on minore TWS à  2 pour règle VR
    TWS[TWS <2] = 2
    VT = polaire3_vect(polaires, TWS, TWD, points_calcul[:,6])
    print ('VT',VT)
    print ('len(VT)',len(VT))







# calcul des temps vers l arrivee
    D_a       = points_calcul[: ,5]   
                # Distances vers l'arrivee
    # print('(212)len(d_a) ',len(D_a))  
    # print('(213) D_a)',D_a)
    T_a       = 60 * D_a / (VT + 0.000001)  
          # Temps vers l'arrivée nb ce temps est en heures
    temps_mini=(T_a[np.argmin(T_a,0)])      # Valeur du temps minimum
# Verification si le but est atteignable dans le temps d'un isochrone    
    if temps_mini < delta_temps / 3600:
            but = True
    indice2= np.argmin(T_a,0)  + numero_dernier_point + 1     #indice du point de temps minimum
    # print ('(201)temps_mini',temps_mini)   # pas de pb fonctionne
    # print ('(202)indice2',indice2)

#    ptn_np2=points_calcul[:, 0:2]   #(X,Y)# Constitution du tableau des points retournes en sortie    
    lf=points_calcul.shape[0]


# Ajout des points calcules au tableau global des isochrones
    isochrone = np.concatenate((isochrone, points_calcul[:,0:5]))  # On rajoute ces points a la fin du tableau isochrone 


# Version variante points calcul 3
#*****************************************************************************************************************
# renumerotation sur la colonne 4  le premier numero est le numero dernier point iso precedent +1  
    N3=np.array( range( int(numero_dernier_point) + 1, points_calcul3.shape[0] +int(numero_dernier_point) + 1,1))  # tableau des indices
    points_calcul3[:,4]=N3     # renumerotation
    TWS3, TWD3 =prevision_tableau3(tig, GR, nouveau_temps, points_calcul3) # Vitesse vent et direction pour nouveaux points (extraction en double)
# on minore TWS à  2 pour règle VR
    TWS3[TWS3 <2] = 2
    VT3 = polaire3_vect(polaires, TWS3, TWD3, points_calcul3[:,6])
# calcul des temps vers l arrivee
    D_a3       = points_calcul3[: ,5]               # Distances vers l'arrivee
    T_a3      = 60 * D_a3 / (VT3 + 0.000001)        # Temps vers l'arrivée nb ce temps est en heures
    temps_mini3=(T_a3[np.argmin(T_a3,0)])      # Valeur du temps minimum
# Verification si le but est atteignable dans le temps d'un isochrone    
    if temps_mini3 < delta_temps / 3600:
            but3 = True
    indice23= np.argmin(T_a3,0)  + numero_dernier_point + 1     #indice du point de temps minimum
    # print ('temps_mini3',temps_mini3) # pas de pb fonctionne
    # print ('(228)indice23',indice23)
#    ptn_np2=points_calcul[:, 0:2]   #(X,Y)# Constitution du tableau des points retournes en sortie    
    lf3=points_calcul3.shape[0]
# Ajout des points calcules au tableau global des isochrones
    isochrone2 = np.concatenate((isochrone2, points_calcul3[:,0:6]))  # On rajoute ces points a la fin du tableau isochrone 







# Utilisation pour trace folium  
    #trace_iso2=np.concatenate((-points_calcul[:,1].reshape(-1,1),points_calcul[:,0].reshape(-1,1)),axis=1)  #(-Y,X)
    print('Isochrone  N° {}  {}  {} points capmini {:6.2f} capmaxi {:6.2f} coeff {:6.2f} '.format(numero_iso, t_iso_formate,longueur,capmini2,capmaxi2,coeff2 ))
    print()
    return lf, nouveau_temps, but, indice2
# ************************************   Fin de la fonction       **********************************************************




def fonction_routeur(xn,yn,x1,y1,t0=time.time()):
    '''x0,y0,x1,y1 depart et arrivee '''
    ''' Le but de la fonction frouteur est a partir de x0 y0 x1 y1 
    de retourner une multipolyline des isochrones'''
    global isochrone,isochrone2,intervalles,TWS,TWD,tig,GR,angle_objectif,temps_mini,A,penalite
# Definition des variables pour le routage
    tig, GR        = chargement_grib()
    A= x1+y1*1j                         # Arrivee sous forme complexe
    pt1_np=np.array([[xn,yn]])          # isochrone de depart (1 point)
    # variante avec amure
    pt2_np=np.array([[xn,yn,True]]) 

    print ('\n(146) pt1_np',pt1_np)     # verification du point de l'isochrone de depart
    print ('(147) pt2_np',pt2_np)
    
    amur_init=True                      # amure initiale par defaut tribord

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
    isochrone2 = np.array([[x0, y0, 0, 0, 0, 1]])# on initialise le tableau isochrone et TWS TWD la derniere colonne ajoutee est l'amure
    TWS, TWD = prevision_tableau3(tig, GR, t0, pt1_np)    # prevision au premier point 
    print ('(\n (137)  premier TWS',TWS) 
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

# # Algorithme de base on calcule tous les isochrones a decommenter
    while but == False:
        l,temps, but, indice = f_isochrone(l,temps) 

# Variante pour test 
    # i=0
    # while i<50:
    #      l,temps, but, indice = f_isochrone(l,temps) 
    #      i+=1

# utilisation de la variante 
    #isochrone=isochrone2

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
    twat =      TWA_ch.reshape((1, -1))
    pol =       POL_ch.reshape((1, -1))
    # tabchemin : x,y,vit vent ,TWD,cap vers point suivant twa vers point suivant
    chem = np.concatenate((chx.T, chy.T, temps_pts.T, vitesse.T, TWD.T, cap.T, twat.T, pol.T), axis=1)

    print ('Heure de depart',time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(t0)))
    #print ("temps à l'arrivee en s ",chem[-1, 2])
    print ("Heure d'arrivée",time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(chem[-1, 2])))
    duree = (temps_cum[-1] - t0)
    #print('temps total en s ', duree)
    h=duree/3600
    #print('temps total en h {:6.2f}' .format(h))
    j = duree // (3600 * 24)
    h = duree // 3600-(j*24)
    mn = (duree - (j * 3600 * 24) - h * 3600) // 60
    s=duree-(j*3600*24+h*3600+mn*60)
#print('temps total  {}h {}mn'.format(duree/3600,(duree-duree//3600))/60)


    print('temps total {:2.0f}j {:2.0f}h {:2.0f}mn {:2.0f}s'.format(j, h, mn ,s ))

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
    # #Depart
    # latitude_d     = '048-37-41-N'
    # longitude_d    = '002-42-25-W'
    # #Point Arrivee 
    # latitude_a     = '050-08-00-N'
    # longitude_a    = '004-15-00-W'

    #   "depart":{"lat":"043-28-20-N" ,"lng":"009-28-58-E"},
    #   "brehat" :{"lat":"048-01-00-N" ,"lng":"009-24-00-E"},
    #   "bouee1":{"lat":"043-01-00-N" ,"lng":"009-24-00-E"}, 


    # x0,y0=chaine_to_dec(latitude_d, longitude_d)  # conversion des latitudes et longitudes en tuple
    # x1,y1=chaine_to_dec(latitude_a, longitude_a)

    # Extraction de donnees du fichier json
    # Extraction de donnees du fichier json
     # Extraction de donnees du fichier json

    penalite=10                                     # penalite pour virement de bord 
    with open('courses.json', 'r') as fichier:
        data = json.load(fichier)
    n_course='463'
    bateau=(data[n_course]["bateau"])
    print('\nBateau : ',bateau)
    fichier_polaires='polaires.'+(data[n_course]["polaires"])


    depart="depart"
    arrivee="arrivee"

    latdep = (data[n_course][depart]["lat"])
    lngdep = (data[n_course][depart]["lng"])
    latar  = (data[n_course][arrivee]["lat"])
    lngar  = (data[n_course][arrivee]["lng"])
    x0,y0=chaine_to_dec(latdep, lngdep)  # conversion des latitudes et longitudes en tuple
    x1,y1=chaine_to_dec(latar, lngar)
    # print ('x0,y0',x0,y0)
    # print ('x1,y1',x1,y1)
    latar=y1
    lngar=x1

    t0=time.time() 



    # on force les coordonnees de depart
    #y0=-42.5763
    #x0=10.1035
    t0=time.time()     
    print ('coordonnees Depart ',x0,y0)
    print ('coordonnees Arrivee',x1,y1)

#*******************************************************************************************
#*******************************************************************************************
# Fonction_routeur  elle retourne les isochrones (multipolyline) et la route ,
    multipolyline,route,comment=fonction_routeur(x0,y0,x1,y1)
#*******************************************************************************************
#*******************************************************************************************
#*******************************************************************************************
    #print ( '\n(341) multipolyline[0]\n',multipolyline[0])
    #print ('\n (342)      multipolyline[1]\n',multipolyline[1])
    
    # print ('\npoint0 ( point de depart de la route )\n',route[0])
    # print ('point1   (premier point de depart de la route) \n',route[1])



    arcomment=np.asarray(comment)

    #print ('caps=\n',arcomment[:,5:6])
    #print ('twa=\n',arcomment[:,6:7])
    inter=np.asarray(arcomment[:,4:5])
    # print ()
    # print ('cap\n')
    # for i in range(len(comment)):
    #     print ('{:4.0f},'.format(comment[i][5]),end='')
    # print()
    # print ('vent\n')
    # for i in range(len(comment)):
    #     print ('{:4.0f},'.format(comment[i][4]),end='')

    # Exportation en pandas et en csv
    indexiso=np.arange(len(comment))
    df = pd.DataFrame(comment, index = indexiso, columns = ['x', 'y', 't', 'vit_vent','angle_vent','cap','twa', 'polaire'])

    print()
    print(df.head(5))

    print()
    print(df.tail(5))
    df.to_csv('fichier_route3.csv')

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
        if (i+1)%2==0:
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
        tooltip.append('<b>'+temps+'<br>Iso N°:'+str(i) +'  +' +heures+'<br> Lat :'+lat+'° - Long :'+lng+'°<br>TWD :' +twd+'°-  TWS :'
                    + tws +'N<br> Cap :' + cap + '° TWA :' +twa +'°<br>Vitesse :' +Vt+'Noeuds</b>')
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
