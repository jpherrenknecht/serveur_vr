#!/bin/env_vr python3.7.5
# coding: utf-8
import os
import time
import math
import numpy as np
from urllib.request import urlretrieve
#from uploadgrib import *
import xarray as xr
import h5py
from datetime import datetime
from scipy.interpolate import RegularGridInterpolator
from pathlib import Path

#le debut de chargement des gribs intervient en heure UTC à
# 03h30 (gfs00) - 9h30(gfs06) - 15h30(gfs12) -  21h30(gfs18) -
# crontab declenche un chargement en heure utc à
# 03h40 4h10 4h40 5h10

# les gribs complets sont disponibles en heure UTC à
# 05 h (gfs00) - 11h(gfs06) - 17(gfs12) -  23(gfs18) -
# les gribs complets sont disponibles en heure d'hiver à
# 06 h (gfs00) - 12h(gfs06) - 18(gfs12) -  00(gfs18) -
# les gribs complets sont disponibles en heure d'ete à
# 07 h (gfs00) - 13h(gfs06) - 19(gfs12) -  01(gfs18) -

basedir = os.path.abspath(os.path.dirname(__file__))
ix = np.arange(129)  # temps
iy = np.arange(181)  # latitudes
iz = np.arange(361)  # longitudes

def chaine_to_dec(latitude, longitude):
    ''' Transforme les chaines latitude et longitude en un tuple (x,y) '''
    ''' Les latitudes nord sont negatives '''
    degre = int(latitude[0:3])
    minutes = int(latitude[4:6])
    secondes = int(latitude[7:9])
    lat = degre + minutes / 60 + secondes / 3600
    if latitude[10] == 'N':
        lat = -lat
    degre = int(longitude[0:3])
    minutes = int(longitude[4:6])
    secondes = int(longitude[7:9])
    long = degre + minutes / 60 + secondes / 3600
    if longitude[10] == 'W':
        long = -long
    return (long, lat)


def prevision(tig, GR, tp, latitude, longitude):
    fn3 = RegularGridInterpolator((ix, iy, iz), GR)
    itemp = (tp - tig) / 3600 / 3
    ilati = (latitude + 90)
    ilong = (longitude) % 360
    print ('indices',itemp,ilati,ilong )
    vcplx = fn3((itemp, ilati, ilong))
    #print('vcplx',vcplx)
    vit_vent_n = np.abs(vcplx) * 1.94384
    angle_vent = (270 - np.angle(vcplx, deg=True)) % 360
    return vit_vent_n, angle_vent


def chargement_grib(tsec):
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
    filename="gribs/gfs_" + date +"-"+strhour+".hdf5"
    filenamehdf5 = os.path.join(basedir,filename)

    print ('Date du grib réference ancien modèle',dategrib_tpl)

    # reconstitution avec un temps qui n'est pas tic
    t = time.localtime()
    utc = time.gmtime()
    decalage_h = t[3] - utc[3]
    #transformation de tsec en heures et mn utc
    ttuple=time.gmtime(tsec)
    #print ('ttuple ',ttuple)
    hutc=ttuple[3]*60+ttuple[4]
    date = time.strftime("%Y%m%d", time.localtime(tsec-decalage_h*3600))
    if (hutc<4*60+35):
        strhour='18'
        date=datemoinsunjour(date)
    elif (hutc<10*60+35): 
        strhour='00'
        date=datemoinsunjour(date)
    elif    (hutc<16*60+35): 
        strhour='06'
        date=datemoinsunjour(date)
    elif    (hutc<22*60+35): 
        strhour='12'2
        date=datemoinsunjour(date)        


    if os.path.exists(filenamehdf5) == False:        #si ce fichier n'existe pas deja
        leftlon, rightlon, toplat, bottomlat = 0, 360, 90, -90
        iprev = ()
        for a in range(0, 387, 3):  # Construit le tuple des indexs des fichiers maxi 387
            iprev += (str(int(a / 100)) + str(int((a % 100) / 10)) + str(a % 10),)
        GR = np.zeros((len(iprev), 181, 360),
                      dtype=complex)  # initialise le np array de complexes qui recoit les donnees
        for indexprev in range(len(iprev)):  # recuperation des fichiers de 0 a 384 h
            prev = iprev[indexprev]
            url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t" + strhour + "z.pgrb2.1p00.f" + \
                  prev + "&lev_10_m_above_ground=on&all_var=on&leftlon=" \
                  + str(leftlon) + "&rightlon=" + str(rightlon) + "&toplat=" + str(toplat) + "&bottomlat=" + str(
                bottomlat) + "&dir=%2Fgfs." + date + "%2F" + strhour
            nom_fichier = "grib_" + date + "_" + strhour + "_" + prev   # nom sous lequ fichier est sauvegarde provisoirement
            urlretrieve(url, nom_fichier)                               # recuperation des fichiers provisoires
            print(' Enregistrement prévision {} + {} heures effectué: '.format(dategrib,prev))  # destine a suivre le chargement des previsions
            if indexprev==0:
                print (url)
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

    #ouverture du fichier hdf5
    f2 = h5py.File(filenamehdf5, 'r')
    list(f2.keys())
    dset1 = f2['dataset_01']
    GR = dset1[:]
    tig = dset1.attrs['time_grib']
    f2.close()
    return tig, GR , filenamehdf5

# def selection_grib ():
#     t = time.localtime()
#     utc = time.gmtime()
#     decalage_h = t[3] - utc[3]
    
#     hdmja= [210,240,270,300,  570,600,630,660,  930,960,990,1020, 1290,1320,1350,1380]      # 210 = 3h30
#     dicgrib={(210):('00','000','012'),(240):('00','015','072'),(270):('00','075','168'),(300):('00','171','384'),
#             (570):('06','000','012'),(600):('06','015','072'),(630):('06','075','168'),(660):('06','171','384'),
#             (930):('12','000','012'),(960):('12','015','072'),(990):('12','075','168'),(1020):('12','171','384'),
#             (1290):('18','000','012'),(1320):('18','015','072'),(1350):('18','075','168'),(1380):('18','171','384')}

#     hutc=utc[3]*60+utc[4]                               # temps utc actuel en minutes depuis 0 h
#     i=0
#     while hutc >hdmja[i]:                               # on cherche l'indice du grib disponible
#         i=i+1
#     indice=i-1                                          #indice du grib dans la journee
#     ngrib = dicgrib[ hdmja[indice]][0]                  # reference du grib
#     v0    = dicgrib[ hdmja[indice]][1]                  # valeur de l'indice de debut
#     v1    = dicgrib[ hdmja[indice]][2]                  # valeur de l'indice de fin



#     indicem1=i-2                                        #indice du grib precedent
#     ngribm1=dicgrib[ hdmja[indicem1]][0]
#     v0m1   = dicgrib[ hdmja[indicem1]][1]
#     v1m1    = dicgrib[ hdmja[indicem1]][2]              # valeur de l'indice de fin

#     dateheuretig=datetime(utc[0] , utc[1] , utc[2] , int(ngrib),0, 0)
#     #print ('dateheuretig',dateheuretig)
#     tig=time.mktime(dateheuretig.timetuple())+decalage_h*3600    #temps initial du grib en sec locales
#     dategrib= str(dateheuretig)
#     date=dategrib[0:10].replace("-","")

#     #print ('ngrib,v0,v1,ngribm1,vom1,v1m1 , date ',ngrib,v0,v1,'  ',ngribm1,v0m1,v1m1, ' ',date)
#     # valeurs=[]
#     # a=v0
#     # j=0
#     # while a<v1:
#     #     a=v0+3*j
#     #     valeurs.append(a)
#     #     j+=1
#     filename="gribs/gfs_"+date +"-"+ngrib+"-"+str(v1)+".hdf5"

#     #recuperation du nom du grib precedent
#     if hutc<210 :           #hutc<3h30
#         #recherche de la date precedente heure  on recule de 6 h
#         utcm1 = time.gmtime(time.time() -21600)         #21600
#         dategrib_tpm1=datetime(utcm1[0] , utcm1[1] , utcm1[2] ,18,0, 0)
#         dategribm1= str(dategrib_tpm1)
#         datec=dategribm1[0:10].replace("-","")
#         #print('datec ',datec)
#         filenamem1="gribs/gfs_"+datec +"-18-384.hdf5"

#     else:

#         filenamem1="gribs/gfs_"+date +"-"+ngribm1+"-"+str(v1m1)+".hdf5"
#        # print('filenamem1 ', filenamem1)

#     # dategrib= str(utcgrib[0])+'-'+str(utcgrib[1])+'-'+str(utcgrib[2])+'-18'
#     # print('dategrib',dategrib)


#     # dategrib_tpl=datetime(utc[0] , utc[1] , utc[2] , int(heure_grib),0, 0)
#     # tig=time.mktime(dategrib_tpl.timetuple())+decalage_h*3600    #temps initial du grib en sec locales
#     # dategrib= str(dategrib_tpl)
#     # date=dategrib[0:10].replace("-","")
#     return filenamem1,filename




# def chargement(filename):    # chargement simple de file name de type : gribs/gfs-20201102-06-072.hdf5

#     GR = np.zeros((129, 181, 360),dtype=complex)  # initialise le np array de complexes qui recoit les donnees
#     date=filename[10:18]
#     strhour=filename [19:21]
#     vmax=filename[22:25]
#     # print('vmax',vmax)
#     # print (strhour)
#     # print( 'strhour.type',type(strhour))
#     dicvaleurs={"12":([0,3,6,9,12]),
#     "72":([15,18,21,24,27,30,33,36,39,42,45,48,51,54,57,60,63,66,69,72]) ,
#     "168":([75,78,81,84,87,90,93,96,99,102,105,108,111,114,117,120,123,126,129,132,135,138,141,144,147,150,153,156,159,162,165,168]) ,
#     "384":([171,174,177,180,183,186,189,192,195,198,201,204,207,210,213,216,219,222,225,228,231,234,237,240,243,246,249,252,255,258,
#     261,264,267,270,273,276,279,282,285,288,291,294,297,300,303,306,309,312,315,318,321,324,327,330,333,336,339,342,345,348,351,354,
#     357,360,363,366,369,372,375,378,381,384]) }
#     valeurs=dicvaleurs[vmax]
#     leftlon, rightlon, toplat, bottomlat = 0, 360, 90, -90
#     for i in range(len(valeurs)):  # recuperation des fichiers  pour les valeurs contenues dans le tableau valeurs
#         prev = valeurs[i]
#         url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t" + strhour + "z.pgrb2.1p00.f" + \
#                 str(prev) + "&lev_10_m_above_ground=on&all_var=on&leftlon=" \
#                 + str(leftlon) + "&rightlon=" + str(rightlon) + "&toplat=" + str(toplat) + "&bottomlat=" + str( bottomlat) \
#                 + "&dir=%2Fgfs." + date + "%2F"\
#                 + strhour
#         nom_fichier = "gribs/grib_" + date + "_" + strhour + "_" + str(prev)   # nom sous lequ fichier est sauvegarde provisoirement
#         urlretrieve(url, nom_fichier)                               # recuperation des fichiers provisoires
#         print(' Enregistrement prévision {}-{} {} heures effectué: '.format(date,vmax,prev))  # destine a suivre le chargement des previsions

#         #exploitation du fichier et mise en memoire dans GR
#         ds = xr.open_dataset(nom_fichier, engine='cfgrib')
#         GR[int(prev/3)] = ds.variables['u10'].data + ds.variables['v10'].data * 1j
#         os.remove(nom_fichier)  # On efface le fichier pour ne pas encombrer
#         os.remove(nom_fichier + '.4cc40.idx')
#     return None








def datemoinsunjour(date):
    '''date est sous la forme yyyymmdd par ex 20201102'''
    '''renvoie le jour precedent sous lameme forme '''
    year=int(date[0:4])
    month=int(date[4:6])
    day=int(date [6:8])
    datejour=datetime(year, month, day ,0,0,0)
    djs=time.mktime(datejour.timetuple())-24*3600   # moins un jour
    datem1 = time.strftime("%Y%m%d", time.localtime(djs))
    return datem1


def ffilename(tsec):
    ''' Fichier telecheargeable a l'instant donne '''

    hdmja= [210,240,270,300,  570,600,630,660,  930,960,990,1020, 1290,1320,1350,1380,2000]      # 210 = 3h30
    dicgrib={(210):('00','000','012'),(240):('00','015','072'),(270):('00','075','168'),(300):('00','171','384'),
            (570):('06','000','012'),(600):('06','015','072'),(630):('06','075','168'),(660):('06','171','384'),
            (930):('12','000','012'),(960):('12','015','072'),(990):('12','075','168'),(1020):('12','171','384'),
            (1290):('18','000','012'),(1320):('18','015','072'),(1350):('18','075','168'),(1380):('18','171','384')}
    dic1={'00':'18','06':'00','12':'06','18':'12'}
    dic2={'012':'384' ,'072':'012','168':'072','384':'168'}

    t = time.localtime()
    utc = time.gmtime()
    decalage_h = t[3] - utc[3]
    #transformation de tsec en heures et mn utc

    ttuple=time.gmtime(tsec)
    #print ('ttuple ',ttuple)
    hutc=ttuple[3]*60+ttuple[4]
    date = time.strftime("%Y%m%d", time.localtime(tsec-decalage_h*3600))
    #print ('date', date )
    #print ('hutc dansffilename',hutc)
    if (hutc<210):
        filename="gribs/gfs-"+datemoinsunjour(date) +"-18-384.hdf5"
        dernier384=filename
        ngrib='18'
        v1='384'

    else :
        i=0
        while hutc >hdmja[i]:                               # on cherche l'indice du grib disponible
            i=i+1
        indice=i-1                                          #indice du grib dans la journee
        ngrib = dicgrib[ hdmja[indice]][0]                  # reference du grib
        #v0    = dicgrib[ hdmja[indice]][1]                  # valeur de l'indice de debut
        v1    = dicgrib[ hdmja[indice]][2]                  # valeur de l'indice de fin
        filename="gribs/gfs-"+date +"-"+ngrib+"-"+v1+".hdf5"

    # dernier384

    if hutc<310:
        dernier384="gribs/gfs-"+datemoinsunjour(date) +"-18-384.hdf5"
    elif hutc<670:
        dernier384="gribs/gfs-"+date+"-00-384.hdf5"
    elif hutc<1030:
        dernier384="gribs/gfs-"+date+"-06-384.hdf5"
    elif hutc<1390:
        dernier384="gribs/gfs-"+date+"-12-384.hdf5"
    else:
        dernier384="gribs/gfs-"+date+"-18-384.hdf5"

    #precedent
    #print (' pour test ngrib v1 hutc ',ngrib,v1,hutc )
    if ngrib=='00':
        if v1=='012':
            filenamem1="gribs/gfs-"+datemoinsunjour(date) +"-18-384.hdf5"
        else:
            filenamem1="gribs/gfs-"+date +"-00-"+dic2[v1]+".hdf5"
        # if ( hutc <310) :
        #     filenamem1="gribs/gfs-"+datemoinsunjour(date) +"-18-384.hdf5"


    else:
        if v1=='012':
            filenamem1="gribs/gfs-"+date +"-"+dic1[ngrib]+"-384.hdf5"
        else:
            filenamem1="gribs/gfs-"+date +"-"+ngrib+"-"+dic2[v1]+".hdf5"
            # if v1==384:
            #     filenamem1="gribs/gfs-"+datemoinsunjour(date) +"-18-168.hdf5"
    if (v1=='384' and hutc <310) :  
        filenamem1="gribs/gfs-"+datemoinsunjour(date) +"-18-168.hdf5"

    return dernier384,filenamem1,filename



def ftig(filename):
    ''' donne l'instant initial du grib en secondes locales '''
    ''' a partir de la date et de l'heure du grib dans le nom du fichier'''
    date    =filename[10:18]
    strhour =filename [19:21]
    year    =int(date[0:4])
    month   =int(date[4:6])
    day     =int(date [6:8])
    datejour=datetime(year, month, day ,int(strhour),0,0)
    tig=time.mktime(datejour.timetuple())
    return tig




def upload384(name) :
    '''reconstitue le nom du dernier grib disponible
      le charge sur nomad au besoin
      et le charge pour la simulation s'il existe deja '''
    GR = np.zeros((129, 181, 360),dtype=complex)  # initialise le np array de complexes qui recoit les donnees
    date=(name[10:18])
    strhour=(name [19:21])
    year=int(date[0:4])
    month=int(date[4:6])
    day=int(date [6:8])
    t = time.localtime()
    utc = time.gmtime()
    decalage_h = t[3] - utc[3]
    print (' Ligne 321 date et heure dans chargement 384', date,strhour )
    datejour=datetime(year, month, day ,int(strhour),0,0)
    tig=time.mktime(datejour.timetuple())+decalage_h*3600  # temps initial du grib en secondes locales

    leftlon, rightlon, toplat, bottomlat = 0, 360, 90, -90
    if os.path.exists(name) == False:        #si ce fichier n'existe pas deja
        iprev = ()
        for a in range(0, 387, 3):  # Construit le tuple des indexs des fichiers maxi 387
            iprev += (str(int(a / 100)) + str(int((a % 100) / 10)) + str(a % 10),)
        for indexprev in range(len(iprev)):  # recuperation des fichiers de 0 a 384 h
            prev = iprev[indexprev]
            url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t" + strhour + "z.pgrb2.1p00.f" + \
                  prev + "&lev_10_m_above_ground=on&all_var=on&leftlon=" \
                  + str(leftlon) + "&rightlon=" + str(rightlon) + "&toplat=" + str(toplat) + "&bottomlat=" + str(
                bottomlat) + "&dir=%2Fgfs." + date + "%2F" + strhour
            nom_fichier = "gribs/grib_" + date + "_" + strhour + "_" + prev   # nom sous lequ fichier est sauvegarde provisoirement
            urlretrieve(url, nom_fichier)                               # recuperation des fichiers provisoires
            print(' Enregistrement prévision {}-{}-{} {} heures effectué: '.format(date,strhour,384,prev))  # destine a suivre le chargement des previsions
            #if prev=='000':
            #    print('url 384', url)
            # exploitation du fichier et mise en memoire dans GR
            ds = xr.open_dataset(nom_fichier, engine='cfgrib')
            GR[indexprev] = ds.variables['u10'].data + ds.variables['v10'].data * 1j
            os.remove(nom_fichier)  # On efface le fichier pour ne pas encombrer
            os.remove(nom_fichier + '.4cc40.idx')
        # on modifie GR pour lui donner un indice 360 egal à l'indice 0
        GR=np.concatenate((GR,GR[:,:,0:1]), axis=2)
        # on calcule le tig a partir de la date dans le fichier
        f1 = h5py.File(name, "w")
        dset1 = f1.create_dataset("dataset_01", GR.shape, dtype='complex', data=GR)
        dset1.attrs['time_grib'] = tig  # transmet le temps initial du grib en temps local en s pour pouvoir faire les comparaisons
        f1.close()
        print('Ligne 351 Dimension de GR a fin de upload384 ',GR.shape)
    return GR, tig


def upload_borne(filename,inf,sup):
    '''Cette fonction charge PR mais ne sauve pas de fichier '''
    date=filename[10:18]
    strhour=filename [19:21]
    binf=int(inf/3)
    bsup=int(sup/3)+1
    dimpr=int(sup/3-inf/3)
    print('bornes',int(inf/3),int(sup/3)+1)
    leftlon, rightlon, toplat, bottomlat = 0, 360, 90, -90
    print('ligne 361 on est dans upload borne')
    if os.path.exists(filename) == False:        # Valeur normale false si ce fichier n'existe pas deja
        PR = np.zeros((dimpr+1, 181, 360),dtype=complex)  # initialise le np array de complexes qui recoit les donnees
        iprev = ()
        for a in range(int(inf),int(sup)+1, 3):  # Construit le tuple des indexs des fichiers maxi 387
            iprev += (str(int(a / 100)) + str(int((a % 100) / 10)) + str(a % 10),)
        print ('ligne 366 on est dans uploadborne')   
        print ('Bornes inf,sup ',inf,sup) 
        print(iprev)
        for indexprev in range(len(iprev)):  # recuperation des fichiers de 0 a 384 h
            prev = iprev[indexprev]
            url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t" + strhour + "z.pgrb2.1p00.f" + \
                  prev + "&lev_10_m_above_ground=on&all_var=on&leftlon=" \
                  + str(leftlon) + "&rightlon=" + str(rightlon) + "&toplat=" + str(toplat) + "&bottomlat=" + str(
                bottomlat) + "&dir=%2Fgfs." + date + "%2F" + strhour
            #print(url)    
          
            nom_fichier = "gribs/grib_" + date + "_" + strhour + "_" + prev   # nom sous lequ fichier est sauvegarde provisoirement
            urlretrieve(url, nom_fichier)                               # recuperation des fichiers provisoires
            print(' Enregistrement prévision {}-{}-{} {} heures effectué: '.format(date,strhour,sup,prev))  # destine a suivre le chargement des previsions
           # exploitation du fichier et mise en memoire dans GR
            ds = xr.open_dataset(nom_fichier, engine='cfgrib')
          
            PR[indexprev] = ds.variables['u10'].data + ds.variables['v10'].data * 1j
            os.remove(nom_fichier)  # On efface le fichier pour ne pas encombrer
            os.remove(nom_fichier + '.4cc40.idx')
        PR=np.concatenate((PR,PR[:,:,0:1]), axis=2)
       
    else :                         # si le fichier existe deja ouverture du fichier hdf5
        f2 = h5py.File(filename, 'r')
        list(f2.keys())
        dset1 = f2['dataset_01']
        GR = dset1[:]
        tig = dset1.attrs['time_grib']
        f2.close()
        PR=GR[binf:bsup,:,:]

    return PR,inf,sup


def chargement_complet(tic):
    dernier384,filenamem1,filename=ffilename(tic)
    

    # on charge le dernier 384 qui servira de base
    if os.path.exists(dernier384) == False:
            print ('le dernier 384  {} n existe pas '.format(dernier384))
            print("On le charge")
            GR,tig=upload384(dernier384)               #si le dernier 384 n'existe pas on le charge en entier (et GR360=GR0)
            print("\nmaintenant le dernier 384 en vigueur est chargé")                              
        # on recupere GR et tig  sur le dernier 384 qui vient  d'etre chargé
       
    else :              #le dernier 384 existe deja on n'a qu'à charger GR et tig à partir du hdf5 sur 
        #print ('Le dernier 384 {} existait et donc on charge directement le hdf5 '.format(dernier384))
        f2 = h5py.File(dernier384, 'r')
        list(f2.keys())
        dset1 = f2['dataset_01']
        GR = dset1[:]
        tig = dset1.attrs['time_grib']
        f2.close()
    tig_formate    = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(tig))
    #print ('Ligne 461 tig du Grib 384 ( heure +1) pour verification',tig_formate)
   
    #on charge le dernier fichier disponible    
    if(filename[22:25]=='384'):  # on est dans le cas ou un nouveau fichier 384 complet est disponible   
        if os.path.exists(filename) == False:   # s'il n'a pas ete deja charge 
            GR,tig=upload384(filename)
            dernier384=filename

    else:    # dans les cas de figure ou on est pas en 384 on va chercher les intermediaires
        if(filename[22:25]=='012'):
            if os.path.exists(filename) == False:   # s'il n'existe pas deja on charge les 4 valeurs soit 12 h
                PR,inf,sup=upload_borne(filename,0,12)
                GR[2:7,:,:]=PR 
                 # on sauve le nouveau fichier sous son nouveau nom # attention a tig c'est le tig de l'ancien
                f1 = h5py.File(filename, "w")
                dset1 = f1.create_dataset("dataset_01", GR.shape, dtype='complex', data=GR)
                dset1.attrs['time_grib'] = tig  # transmet le temps initial du grib en temps local en s pour pouvoir faire les comparaisons
                f1.close()
                tig_formate    = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(tig))
                print ('L 414 Grib 012  tig pour verification ',tig_formate) 


        elif (filename[22:25]=='072') : # on va pas s'embeter on  recharge de 0 à72 soit 20 valeurs
            if os.path.exists(filename) == False:   # s'il n'existe pas deja
                PR,inf,sup=upload_borne(filename,0,72)
                GR[2:27,:,:]=PR 
                 # on sauve le nouveau fichier sous son nouveau nom # attention a tig c'est le tig de l'ancien
                f1 = h5py.File(filename, "w")
                dset1 = f1.create_dataset("dataset_01", GR.shape, dtype='complex', data=GR)
                dset1.attrs['time_grib'] = tig  # transmet le temps initial du grib en temps local en s pour pouvoir faire les comparaisons
                f1.close()

                tig_formate    = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(tig))
                print ('L 428 Grib 072  tig pour verification ',tig_formate)




        elif (filename[22:25]=='168') : # Pour l'instant on ne s'embete pas on  recharge de 0 à 168 soit 56 valeurs
            if os.path.exists(filename) == False:   # s'il n'existe pas deja
                PR,inf,sup=upload_borne(filename,0,168)
                GR[2:59,:,:]=PR 
                 # on sauve le nouveau fichier sous son nouveau nom # attention a tig c'est le tig de l'ancien
                f1 = h5py.File(filename, "w")
                dset1 = f1.create_dataset("dataset_01", GR.shape, dtype='complex', data=GR)
                dset1.attrs['time_grib'] = tig  # transmet le temps initial du grib en temps local en s pour pouvoir faire les comparaisons
                f1.close() 

                tig_formate    = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(tig))
                print ('L 444 Grib 168  tig pour verification',tig_formate)



    if os.path.exists(filename) == True:
        print ('Le fichier utilisé pour les simulations est  ',filename)
        print()
    # print (' le dernier 384 {} existe a bien été chargé et on peut se servir de GR et tig du 384 '.format(dernier384))
    return tig,GR,filename



def chargement_fichier(nomfichier):  # fichier existant
    if os.path.exists(filename) == True: 
        f2 = h5py.File(dernier384, 'r')
        list(f2.keys())
        dset1 = f2['dataset_01']
        GR = dset1[:]
        tig = dset1.attrs['time_grib']
        f2.close()
    else :
        print ("Le fichier {} n'existe pas et doit etre chargé depuis NMEA".format(nomfichier))
        tig, GR=0,0        
    return tig,GR





if __name__ == '__main__':

    tic=time.time()
    # date et heure simulation chargement grib
    datejour       = datetime(2020,11,14, 7,5,0)           # en heures locales
    djs            = time.mktime(datejour.timetuple())   # transformation en secondes
    datem1         = time.strftime("%Y%m%d", time.localtime(djs))
    datem1_formate = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(djs))
    tic_formate    = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(tic))
    # djstuple=time.gmtime(djs)


    print()
    print('**************************************************************************************************')
    print ('Heure locale au  lancement du programme',tic_formate)
    #print('**************************************************************************************************')
    # print ('Date simulation en temps local',datem1_formate)

    # print ('tic en s : ',tic)
    # print ('djs-tic',djs-tic)
    # print()
    dateessai =tic                  # dateessai chargement
    dernier384,filenamem1,filename=ffilename(dateessai)

    if os.path.exists(filename) == True:
        c1=' Est déjà chargé' 
    else:
        c1=" N'est pas encore chargé "    
    
    if os.path.exists(filenamem1) == True:
        c2=' Est déjà chargé' 
    else:
        c2=" N'est pas encore chargé " 
    if os.path.exists(filename) == True:
        c3=' Est déjà chargé' 
    else:
        c3=" N'est pas encore chargé "     

    print()

    print('Nom du dernier 384 chargeable {}  {}:'.format(dernier384,c1))
    print('Nom du precedent   chargeable {}  {}:'.format(filenamem1,c2))
    print('Nom du   fichier   chargeable {}  {}:'.format(filename,c3))
    print()
    print('**************************************************************************************************')
    print()

    tig, GR ,filename   = chargement_complet(dateessai)
    tig_formate       = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(tig))
    tic_formate_local = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(tic))
    tigold, GRold,filenameold   = chargement_grib(dateessai)
    # print (tig, tigold)
    # # test sur les valeurs GR
    # print ('GRold[0,0,0]',GRold[0][0][0])
    # print ('GR[0,0,0]',GR[0][0][0])


    # prevision avec date donnee    

    print ('\n---------------------------------\
            \nDate et heure de la prévision \
            \n---------------------------------')
    dateprev=datetime(2020 , 11 , 16, 23, 10,  0)
    #print ('\nDateprev : ',dateprev , ' local')
    dateprev_s=time.mktime(dateprev.timetuple()) # en secondes locales
    dateprev_formate_local = time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(dateprev_s))
    
    #print ('dateprev_s en local ',dateprev_s )
    print('Date de la prevision en heure locale',dateprev_formate_local)
   # prevision proprement dite

    latitude_d = '036-35-39-N'
    longitude_d = '024-21-41-W'
    d = chaine_to_dec(latitude_d, longitude_d)  # co


    print ('\nPrevisions avec Nouveau  grib') 
    print('Fichier utilise', filename)  
    vit_vent_n, angle_vent = prevision(tig, GR,dateprev_s, d[1], d[0])
    print('\nLe {} heure Locale Pour latitude {:6.2f} et longitude{:6.2f} '.format(dateprev_formate_local, d[1], d[0]))
    print('\tAngle du vent   {:6.3f} °'.format(angle_vent))
    print('\tVitesse du vent {:6.3f} Noeuds'.format(vit_vent_n))

    print ('\nPrevisions avec le dernier 384') 
    print('Fichier utilise', dernier384)
    tig384,GR384= chargement_fichier(dernier384) 
    vit_vent_n, angle_vent = prevision(tig384, GR384,dateprev_s, d[1], d[0])
    print('\nLe {} heure Locale Pour latitude {:6.2f} et longitude{:6.2f} '.format(dateprev_formate_local, d[1], d[0]))
    print('\tAngle du vent   {:6.3f} °'.format(angle_vent))
    print('\tVitesse du vent {:6.3f} Noeuds'.format(vit_vent_n))


    print ('\nPrevisions avec ancien systeme')
    print('Fichier utilise', filenameold) 
    vit_vent_n, angle_vent = prevision(tigold, GRold,dateprev_s, d[1], d[0])
  #  print('\nLe {} heure Locale Pour latitude {:6.2f} et longitude{:6.2f} '.format(dateprev_formate_local, d[1], d[0]))
    print('\tAngle du vent avec Old  {:6.3f} °'.format(angle_vent))
    print('\tVitesse du vent avec Old {:6.3f} Noeuds'.format(vit_vent_n))
