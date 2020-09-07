import os
import math
import requests
import numpy as np
import pandas as pd
import csv
import json
import time

PI=math.pi
val='polaires.polaires_figaro2'
exec('from '+val+ ' import *')
#from polaires.polaires_class40 import *
#from polaires.polaires_ultime import *
from uploadgrib import *
from fonctions_vr import *



tic =time.time()

#chargement du grib
tig, GR        = chargement_grib()
# Extraction de donnees du fichier json
with open('courses.json', 'r') as fichier:
    data = json.load(fichier)
print('data')

# n_course='447'
# bateau=(data[n_course]["bateau"])
# print('\nBateau : ',bateau)
# fichier_polaires='polaires.'+(data[n_course]["polaires"])

# print (fichier_polaires)
# print()
# latdep = (data[n_course]["depart"]["lat"])
# lngdep = (data[n_course]["depart"]["lng"])
# latar  = (data[n_course]["bouee1"]["lat"])
# lngar  = (data[n_course]["bouee1"]["lng"])


# print ('latdep',latdep)
# print ('lngdep',lngdep)
# x0,y0=chaine_to_dec(latdep, lngdep)  # conversion des latitudes et longitudes en tuple
# x1,y1=chaine_to_dec(latar, lngar)

# print ('coordonnees Depart ',x0,y0)
# print ('coordonnees Arrivee',x1,y1)


def deplacement2(D, d_t, HDG, VT):
    '''D Depart point complexe ,d_t duree en s  , HDG tableau de caps en° ,vT Tableau de vitesses Polaires en Noeuds'''
    '''Fonctionne avec des np.array'''
    HDG_R = HDG * math.pi / 180
    A = D + (d_t / 3600 / 60 * VT * (np.sin(HDG_R) / math.cos(D.imag * math.pi / 180) - np.cos(HDG_R) * 1j))
    return A


def dist_cap(x0,y0,x1,y1):
    '''retourne la distance et l'angle du deplacement entre le depart et l'arrivee
    en tenant compte de la courbure et du racourcissement des distances sur l'axe x'''
    coslat= math.cos(y0 * math.pi / 180)
    C=(x1-x0)*coslat +(y1-y0)*1j
    return np.abs(C), (450 + np.angle(C, deg=True)) % 360

def dist_cap_r(x0,y0,x1,y1):
    '''retourne la distance et l'angle du deplacement entre le depart et l'arrivee
    en tenant compte de la courbure et du racourcissement des distances sur l'axe x
    la fonction est identique à la precedente mais le retour est en radian '''
    coslat= math.cos(y0 * PI / 180)
    C=(x-x0)*coslat +(y-y0)*1j
    return np.abs(C), (5*PI/2 + np.angle(C)) % (2*PI)


def temps_depl (x0,y0,x1,y1,polar):
    dist,cap_r=dist_cap_r(x0,y0,x1,y1)
    dt=(( ((x1-x0)+(y1-y0)*1j)  /  ((math.sin(cap_r)/math.cos(y0*math.pi/180))- math.cos(cap_r)*1j)   ) *(60*3600/polar)).real
    return dt

def temps_depl2 (x0,y0,t0,x1,y1):
    dist,cap=dist_cap(x0,y0,x1,y1)
    vitesse2=v_polaire(x0,y0,t0,cap)
    cap_r=cap*math.pi/180    
    dt=(( ((x1-x0)+(y1-y0)*1j)  /  ((math.sin(cap_r)/math.cos(y0*math.pi/180))- math.cos(cap_r)*1j)   ) *(60*3600/vitesse2)).real
    return dt


def v_polaire(x0,y0,t0,cap):
    ''' recherche de la polaire connaissant le point et l'instant de depart et le cap suivi '''
    '''tig et GR sont les variables globales '''
    vit_vent, angle_vent=prevision(tig, GR,   t0, y0, x0)
    print('vitesse du vent {} et angle du vent dans fonction polaire {}'.format(vit_vent,angle_vent))
    tw =twa(cap, angle_vent)

    print('twa dans fonction v_polaire {}'.format(tw))
    polar= polaire(polaires, vit_vent, tw)[0]
    return polar



# Recuperation du fichier csv et transformation en pandas
fichier='fichier_route2.csv'
df=pd.read_csv(fichier)

print('\nHead')
print('Taille pandas',df.shape)
print (df.head(130))

print( '\nFin')
print (df.tail())
# Transformation du fichier pandas en tableau Numpy
route=df.to_numpy()

# reconstitution du chemin
# extraction des coordonnees et de la vitesse

x0=route[0,1]
y0=route[0,2]
t=route[0,3]

vit_vent, angle_vent=prevision(tig, GR,t, y0, x0)

cap0=route[0,6]
tw =twa(cap0, angle_vent)
polar= polaire(polaires, vit_vent, tw)[0]
print('\n')
#print (' {:6.4f} {:6.4f} {} {:4.2f} {:4.2f} {:4.2f} {:4.2f} {:4.2f}'.format(x0,y0,t,vit_vent,angle_vent,cap0,tw,polar))

A=deplacement2(x0+y0*1j, route[1,3]-route[0,3], cap0, polar)
x1=A.real
y1=A.imag

#print ('Nouveau point',x1,y1)


# on reconstitue 
x=x0
y=y0

print ('  Depart  {:6.4f}, y {:6.4f}'.format(x,y))

#" reconstititution pour voir "
# for i in range (df.shape[0]-1):
#     dt=route[i+1,3]-route[i,3]
#     cap=route[i,6]
#     t=route[i,3] 
#     vit_vent, angle_vent=prevision(tig, GR,   t, y, x)
#     tw =twa(cap, angle_vent)
#     polar= polaire(polaires, vit_vent, tw)[0]
#     x=deplacement2(x+y*1j, dt, cap, polar).real
#     y=deplacement2(x+y*1j, dt, cap, polar).imag

#    print ('  {}  {:6.4f},  {:6.4f}  dt {:6.2f}  dx {:6.4f}   dy {:6.4f}'.format(i+1, x,y, dt  ,route[i+1,1] - x, route[i,2] - y))

# Recalcul du dernier temps


print('Liste des caps suivis')
print(df['cap'][0:50])
print()

print('Liste des TYWA suivies')
print(df['twa'][0:50])
print()


caps=df['cap'][0:50]

for i in range (len(caps)):
    print ('{:4.2f},'.format(caps[i]))

for i in range (len(twa)):
    print ('{:4.2f},'.format(twa[i]))





# calcul sur premier point pour test tempspour passer a l'isochrone suivant
i=0
cap=route[i,6]  # cap suivi
t=route[i,3] 
vit_vent, angle_vent=prevision(tig, GR,   t, y0, x0)
tw =twa(cap, angle_vent)
polar= polaire(polaires, vit_vent, tw)[0] # polaire en ce point
print('Calcul de déplacement connaissant le depart le cap la polaire et le temps')
dt =500                  
print ('Au Point de depart {:6.4f}  {:6.4f} Polaire {:6.2f} Noeuds cap {}° dt {:5.2f}s'.format(x0,y0,polar,cap,dt ))
x1=x0+polar*dt/3600/60*math.sin(cap*math.pi/180)/math.cos(y0*math.pi/180)
y1=y0-polar*dt/3600/60*math.cos(cap*math.pi/180)
print ('Après deplacement  {:6.4f}  {:6.4f}  '.format(x1,y1))
print()


x0=route[0,1]
y0=route[0,2]
t0=route[0,3]
cap=route[0,6]
vitesse=v_polaire(x0,y0,t0,cap)
print ('La vitesse polaire en {:6.4f} {:6.4f} à {:9.4f}s cap{:8.6f} est {:6.4f}'.format(x0,y0,t0,cap,vitesse))

print("Calcul inverse on connait le depart, l'arrivee la polaire au depart et on cherche le temps")
#print("Calcul d'un temps de parcours connaissant les points de depart et arrivée")
# le calcul suivant sert comme données pour le test
x=deplacement2(x0+y0*1j, dt, cap, polar).real
y=deplacement2(x0+y0*1j, dt, cap, polar).imag
# On verifie que cela fonctionne bien
print("Test d'un parcours : Donnees Depart {:6.4f} {:6.4f} Arrivee {:6.4f} {:6.4f} polaire {:6.2f} ".format(x0,y0,x,y,polar))
delta_t = temps_depl (x0,y0,x,y,polar)
print('Temps de parcours :{:6.2f}s '.format(delta_t))  

t0=route[0,3]
delta_t2 = temps_depl2 (x0,y0,t0,x,y)
print('Temps de parcours 2 :{:6.2f}s '.format(delta_t2))  

#************************************************************************************************
#************************************************************************************************
# on va faire un essai de0 racourcissement de route entre deux indices
i=23
j=30
xi=route[i,1]
yi=route[i,2]
ti=route[i,3]
capi=route[i,6]
twai=route[i,7]
polairei=route[i,8]
"on essaye d'aller directement au point j"

xf=route[j,1]
yf=route[j,2]
tf=route[j,3]
capf=route[j,6]
twaf=route[j,7]
polairef=route[j,8]
print('\nTest entre les points{} et {}'.format(i,j))
print('temps initial',ti)
print('xi yi capi twai polairei ',xi, yi,capi,twai,polairei)
print('xf yf ',xf, yf)
print ('delta_t',tf-ti)

print('Calcul dans le sens direct')
x=deplacement2(xi+yi*1j, tf-ti, capi, polairei).real
y=deplacement2(xi+yi*1j, tf-ti, capi, polairei).imag
print('x y calcules directement ',x, y)

temps_parcours = temps_depl2 (xi,yi,ti,xf,yf)
print('\nNouveau temps de parcours',temps_parcours)
#calcul par les indices
t2=(j-i)*600
print ('calcul par les indices',t2)
print('gain de temps ',t2-temps_parcours)

tac =time.time()
print ('\nTemps de calcul',tac-tic)
print()
print()
