
import os
import time
from datetime import timedelta
import math
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
import json
import folium
import webbrowser
from uploadgrib import *
from fonctions_vr import *

val='polaires.polaires_figaro2'
exec('from '+val+ ' import *')

from global_land_mask import globe
import pickle
from flask import Flask, redirect, url_for,render_template, request , session , flash
from flask_sqlalchemy import SQLAlchemy

tic=time.time()









from flask import Flask, redirect, url_for,render_template, request , session , flash
from flask_sqlalchemy import SQLAlchemy
#from frouteur import frouteur


app = Flask(__name__)
app.secret_key="Hello"
app.permanent_session_lifetime = timedelta(days=1)     # minutes=10

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
db = SQLAlchemy(app)

tic=time.time()



class user(db.Model):                                              # creation du modele de base de donnée
    id     = db.Column(db.Integer, primary_key=True)
    nom    = db.Column(db.String(100))
    prenom = db.Column(db.String(100))





def f_isochrone(l, temps_initial_iso):
    ''' Calcule le nouvel isochrone a partir d'un tableau de points pt2cplx tableau numpy de cplx'''
    ''' deltatemps, tig , U, V sont supposees etre des variables globales'''
    ''' Retourne les nouveaux points el le nouveau temps et implemente le tableau general des isochrones'''
    global isochrone,TWS,TWD
    points=(isochrone[-l:,0:2])
    numero_iso           = int(isochrone[-1][2] + 1)
    delta_temps          = intervalles[numero_iso]  # Ecart de temps entre anciens points et nouveaux en s
    nouveau_temps        = temps_initial_iso + delta_temps
    t_iso_formate        = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(temps_initial_iso + delta_temps))
    numero_dernier_point = int(isochrone[-1][4])                   # dernier point isochrone precedent
    numero_premier_point = int(isochrone[-1][4]) - points.shape[0]   # premier point isochrone precedent
    but                  = False 
    # on recupere toutes les previsions meteo d'un coup pour l'ensemble des points de depart
    # TWS, TWD = prevision_tableau3(tig, GR, temps_initial_iso, points)
    points_calcul2=np.array([[0,0,0,0,0,0,0]]) # initialisation pour Numpy du brouillard des points calcules
# pour chacun des points de l'isochrone 
    for i in range(points.shape[0]):
        HDG = range_cap(dist_cap4(points[i], A)[1], TWD[i], angle_objectif, angle_twa_pres, angle_twa_ar)  # Calcul des caps a etudier
        VT  = polaire2_vect(polaires, TWS[i], TWD[i], HDG)                                                  # Vitesses polaires sur ces caps
        X1,Y1,Da1,Ca1=deplacement_x_y_tab_ar(points[i][0],points[i][1],delta_temps,HDG,VT,A) #Coordonnees des nouveaux points calcules sous forme X,Y
        L=len(X1)                                                                            # nombre de ( caps ) points etudies  
        niso1     = np.ones(L)*numero_iso                                                         # numero isochrone
        npointsm1 = np.ones(L)*i  +numero_premier_point +1    # numero du point mere i = 0 correspond au premier point de l'isochrone precedent
        npoints1  = np.array(range(L)) +1                      # numero du point  sans importance sera renumeroté
        X         = X1.reshape(-1,1)
        Y         = Y1.reshape(-1,1)
        niso      = niso1.reshape(-1,1)
        npointsm  = npointsm1.reshape(-1,1)
        npoints   = npoints1.reshape(-1,1)
        Da        = Da1.reshape(-1,1)
        Ca        = Ca1.reshape(-1,1)
        # maintenant on forme le tableau correspondant à n_pts_x
        n_pts_x2       = np.concatenate((X,Y,niso,npointsm,npoints,Da,Ca), axis = 1)    # tableau des points pour un point de base
        points_calcul2 = np.concatenate((points_calcul2,n_pts_x2), axis         = 0)           # tableau du brouillard pour tous les points de base 
#Version Numpy    
    points_calcul2 = np.delete(points_calcul2,0,0)                                    # on retire le premier terme de points_calcul2
    points_calcul2 = points_calcul2[points_calcul2[: ,6].argsort(kind = 'mergesort')]   # tri stable sur 6eme colonne (caps vers arrivee)
    k=0                                                                             # on regroupe les  caps 359 et 1
    while (((points_calcul2[k][6]-points_calcul2[k-1][6])<-330)and (k<points_calcul2.shape[0]-1)):
        points_calcul2[k][6]+=360
        k+=1
    points_calcul2= points_calcul2[points_calcul2[:,6].argsort(kind='mergesort')]   # les caps en 361 sont replaces a la fin 
    capmini2 = points_calcul2[0][6]
    capmaxi2 = points_calcul2[-1][6]
    coeff2   = 49/ (capmaxi2-capmini2)  # coefficient pour ecremer et garder 50 points
#ecremage arrondi et tri
    points_calcul2[:,6]=np.around(points_calcul2[:,6]*coeff2,0)                   # La colonne 6 est arrondie  
    points_calcul2     = points_calcul2[points_calcul2[:,5].argsort(kind='mergesort')] # On trie sur les distances 
    points_calcul2     = points_calcul2[points_calcul2[:,6].argsort(kind='mergesort')] # On trie sur les caps mais l'ordre des distances est respecté
# ecremage proprement dit
    for i in range(points_calcul2.shape[0] - 1, 0, -1):  # ecremage
        if (points_calcul2[i][6]) == (points_calcul2[i - 1][6]):
            points_calcul2 = np.delete(points_calcul2, i, 0)
    longueur= points_calcul2.shape[0] 
# verification points terre ou mer
    for i in range(points_calcul2.shape[0] - 1, 0, -1):  # ecremage 
        is_on_land = globe.is_land(-points_calcul2[i][1], points_calcul2[i][0])   # point de latitude -y et longitude x
        if (is_on_land==True):
            points_calcul2 = np.delete(points_calcul2, i, 0)
    points_calcul2[:,6]= np.floor(points_calcul2[:,6]/coeff2)       # on retablit le cap en valeur a rechanger en around 0 decimale
    points_calcul2     = points_calcul2[points_calcul2[:,6].argsort(kind='mergesort')] #on trie sur les caps a voir si necessaire !
# renumerotation sur la colonne 4  le premier numero est le numero dernier point iso precedent +1  
    N=np.array( range( int(numero_dernier_point) + 1, points_calcul2.shape[0] +int(numero_dernier_point) + 1,1))  # tableau des indices
    points_calcul2[:,4]=N     # renumerotation
    TWS, TWD =prevision_tableau3(tig, GR, nouveau_temps, points_calcul2) # Vitesse vent et direction pour nouveaux points (extraction en double)
# on minore TWS à  2 pour règle VR
    TWS[TWS <2] = 2
    VT = polaire3_vect(polaires, TWS, TWD, points_calcul2[:,6])
# calcul des temps vers l arrivee
    D_a       = points_calcul2[: ,5]               # Distances vers l'arrivee
    T_a       = 60 * D_a / (VT + 0.000001)        # Temps vers l'arrivée nb ce temps est en heures
    temps_mini=(T_a[np.argmin(T_a,0)])      # Valeur du temps minimum
# Verification si le but est atteignable dans le temps d'un isochrone    
    if temps_mini < delta_temps / 3600:
            but = True
    indice2= np.argmin(T_a,0)  + numero_dernier_point + 1     #indice du point de temps minimum
#    ptn_np2=points_calcul2[:, 0:2]   #(X,Y)# Constitution du tableau des points retournes en sortie    
    lf=points_calcul2.shape[0]
# Ajout des points calcules au tableau global des isochrones
    isochrone = np.concatenate((isochrone, points_calcul2[:,0:5]))  # On rajoute ces points a la fin du tableau isochrone 
# Utilisation pour trace folium  
    #trace_iso2=np.concatenate((-points_calcul2[:,1].reshape(-1,1),points_calcul2[:,0].reshape(-1,1)),axis=1)  #(-Y,X)
    print(' Isochrone  N° {}  {}  {} points capmini {:6.2f} capmaxi {:6.2f} coeff {:6.2f} '.format(numero_iso, t_iso_formate,longueur,capmini2,capmaxi2,coeff2  ))
    return lf, nouveau_temps, but, indice2
# ************************************   Fin de la fonction       **********************************************************




def fonction_routeur(xn,yn,x1,y1,t0=time.time()):
    '''x0,y0,x1,y1 depart et arrivee '''
    ''' Le but de la fonction frouteur est a partir de x0 y0 x1 y1 
    de retourner une multipolyline des isochrones'''
    global isochrone,intervalles,TWS,TWD,tig,GR,angle_objectif,temps_mini,A
# Definition des variables pour le routage
    tig, GR        = chargement_grib()
    A= x1+y1*1j                         # Arrivee sous forme complexe
    pt1_np=np.array([[xn,yn]])          # isochrone de depart (1 point)
    l=pt1_np.shape[0]                   # longueur de l'isochrone de depart (1)
    temps=t0                            # Definition du temps à l'isochrone de depart par defaut time.time()
    angle_objectif = 90                 # amplitude des angle balayes vers l'objectif 
    temps_mini = 0                      # temps entre le dernier isochrone et l'objectif 
# definition des temps des isochrones
    dt1           = np.ones(72) * 600  # intervalles de temps toutes les 10mn pendant une heure puis toutes les heures
    dt2           = np.ones(370) * 3600
    intervalles   = np.concatenate(([t0 - tig], dt1, dt2))
    temps_cumules = np.cumsum(intervalles)
    but = False
    isochrone = np.array([[x0, y0, 0, 0, 0]])# on initialise le tableau isochrone et TWS TWD
    TWS, TWD = prevision_tableau3(tig, GR, t0, pt1_np)  
    print ('(137  premier TWS',TWS) 
# on imprime les donnees de depart    
    print()
    print('Depart :      Latitude {:6.4f}     \tLongitude {:6.4f}'.format(y0, x0))
    print('Arrivee:      Latitude {:6.4f}     \tLongitude {:6.4f}'.format(y1, x1))
    tig_formate_utc = time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tig))
    tic_formate_local = time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(tic))
    print('Heure UTC du dernier Grib             ',tig_formate_utc)
    print('Heure Locale de depart de la prevision',tic_formate_local)
    print ('Ecart en heures ( = ecart - ecartUTC ) ', (tic-tig)/3600)
    print() 
# on calcule tous les isochrones
    while but == False:
        l,temps, but, indice = f_isochrone(l,temps) 
# Reconstitution de la route a emprunter  indice  est l'indice de temps minimum du dernier point 
    a = int(indice)                 # indice du point de la route la plus courte
    n = int(isochrone[-1][2])       # nombre d'isochrones
    dico=dict(zip(isochrone[:,4],isochrone[:,3]))   #dictionnaire des points et points meres
    route = [a]
    for i in range(n):
        a = int(dico[a])
        route.append(a)  # route contient les indices successifs des points a emprunter a l'envers
    route.reverse()
    chemin = np.zeros(len(route) + 1, dtype=complex)  # on initialise le np array de complexes qui va recevoir les donnees
    i = 0
    for n in (route):
        chemin[i] = isochrone[n][0] + isochrone[n][1] * 1j
        i += 1
    chemin[i] = A
    # maintenant on reconstitue le chemin avec les caps les TWA et les previsions
    l = len(chemin)
    temps_cum = temps_cumules[:l]
    temps_cum[-1] = temps_cum[-2] + temps_mini * 3600  # le dernier terme est le temps entre le dernier isochrone et l'arrive
    TWS_ch, TWD_ch = prevision_tableau2(GR, temps_cum, chemin)# previsions meteo aux differents points pour reconstitution 
    distance, cap1 = dist_cap3(chemin[0:-1], chemin[1:])    # distance et angle de chaque point au suivant
    #dist = np.append(distance, [0])                         # on rajoute un 0 pour la distance arrivee et l angle arrivee
    HDG_ch = np.append(cap1, [0])                           # tableau des caps aux differents points
    TWA_ch = twa(HDG_ch, TWD_ch)                            # calculs twa sous forme de tableau pour les differents points
    POL_ch = polaire3_vect(polaires, TWS_ch, TWD_ch, HDG_ch)# calcul des polaires aux differents points du chemin
    temps_cum += tig
    # mise en forme pour concatener
    chx =       chemin.real.reshape((1, -1))
    chy =       chemin.imag.reshape((1, -1))
    temps_pts = temps_cum.reshape((1, -1))
    vitesse =   TWS_ch.reshape((1, -1))
    TWD =       TWD_ch.reshape((1, -1))
    cap =       HDG_ch.reshape((1, -1))
    twat =       TWA_ch.reshape((1, -1))
    pol =       POL_ch.reshape((1, -1))
    # tabchemin : x,y,vit vent ,TWD,cap vers point suivant twa vers point suivant
    chem = np.concatenate((chx.T, chy.T, temps_pts.T, vitesse.T, TWD.T, cap.T, twat.T, pol.T), axis=1)
# confection de la route à suivre avec les tooltips
    route3=[]
    comment=[]
    for i in range (0,len(chem),1):
        temps=time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(chem[i, 2]))
        # heures=str(((chem[i, 2])- t0)//3600)
        # long=str(-round(chem[i, 0], 2))
        # lat=str(-round(chem[i, 1], 2))
        # tws = str(round(chem[i, 3], 1))
        # twd = str(round(chem[i, 4], 0))
        cap = str(round(chem[i, 5], 0))
        # twaroute = str(round(chem[i, 6], 0))
        # Vt  = str(round(chem[i, 7], 2))
        route3.append([-chem[i, 1],chem[i, 0]])   # dans la version leaflet on a le temps en trois
        comment.append([-chem[i, 1],chem[i, 0],chem[i, 2],chem[i, 3],chem[i, 4],chem[i, 5],chem[i, 6],chem[i, 7]])
    #Confection de la multipolyline pour le trace des isochrones 
    X=isochrone[:,0].reshape(-1,1)
    Y=isochrone[:,1].reshape(-1,1)
    N=isochrone[:,2].reshape(-1,1)
    points=np.concatenate((-Y,X,N),1)
    polyline=np.split(points[:,0:2],np.where(np.diff(points[1:,2])==1)[0]+2)
    
    multipolyline=[arr.tolist() for arr in polyline]
    del multipolyline[0][0]
    return multipolyline,route3,comment
























##partie serveur web


@app.route('/')
def index():
  return render_template('index.html')



@app.route('/map2')
def map2():
  return render_template("map2.html")

@app.route('/leafletbase')
def leafletbase():
  return render_template("leafletbase.html")




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
    resultat1 = request.form                                  # dictionnaire avec les resultats de la requete
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
    return render_template("resultat3.html", polyline=fonction_routeur(x0,y0,x1,y1), result=request.form)



@app.route('/leaflet',methods = ["GET", "POST"])
def leaflet():
    global x0,y0,x1,y1
    latitude_d     = '049-54-17-N'
    longitude_d    = '006-46-01-W' 
    x0,y0=chaine_to_dec(latitude_d, longitude_d)  # conversion des latitudes et longitudes en tuple
    
    #Point Arrivee 
    latitude_a     = '051-21-00-N'
    longitude_a    = '009-39-00-W'
    t0=time.time() 
    x1,y1=chaine_to_dec(latitude_a, longitude_a)
# on tient compte des valeurs retournees par get
    latdep        = float(request.args['latdep'])
    lngdep        = float(request.args['lngdep'])
    x0=lngdep
    y0=-latdep
    lngar=x1
    latar=-y1
    
    print ('latar',latar)
    print ('lngar',latar)



    multipolyline,route,comment=fonction_routeur(lngdep,latdep,x1,y1)
    #print ('route',route)

    red=[]
    black=[]

    print (multipolyline[0:1])

    for i in range(len(multipolyline)):
        if (i+1)%6==0:
                black.append(multipolyline[i])
        else:
                red.append(multipolyline[i])  
    return render_template("leaflet.html", multipolyred=red,multipolyblack=black,route=route,comment=comment,lngdep=lngdep,latdep=latdep,lngar=lngar,latar=latar, result=request.form)





@app.route('/windleaf',methods =["GET", "POST"])
def windleaf():
    global x0,y0,x1,y1
    latitude_d     = '044-23-12-N'
    longitude_d    = '008-55-00-E' 
    x0,y0=chaine_to_dec(latitude_d, longitude_d)  # conversion des latitudes et longitudes en tuple
    
    #Point Arrivee 
     #Point Arrivee 
    latitude_a     = '043-01-00-N'
    longitude_a    = '009-24-00-E'

# Extraction de donnees du fichier json
     # Extraction de donnees du fichier json
    with open('courses.json', 'r') as fichier:
        data = json.load(fichier)
    n_course='463'
    bateau=(data[n_course]["bateau"])
    print('\nBateau : ',bateau)
    fichier_polaires='polaires.'+(data[n_course]["polaires"])

    latdep = (data[n_course]["courant"]["lat"])
    lngdep = (data[n_course]["courant"]["lng"])
    latar  = (data[n_course]["bouee3"]["lat"])
    lngar  = (data[n_course]["bouee3"]["lng"])
    x0,y0=chaine_to_dec(latdep, lngdep)  # conversion des latitudes et longitudes en tuple
    x1,y1=chaine_to_dec(latar, lngar)
    print ('x0,y0',x0,y0)
    print ('x1,y1',x1,y1)
    latar=y1
    lngar=x1

    t0=time.time() 

 
# on tient compte des valeurs retournees par get
    latdep        = -float(request.args['latdep'])
    lngdep        = float(request.args['lngdep'])
    x0=lngdep
    y0=latdep


# #Depart force les 3 lignes seront à supprimer
#     latitude_d     = '043-17-12-N'
#     longitude_d    = '010-07-49-E'
#     x0,y0=chaine_to_dec(latitude_d, longitude_d)  # conversion des latitudes et longitudes en tuple
    
#     latdep=-y0
#     lngdep=x0
#     lngar=x1
#     latar=-y1
    
  
    multipolyline,route,comment=fonction_routeur(lngdep,latdep,x1,y1)
   
    # print ( '\n(295)(main) multipolyline[0]\n',multipolyline[0])
    # print ('\n             multipolyline[1]\n',multipolyline[1])
    
    # print ('\npoint0\n',route[0])
    # print ('point1\n',route[1])


    #print ( '\nmultipolyline[0]\n',multipolyline[0])
    #print ('\nmultipolyline[1]\n',multipolyline[1])
    red=[]
    black=[]
    for i in range(len(multipolyline)):
        if (i+1)%6==0:
                black.append(multipolyline[i])
        else:
                red.append(multipolyline[i]) 

    return render_template("windleaf.html", multipolyred=red,multipolyblack=black,route=route,comment=comment,lngdep=lngdep,latdep=latdep,lngar=lngar,latar=latar, result=request.form)


    









if __name__ == "__main__" :
    db.create_all()                 #creation de la base de donnees
    app.debug=True
    app.config['JSON_AS_ASCII']=False
    app.run(host='127.0.0.1', port=8080, debug=True)
