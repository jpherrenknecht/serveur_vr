
import os
import time
from datetime import timedelta
import math
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
import folium
import webbrowser
from uploadgrib import *
from fonctions_vr import *
import webbrowser
from polaires.polaires_ultime import *
from operator import itemgetter
from global_land_mask import globe
import pickle
from frouteur import *
#from shapely.geometry import Point,Polygon
#from shapely import speedups

from flask import Flask, redirect, url_for,render_template, request , session , flash
from flask_sqlalchemy import SQLAlchemy
#from frouteur import frouteur


app = Flask(__name__)
app.secret_key="Hello"
app.permanent_session_lifetime = timedelta(days=1)     # minutes=10

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
db = SQLAlchemy(app)

tig,GR = chargement_grib2()
angle_objectif = 90
dico = {}
indice = 0
t_v_ar_h = 0
nouveau_temps = 0
tic = time.time()
dt1           = np.ones(72) * 600  # intervalles de temps toutes les 10mn pendant une heure puis toutes les heures
dt2           = np.ones(370) * 3600
intervalles   = np.concatenate(([tic - tig], dt1, dt2))
temps_cumules = np.cumsum(intervalles)


(filenamehdf5,dategrib,tig )= filename()
# Depart ou position actuelle 
latitude_d = '040-38-42-N'
longitude_d = '073-25-36-W'

#todo Arrivee cap Lizard
latitude_a = '040-00-00-N'
longitude_a = '070-20-00-W'
d  = chaine_to_dec(latitude_d, longitude_d)  # conversion des latitudes et longitudes en tuple
ar = chaine_to_dec(latitude_a, longitude_a)

D = cplx(d)  # transformation des tuples des points en complexes
A = cplx(ar)

x0,y0=d    
x1,y1=ar

 
# Initialisation du tableau des points d'isochrones
# 0: x du point (longitude), 1: y du point (latitude) , 2: N° isochrone , 3: N° du pt mere ,
# 4: N° du pt , 5: Distance a l'arrivee , 6: Cap vers l'arrivee
isochrone     = [[D.real, D.imag, 0, 0, 0, dist_cap(D, A)[0], dist_cap(D, A)[1]]]


def f_isochrone(pt_init_cplx, temps_initial_iso):
    ''' Calcule le nouvel isochrone a partir d'un tableau de points pt2cplx tableau numpy de cplx'''
    ''' deltatemps, tig , U, V sont supposees etre des variables globales'''
    ''' Retourne les nouveaux points el le nouveau temps et implemente le tableau general des isochrones'''

    global isochrone, intervalles, t_v_ar_h,dico

    numero_iso           = int(isochrone[-1][2] + 1)
    delta_temps          = intervalles[numero_iso]  # Ecart de temps entre anciens points et nouveaux en s
    nouveau_temps = temps_initial_iso + delta_temps
    t_iso_formate        = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(temps_initial_iso + delta_temps))
    numero_dernier_point = (isochrone[-1][4])  # dernier point isochrone precedent
    numero_premier_point = isochrone[-1][4] - pt_init_cplx.size
   
    but                  = False
    points_calcul        = []
    caps_x               = []
    tab_t                = []  # tableau des temps vers l arrivee en ligne directe
    trace_iso            = []  # tableau de tuples
    trace_iso2           = []   # tableau de listes
    trace_iso_cap        = []
  
    
    # on recupere toutes les previsions meteo d'un coup pour l'ensemble des points de depart
    TWS, TWD = prevision_tableau(tig, GR, temps_initial_iso, pt_init_cplx)


    # pour chaque point de l'isochrone precedent  donnés en entrée (isochrone précédent)
    for i in range(pt_init_cplx.size):
       
        HDG = range_cap(dist_cap(pt_init_cplx[0][i], A)[1], TWD[i], angle_objectif, angle_twa_pres, angle_twa_ar)  # Calcul des caps a etudier
        VT = polaire2_vect(polaires, TWS[i], TWD[i], HDG)
        n_pts_x = deplacement2(pt_init_cplx[0][i], delta_temps, HDG, VT)   #coordonnees des nouveaux points calcules
      
        for j in range(len(n_pts_x)):                     # pour chaque point initial i on a j points finaux 
            cap_arrivee = dist_cap(A,n_pts_x[j])[1]
            distance_arrivee = dist_cap(n_pts_x[j], A)[0]
            points_calcul.append(
            [n_pts_x[j].real, n_pts_x[j].imag, numero_iso, numero_premier_point+i+1 , 1, distance_arrivee,cap_arrivee])

    #tri de la liste de tous les  points obtenus
        points_calcul=sorted(points_calcul,key=lambda colonnes :colonnes[6])
   


        k=0
        while (points_calcul[k][6]-points_calcul[k-1][6])<-357 :
            #print(' i', i, ' ', points_calcul[i][6])    
            points_calcul[k][6]+=360
            k+=1
        points_calcul=sorted(points_calcul,key=lambda colonnes :colonnes[6])
        capmini=points_calcul[0][6]
        capmaxi=points_calcul[-1][6]
    
    
    coeff2 = 49/ (capmaxi-capmini)  # coefficient pour ecremer et garder 50 points
   
    for j in range(len(points_calcul)):  # partie ecremage
        points_calcul[j][6] = int(coeff2 * points_calcul[j][6])
    pointsx = sorted(points_calcul, key=itemgetter(6, 5))  # tri de la liste de points suivant la direction (indice  " \
    pointsx = np.asarray(pointsx)

    for i in range(len(pointsx) - 1, 0, -1):  # ecremage
        if (pointsx[i][6]) == (pointsx[i - 1][6]):
            pointsx = np.delete(pointsx, i, 0)

    longueur=len(pointsx)
   
    # verification points terre ou mer
    for i in range(len(pointsx)-1, -1, -1):  # ecremage proprement dit 
        is_on_land = globe.is_land(-pointsx[i][1], pointsx[i][0])
        if (is_on_land==True):
            pointsx = np.delete(pointsx, i, 0)

    # on peut restituer les caps initiaux et retrier par cap
    for i in range(len(pointsx)):
         pointsx[i][6] = int(pointsx[i][6] / coeff2)  # on retablit le cap en valeur
    
    # maintenant on trie comme un np.array
    pointsx= pointsx[pointsx[:,6].argsort(kind='mergesort')]

    for i in range(len(pointsx)):  # renumerotation
        pointsx[i][4] = i + numero_dernier_point + 1
        dico[pointsx[i][4]] = pointsx[i][3]
        trace_iso.append((-pointsx[i][1], pointsx[i][0]))
        trace_iso_cap.append((-pointsx[i][1], pointsx[i][0],pointsx[i][6]))
        trace_iso2.append([-pointsx[i][1], pointsx[i][0]])

        # on cherche les temps vers l'arrivee des nouveaux points
        vit_vent, TWD = prevision(tig, GR, nouveau_temps, pointsx[i][1], pointsx[i][0])
        twa = 180 - abs(((360 - TWD + pointsx[i][6]) % 360) - 180)

        resultat = polaire(polaires, vit_vent, twa)
        d_a = pointsx[i][5]
        t_a = 60 * d_a / (resultat + 0.000001)  # nb ce temps est en heures
        tab_t.append(t_a)
        # print('temps',t_a)
        if t_a < delta_temps / 3600:
            but = True
    
    # indice du temps minimum
    indice = tab_t.index(min(tab_t)) + numero_dernier_point + 1
    t_v_ar_h = min(tab_t)
    isochrone = np.concatenate((isochrone, pointsx))  # On rajoute ces points a la fin du tableau isochrone
    ptn_cplx = np.array([pointsx[:, 0] + pointsx[:, 1] * 1j])  # on reforme un tableau numpy de complexes pour la sortie
    print(' Isochrone calculé N° {}  {}  {} points cap mini  {:4.2f}  cap maxi {:4.2f}  '.format(numero_iso, t_iso_formate,longueur,capmini ,  capmaxi  ))

    return ptn_cplx, nouveau_temps, but, indice,trace_iso2




class user(db.Model):                                              # creation du modele de base de donnée
    id     = db.Column(db.Integer, primary_key=True)
    nom    = db.Column(db.String(100))
    prenom = db.Column(db.String(100))


#Depart : Latitude -43.6450  Longitude -59.4267
#Arrivee: Latitude -49.25  Longitude -5.17

latar=49.25
longar=-5.16666666

#partie fonction python
def polylinetest():
  polyline=[[[49,2],[48,2.53],[47.5,2.2],[46.5,1.1]],  [[50,-2],[48,1.5],[47.5,1.9],[46.5,-1.52]]]
  #time.sleep(10)
  return polyline


def frouteur(x0,y0,x1,y1,t0=time.time()):

    '''d et ar depart et arrivee sous forme de tupple ,
     tig instant initial du grib , GR valeurs du grib 
     tic instant de depart de la prevision par defaut instant actuel'''
    trace_total=[]
    but = False
    D=x0+y0*1j
    A=x1+y1*1j
   
    # on initialise l'isochrone de depart avec le depart et le temps au depart
    pt1_cpx = np.array([[D]])
    temps=t0
    i=0
    while but == False:
        pt1_cpx, temps, but, indice,trace_iso2 = f_isochrone(pt1_cpx, temps)  
        trace_total.append(trace_iso2)  
    # trace iso 

    return trace_total



##partie serveur web


@app.route('/')
def index():
  return render_template('index.html')



@app.route('/map2')
def map2():
  return render_template("map2.html")



@app.route('/resultat',methods = ['POST'])
def resultat():
  resultat1 = request.form                                    # dictionnaire avec les resultats de la requete
                                                              # resultat = request.args dans le cas d'une requete 'GET'
  latdep                 = resultat1['lat']
  longdep                = resultat1['long']
  #frouteur (latdep,longdep,latar,longar) 
  return render_template("resultat.html", total=add(latdep,longdep) , result=request.form)



@app.route('/resultat2',methods = ['POST'])
def resultat2():
  resultat1 = request.form                                    # dictionnaire avec les resultats de la requete
                                                              # resultat = request.args dans le cas d'une requete 'GET'
  latdep                 = resultat1['lat']
  longdep                = resultat1['lng']
  #frouteur (latdep,longdep,latar,longar)
 
  return render_template("resultat2.html", total=add(latdep,longdep) , result=request.form)


@app.route('/resultat3',methods = ['POST'])
def resultat3():  
  result = request.form                                    # dictionnaire avec les resultats de la requete
                                                             # resultat = request.args dans le cas d'une requete 'GET'
  latdep                 = float(result['latdep'])
  lngdep                 = float(result['lngdep'])
  #polyline=test()
  
  return render_template("resultat3.html", result=request.form)


@app.route('/leaflet',methods = ['POST'])
def leaflet():  
  result = request.form                                    # dictionnaire avec les resultats de la requete
                                                             # resultat = request.args dans le cas d'une requete 'GET'
  latdep                 = float(result['latdep'])
  lngdep                 = float(result['lngdep'])
  #polyline=test()
  
  return render_template("leaflet.html",  result=request.form)





@app.route('/numpyhtml')
def numpy():  
  return render_template("numpyhtml.html",polyline=polylinetest())











if __name__ == "__main__" :
    db.create_all()                 #creation de la base de donnees
    app.debug=True
    app.run(host='127.0.0.1', port=8080, debug=True)