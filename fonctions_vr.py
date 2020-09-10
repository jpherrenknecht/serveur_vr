
import numpy as np
import math
import time
import datetime
import os
import folium
tic = time.time()
basedir = os.path.abspath(os.path.dirname(__file__))
# **************************************   Fonctions   ******************************************************************

def TWAO( HDG,TWD):
    '''retourne un ndarray de twa orientees babord<0 tribord>0 à partir de ndarray HDG et TWD'''
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


def twa(cap, dvent):
    twa = 180 - abs(((360 - dvent + cap) % 360) - 180)
    return twa
    
def deplacement2(D, d_t, HDG, VT):
    '''D Depart point complexe ,d_t duree en s  , HDG tableau de caps en° ,vT Tableau de vitesses Polaires en Noeuds'''
    '''Fonctionne avec des np.array, un pointy de depart  tableau de points en arrivee'''
    HDG_R = HDG * math.pi / 180
    A = D + (d_t / 3600 / 60 * VT * (np.sin(HDG_R) / math.cos(D.imag * math.pi / 180) - np.cos(HDG_R) * 1j))
    return A

def deplacement_x_y(x0,y0,d_t,HDG,VT):
    ''' fonction donnant le tuple point d arrivée en fonction des coordonnées du point de depart ''' 
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

def trace_points_folium (points_cpx):
#on extrait les coordonnes pour tracer
    X=points_cpx.real.reshape(-1,1)
    Y=points_cpx.imag.reshape(-1,1)
    points=np.concatenate((-Y,X),axis=1)
    for point in points :
        folium.CircleMarker(point,color='black', radius=1,fill_color='black',fill_opacity=0.3).add_to(carte)

    return None

if __name__ == '__main__':
#    print ('Test')
    import numpy as np
        # test de distance et cap tableau de complexes pour les point de de part et complexe pour l'arrivee

    #Depart
    latitude_d     = '047-39-09-N'
    longitude_d    = '003-53-09-W'
    #Point Arrivee 
    latitude_a     = '049-30-00-N'
    longitude_a    = '005-06-00-W'




    d  = chaine_to_dec(latitude_d, longitude_d)  # conversion des latitudes et longitudes en tuple
    ar = chaine_to_dec(latitude_a, longitude_a)
    ar=d
    d=(-73.62,-40.46)
    print(d)
    D = cplx(d)  # transformation des tuples des points en complexes
    A = cplx(ar)
    print ('Arrivee',A)

    HDG = np.array( [ 0,1,2,3,4,5])
    VT =  np.array( [2.94700956 ,2.89013849, 2.83244379 ,2.77321923, 2.71399466 ,2.6547701 ])

    a=np.array([[2+5*1j,3+4*1j,7+8*1j]])
    delta_temps=600
    i=0
    n_pts_x = deplacement2(a[0][i], delta_temps, HDG, VT)
    print('base')
    print ('HDG : ',HDG )
    print('resultat n _pts_x',n_pts_x)


# meme chose avec un tableau de points
    print()
    print('Variante')
    points=np.concatenate((a.real.reshape(-1,1),a.imag.reshape(-1,1)),axis=1).tolist()
    print('points',points)
    d_t=600
    i=0
    X,Y,Da,Ca=deplacement_x_y_tab_ar(points[i][0],points[i][1],d_t,HDG,VT,A)

    print('x depart',points[i][0])
    print('y depart',points[i][i])
    print('X',X)
    print('Y',Y)
    print('Da',Da)
    print('Ca',Ca)

    X.reshape(-1,1)
    Y.reshape(-1,1)


        # # test deplacement_x_y
    # res=range_cap( 291,3,90,40,20)
    # print (res)
    # res=range_cap( 291,359,90,40,20)
    # print (res)


    # x0=-5.811
    # y0=-46.0594
    # d_t=300
    # HDG=254.9
    # VT=6.87


    # deplacement_x_y(x0,y0, d_t, HDG, VT)
    # print()
    # print (x,y)
    # print()