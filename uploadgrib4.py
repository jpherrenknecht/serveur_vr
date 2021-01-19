#!/bin/env_vr python3.7.5
# coding: utf-8

#le debut de chargement des gribs intervient en heure UTC à
# 9h30(gfs06) - 15h30(gfs12) -  21h30(gfs18) - 03h30 (gfs00)
# en heure d'hiver
# 10h30(gfs06) - 16h30(gfs12) -  22h30(gfs18) - 04h30 (gfs00)


# les gribs complets sont disponibles en heure UTC à
# 11h(gfs06) - 17(gfs12) -  23(gfs18) - 05 h (gfs00)
# les gribs complets sont disponibles en heure d'hiver à
# 12h(gfs06) - 18(gfs12) -  00(gfs18) - 06 h (gfs00)
# les gribs complets sont disponibles en heure d'ete à
# 13h(gfs06) - 19(gfs12) -  01(gfs18) - 07 h (gfs00)
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
import requests


tic=time.time()
ticstruct = time.localtime()
utc = time.gmtime()
decalage = ticstruct[3] - utc[3]
leftlon, rightlon, toplat, bottomlat = 0, 360, 90, -90
# constitution d'un nom de fichier
basedir = os.path.abspath(os.path.dirname(__file__))
ix = np.arange(129)  # temps
iy = np.arange(181)  # latitudes
iz = np.arange(361)  # longitudes

# recherche du dernier grib disponible
# # *************************************************************************************
# avec tic 
date_tuple           = time.gmtime(tic)             # transformation en tuple utc
date_formatcourt     = time.strftime("%Y%m%d", time.gmtime(tic))
dateveille_tuple     = time.gmtime(tic-86400) 
dateveille_formatcourt=time.strftime("%Y%m%d", time.gmtime(tic-86400))



# # *************************************************************************************
# pour faire differents essais qui ne soient pas basés  sur le tic
# ces lignes pourront simplement etre commentees en final
datejour         = datetime(2021,1,17, 12,30,0)                  # en heures locales
dateessai_sec    = time.mktime(datejour.timetuple()) # c'est l'equivalent du tic

date_tuple       = time.gmtime(dateessai_sec) 
date_formatcourt = time.strftime("%Y%m%d", time.gmtime(dateessai_sec))
dateveille_tuple = time.gmtime(dateessai_sec-86400) 
dateveille_formatcourt=time.strftime("%Y%m%d", time.gmtime(dateessai_sec-86400))

# print (date_tuple)
# print(date_formatcourt)
# print (dateveille_formatcourt_utc)
# print(dateveille_tuple)
#*****************************************************************************************




# le but est de charger le dernier grib 384 disponible
    # les heures sont donc en utc 5h 11h 17h 23h 
    # avant 5h c'est le grib 18 de la veille 
    # avant 11h  soit 300 mn c'est le gfs 00 du jour  
    # avant 17h soit c'est le gfs 06
    # avant 23h soit c'est le gfs 12
    # entre 23h et 0h- c'est le gfs 18 du jour 
    
# on divise mn_jour par 360


def filename(temps_secondes):
    date_tuple       = time.gmtime(temps_secondes) 
    date_formatcourt = time.strftime("%Y%m%d", time.gmtime(temps_secondes))
    dateveille_tuple = time.gmtime(temps_secondes-86400) 
    dateveille_formatcourt=time.strftime("%Y%m%d", time.gmtime(temps_secondes-86400))
    mn_jour_utc =date_tuple[3]*60+date_tuple[4]
    # heuregrib=datetime(date_tuple[0],date_tuple[1],date_tuple[2],6,0,0) # en heures locales
    # tig=time.mktime(heuregrib.timetuple())     # transformation en secondes attention ce sont des secondes locales

    if (mn_jour_utc <300):
        filename384="gribs/gfs_"+dateveille_formatcourt+"-18-384.hdf5"
        tig=time.mktime(datetime(dateveille_tuple[0],dateveille_tuple[1],dateveille_tuple[2],18,0,0).timetuple())+decalage*3600
    elif (mn_jour_utc<660):   
        filename384="gribs/gfs_"+date_formatcourt+"-00-384.hdf5"
        tig=time.mktime(datetime(date_tuple[0],date_tuple[1],date_tuple[2],0,0,0).timetuple())+decalage*3600
    elif (mn_jour_utc<1020): 
        filename384="gribs/gfs_"+date_formatcourt+"-06-384.hdf5"
        tig=time.mktime(datetime(date_tuple[0],date_tuple[1],date_tuple[2],6,0,0).timetuple())+decalage*3600
    elif (mn_jour_utc<1380):   
        filename384="gribs/gfs_"+date_formatcourt+"-12-384.hdf5"
        tig=time.mktime(datetime(date_tuple[0],date_tuple[1],date_tuple[2],12,0,0).timetuple())+decalage*3600
    else:    
        filename384="gribs/gfs_"+date_formatcourt+"-18-384.hdf5"
        tig=time.mktime(datetime(date_tuple[0],date_tuple[1],date_tuple[2],18,0,0).timetuple())+decalage*3600
    filenamehdf5 = os.path.join(basedir,filename384)    
    return filenamehdf5,date_formatcourt,tig  




def filename2():
    '''ancienne version''' 
    ''' retourne le nom du fichier du dernier grib sous lequel le grib chargé sera sauvé ou du dernier grib disponible
       la date du grib et le tig en secondes locales '''
    t = time.localtime()
    utc = time.gmtime()
    decalage_h = t[3] - utc[3]
    heures = [0,6,12,18]
        #on bloque l'heure du grib
    heure_grib = heures[((utc[3] + 19) // 6) % 4]  #
    #si utc inferieur à 5 la date doit etre celle de la veille
    if utc[3]<5:
        utc = time.gmtime(time.time() -18000)
    dategrib =datetime(utc[0] , utc[1] , utc[2] , int(heure_grib),0, 0)
    tig=time.mktime(dategrib.timetuple())+decalage_h*3600

    date= str(dategrib)
    filename="gribs/grib_gfs_" + date + ".hdf5"
    filenamehdf5 = os.path.join(basedir,filename)
    
    #time.time()- tig correspond bien à l'ecart de temps avec le grib
    return filenamehdf5,date,tig


def chargement_384(filenamehdf5):
    if os.path.exists(filenamehdf5) == True:        #si ce fichier n'existe pas deja
        strhour =filenamehdf5[-11:-9]
        date    =filenamehdf5[-20:-12]
        year =int(filenamehdf5[-20:-16])
        month=int(filenamehdf5[-16:-14])
        day  =int(filenamehdf5[-14:-12])
        dategrib=datetime(year , month , day , int(strhour),0, 0)
        iprev = []
        for a in range(0, 387, 3):  # Construit le tuple des indexs des fichiers maxi 387
            iprev += (str(int(a / 100)) + str(int((a % 100) / 10)) + str(a % 10),)
        GR = np.zeros((len(iprev), 181, 360), dtype=complex)  # initialise le np array de complexes qui recoit les donnees
        for indexprev in range(len(iprev)):  # recuperation des fichiers de 0 a 384 h
            prev = iprev[indexprev]
            url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t" + strhour + "z.pgrb2.1p00.f" + \
                prev + "&lev_10_m_above_ground=on&all_var=on&leftlon=" \
                + str(leftlon) + "&rightlon=" + str(rightlon) + "&toplat=" + str(toplat) + "&bottomlat=" + str(
                bottomlat) + "&dir=%2Fgfs." + date + "%2F" + strhour

            ret = requests.head(url)
            print(ret.status_code)   
            nom_fichier = "grib_" + date + "_" + strhour + "_" + prev   # nom sous lequel le  fichier est sauvegarde provisoirement
            urlretrieve(url, nom_fichier)                               # recuperation des fichiers provisoires
            print(' Enregistrement prévision {} + {} heures effectué: '.format(dategrib,prev))  # destine a suivre le chargement des previsions

            # exploitation du fichier et mise en memoire dans GR
            ds = xr.open_dataset(nom_fichier, engine='cfgrib')
            GR[indexprev] = ds.variables['u10'].data + ds.variables['v10'].data * 1j
            os.remove(nom_fichier)  # On efface le fichier pour ne pas encombrer
            os.remove(nom_fichier + '.4cc40.idx')

        # on modifie GR pour lui donner un indice 360 egal à l'indice 0
        GR=np.concatenate((GR,GR[:,:,0:1]), axis=2)

        # sauvegarde dans fichier hdf5 du tableau GR
        #filename = "~/PycharmProjects/VR_version2/gribs/grib_gfs_" + dategrib + ".hdf5"
        f1 = h5py.File(filenamehdf5, "w")
        dset1 = f1.create_dataset("dataset_01", GR.shape, dtype='complex', data=GR)
        dset1.attrs['time_grib'] = tig  # transmet le temps initial du grib en temps local en s pour pouvoir faire les comparaisons
        f1.close()
    else:    #s'il existe deja ouverture du fichier hdf5
        f2 = h5py.File(filenamehdf5, 'r')
        list(f2.keys())
        dset1 = f2['dataset_01']
        GR = dset1[:]
        tig = dset1.attrs['time_grib']
        f2.close()
    return tig, GR,filenamehdf5

#test_existence_fichier




if __name__ == '__main__':

    #filenamehdf5,date,tig=filename()
    print()
    print (filename(tic))
    filenamehdf5,date_formatcourt,tig=filename(tic)
    tig, GR,filenamehdf5=chargement_384(filenamehdf5)
    print()
    ret = requests.head('http://www.example.com')
    print(ret.status_code)
    