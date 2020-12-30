
import numpy as np
from scipy.interpolate import RegularGridInterpolator,interp2d,interpn
import math
import time
import datetime
import os
import json
from json import dumps
from json import JSONEncoder
import folium
tic = time.time()
basedir = os.path.abspath(os.path.dirname(__file__))
import numba
from numba import jit

# **************************************   Fonctions   ******************************************************************


def cabs(a):
    if a<0 :
       a=-a
    return a    


def twa(cap, dvent):
    twa = 180 - abs(((360 - dvent + cap) % 360) - 180)
    return twa    

def Twao( HDG,TWD):
    '''retourne un ndarray de twa orientees babord<0 tribord>0 à partir de ndarray HDG et TWD'''
    A=np.mod((HDG-TWD+360),360)
    return np.where(A<180,-A,360-A)

@jit(nopython=True)
def ftwaov2( HDG,TWD):
    '''retourne une twa orientee babord<0 tribord>0 à partir de ndarray '''
    ''' le temps est divise par 4 avec @jit'''
    A=np.mod((HDG-TWD+360),360)
    return np.where(A<180,-A,360-A)    


def test_virement(HDG,TWD,tribord_init):
    '''retourne un np array booleen True si virement , tribord_init = True or False
    HDG et  TWD np array  Nouveaux caps et Directions de vent
    Voir jupyter notebook pour explications'''
    Virement= np.where( np.where(np.mod((HDG-TWD+360),360)<180,False,True) ==tribord_init,False,True)
    return Virement


def chaine_to_dec(latitude, longitude):
    ''' Transforme les chaines latitude et longitude en un tuple (x,y) '''
    '''les latitudes nord et longitudes W  sont transformées en negatifs'''
    ''' retourne la longitude en premier'''
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
    '''les latitudes nord et longitudes W  sont transformées en negatifs'''
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
    ''' transforme un tuple (lng,lat) en nparray complex'''
    D = (d[0] + d[1] * 1j)
    return D



    
def deplacement21(D, d_t, HDG, VT):
    '''D Depart point complexe ,d_t duree en s  , HDG tableau de caps en° ,vT Tableau de vitesses Polaires en Noeuds'''
    '''Fonctionne avec des np.array, un pointy de depart  tableau de points en arrivee'''
    HDG_R = HDG * math.pi / 180
    A = D + (d_t / 3600 / 60 * VT * (np.sin(HDG_R) / math.cos(D.imag * math.pi / 180) - np.cos(HDG_R) * 1j))
    return A



def deplacement_x_y(x0,y0,d_t,HDG,VT):
    ''' fonction donnant le tuple point d arrivée en fonction des coordonnées du point de depart ''' 
    '''HDG et VT sont des np.array '''
    HDG_R = HDG * math.pi / 180     # cap en radians
    x= x0+ d_t / 3600 / 60 * VT * (np.sin(HDG_R) / math.cos(y0 * math.pi / 180)) 
    y= y0- d_t / 3600 / 60 * VT * np.cos(HDG_R)
    return x,y

@jit(nopython=True)
def deplacement_x_y_v2(x0,y0,d_t,HDG,VT):
    ''' fonction donnant le tuple point d arrivée en fonction des coordonnées du point de depart ''' 
    '''HDG et VT sont des np.array  acceleration 30% avec numba @jit'''
    HDG_R = HDG * math.pi / 180     # cap en radians
    x= x0+ d_t / 3600 / 60 * VT * (np.sin(HDG_R) / math.cos(y0 * math.pi / 180)) 
    y= y0- d_t / 3600 / 60 * VT * np.cos(HDG_R)
    return x,y





def deplacement_x_y_tab_ar(x0,y0,d_t,HDG,VT,A):
    ''' fonction donnant le tuple point d arrivée en fonction des coordonnées du point de depart ''' 
    ''' c'est cette fonction qui sert dans le calcul des isochrones '''
    ''' donne egalement le cap vers 'arrivee et la distance vers l'arrivee '''
    HDG_R = HDG * math.pi / 180     # cap en radians
    X= x0+ d_t / 3600 / 60 * VT * (np.sin(HDG_R) / math.cos(y0 * math.pi / 180)) 
    Y= y0- d_t / 3600 / 60 * VT * np.cos(HDG_R)
    Pointscpx=X+Y*1j
    Di,Ca=dist_cap(Pointscpx, A)

    return X,Y,Di,Ca

def deplacement_x_y_tab_ar_twa(x0,y0,d_t,HDG,VT,A,twa):
    ''' fonction donnant le tuple point d arrivée en fonction des coordonnées du point de depart ''' 
    ''' c'est cette fonction qui sert dans le calcul des isochrones '''
    ''' donne egalement le cap vers 'arrivee et la distance vers l'arrivee '''
    # integre une penalite si la nouvelle twa est de signe inverse de la nouvelle
    
    HDG_R = HDG * math.pi / 180     # cap en radians
    X= x0+ d_t / 3600 / 60 * VT * (np.sin(HDG_R) / math.cos(y0 * math.pi / 180)) 
    Y= y0- d_t / 3600 / 60 * VT * np.cos(HDG_R)
    Pointscpx=X+Y*1j
    Di,Ca=dist_cap(Pointscpx, A)

    return X,Y,Di,Ca

def deplacement_old (x0,y0,d_t,twa,tws,twd,HDG,A, penalite):
    ''' Fonction globale calculant le deplacement avec penalite sur l'ensemble du np.array de caps HDG
        twa est la twa orientee pour arriver au point 
        tws et twd ont deja ete calcules pour ce point'''
    VT  = polaire2_vect(polaires, tws,twd, HDG)  # ensemble des vitesses polaires
    TWAO=Twao(HDG,twd )                          # Ensemble des twa orientées
                                                 # tableau des penalites    
    HDG_R = HDG * math.pi / 180                  # caps en radians
    X= x0+ d_t / 3600 / 60 * VT * (np.sin(HDG_R) / math.cos(y0 * math.pi / 180)) 
    Y= y0- d_t / 3600 / 60 * VT * np.cos(HDG_R)
    Pointscpx=X+Y*1j
    Di,Ca=dist_cap(Pointscpx, A)
    return X,Y,Di,Ca,TWAO


def deplacement(x0,y0,d_t,HDG,TWD,VT,A,twa,penalite):
    ''' fonction donnant le tuple point d arrivée en fonction des coordonnées du point de depart ''' 
    ''' c'est cette fonction qui sert dans le calcul des isochrones '''
    ''' donne egalement le cap vers 'arrivee et la distance vers l'arrivee '''
    # integre une penalite si la nouvelle twa est de signe inverse de la nouvelle
   
    TWAO=Twao( HDG,TWD)
    Virement=np.where(TWAO*twa>0,False,True)
    #TWA=np.abs(TWAO)
    #print(TWAO)
    #VT=polaire2_vect(HDG,TWD)
    #print (VT)
    #print (Virement)
    DT=np.ones(len(VT))*d_t-Virement*penalite
    #print(DT)
    HDG_R = HDG * math.pi / 180     # cap en radians
    X= x0+ DT / 3600 / 60 * VT * (np.sin(HDG_R) / math.cos(y0 * math.pi / 180)) 
    Y= y0- DT / 3600 / 60 * VT * np.cos(HDG_R)
    Pointscpx=X+Y*1j
    Di,Ca=dist_cap(Pointscpx, A)

    return X,Y,Di,Ca

#@jit(nopython=True)
def deplacement2(x0,y0,d_t,HDG,TWD,VT,A,twa,penalite):
    ''' fonction donnant le tuple point d arrivée en fonction des coordonnées du point de depart ''' 
    ''' c'est cette fonction qui sert dans le calcul des isochrones '''
    ''' ameliore deplacement de 30% '''
    # integre une penalite si la nouvelle twa est de signe inverse de la nouvelle
    if penalite !=0 :   
        TWAO=ftwaov2( HDG,TWD)
        Virement=np.where(TWAO*twa>0,False,True)
        # s'il y a virement on est penalise de la duree en secondes donc pour dt =600 s on est penalise de 100s si penalite =100
        # avec winchs pros 50% pendant 75 s =32 s
        DT=np.ones(len(VT))*d_t-Virement*penalite
        HDG_R = HDG * math.pi / 180     # cap en radians
        X= x0+ DT / 3600 / 60 * VT * (np.sin(HDG_R) / math.cos(y0 * math.pi / 180)) 
        Y= y0- DT / 3600 / 60 * VT * np.cos(HDG_R)
    else :
        HDG_R = HDG * math.pi / 180     # cap en radians
        X= x0+ d_t / 3600 / 60 * VT * (np.sin(HDG_R) / math.cos(y0 * math.pi / 180)) 
        Y= y0- d_t / 3600 / 60 * VT * np.cos(HDG_R)

    Di,Ca=dist_cap(X+Y*1j, A)
    return X,Y,Di,Ca




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
    ''' cette fonction ne tient pas compte de l'effet latitude'''
    C = A - D
    return np.abs(C), (450 + np.angle(C, deg=True)) % 360
    


def dist_cap2(x0,y0,x1,y1):
    '''retourne la distance et l'angle du deplacement entre le depart et l'arrivee
    en tenant compte de la courbure et du racourcissement des distances sur l'axe x'''
    coslat= math.cos(y0 * math.pi / 180)
    C=(x-x0)*coslat +(y-y0)*1j
    return np.abs(C), (450 + np.angle(C, deg=True)) % 360


def dist_cap3(D,A):
    ''' retourne la distance et l'angle du deplacement entre le depart et l'arrivee 
    les points de depart et arrivee sont sous forme complexe'''
    coslat= np.cos(D.imag * math.pi / 180)
    C=(A.real-D.real)*coslat +(A.imag-D.imag)*1j
    return np.abs(C), (450 + np.angle(C, deg=True)) % 360


def dist_cap4(points,A):
    ''' ppoints est une  liste de points a 2 dimensions , a est un point complexe '''
    ''' on retourne un tableau des distances et des caps '''
    #print(points.shape)
    D=points[0]+points[1]*1j   # on transforme les points en points complexes
    C = A - D
    return np.abs(C), (450 + np.angle(C, deg=True)) % 360

#@jit(nopython=True)
def rangenavi(capa, capb):
    '''@jit ralentit la fonction'''

    if capb > capa:
        range = np.arange(capa, capb, 1)
    else:
        range = np.concatenate((np.arange(0, capb + 1, 1), np.arange(capa, 360, 1)), axis=0)
    return range


def range_cap(direction_objectif, direction_vent, a_vue_objectif, angle_pres, angle_var):
    # print ('direction_vent indice i',direction_vent)
    # print('direction_objectif indice i', direction_objectif)
    '''pas d'acceleration avec @jit '''
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

# barriere=np.array([[-56.0, -180.0], [-56.4167, -175.0], [-56.25, -170.0], [-55.6667, -165.0], [-54.75, -160.0], [-53.9167, -155.0],
#                      [-53.6667, -150.0], [-53.6667, -140.0], [-53.6667, -145.0], [-53.6667, -135.0], [-53.9167, -130.0], [-54.0833, -125.0], 
#                      [-54.25, -120.0], [-54.6667, -115.0], [-55.25, -110.0], [-55.75, -105.0], [-56.25, -100.0], [-57.0, -95.0], [-57.75, -90.0],
#                      [-58.5, -85.0], [-59.0, -80.0], [-58.75, -75.0], [-58.0, -70.0], [-57.0, -65.0], [-56.0, -60.0], [-55.0, -55.0], [-50.0, -50.0], 
#                      [-47.5, -45.0], [-46.0, -40.0], [-44.5, -35.0], [-44.0, -30.0], [-43.5, -25.0], [-43.5, -20.0], [-43.5, -15.0], [-44.0, -10.0], 
#                      [-44.5, -5.0], [-44.5, 0.0],
#                      [-44.6667, 5.0], [-44.8333, 10.0], [-45.0, 15.0], [-45.1667, 20.0], [-45.25, 25.0], [-45.3333, 30.0],
#                      [-44.3333, 35.0], [-43.500, 40.0], [-42.66667, 45.0], [-42.6667, 50.0],  [-44.5000, 55.0], [-48.667, 60.0], [-50.5833, 65.0],                    
#                      [-50.9167, 70.0], [-50.9167, 75.0], [-50.6667, 80.0],[-50.4167, 85.0],[-50.0, 90.0], [-49.0, 95.0], [-47.75, 100.0],
#                      [-46.0, 105.0], [-46.0, 110.0], [-46.0, 115.0], [-46.0, 120.0], [-50.75, 130.0], [-51.9167, 135.0], [-52.25, 140.0],
#                      [-52.4167, 145.0], [-52.75, 150.0], [-53.25, 155.0], [-53.8333, 160.0], [-54.25, 165.0],[-54.8333, 170.0], [-55.4167, 175.0], [-56.0, 180.0]])


      





course="440.1"
fichier='static/js/courses.json'

with open(fichier, 'r') as fichier:                      # change dans fichier courants
    data2 = json.load(fichier)
    barriere= np.array(data2[course]['barriere'])    #extraction de la barriere et transformation en np.array
    



def inbarriere(lat,lng):
    a=np.where(barriere[:,1]>=lng)[0][0]
    b=np.where(barriere[:,1]<=lng)[0][-1]
    lat1=barriere[a][0]
    lat2=barriere[b][0]
    lng1=barriere[a][1]
    lng2=barriere[b][1]
    latbarriere=lat1+(lng-lng1)/(lng2-lng1)*(lat2-lat1)
    if (lat-latbarriere>0):
        lin=False
    else :
        lin=True
    return lin





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

def trace_points_folium (points_cpx):
#on extrait les coordonnes pour tracer
    X=points_cpx.real.reshape(-1,1)
    Y=points_cpx.imag.reshape(-1,1)
    points=np.concatenate((-Y,X),axis=1)
    for point in points :
        folium.CircleMarker(point,color='black', radius=1,fill_color='black',fill_opacity=0.3).add_to(carte)

    return None

def polaire2_vectv2(polaires,tab_twa, tab_tws,vit_vent,angle_vent,tableau_caps):
    '''il n'y a qu'une vitesse et un angle mais plusieurs caps '''
    ''' 20% plus performant que la fonction de base'''
    #transformation tableau de caps en un point en tableau de donnees (twa , vit_vent)
    l=len(tableau_caps)
    twax = 180 - np.abs(((360 - angle_vent + tableau_caps) % 360) - 180)  # broadcasting
    twa  = twax.reshape(-1,1)
    vvent = (np.ones(l)*vit_vent).reshape(-1,1)
    donnees= np.concatenate((twa,vvent), axis = 1) 
    valeurs = interpn((tab_twa, tab_tws), polaires, donnees, method='linear')
    return valeurs



def polaire3_vect(polaires,tab_twa, tab_tws,TWS,TWD,HDG):
    '''Retourne un tableau de polaires en fonction des polaires bateau  de TWS TWD et HDG'''
    '''TWS true Wind speed, TWD true wind direction , HDG caps'''
    '''Les trois tableaux doivent avoir la meme dimension'''
    TWA=(180 - np.abs(((360 - TWD + HDG) % 360) - 180)).reshape((-1, 1))
    TWS2=TWS.reshape((-1, 1))
    donnees=np.concatenate((TWA,TWS2),axis=1)
    valeurs = interpn((tab_twa, tab_tws), polaires, donnees, method='linear')
    return valeurs

# def polaire2_vect(polaires,tws,twd,HDG):
#     '''ici un seul point avec une seule tws twd
#      mais plusieurs caps'''
#     # on ajuste les tableaux TW et TWD à HDG
#     l=len(HDG)
#     TWD = (np.ones(l)*twd)
#     TWA = (180 - np.abs(((360 - TWD + HDG) % 360) - 180)).reshape((-1, 1))
#     TWS = (np.ones(l) * tws).reshape((-1, 1))
#     donnees = np.concatenate((TWA, TWS), axis=1)
#     valeurs = interpn((y1, x1), polaires, donnees, method='linear')
#     return valeurs




if __name__ == '__main__':
    
    #print ('course',course)test de polaires
    course="440.1"
    fichier='static/js/courses.json'
    #extraitbarriere (fichier,course)


    # test extraction fichier json
    with open('static/js/courses.json', 'r') as fichier:    # ce fichier est dans les fichiers static
        data1 = json.load(fichier)  
        bateau=  (data1[course]["bateau"])

    with open('static/js/polars.json', 'r') as fichier:   # ce fichier est dans les fichiers static
        data2 = json.load(fichier)
        angle_twa_pres=data2[bateau]["pres_mini"]
        angle_twa_ar= data2[bateau]["var_mini"]
        l1=data2[bateau]["tab_tws"]
        l2=data2[bateau]["tab_twa"]
        polaires=data2[bateau]["polaires"]

    
    tab_tws=l1
    tab_twa=l2
    vit_vent=15
    angle_vent=0
    tableau_caps=np.array([45,60,90,120])   # en fait ce sont les tests sur des twa
    vitesses_test=polaire2_vectv2(polaires,tab_twa, tab_tws,vit_vent,angle_vent,tableau_caps)
    print()
    print('test de polaires sur twa 45 60 90 120 et vent 15 noeuds',vitesses_test)
    print()
#    #test de rangenavi
#    # 
#     capa=30
#     capb=50
#     angle_twa_pres = 36
#     angle_twa_ar = 20
   
#     angle_pres = 36
#     angle_var = 20
#     direction_objectif=130
#     direction_vent=80
#     a_vue_objectif=180



#     tic = time.time()
#     for i in range (10000):
#         res=range_cap(direction_objectif, direction_vent, a_vue_objectif, angle_pres, angle_var)

#     tac=time.time()  

#     print()
#     print (res)
#     print('temps execution base en secondes',tac-tic)
#     print()
    
  


    # #test de deplacement

    # HDG = np.array( [ 0,1,2,3,4,5])

    # VT =  np.array( [2.94700956 ,2.89013849, 2.83244379 ,2.77321923, 2.71399466 ,2.6547701 ])
    # TWD=  np.array( [300 ,305, 315 ,80, 27.5 ,2.65 ])
    # d_t=600
    # x0,y0=-73.62,-40.46
    # twa=30
    # penalite=0
    # # Point Arrivee 
    # latitude_a     = '049-30-00-N'
    # longitude_a    = '005-06-00-W'
    # ar = chaine_to_dec(latitude_a, longitude_a)
    # A = cplx(ar)


    # tic = time.time()
    # for i in range (100000):

    #     #res=deplacement_x_y_v2(x0,y0,d_t,HDG,VT)
    #     res=deplacement(x0,y0,d_t,HDG,TWD,VT,A,twa,penalite)
    # tac=time.time()   
    # print('temps execution base en secondes',tac-tic)
    # print (res[0])
    # print (res[1])

    # tic = time.time()
    # for i in range (100000):
    #     res=deplacement2(x0,y0,d_t,HDG,TWD,VT,A,twa,penalite)
    #     # #res=deplacement_x_y_v2(x0,y0,d_t,HDG,VT)
    #     # if penalite !=0 :
    #     #     res=deplacement2(x0,y0,d_t,HDG,TWD,VT,A,twa,penalite)
    #     # else :
    #     #     res=deplacement_x_y_v2(x0,y0,d_t,HDG,VT)

    #     Di,Ca=dist_cap(res[0]+res[1]*1j, A)

    # tac=time.time()   
    # print('temps execution variante en secondes',tac-tic)
    # print (res[0])
    # print (res[1])



    # tic = time.time()
    # for i in range (100000):
    #     res=deplacement_x_y_v2(x0,y0,d_t,HDG,VT)
    #     Di,Ca=dist_cap(res[0]+res[1]*1j, A)


    # tac=time.time()   
    # print('\ntemps execution solution simple',tac-tic)
    # print (res[0])
    # print (res[1])
    # print ()


    


# #    print ('Test')
#     import numpy as np
#         # test de distance et cap tableau de complexes pour les point de de part et complexe pour l'arrivee

#     #Depart
#     latitude_d     = '047-39-09-N'
#     longitude_d    = '003-53-09-W'
#     #Point Arrivee 
#     latitude_a     = '049-30-00-N'
#     longitude_a    = '005-06-00-W'




#     d  = chaine_to_dec(latitude_d, longitude_d)  # conversion des latitudes et longitudes en tuple
#     ar = chaine_to_dec(latitude_a, longitude_a)
#     ar=d
#     d=(-73.62,-40.46)
#     print(d)
#     D = cplx(d)  # transformation des tuples des points en complexes
#     A = cplx(ar)
#     print ('Arrivee',A)

#     HDG = np.array( [ 0,1,2,3,4,5])
#     VT =  np.array( [2.94700956 ,2.89013849, 2.83244379 ,2.77321923, 2.71399466 ,2.6547701 ])

#     a=np.array([[2+5*1j,3+4*1j,7+8*1j]])
#     delta_temps=600
#     i=0
#     n_pts_x = deplacement2(a[0][i], delta_temps, HDG, VT)
#     print('base')
#     print ('HDG : ',HDG )
#     print('resultat n _pts_x',n_pts_x)


# # meme chose avec un tableau de points
#     print()
#     print('Variante')
#     points=np.concatenate((a.real.reshape(-1,1),a.imag.reshape(-1,1)),axis=1).tolist()
#     print('points',points)
#     d_t=600
#     i=0
#     X,Y,Da,Ca=deplacement_x_y_tab_ar(points[i][0],points[i][1],d_t,HDG,VT,A)

#     print('x depart',points[i][0])
#     print('y depart',points[i][i])
#     print('X',X)
#     print('Y',Y)
#     print('Da',Da)
#     print('Ca',Ca)

#     X.reshape(-1,1)
#     Y.reshape(-1,1)


#     print()

#         # # test deplacement_x_y
#     # res=range_cap( 291,3,90,40,20)
#     # print (res)
#     # res=range_cap( 291,359,90,40,20)
#     # print (res)


#     # x0=-5.811
#     # y0=-46.0594
#     # d_t=300
#     # HDG=254.9
#     # VT=6.87


#     # deplacement_x_y(x0,y0, d_t, HDG, VT)
#     # print()
#     # print (x,y)
#     # print()