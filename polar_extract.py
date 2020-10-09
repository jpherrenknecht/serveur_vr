# Source
# # # http://toxcct.free.fr/polars/generator.htm
# # # http://toxcct.free.fr/polars/help/csvgen_input.htm
# # # pour obtenir les donnees brutes dans vr dashboard raw values reperer la ligne et la copier
# copies des donnees brutes - retirer tWA TWS le replacer par 0, remplacer les ; par des , - ajouter   : ],[ à la fin de chaque ligne, polaires=np.array([[ au debut et ]])
import numpy as np
import json
import time
from scipy.interpolate import RegularGridInterpolator,interp2d,interpn


with open('polars.json', 'r') as fichier:
    data = json.load(fichier)


def fpolaire(polaires, tws, twa): # polaire simple
    return interpn((tab_twa,tab_tws), polaires, [twa, tws], method='linear')
    

def ftwa(hdg,twd):
    return 180 - abs(((360 - twd + hdg) % 360) - 180)


def polaire2_vect(polaires,tws,twd,HDG):
    '''ici un seul point avec une seule tws twd
     mais plusieurs caps'''
    # on ajuste les tableaux TW et TWD à HDG
    l=len(HDG)
    TWA = (180 - np.abs(((360 - twd + HDG) % 360) - 180)).reshape((-1, 1))
    TWS = (np.ones(l) * tws).reshape((-1, 1))
    donnees = np.concatenate((TWA, TWS), axis=1)
    valeurs = interpn((tab_twa,tab_tws), polaires, donnees, method='linear')
    return valeurs




bateau='maxitrix'
tab_tws=np.array(data[bateau]["tab_tws"])
tab_twa=np.array(data[bateau]["tab_twa"])
polaires=np.array(data[bateau]["polaires"])
# print(tab_tws)    
# print(polaires)








tws=19
twd=10
hdg=120
HDG = np.array([120, 130, 140,270])  # caps
twa=ftwa(hdg,twd)
TWA=ftwa(HDG,twd)
print('twa test simple',twa)
print('TWA test sur tableau de HDG ',TWA)

#test de vitesse
tic = time.time()
for i in range (10000):
   ''' polaires en un point avec differents caps''' 
   POL=polaire2_vect(polaires,tws,twd,HDG)

tac=time.time()
print('vpolaire',POL)
print()
print ('temps en base',tac-tic,'s')
print()

#************************************************************

# tic = time.time()
# for i in range (10000):
#    ''' polaires en un point avec differents caps''' 
#    POL=polaire2_vectv2(polaires,tws,twd,HDG)
# tac=time.time()
# print('vpolaire',POL)
# print()
# print ('temps en variante',tac-tic,'s')

#************************************************************