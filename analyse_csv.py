import os
import math
import requests
import numpy as np
import pandas as pd
import csv
from polaires.polaires_class40 import *

def deplacement2(D, d_t, HDG, VT):
    '''D Depart point complexe ,d_t duree en s  , HDG tableau de caps en° ,vT Tableau de vitesses Polaires en Noeuds'''
    '''Fonctionne avec des np.array'''
    HDG_R = HDG * math.pi / 180
    A = D + (d_t / 3600 / 60 * VT * (np.sin(HDG_R) / math.cos(D.imag * math.pi / 180) - np.cos(HDG_R) * 1j))
    return A



fichier='fichier_route.csv'
#df = pd.read_csv(url)  #Si separateur =;
# cr = csv.reader(open(fichier, newline=''), delimiter=' ', quotechar='|')
# for row in cr:
#     print (row)

df=pd.read_csv(fichier)
print(df.head())


# reconstitution du chemin
# extractioçn des coordonnees et de la vitesse

x0=df['x'][0]
y0=df['y'][0]
t=df['t'][0]
vit_vent=df['vitesse_v'][0]
angle_vent=df['angle_v'][0]
cap=df['cap'][0]
twa     =df['twa'][0]

D=x0+y0*1j
d_t=df['t'][1]-df['t'][0]

polar=polaire(polaires, vit_vent, twa)     # polaires est le tableau des polaires pour le type de bateau

A=deplacement2(D, d_t, cap, polar)

print('Nouvelles coordonnées')
print(A)


# calcul de la polaire en fonction de la vitesse du vent et twa

polaire=polaire(polaires, vit_vent, twa)
print(polaire)
print('ecart de temps')
print (df['t'][1]-df['t'][0])

