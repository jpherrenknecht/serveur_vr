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


def selection_grib ():
    t = time.localtime()
    utc = time.gmtime()
    decalage_h = t[3] - utc[3]
    #date=datetime(utc[0] , utc[1] , utc[2] , int(heure_grib),0, 0)# date qui servira pour les noms de gribs
      
    hdmja= [210,240,270,300,  570,600,630,660,  930,960,990,1020, 1290,1320,1350,1380]      # 210 = 3h30
    dicgrib={(210):('00','000','012'),(240):('00','015','072'),(270):('00','075','168'),(300):('00','171','384'),
            (570):('06','000','012'),(600):('06','015','072'),(630):('06','075','168'),(660):('06','171','384'),
            (930):('12','000','012'),(960):('12','015','072'),(990):('12','075','168'),(1020):('12','171','384'),
            (1290):('18','000','012'),(1320):('18','015','072'),(1350):('18','075','168'),(1380):('18','171','384')}

    hutc=utc[3]*60+utc[4]                               # temps utc actuel en minutes depuis 0 h
    i=0
    while hutc >hdmja[i]:                               # on cherche l'indice du grib disponible
        i=i+1
    indice=i-1                                          #indice du grib dans la journee
    ngrib = dicgrib[ hdmja[indice]][0]                  # reference du grib
    v0    = dicgrib[ hdmja[indice]][1]                  # valeur de l'indice de debut
    v1    = dicgrib[ hdmja[indice]][2]                  # valeur de l'indice de fin
    


    indicem1=i-2                                        #indice du grib precedent
    ngribm1=dicgrib[ hdmja[indicem1]][0]
    v0m1   = dicgrib[ hdmja[indicem1]][1]
    v1m1    = dicgrib[ hdmja[indicem1]][2]              # valeur de l'indice de fin
    
    dateheuretig=datetime(utc[0] , utc[1] , utc[2] , int(ngrib),0, 0)
    #print ('dateheuretig',dateheuretig)
    tig=time.mktime(dateheuretig.timetuple())+decalage_h*3600    #temps initial du grib en sec locales 
    dategrib= str(dateheuretig) 
    date=dategrib[0:10].replace("-","")

    #print ('ngrib,v0,v1,ngribm1,vom1,v1m1 , date ',ngrib,v0,v1,'  ',ngribm1,v0m1,v1m1, ' ',date)
    # valeurs=[]
    # a=v0
    # j=0
    # while a<v1:
    #     a=v0+3*j
    #     valeurs.append(a)
    #     j+=1
    filename="gribs/gfs_"+date +"-"+ngrib+"-"+str(v1)+".hdf5"

    #recuperation du nom du grib precedent
    if hutc<210 :           #hutc<3h30
        #recherche de la date precedente heure  on recule de 6 h
        utcm1 = time.gmtime(time.time() -21600)         #21600
        dategrib_tpm1=datetime(utcm1[0] , utcm1[1] , utcm1[2] ,18,0, 0)
        dategribm1= str(dategrib_tpm1) 
        datec=dategribm1[0:10].replace("-","")
        #print('datec ',datec)
        filenamem1="gribs/gfs_"+datec +"-18-384.hdf5"

    else:

        filenamem1="gribs/gfs_"+date +"-"+ngribm1+"-"+str(v1m1)+".hdf5"
       # print('filenamem1 ', filenamem1)

    # dategrib= str(utcgrib[0])+'-'+str(utcgrib[1])+'-'+str(utcgrib[2])+'-18'
    # print('dategrib',dategrib)
    
                   
    # dategrib_tpl=datetime(utc[0] , utc[1] , utc[2] , int(heure_grib),0, 0)
    # tig=time.mktime(dategrib_tpl.timetuple())+decalage_h*3600    #temps initial du grib en sec locales 
    # dategrib= str(dategrib_tpl) 
    # date=dategrib[0:10].replace("-","")
    return filenamem1,filename




def chargement(filename):    # chargement simple de file name de type : gribs/gfs-20201102-06-072.hdf5

    GR = np.zeros((129, 181, 360),dtype=complex)  # initialise le np array de complexes qui recoit les donnees
    date=filename[10:18]
    strhour=filename [19:21]
    vmax=filename[22:25]
    # print('vmax',vmax)
    # print (strhour)
    # print( 'strhour.type',type(strhour))
    dicvaleurs={"12":([0,3,6,9,12]),
    "72":([15,18,21,24,27,30,33,36,39,42,45,48,51,54,57,60,63,66,69,72]) ,
    "168":([75,78,81,84,87,90,93,96,99,102,105,108,111,114,117,120,123,126,129,132,135,138,141,144,147,150,153,156,159,162,165,168]) ,
    "384":([171,174,177,180,183,186,189,192,195,198,201,204,207,210,213,216,219,222,225,228,231,234,237,240,243,246,249,252,255,258,
    261,264,267,270,273,276,279,282,285,288,291,294,297,300,303,306,309,312,315,318,321,324,327,330,333,336,339,342,345,348,351,354,
    357,360,363,366,369,372,375,378,381,384]) }
    valeurs=dicvaleurs[vmax]
    leftlon, rightlon, toplat, bottomlat = 0, 360, 90, -90
    for i in range(len(valeurs)):  # recuperation des fichiers  pour les valeurs contenues dans le tableau valeurs
        prev = valeurs[i]
        url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t" + strhour + "z.pgrb2.1p00.f" + \
                str(prev) + "&lev_10_m_above_ground=on&all_var=on&leftlon=" \
                + str(leftlon) + "&rightlon=" + str(rightlon) + "&toplat=" + str(toplat) + "&bottomlat=" + str( bottomlat) \
                + "&dir=%2Fgfs." + date + "%2F"\
                + strhour
        nom_fichier = "gribs/grib_" + date + "_" + strhour + "_" + str(prev)   # nom sous lequ fichier est sauvegarde provisoirement
        urlretrieve(url, nom_fichier)                               # recuperation des fichiers provisoires
        print(' Enregistrement prévision {}-{} {} heures effectué: '.format(date,vmax,prev))  # destine a suivre le chargement des previsions

        #exploitation du fichier et mise en memoire dans GR
        ds = xr.open_dataset(nom_fichier, engine='cfgrib')
        GR[int(prev/3)] = ds.variables['u10'].data + ds.variables['v10'].data * 1j
        os.remove(nom_fichier)  # On efface le fichier pour ne pas encombrer
        os.remove(nom_fichier + '.4cc40.idx')
    return None








def datemoinsunjour(date):
    '''date est sous la forme yyyymmdd par ex 20201102'''
    '''renvoie le jour precedent sous lameme forme '''
    year=int(date[0:4])
    month=int(date[4:6])
    day=int(date [6:8])
    datejour=datetime(year, month, day ,0,0,0)
    djs=time.mktime(datejour.timetuple())-3600   # moins une heure
    datem1 = time.strftime("%Y%m%d", time.localtime(djs))
    return datem1


def ffilename():
    t = time.localtime()
    utc = time.gmtime()
    decalage_h = t[3] - utc[3]
    tic=time.time()
    date = time.strftime("%Y%m%d", time.localtime(time.time()-decalage_h*3600))
    hdmja= [210,240,270,300,  570,600,630,660,  930,960,990,1020, 1290,1320,1350,1380]      # 210 = 3h30
    dicgrib={(210):('00','000','012'),(240):('00','015','072'),(270):('00','075','168'),(300):('00','171','384'),
            (570):('06','000','012'),(600):('06','015','072'),(630):('06','075','168'),(660):('06','171','384'),
            (930):('12','000','012'),(960):('12','015','072'),(990):('12','075','168'),(1020):('12','171','384'),
            (1290):('18','000','012'),(1320):('18','015','072'),(1350):('18','075','168'),(1380):('18','171','384')}
    hutc=utc[3]*60+utc[4]                               # temps utc actuel en minutes depuis 0 h sert a selectionner le fichier
    i=0
    while hutc >hdmja[i]:                               # on cherche l'indice du grib disponible
        i=i+1
    indice=i-1                                          #indice du grib dans la journee
    ngrib = dicgrib[ hdmja[indice]][0]                  # reference du grib
    #v0    = dicgrib[ hdmja[indice]][1]                  # valeur de l'indice de debut
    v1    = dicgrib[ hdmja[indice]][2]                  # valeur de l'indice de fin

    filename="gribs/gfs-"+date +"-"+ngrib+"-"+v1+".hdf5"
    
    return filename



def fichier_precedent(filename):
    date=filename[10:18]
    strhour=filename [19:21]
    vmax=filename[22:25]
    datem1=datemoinsunjour(date)
    dic1={'00':'18','06':'00','12':'06','18':'12'}
    dic2={'012':'384' ,'072':'012','168':'072','384':'168'}
    print (dic1['12'])
    if strhour=='00':
        if vmax=='012':
            datem1=datemoinsunjour(date)
            filenamem1="gribs/gfs-"+datem1 +"-18-384.hdf5"
        else:    
            filenamem1="gribs/gfs-"+date +"-00-"+dic2[vmax]+".hdf5"
    else:
        if vmax=='012':
            filenamem1="gribs/gfs-"+date +"-"+dic1[strhour]+"-384.hdf5"
        else:        
            filenamem1="gribs/gfs-"+date +"-"+strhour+"-"+dic2[vmax]+".hdf5"
    return filenamem1

def fdernier384(filename):
    date=filename[10:18]
    strhour=filename [19:21]
    datem1=datemoinsunjour(date)
    dic1={'00':'18','06':'00','12':'06','18':'12'}
    if strhour=='00':
        dernier384="gribs/gfs-"+datem1 +"-18-384.hdf5"
    else :
        dernier384="gribs/gfs-"+date +"-"+dic1[strhour]+"-384.hdf5"
    return dernier384          

def ftig(filename):
    ''' donne l'instant initial du grib en secondes locales '''
    ''' a partir de la date et de l'heure du grib dans le nom du fichier'''
    date=filename[10:18]
    strhour=filename [19:21]
    year=int(date[0:4])
    month=int(date[4:6])
    day=int(date [6:8])
    datejour=datetime(year, month, day ,0,0,0)
    tig=time.mktime(datejour.timetuple())
    return tig




def upload384(name) :
    '''reconstitue le nom du dernier grib disponible
      le charge sur nmea au besoin 
      et le charge pour la simulation s'il existe deja '''
    GR = np.zeros((129, 181, 360),dtype=complex)  # initialise le np array de complexes qui recoit les donnees
    date=name[10:18]
    strhour=name [19:21]
   
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
            if prev=='000':
                print('url 384', url)  
            # exploitation du fichier et mise en memoire dans GR
            ds = xr.open_dataset(nom_fichier, engine='cfgrib')
            GR[indexprev] = ds.variables['u10'].data + ds.variables['v10'].data * 1j
            os.remove(nom_fichier)  # On efface le fichier pour ne pas encombrer
            os.remove(nom_fichier + '.4cc40.idx')

        # on modifie GR pour lui donner un indice 360 egal à l'indice 0
        GR=np.concatenate((GR,GR[:,:,0:1]), axis=2)
        # on calacule le tig a partir de la date dans le fichier
        tig=ftig(filename)
        
        f1 = h5py.File(name, "w")
        dset1 = f1.create_dataset("dataset_01", GR.shape, dtype='complex', data=GR)
        dset1.attrs['time_grib'] = tig  # transmet le temps initial du grib en temps local en s pour pouvoir faire les comparaisons
        f1.close()
    return None


def upload_borne(filename,inf,sup):
    date=filename[10:18]
    strhour=filename [19:21]
    dimpr=int(sup/3-inf/3)
    #print('bornes',int(inf/3),int(sup/3)+1)
    PR = np.zeros((dimpr+1, 181, 360),dtype=complex)  # initialise le np array de complexes qui recoit les donnees
    leftlon, rightlon, toplat, bottomlat = 0, 360, 90, -90
    
    if os.path.exists(filename) == True:        # Valeur normale false si ce fichier n'existe pas deja
        iprev = ()
        for a in range(int(inf),int(sup)+1, 3):  # Construit le tuple des indexs des fichiers maxi 387
            iprev += (str(int(a / 100)) + str(int((a % 100) / 10)) + str(a % 10),)
        print(iprev)
        for indexprev in range(len(iprev)):  # recuperation des fichiers de 0 a 384 h
            prev = iprev[indexprev]
            url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t" + strhour + "z.pgrb2.1p00.f" + \
                  prev + "&lev_10_m_above_ground=on&all_var=on&leftlon=" \
                  + str(leftlon) + "&rightlon=" + str(rightlon) + "&toplat=" + str(toplat) + "&bottomlat=" + str(
                bottomlat) + "&dir=%2Fgfs." + date + "%2F" + strhour
            if prev=='000':
                print('url partiel',url)    
            nom_fichier = "gribs/grib_" + date + "_" + strhour + "_" + prev   # nom sous lequ fichier est sauvegarde provisoirement
            urlretrieve(url, nom_fichier)                               # recuperation des fichiers provisoires
            print(' Enregistrement prévision {}-{}-{} {} heures effectué: '.format(date,strhour,384,prev))  # destine a suivre le chargement des previsions
           # exploitation du fichier et mise en memoire dans GR

            
            ds = xr.open_dataset(nom_fichier, engine='cfgrib')
            PR[indexprev] = ds.variables['u10'].data + ds.variables['v10'].data * 1j
            os.remove(nom_fichier)  # On efface le fichier pour ne pas encombrer
            os.remove(nom_fichier + '.4cc40.idx')

    return PR,inf,sup
        
    
def chargement_complet():
    filename=ffilename()    # nom du dernier chargeable partiel
    if os.path.exists(filename) == True:      # la valeur normale est False True est pour les tests
    # on analyse le nom du fichier
        date=filename[10:18]
        strhour=filename [19:21]
        vmax=filename[22:25]
        datem1=datemoinsunjour(date)

        dernier384=fdernier384(filename)      # on cherche le nom du dernier fichier 384
        if os.path.exists(dernier384) == False: 
            print("Le dernier fichier 384 n'a pas ete charge") 
            upload384(filename)               #si le dernier 384 n'existe pas on le charge
                                        # on cherche le fichier precedent
        # on recupere GR et tig  sur le dernier 384
        f2 = h5py.File(dernier384, 'r')
        list(f2.keys())
        dset1 = f2['dataset_01']
        GR = dset1[:]
        tig = dset1.attrs['time_grib']
        f2.close()
        print (GR[0,0,0])

          
        PR,inf,sup=upload_borne(filename,0,384)
        print(filename)
        print(inf,sup)
        print (PR[0,0,0])
        #if os.path.exists(filename) == False:        #si ce fichier n'existe pas deja

    return None    





if __name__ == '__main__':

    filename=ffilename()
    print()
    print('nom du fichier chargeable :',filename)
    print('Nom du dernier 384        :',fdernier384(filename))
    print()
    chargement_complet()
