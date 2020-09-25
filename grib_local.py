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

''' ce fichier charge le grib autour de la position sous forme de fichier json'''
'''Pour linstant on va charger autour de latitude 42 à55  et longitude 3   à -10'''

#on recupere le grib principal
tig, GR        = chargement_grib()
print(tig)
print ('Temps grib en heure locale',time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(tig)))


def prevision0(tig, GR, tp, latitude, longitude):
    fn3 = RegularGridInterpolator((ix, iy, iz), GR)
    itemp = int((tp - tig) / 3600 / 3)
    ilati = int((latitude + 90))
    ilong = int((longitude) % 360)
    #print (GR(0,0,0))
    print ('indices',itemp,ilati,ilong )
    vcplx = fn3((itemp, ilati, ilong))
    #print('vcplx',vcplx)
    vit_vent_n = np.abs(vcplx) * 1.94384
    angle_vent = (270 - np.angle(vcplx, deg=True)) % 360
    return vit_vent_n, angle_vent


 # EXTRACTION D'UN POINT    
tp=tig
latitude=-90
longitude=0

tws,twd= prevision0(tig, GR, tp, latitude, longitude)

print (tws,twd)