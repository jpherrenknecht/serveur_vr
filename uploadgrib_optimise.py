
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
import numba
from numba import jit
print(numba.__version__)

# les gribs complets sont disponibles en heure d'ete à
# 13h(gfs06) - 19(gfs12) -  01(gfs18) - 07 h (gfs00)
# les gribs complets sont disponibles en heure d'hiver à
# 12h(gfs06) - 18(gfs12) -  00(gfs18) - 06 h (gfs00)

# renvoie le chemin absolu du repertoire courant ici /home/jphe/PycharmProjects/VR_version2
basedir = os.path.abspath(os.path.dirname(__file__))


ix = np.arange(129)  # temps
iy = np.arange(181)  # latitudes
iz = np.arange(361)  # longitudes


def chainetemps_to_int(chainetemps):
    '''Convertit une chaine de temps en valeur entiere '''
    '''retourne egalement le temps en s ou le temps formate '''
    day = int(chainetemps[0:2])
    month = int(chainetemps[3:5])
    year = int(chainetemps[6:10])
    hour = int(chainetemps[11:13])
    mins = int(chainetemps[14:16])
    secs = int(chainetemps[17:19])
    strhour = chainetemps[11:13]
    date = chainetemps[6:10] + chainetemps[3:5] + chainetemps[0:2]

    #print('strhour : ',strhour)
    #print('date : ',date)

    t = time.localtime()
    utc = time.gmtime()
    decalage_s = (t[3] - utc[3]) * 3600
    t_s_local = time.mktime((year, month, day, hour +1, mins, secs, 0, 0, 0))
    t_s_utc = t_s_local - decalage_s
    #todo pourquoi le +1
    formate_local = time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(t_s_local))
    # t_s est un temps en secondes locales
    return t_s_local, day, month, year, hour, mins, secs, date, strhour, formate_local, t_s_utc


def chaine_to_dec(latitude, longitude):
    ''' Transforme les chaines latitude et longitude en un tuple (x,y) '''
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


def filename():
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


def ouverture_fichier(filename):
    # ouverture du fichier hdf5
    f2 = h5py.File(filename, 'r')
    list(f2.keys())
    dset1 = f2['dataset_01']
    GR = dset1[:]
    tig = dset1.attrs['time_grib']
    f2.close()
    return tig, GR




def chargement_grib():
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

    #print ('dategrib_tpl',dategrib_tpl)

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
            nom_fichier = "grib_" + date + "_" + strhour + "_" + prev
            urlretrieve(url, nom_fichier)  # recuperation des fichiers provisoires
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

    # ouverture du fichier hdf5
    f2 = h5py.File(filenamehdf5, 'r')
    list(f2.keys())
    dset1 = f2['dataset_01']
    GR = dset1[:]
    tig = dset1.attrs['time_grib']
    f2.close()
    return tig, GR



def prevision0(tig, GR, tp, latitude, longitude):
    #fn3 = RegularGridInterpolator((ix, iy, iz), GR)
    itemp = int((tp - tig) / 3600 / 3)
    ilati = int((latitude + 90))
    ilong = int((longitude) % 360)

    # print (GR(0,0,0))

    # print ('indices',itemp,ilati,ilong )

    #vcplx = fn3((itemp, ilati, ilong))
    #print('vcplx',vcplx)
    vit_vent_n = np.abs(vcplx) * 1.94384
    angle_vent = (270 - np.angle(vcplx, deg=True)) % 360
    return vit_vent_n, angle_vent



def prevision(tig, GR, tp, latitude, longitude):
    fn3 = RegularGridInterpolator((ix, iy, iz), GR)
    itemp = (tp - tig) / 3600 / 3
    ilati = (latitude + 90)
    ilong = (longitude) % 360

   # print ('indices',itemp,ilati,ilong )

    vcplx = fn3((itemp, ilati, ilong))
    #print('vcplx',vcplx)
    vit_vent_n = np.abs(vcplx) * 1.94384
    angle_vent = (270 - np.angle(vcplx, deg=True)) % 360
    return vit_vent_n, angle_vent






def prevision_tableau (tig,GR,tp,points):
    '''Le tableau des points est un tableau de points complexes'''
    '''retourne un tableau des previsions angles et vitesses '''
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

    #print ('e.shape)',e.shape)
    #print ('e',e)
    prevs = fn3((e))   #prevs est un tableau de complexes des vecteurs du vent aux differents points
    vitesse = np.abs(prevs) * 1.94384
    #print (vitesse)
    angle_vent = (270 - np.angle(prevs, deg=True)) % 360
    #print (angle_vent)
    return vitesse, angle_vent
    #return None


 # @jit(nopython=True) bloque sur regulargrid
def prevision_tableau3 (tig,GR,tp,pointsxy):
    '''Le tableau des points est un tableau de points np array x y'''
    '''retourne un tableau des previsions angles et vitesses '''
    fn3 = RegularGridInterpolator((ix, iy, iz), GR)
    itemp=np.ones( pointsxy.shape[0])*(tp - tig) / 3600 / 3
    item =itemp.reshape((-1,1))
    ilati =  pointsxy.T[1] + 90
    ilat= ilati.reshape((-1,1))
    ilong =  pointsxy.T[0]%360
    ilon=ilong.reshape((-1,1))
    e=np.concatenate((item,ilat,ilon ),axis=1)
    prevs = fn3((e))   #prevs est un tableau de complexes des vecteurs du vent aux differents points
    vitesse = np.abs(prevs) * 1.94384
    angle_vent = (270 - np.angle(prevs, deg=True)) % 360
    return vitesse, angle_vent
   

#@jit(nopython=True)
def prevision_tableau3v2 (tig,GR,tp,pointsxy):
    '''Le tableau des points est un tableau de points np array x y'''
    '''retourne un tableau des previsions angles et vitesses '''
    ''' ici on va utiliser l'interpolation 3d simple '''
    ''' cette variante n'est pas performante '''
    
  
    return TWS,TWD




def prevision_tableau2 (GR,temp,point):
    ''' calcule les previsions a partir d'une liste des temps par rapport au depart et des points sous forme complexe'''
    temps = temp.reshape((1, -1))
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
    
#@jit(nopython=True)
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

def previsionv3( tp, latitude, longitude):
    
    itemp = (tp - tig) / 3600 / 3
    ilati = (latitude + 90)
    ilong = (longitude) % 360
    iitemp=math.floor(itemp)
    iilati=np.floor(ilati)
    iilong=np.floor(ilong)
    ditemp=np.mod(itemp,1)
    dilati=np.mod(ilati,1)
    dilong=np.mod(ilong,1)
    print(latitude)
    print(type(latitude))

    for i in range (len(latitude)):
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




def polairev2(polaires, ws, twa):
    '''interpolation bilineaire en utilisant np.interp 
      20 fois plus rapide que avec interpn scipy '''
    i= np.where(tab_tws>ws)[0][0] 
    j= np.where(tab_twa>twa)[0][0] 
    twa_i= tab_twa[j-1]
    twa_s= tab_twa[j]
    xp=tab_tws
    yp=polaires[j-1]
    yp2=polaires[j]
    a=np.interp(ws, xp, yp)
    b=np.interp(ws, xp, yp2)
    c=a+(b-a)*(twa-twa_i)/(twa_s-twa_i)
    return c



if __name__ == '__main__':

    #chargement_grib()
    tig, GR = chargement_grib()
    tic = time.time()
    dateprev=datetime(2020 , 10 , 14, 20, 0,  0)
    dateprev_s=time.mktime(dateprev.timetuple())
    t=dateprev_s
    # print()
    # print ('tig en s ',tig)
    # print ('tic en s ',tic)
    # print ('Ecart', (tic-tig)/3600,'h')
    # tig_formate_utc = time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tig))
    # tic_formate_local = time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(tic))
    # print('\n Date et Heure UTC du dernier Grib             ',tig_formate_utc) 
    # print(' Date et Heure locales                         ',tic_formate_local) 
    # # Depart
    latitude_d = '045-30-00-N'
    longitude_d = '002-30-00-W'
    d = chaine_to_dec(latitude_d, longitude_d)  # co
    #print ('latitude et longitude',d)
# prevision avec date donnee   
    print ('\nPrévision à date et heure données \
            \n---------------------------------')
    print('Latitude {:6.2f}  Longitude{:6.2f} '.format( d[1], d[0]))
    print ('Dateprev : ',dateprev , ' local\n')
    # je peux la transformer en secondes mais ce sont des secondes locales
    #print ('dateprev_s en local ',dateprev_s )
    dateprev_formate_local = time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(dateprev_s))
    #print('dateprev_formate_local',dateprev_formate_local)



    pointsxy=np.array([[ -0.87032012 ,-49.83946699],
 [ -0.83248916, -49.90065455],
 [ -0.81971905, -49.93485451],
 [ -0.80529613, -49.96476786],
 [ -0.77772437, -50.00859442],
 [ -0.76334869, -50.03604005],
 [ -0.76003832, -50.04968596],
 [ -0.75118898, -50.06941713],
 [ -0.74052764, -50.09022992],
 [ -0.7295605 , -50.11107592],
 [ -0.72504033, -50.12439522],
 [ -0.72063924, -50.13725439],
 [ -0.71824288, -50.14777706],
 [ -0.71039723, -50.16325661],
 [ -0.71008435, -50.17083113],
 [ -0.71020694, -50.17844035],
 [ -0.70759944, -50.1880287 ],
 [ -0.70768772, -50.1948782 ],
 [ -0.70768096, -50.2022253 ],
 [ -0.70804851, -50.20841412],
 [ -0.70590563, -50.21715868],
 [ -0.70597731, -50.22393992],
 [ -0.70624721, -50.23006079],
 [ -0.70681008, -50.23618725],
 [ -0.70518631, -50.243162  ],
 [ -0.70528378, -50.24975783],
 [ -0.70554009, -50.25517325],
 [ -0.70644158, -50.26064464],
 [ -0.70604613, -50.267076  ],
 [ -0.70611491, -50.27244916],
 [ -0.70633142, -50.27837308],
 [ -0.70733614, -50.2830499 ],
 [ -0.7075494 , -50.2884744 ],
 [ -0.70776494, -50.29433635],
 [ -0.7082987 , -50.2990583 ],
 [ -0.70905039, -50.30433556],
 [ -0.70970965, -50.30887294],
 [ -0.71002979, -50.31436354],
 [ -0.71041761, -50.31949278],
 [ -0.71094686, -50.32416491],
 [ -0.7115069 , -50.3292087 ],
 [ -0.71190246, -50.33377651],
 [ -0.71280207, -50.33841153],
 [ -0.71382812, -50.34293253],
 [ -0.71471183, -50.34753102],
 [ -0.71604503, -50.35212742],
 [ -0.71716778, -50.35601651],
 [ -0.71860353, -50.36058848],
 [ -0.71994664, -50.36515324],
 [ -0.72123869, -50.36913942],
 [ -0.72268974, -50.37361455],
 [ -0.72293186, -50.37470017],
 [ -0.7245193 , -50.37840603],
 [ -0.7263222 , -50.38318843],
 [ -0.72741207, -50.3865141 ],
 [ -0.72914484, -50.39074602],
 [ -0.73122609, -50.394996  ],
 [ -0.73297276, -50.39900232],
 [ -0.73511672, -50.40331658],
 [ -0.73735935, -50.4071987 ],
 [ -0.73959063, -50.4111554 ],
 [ -0.74209549, -50.41550129],
 [ -0.74463996, -50.41944766],
 [ -0.74739124, -50.42389251],
 [ -0.7498036 , -50.42755324],
 [ -0.75273898, -50.43172602],
 [ -0.75596186, -50.43616129],
 [ -0.75917769, -50.44051694],
 [ -0.76194417, -50.44469763],
 [ -0.76507311, -50.44877253],
 [ -0.76821614, -50.45310967],
 [ -0.77154048, -50.45750565],
 [ -0.77536185 ,-50.46193292],
 [ -0.77905737, -50.46664669],
 [ -0.78288292, -50.47089079],
 [ -0.78686591, -50.47542027],
 [ -0.79150966, -50.4804406 ],
 [ -0.79621163, -50.48516346],
 [ -0.80040043, -50.48963482],
 [ -0.80543308, -50.49472186],
 [ -0.81046715, -50.49980643],
 [ -0.81559113, -50.50493143],
 [ -0.8213169 , -50.51021354],
 [ -0.82702156, -50.5154996 ],
 [ -0.83344769, -50.52090903],
 [ -0.83987051, -50.5265611 ],
 [ -0.84726651, -50.53261531],
 [ -0.8548527 , -50.53863006],
 [ -0.862152  , -50.54461419],
 [ -0.87092882, -50.55118747],
 [ -0.88001872, -50.55788096],
 [ -0.88976622, -50.56467174],
 [ -0.9007838 , -50.57219231],
 [ -0.91200173, -50.57985909],
 [ -0.92448579, -50.58794307],
 [ -0.93828419, -50.59624583],
 [ -0.95452518, -50.6055456 ],
 [ -0.97242131, -50.61547301],
 [ -0.99625365, -50.62684816],
 [ -1.03342155, -50.64129245],
 [ -1.07884553, -50.65847124]])







    # prevision proprement dite
    tic =time.time()
    for i in range (10000): 
        TWS,TWD=     prevision_tableau3 (tig,GR,t,pointsxy)
        
    tac=time.time()  
    print (TWS)
    print('temps d execution base' ,tac-tic,'s')

    tic =time.time()
    for i in range (10000): 
        TWS,TWD=     prevision_tableau3v2 (tig,GR,t,pointsxy)
    tac=time.time()  
    print (TWS)
    print('temps d execution variante' ,tac-tic,'s')

    tic =time.time()
    
    











#   #  print('\nLe {} heure Locale Pour latitude {:6.2f} et longitude{:6.2f} '.format(dateprev_formate_local, d[1], d[0]))
#     print('\tAngle du vent v1  {:6.1f} °'.format(angle_vent))
#     print('\tVitesse du vent v1{:6.3f} Noeuds'.format(vit_vent_n))
#     print()
# #  print('\nLe {} heure Locale Pour latitude {:6.2f} et longitude{:6.2f} '.format(dateprev_formate_local, d[1], d[0]))
#     print('\tAngle du vent v2  {:6.1f} °'.format(angle_vent2))
#     print('\tVitesse du vent  v2 {:6.3f} Noeuds'.format(vit_vent_n2))


#     print()


#     print('temps execution ',tac-tic,'s')



# # prevision avec temps instantane
#     print ("\nPrévision à l'instant de l'heure locale\
#             \n---------------------------------")
#     print()
#     print('Heure Locale ',tic_formate_local)
#     vit_vent_n, angle_vent = prevision(tig, GR,tic, d[1], d[0])
#   #  print('\nLe {} heure Locale Pour latitude {:6.2f} et longitude{:6.2f} '.format(dateprev_formate_local, d[1], d[0]))
#     print('\tAngle du vent   {:6.1f} °'.format(angle_vent))
#     print('\tVitesse du vent {:6.3f} Noeuds'.format(vit_vent_n))


# # prevision avec temps instantane
#     print ("\nPrévision corrigee proche VR\
#             \n---------------------------------")
#     print()
#     print('Heure Locale ',tic_formate_local)
#     ticvr=tic+6500
#     vit_vent_n, angle_vent = prevision(tig, GR,ticvr, d[1], d[0])
#   #  print('\nLe {} heure Locale Pour latitude {:6.2f} et longitude{:6.2f} '.format(dateprev_formate_local, d[1], d[0]))
#     print('\tAngle du vent   {:6.1f} °'.format(angle_vent))
#     print('\tVitesse du vent {:6.3f} Noeuds'.format(vit_vent_n))




    # #version tableau np complexe******************************************************************************

    # points=np.array([[-67-39*1j, -65-40*1j]])
    # points = np.array([[d[0] + d[1] * 1j]])
    # cplx = np.array([[-10 - 2 * 1j, -15 + 3 * 1j, 50 + 10 * 1j]])
    # prevs=prevision_tableau(tig, GR, tic, cplx)
    # print('\nresultat avec tableau',prevs)
    # print()

    # #version tableau np x y******************************************************************************

    # cplx=np.array([[-10 - 2 * 1j, -15 + 3 * 1j, 50 + 10 * 1j]])
    # points=np.concatenate((cplx.real.reshape(-1,1),cplx.imag.reshape(-1,1)),axis=1)
    # prevs3=prevision_tableau3(tig, GR, tic, points)
    # print('\nresultat avec tableau 3',prevs3)
    # print()

    # # print()
    # # print(prevs)







    # print ('\nVERSION AVEC DATE EN DUR------------------------------------ ')
    
    # for k in range (0,5,1):
    #     dateprev_s+=3600
    #     date_prev_formate = time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(dateprev_s))
    #     vit_vent_n, angle_vent = prevision(tig, GR, dateprev_s, d[1], d[0])
    #     print('\nLe {} heure UTC Pour latitude {:6.2f} et longitude{:6.2f} '.format(date_prev_formate, d[1], d[0]))
    #     print('\tAngle du vent   {:6.1f} °'.format(angle_vent))
    #     print('\tVitesse du vent {:6.3f} Noeuds'.format(vit_vent_n))
    
    #     print()