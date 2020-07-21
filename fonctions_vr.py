
import numpy as np
import math
import time
import datetime
import os
tic = time.time()
basedir = os.path.abspath(os.path.dirname(__file__))
# **************************************   Fonctions   ******************************************************************

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

def chaine_to_cplx(latitude, longitude):
    ''' Transforme les chaines latitude et longitude en un complexe  (x+iy) '''
    degre = int(latitude[0:2])
    minutes = int(latitude[3:5])
    secondes = int(latitude[6:8])
    lat = degre + minutes / 60 + secondes / 3600
    if latitude[9] == 'N':
        lat = -lat
    degre = int(longitude[0:2])
    minutes = int(longitude[3:5])
    secondes = int(longitude[6:8])
    long = degre + minutes / 60 + secondes / 3600
    if longitude[9] == 'W':
        long = -long
    position = long + lat * 1j

    return position


def cplx(d):
    ''' transforme un tuple en nparray complex'''
    D = (d[0] + d[1] * 1j)
    return D

def twa(cap, dvent):
    twa = 180 - abs(((360 - dvent + cap) % 360) - 180)
    return twa

def deplacement2(D, d_t, HDG, VT):
    '''D Depart point complexe ,d_t duree en s  , HDG tableau de caps en° ,vT Tableau de vitesses Polaires en Noeuds'''
    '''Fonctionne avec des np.array'''
    HDG_R = HDG * math.pi / 180
    A = D + (d_t / 3600 / 60 * VT * (np.sin(HDG_R) / math.cos(D.imag * math.pi / 180) - np.cos(HDG_R) * 1j))
    return A

def calcul_points(D, tp, d_t, TWD, vit_vent, ranged, polaires):
    '''tp temps au point D; d_t duree du deplacement en s ; angle du vent au point ; Vitesse du vent au point ; caps a simuler  ; polaires du bateau  '''
    '''retourne un tableau points sous forme de valeurs complexes'''
    points_arrivee = np.zeros((ranged.shape), dtype=complex)  # Init tableau   points d'arrivee sous forme complexe
    range_radian = (-ranged + 90) * math.pi / 180
    vit_noeuds = polaire2_vect(polaires, vit_vent, TWD, ranged)  # Vitesses suivant les differents caps
    points_arrivee = D + (d_t / 3600 / 60 * vit_noeuds * (
                np.cos(range_radian) / math.cos(D.imag * math.pi / 180) - np.sin(range_radian) * 1j))
    return points_arrivee, tp + d_t





def dist_cap(D, A):
    '''retourne la distance et l'angle du deplacement entre le depart et l'arrivee'''
    C = A - D
    return np.abs(C), (450 + np.angle(C, deg=True)) % 360


def rangenavi(capa, capb):
    if capb > capa:
        range = np.arange(capa, capb, 1)
    else:
        range = np.concatenate((np.arange(0, capb + 1, 1), np.arange(capa, 360, 1)), axis=0)
    return range


def range_cap(direction_objectif, direction_vent, a_vue_objectif, angle_pres, angle_var):
    # print ('direction_vent indice i',direction_vent)
    # print('direction_objectif indice i', direction_objectif)
    direction_vent, direction_objectif = int(direction_vent), int(direction_objectif)
    cap1 = (direction_vent + angle_pres) % 360
    cap2 = (direction_vent - angle_pres + 1) % 360
    cap3 = (180 + direction_vent + angle_var) % 360
    cap4 = (180 + direction_vent - angle_var + 1) % 360
    cap5 = (direction_objectif - a_vue_objectif) % 360

    cap6 = (direction_objectif + a_vue_objectif) % 360

    z1 = rangenavi(cap1, cap4)
    z2 = rangenavi(cap3, cap2)
    z3 = rangenavi(cap5, cap6)
    range1 = np.intersect1d(z1, z3)
    range2 = np.intersect1d(z2, z3)

    rangetotal = np.concatenate((range1, range2), axis=0)
    return rangetotal

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

    dategrib =datetime.datetime(utc[0] , utc[1] , utc[2] , int(heure_grib),0, 0)
    tig=time.mktime(dategrib.timetuple())+decalage_h*3600

    date= str(dategrib)
    filename="gribs/grib_gfs_" + date + ".hdf5"
    filenamehdf5 = os.path.join(basedir,filename)
    
    #time.time()- tig correspond bien à l'ecart de temps avec le grib
    return filenamehdf5,date,tig

