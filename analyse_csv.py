import os
import math
import requests
import numpy as np
import pandas as pd
import csv
import json

from polaires.polaires_class40 import *
from uploadgrib import *


with open('courses.json', 'r') as fichier:
    data = json.load(fichier)

#chargement du grib
tig, GR        = chargement_grib()

#print  (data["features"])
#print  (data["features"]["bateau"])
print()
bateau=(data["DREAMH CUP"]["bateau"])
print('\nBateau : ',bateau)
print()
#polaires='polaires.polaires_'+bateau+'.py'
#from polaires import*


def deplacement2(D, d_t, HDG, VT):
    '''D Depart point complexe ,d_t duree en s  , HDG tableau de caps en° ,vT Tableau de vitesses Polaires en Noeuds'''
    '''Fonctionne avec des np.array'''
    HDG_R = HDG * math.pi / 180
    A = D + (d_t / 3600 / 60 * VT * (np.sin(HDG_R) / math.cos(D.imag * math.pi / 180) - np.cos(HDG_R) * 1j))
    return A



fichier='fichier_route.csv'
df=pd.read_csv(fichier)
print(df.head(15))
print (df.tail())
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
print (' {:6.4f} {:6.4f} {} {:4.2f} {:4.2f} {:4.2f} {:4.2f} {:4.2f}'.format(x0,y0,t,vit_vent,angle_vent,cap0,tw,polar))

A=deplacement2(x0+y0*1j, route[1,3]-route[0,3], cap0, polar)
x1=A.real
y1=A.imag

#print ('Nouveau point',x1,y1)


# on reconstitue 
x=x0
y=y0

print ('  {} x {:6.4f}, y {:6.4f}'.format(0, x,y))

for i in range (84):
    dt=route[i+1,3]-route[i,3]
    cap=route[i,6]
    t=route[i,3] 
    vit_vent, angle_vent=prevision(tig, GR,   t, y, x)
    tw =twa(cap, angle_vent)
    polar= polaire(polaires, vit_vent, tw)[0]
    x=deplacement2(x+y*1j, dt, cap, polar).real
    y=deplacement2(x+y*1j, dt, cap, polar).imag
    print ('  {}  {:6.4f},  {:6.4f}  dt {:6.2f}  dx {:6.4f}   dy {:6.4f}'.format(i+1, x,y, dt  ,route[i+1,1] - x, route[i,2] - y))





