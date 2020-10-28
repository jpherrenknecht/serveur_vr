#!/bin/env_vr python3.7.5
# coding: utf-8
import os
import time
import math
import numpy as np
from urllib.request import urlretrieve
import xarray as xr
import h5py
from datetime import datetime
from scipy.interpolate import RegularGridInterpolator
from pathlib import Path

#le debut de chargement des gribs intervient en heure UTC à
# 9h30(gfs06) - 15h30(gfs12) -  21h30(gfs18) - 03h30 (gfs00)


# les gribs complets sont disponibles en heure UTC à
# 11h(gfs06) - 17(gfs12) -  23(gfs18) - 05 h (gfs00)
# les gribs complets sont disponibles en heure d'hiver à
# 12h(gfs06) - 18(gfs12) -  00(gfs18) - 06 h (gfs00)
# les gribs complets sont disponibles en heure d'ete à
# 13h(gfs06) - 19(gfs12) -  01(gfs18) - 07 h (gfs00)


# Creation de la date du grib qui va etre chaarge
t = time.localtime()
utc = time.gmtime()
print('heure',utc[3])

a=utc[3]
a=2
print ('date',utc[0],'-',utc[1],'-',utc[2] )

utcgrib = time.gmtime(time.time() -18000)
print ('utcgrib 3 ',utcgrib[3])

if a<5:       # c'est le grib gfs 18 de la veille 
    utcgrib = time.gmtime(time.time() -18000)
    dategrib= str(utcgrib[0])+'-'+str(utcgrib[1])+'-'+str(utcgrib[2])+'-18'
print ('dategrib : ',dategrib)

# renvoie le chemin absolu du repertoire courant ici /home/jphe/PycharmProjects/VR_version2
basedir = os.path.abspath(os.path.dirname(__file__))


ix = np.arange(129)  # temps
iy = np.arange(181)  # latitudes
iz = np.arange(361)  # longitudes




'''reconstitue le nom du dernier grib disponible
    le charge sur nmea au besoin 
    et le charge pour la simulation s'il existe deja '''
t = time.localtime()
utc = time.gmtime()
decalage_h = t[3] - utc[3]
heures = [0,6,12,18]
heure_grib = heures[((utc[3] + 19) // 6) % 4]  # heure du grib
#si utc inferieur à 5 la date doit etre celle de la veille l'heure est inchangée
if utc[3]<5:
    utc = time.gmtime(time.time() -18000)
dategrib_tpl=datetime(utc[0] , utc[1] , utc[2] , int(heure_grib),0, 0)
tig=time.mktime(dategrib_tpl.timetuple())+decalage_h*3600    #temps initial du grib en sec locales 
dategrib= str(dategrib_tpl) 
date=dategrib[0:10].replace("-","")
strhour=dategrib[11:13]
filename="gribs/grib_gfs_" + date +"-"+strhour+".hdf5"
filenamehdf5 = os.path.join(basedir,filename)

print ('Grib',dategrib_tpl)
print (utc)
print('heure',utc[3])
print ('minutes',utc[4])
# heures utc de mise a disposition des gribs
# l'idee est de declencher upoalgribs  toutes les 15 mn entre 9h35 et 11h 5 soit 6 fois 
# heures de mise a jour en mn 9h30 = 9*60+30 mn etc..
h0=3*60
h1=9*60
h2=15*60
h3=21*60

hdmja= [h0+30,h0+60,h0+90,h0+120,  h1+30,h1+60,h1+90,h1+120, h2+30,h2+60,h2+90,h2+120 ,h3+30,h3+60,h3+90,h3+120]  
dicgrib={(h0+30):('00',0,12),(h0+60):('00',15,72),(h0+90):('00',75,168),(h0+120):('00',171,384),
         (h1+30):('06',0,12),(h1+60):('06',15,72),(h1+90):('06',75,168),(h1+120):('06',171,384),
         (h2+30):('12',0,12),(h2+60):('12',15,72),(h2+90):('12',75,168),(h2+120):('12',171,384),
         (h3+30):('18',0,12),(h3+60):('18',15,72),(h3+90):('18',75,168),(h3+120):('18',171,384)}
hutc=utc[3]*60+utc[4]
i=0
while hutc >hdmja[i]:    # on cherche l'indice du grib disponible
    i=i+1
j=i-1
ngrib = dicgrib[ hdmja[i-1]][0]
v0    = dicgrib[ hdmja[i-1]][1]
v1    = dicgrib[ hdmja[i-1]][2]
valeurs=[v0]
j=1
a=v0
while a<v1:
    a=v0+3*j
    valeurs.append(a)
    j+=1
print (date)
print(ngrib,' ', valeurs) 
filename="gribs/grib_gfs_" + date +"-"+strhour+"-"+str(v1)+".hdf5"   
print (filename)

# cest le nom du fichier qu'on va charger
# chargement des fichiers
leftlon, rightlon, toplat, bottomlat = 0, 360, 90, -90
# for i in range(len(valeurs)):  # recuperation des fichiers de 0 a 384 h
#     prev = valeurs[i]
#     url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t" + strhour + "z.pgrb2.1p00.f" + \
#                   str(prev) + "&lev_10_m_above_ground=on&all_var=on&leftlon=" \
#                   + str(leftlon) + "&rightlon=" + str(rightlon) + "&toplat=" + str(toplat) + "&bottomlat=" + str(
#                 bottomlat) + "&dir=%2Fgfs." + date + "%2F" + strhour
#     nom_fichier = "grib_" + date + "_" + strhour + "_" + str(prev)   # nom sous lequ fichier est sauvegarde provisoirement
#     urlretrieve(url, nom_fichier)                               # recuperation des fichiers provisoires
#     print(' Enregistrement prévision {} + {} heures effectué: '.format(dategrib,prev))  # destine a suivre le chargement des previsions
