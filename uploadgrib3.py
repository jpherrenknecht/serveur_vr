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

tic=time.time()
ticstruct = time.localtime()
utc = time.gmtime()
decalage_h = ticstruct[3] - utc[3]
leftlon, rightlon, toplat, bottomlat = 0, 360, 90, -90
# constitution d'un nom de fichier
basedir = os.path.abspath(os.path.dirname(__file__))
ix = np.arange(129)  # temps
iy = np.arange(181)  # latitudes
iz = np.arange(361)  # longitudes
#filenameold="gribs/gfs_" + datemoinsunjour(datem1) +"-"+strhour+".hdf5"

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

def chargement_hdf5(fichiergrib):
    
    f2 = h5py.File(fichiergrib, 'r')
    list(f2.keys())
    dset1 = f2['dataset_01']
    GR =  dset1[:]
    tig = dset1.attrs['time_grib']
    f2.close()
    print('\nNom du fichier grib chargé ',fichiergrib)
    print()
    return tig,GR ,fichiergrib


def nomfichiers():
    tic=time.time()
    dateessai_tuple      = time.gmtime(tic)             # transformation en tuple utc
    mn_utc=dateessai_tuple[3]*60+dateessai_tuple[4]
    dateessai_sec        = tic
    dateessai_formatcourt=time.strftime("%Y%m%d", time.localtime(dateessai_sec))
    dateessai_formatcourt_utc=time.strftime("%Y%m%d", time.gmtime(dateessai_sec))
    datem1_utc=time.strftime("%Y%m%d", time.gmtime(dateessai_sec-86400))     # jour moins un 
     
    # recherche de l'heure anterieure
    hdja= [0,215,245,275,305,  575,605,635,665,  935,965,995,1025, 1295,1325,1355,1385,1410,1500]      # 210 = 3h30
    hdja2= [0, 305,  665, 1025,1385,1500] 
    dicgrib={(0):('18-384'),(215):('00-012'),(245):('00-072'),(275):('00-168'),(305):('00-384'),
            (575):('06-012'),(605):('06-072'),(635):('06-168'),(665):('06-384'),
            (935):('12-012'),(965):('12-072'),(995):('12-168'),(1025):('12-384'),
            (1295):('18-012'),(1325):('18-072'),(1355):('18-168'),(1385):('18-384')}
    dicgrib2={(0):('18-384'),(305):('00-384'),(665):('06-384'),(1025):('12-384'),(1385):('18-384'),(1500):('18-384')}   

    i=0
    while mn_utc >=hdja[i]:                               # on cherche l'indice du grib disponible
        i=i+1
    indice=i-1
    if indice==1385:
        filename="gribs/gfs_"+dateessai_formatcourt_utc+"-"+dicgrib[hdja[indice]]+".hdf5"
    if indice==0:
        filename="gribs/gfs_"+datem1_utc+"-"+dicgrib[hdja[indice]]+".hdf5"
    else:       
        filename="gribs/gfs_"+dateessai_formatcourt_utc+"-"+dicgrib[hdja[indice]]+".hdf5"

    i=0
    while mn_utc >hdja2[i]:                               # on cherche l'indice du grib disponible
        i=i+1
    indice2=i-1  
    # recherche du nom du fichier 384 anterieur dans dictionnaire
    dicgrib2={(0):('18-384'),(305):('00-384'),(665):('06-384'),(1025):('12-384'),(1385):('18-384'),(1500):('18-384')}
    if indice2==1385:
        filename384="gribs/gfs_"+dateessai_formatcourt_utc+"-"+dicgrib[hdja[indice]]+".hdf5"
        filenameold="gribs/gfs_"+dateessai_formatcourt_utc+"-"+dicgrib[hdja[indice]][0:2]+".hdf5"
    if indice2==0:
        filename384="gribs/gfs_"+datem1_utc+"-"+dicgrib2[hdja2[indice2]]+".hdf5"
        filenameold="gribs/gfs_"+datem1_utc+"-"+dicgrib2[hdja2[indice2]][0:2]+".hdf5"
    else:
        filename384="gribs/gfs_"+dateessai_formatcourt_utc+"-"+dicgrib2[hdja2[indice2]]+".hdf5"
        filenameold="gribs/gfs_"+dateessai_formatcourt_utc+"-"+dicgrib2[hdja2[indice2]][0:2]+".hdf5"

    filename = os.path.join(basedir,filename)
    filenameold = os.path.join(basedir,filenameold)
    filename384 = os.path.join(basedir,filename384)
    return  filenameold,filename384,filename   




def chargement_fichier_provisoire(filename):
    '''chargement d'un fichier avec le nom defini contenant la date et l'indice max'''
    '''Pour l'instant  par securite on charge tout a partir de 0 '''
    #print('Chargement provisoire')
    date    =filename[-20:-12]
    #print (date)
    strhour =filename [-11:-9]
    #print(strhour)
    imax=filename [-8:-5]
    # print (strhour)
    # print('imax',imax)
    # constitution de la liste des fichiers a charger
    PR = np.zeros((int(int(imax)/3)+1, 181, 360),dtype=complex)  # initialise le np array de complexes qui recoit les donnees
    iprev = []
    for a in range(0, int(imax)+3, 3):  # Construit le tuple des indexs des fichiers maxi 387
        iprev.append(str(int(a / 100)) + str(int((a % 100) / 10)) + str(a % 10))
    for indexprev in range(len(iprev)):  # recuperation des fichiers de 0 a 384 h
            prev = iprev[indexprev]
            url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t" + strhour + "z.pgrb2.1p00.f" + \
                  prev + "&lev_10_m_above_ground=on&all_var=on&leftlon=" \
                  + str(leftlon) + "&rightlon=" + str(rightlon) + "&toplat=" + str(toplat) + "&bottomlat=" + str(
                bottomlat) + "&dir=%2Fgfs." + date + "%2F" + strhour
       
            nom_fichier = "gribs/grib_" + date + "_" + strhour + "_" + prev   # nom sous lequel le fichier est sauvegarde provisoirement
            nom_fichier = os.path.join(basedir,nom_fichier)
            urlretrieve(url, nom_fichier)                               # recuperation des fichiers provisoires
            print(' Enregistrement prévision {}-{}-{} {} heures effectué: '.format(date,strhour,imax,prev))  # destine a suivre le chargement des previsions
            
             # exploitation du fichier et mise en memoire dans fichier provisoire PR
            ds = xr.open_dataset(nom_fichier, engine='cfgrib')
            PR[indexprev] = ds.variables['u10'].data + ds.variables['v10'].data * 1j
            os.remove(nom_fichier)  # On efface le fichier pour ne pas encombrer
            os.remove(nom_fichier + '.4cc40.idx')

    PR=np.concatenate((PR,PR[:,:,0:1]), axis=2)
    return PR

def chargement_fichier384(filename384):
    imax=filename384 [-8:-5]
    # print('Chargement_fichier384')
    # print('imax',imax)
    if imax=='384':
        # print('imax=384')
        # on verifie qu'il n'existe pas deja
        if os.path.exists(filename384) == False:
            # print('le fichier 384 n existe pas')
            year =int(filename384[-20:-16])
            # print('year',year)
            month=int(filename384[-16:-14])
            # print('month',month)
            
            day  =int(filename384[-14:-12])
            # print('day',day)
            date    =filename384[-20:-12]
            # print(date)
            strhour =filename384 [-11:-9]
            # print(strhour)
            dategrib=datetime(year , month , day , int(strhour),0, 0)

            tig=time.mktime(dategrib.timetuple())+decalage_h*3600    #temps initial du grib en sec locales 
            tig_formate    = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(tig)) #tig en secondes locales 
                        
            GR = np.zeros((129, 181, 360),dtype=complex)  # initialise le np array de complexes qui recoit les donnees
            iprev = []
            for a in range(0, 387, 3):  # Construit le tuple des indexs des fichiers maxi 387
                iprev.append(str(int(a / 100)) + str(int((a % 100) / 10)) + str(a % 10))
            for indexprev in range(len(iprev)):  # recuperation des fichiers de 0 a 384 h
                    prev = iprev[indexprev]
                    url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t" + strhour + "z.pgrb2.1p00.f" + \
                        prev + "&lev_10_m_above_ground=on&all_var=on&leftlon=" \
                        + str(leftlon) + "&rightlon=" + str(rightlon) + "&toplat=" + str(toplat) + "&bottomlat=" + str(
                        bottomlat) + "&dir=%2Fgfs." + date + "%2F" + strhour
            
                    nom_fichier = "gribs/grib_" + date + "_" + strhour + "_" + prev   # nom sous lequel le fichier est sauvegarde provisoirement
                    nom_fichier = os.path.join(basedir,nom_fichier)
                    urlretrieve(url, nom_fichier)                               # recuperation des fichiers provisoires
                    print(' Enregistrement prévision {}-{}-{} {} heures effectué: '.format(date,strhour,imax,prev))  # destine a suivre le chargement des previsions
                    
                    # exploitation du fichier et mise en memoire dans fichier provisoire PR
                    ds = xr.open_dataset(nom_fichier, engine='cfgrib')
                    GR[indexprev] = ds.variables['u10'].data + ds.variables['v10'].data * 1j
                    os.remove(nom_fichier)  # On efface le fichier pour ne pas encombrer
                    os.remove(nom_fichier + '.4cc40.idx')
                
            GR=np.concatenate((GR,GR[:,:,0:1]), axis=2)
            # sauvegarde
            f1 = h5py.File(filename384, "w")
            dset1 = f1.create_dataset("dataset_01", GR.shape, dtype='complex', data=GR)
            dset1.attrs['time_grib'] = tig  # transmet le temps initial du grib en temps local en s pour pouvoir faire les comparaisons
            f1.close()


        else :     # au cas ou le fichier existerai deja
            print ('le fichier existe deja ')
            tig,GR,filename384=chargement_hdf5(filename384)                    
    else :
        print("erreur: le fichier n'est pas un 384")    
    return tig,GR,filename


def chargement_old(filenameold):
    #ouverture du fichier hdf5
    f2 = h5py.File(filenameold, 'r')
    list(f2.keys())
    dset1 = f2['dataset_01']
    GR = dset1[:]
    tig = dset1.attrs['time_grib']
    f2.close()
    return tig,GR,filenameold
 


def chargement_grib():
    date_sec=tic
    filenameold,filename384,filename=nomfichiers() 

    if os.path.exists(filename384) == False:    #s'il n'existe pas on le charge completement
       tig,GR,filename384=chargement_fichier384(filename384)
    else :         
       tig,GR,filename384=chargement_hdf5(filename384)
    if filename!=filename384 :
        if os.path.exists(filename) == False:    #s'il n'existe pas on le charge completement
            PR=chargement_fichier_provisoire(filename)
            # il ne nous reste plus qu'a substituer dans le 384
            # on cherche l indice superieur
            imax=filename [-8:-5]
            # on substitue les indices 
            indicemax=int(int(imax)/3+3)
            GR[2:indicemax,:,:]=PR
            # et on le sauve
            f1 = h5py.File(filename, "w")
            dset1 = f1.create_dataset("dataset_01", GR.shape, dtype='complex', data=GR)
            dset1.attrs['time_grib'] = tig  # transmet le temps initial du grib en temps local en s pour pouvoir faire les comparaisons
            f1.close()

        else :         
            tig,GR,filename=chargement_hdf5(filename)

    return tig,GR,filename   





def prevision0(tig, GR, tp, latitude, longitude):

    #tp =tp-3600    # ajustement pour VR qui semble ne fonctionner qu'en UTC et ne pas tenir compte de l'heure locale
    #fn3 = RegularGridInterpolator((ix, iy, iz), GR)
    itemp = int((tp - tig) / 3600 / 3)
    ilati = int((latitude + 90))
    ilong = int((longitude) % 360)

    

    #print ('indices',itemp,ilati,ilong )

    #vcplx = fn3((itemp, ilati, ilong))
    #print('vcplx',vcplx)
    vit_vent_n = np.abs(vcplx) * 1.94384
    angle_vent = (270 - np.angle(vcplx, deg=True)) % 360
    return vit_vent_n, angle_vent



def prevision(tig, GR, tp, latitude, longitude):

   # tp =tp-3600    # ajustement pour VR qui semble ne fonctionner qu'en UTC et ne pas tenir compte de l'heure locale
    fn3 = RegularGridInterpolator((ix, iy, iz), GR)
    itemp = (tp - tig) / 3600 / 3
    ilati = (latitude + 90)
    ilong = (longitude) % 360

    #print ('indices',itemp,ilati,ilong )

    vcplx = fn3((itemp, ilati, ilong))
    #print('vcplx',vcplx)
    vit_vent_n = np.abs(vcplx) * 1.94384
    angle_vent = (270 - np.angle(vcplx, deg=True)) % 360
    return vit_vent_n, angle_vent

def previsionv2(tig, GR, tp, latitude, longitude):
    ''' calcul optimise 1/20eme du temps initial !! '''
    itemp = (tp - tig) / 3600 / 3
    ilati = (latitude + 90)
    ilong = (longitude) % 360
    iitemp=math.floor(itemp)
    iilati=math.floor(ilati)
    iilong=math.floor(ilong)
    ditemp=itemp%1
    dilati=ilati%1
    dilong=ilong%1
    v000=GR[iitemp][iilati][iilong]
    v010=GR[iitemp][iilati+1][iilong]
    v001=GR[iitemp][iilati][iilong+1]
    v011=GR[iitemp][iilati+1][iilong+1]
    v0x0=v000+dilati*(v010-v000)
    v0x1=v001+dilati*(v011-v001)
    v0xx=v0x0+dilong*(v0x1-v0x0)
    v100=GR[iitemp+1][iilati][iilong]
    v110=GR[iitemp+1][iilati+1][iilong]
    v101=GR[iitemp+1][iilati][iilong+1]
    v111=GR[iitemp+1][iilati+1][iilong+1]
    v1x0=v100+dilati*(v110-v100)
    v1x1=v101+dilati*(v111-v101)
    v1xx=v1x0+dilong*(v1x1-v1x0)
    vxxx=v0xx+ditemp*(v1xx-v0xx)   
    vit_vent_n = np.abs(vxxx) * 1.94384
    angle_vent = (270 - np.angle(vxxx, deg=True)) % 360
    
    return vit_vent_n, angle_vent





def prevision_tableau (tig,GR,tp,points):
    '''Le tableau des points est un tableau de points complexes'''
    '''retourne un tableau des previsions angles et vitesses '''
   
    #tp =tp-3600    # ajustement pour VR qui semble ne fonctionner qu'en UTC et ne pas tenir compte de l'heure locale
    fn3 = RegularGridInterpolator((ix, iy, iz), GR)
    itemp=np.ones( points.shape)*(tp - tig) / 3600 / 3
    #print('shape base',points.shape)
    #print ('itemp  base',itemp)
    ilati = np.imag(points) + 90
    #print('ilati base',ilati)
    ilong = np.real(points) %360
    e=np.concatenate((itemp.T,ilati.T,ilong.T ),axis=1)

    #print ('tableau e\n',e)

    # print ('e.shape)',e.shape)
    # print ('e',e)
    prevs = fn3((e))   #prevs est un tableau de complexes des vecteurs du vent aux differents points
    vitesse = np.abs(prevs) * 1.94384
    #print (vitesse)
    angle_vent = (270 - np.angle(prevs, deg=True)) % 360
    #print (angle_vent)

    return vitesse, angle_vent

def prevision_tableau3 (tig,GR,tp,pointsxy):
    '''Le tableau des points est un tableau de points np array x y'''
    '''retourne un tableau des previsions angles et vitesses '''
    #tp =tp-3600    # ajustement pour VR qui semble ne fonctionner qu'en UTC et ne pas tenir compte de l'heure locale
    fn3 = RegularGridInterpolator((ix, iy, iz), GR)

    itemp=np.ones( pointsxy.shape[0])*(tp - tig) / 3600 / 3
    #print ('itemp ',itemp)
    item =itemp.reshape((-1,1))

    ilati =  pointsxy.T[1] + 90
    #print('ilati',ilati)
    ilat= ilati.reshape((-1,1))

    ilong =  pointsxy.T[0]%360
    #print('ilong',ilong)



    ilon=ilong.reshape((-1,1))
    e=np.concatenate((item,ilat,ilon ),axis=1)
    #print(e)
    #print ('e.shape)',e.shape)
    #print ('e',e)
    prevs = fn3((e))   #prevs est un tableau de complexes des vecteurs du vent aux differents points
    vitesse = np.abs(prevs) * 1.94384
    #print (vitesse)
    angle_vent = (270 - np.angle(prevs, deg=True)) % 360
    #print (angle_vent)
    return vitesse, angle_vent
    #return None


def prevision_tableau2 (GR,temp,point):
    ''' calcule les previsions a partir d'une liste des temps par rapport au depart et des points sous forme complexe'''
    
    temps = temp.reshape((1, -1))    #-3600              # Ajustement VR 3600 
    points=point.reshape((1, -1))
    fn3 = RegularGridInterpolator((ix, iy, iz), GR)
    tab_itemp=temps.reshape((1,-1))/ 3600 / 3
    ilati = np.imag(points) + 90
    ilong = np.real(points) %360
    e = np.concatenate(( tab_itemp.T, ilati.T, ilong.T), axis=1)
    prevs = fn3((e))   #prevs est un tableau de complexes des vecteurs du vent aux differents points
    vitesse = np.abs(prevs) * 1.94384
    #print (vitesse)
    angle_vent = (270 - np.angle(prevs, deg=True)) % 360
    #print (angle_vent)

    return vitesse, angle_vent














if __name__ == '__main__':
    # print()
    # print('**uploadgrib3.py********************************************************************************************')
    # tic=time.time()                                    # temps instantane en secondes locales
    # # date et heure simulation chargement grib************************************
    # datejour            = datetime(2020,11,20, 11,6,0)                  # en heures locales
    # # *************************************************************************************
    # dateessai=datejour
    # dateessai_sec        = time.mktime(dateessai.timetuple())  
    dateessai_sec=tic           # transformation en secondes
    # dateessai_tuple      = time.gmtime(dateessai_sec)                      # transformation en tuple utc
    # # verification
    # dateessai_formate = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(dateessai_sec))
    # tic_formate    = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(tic))
    # dateessai_formatcourt=time.strftime("%Y%m%d", time.localtime(dateessai_sec))
    # dateessai_formatcourt_utc=time.strftime("%Y%m%d", time.gmtime(dateessai_sec))
    # datem1_utc=time.strftime("%Y%m%d", time.gmtime(dateessai_sec-86400))

    # tic_formatcourt=time.strftime("%Y%m%d", time.localtime(tic))
    # print ('Fichiers necessaires a la date du ',dateessai_formate)
    # # print(tic_formate)
    # # print('dateessaiformatcourt',dateessai_formatcourt)
    # print('dateessaiformatcourt_utc',dateessai_formatcourt_utc)
    # print('date moins un jour',datem1_utc)
    # # print(tic_formatcourt)
    # # print(dateessai_tuple)

  

    filenameold,filename384,filename=nomfichiers()
    # print()
    # print (filenameold)
    # print (filename384)
    # print (filename)
    # print()
    # #print( filename [-8:-5])

    tig,GR,filename=chargement_grib()
    
    # maintenant on fait des verifications
    # date et heure simulation de prevision meteo ********************************
    dateprev       =datetime(2020,11,25,22, 1,  0)
    dateprev_s=time.mktime(dateprev.timetuple()) # en secondes locales
    dateprev_formate_local = time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(dateprev_s))
    dateprev=tic
    print()
    #*****************************************************************************

    # latitude_d = '036-35-39-N'
    # longitude_d = '024-21-41-W'


    latitude='046-28-16-N'
    longitude='001-49-53-W'
    d = chaine_to_dec(latitude, longitude)  

    #print ('\nPrevisions avec Nouveau  grib') 
    tig,GR,filename=chargement_grib()
    #print('Fichier utilise', filename)
    # print(tig)
    # tig_formate    = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(tig))
    # print('tig formate',tig_formate)
    # print('tic formate',tic_formate)
    # print('ecart tic tig ',(tic-tig)/3600)
    vit_vent_n, angle_vent = prevision(tig, GR,dateessai_sec, d[1], d[0])
    
    print('Le{} heure Locale Pour latitude {:6.2f} et longitude{:6.2f} '.format(dateprev_formate_local, d[1], d[0]))
    print('\tAngle du vent   {:6.3f} °'.format(angle_vent))
    print('\tVitesse du vent {:6.3f} Noeuds'.format(vit_vent_n))


    print ('\nPrevisions avec grib 384 ') 
    tig,GR,filename384= chargement_fichier384(filename384)
    print('Fichier 384 utilise', filename384)
    vit_vent_n, angle_vent = prevision(tig, GR,dateessai_sec, d[1], d[0])
    print('Le{} heure Locale Pour latitude {:6.2f} et longitude{:6.2f} '.format(dateprev_formate_local, d[1], d[0]))
    print('\tAngle du vent   {:6.3f} °'.format(angle_vent))
    print('\tVitesse du vent {:6.3f} Noeuds'.format(vit_vent_n))

    # print ('\nPrevisions avec ancien modele de grib ') 
    # tig,GR,filenameold= chargement_old(filenameold)
    # print('Fichier old utilise', filenameold)
    # vit_vent_n, angle_vent = prevision(tig, GR,dateessai_sec, d[1], d[0])
    # print('Le{} heure Locale Pour latitude {:6.2f} et longitude{:6.2f} '.format(dateprev_formate_local, d[1], d[0]))
    # print('\tAngle du vent   {:6.3f} °'.format(angle_vent))
    # print('\tVitesse du vent {:6.3f} Noeuds'.format(vit_vent_n))
    # print('**********************************************************************************************')
    # print()


    