
import os
import time
from datetime import timedelta
import math
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
import json
from json import dumps
from json import JSONEncoder

import folium
import webbrowser
from uploadgrib import *
from fonctions_vr import *

val='polaires.polaires_imoca'
exec('from '+val+ ' import *')

from global_land_mask import globe
import pickle
from flask import Flask, redirect, url_for,render_template, request , session , flash , jsonify
from flask_sqlalchemy import SQLAlchemy

tic=time.time()


from flask import Flask, redirect, url_for,render_template, request , session , flash
from flask_sqlalchemy import SQLAlchemy
#from frouteur import frouteur


app = Flask(__name__)
app.secret_key="Hello"
app.permanent_session_lifetime = timedelta(days=1)     
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
db = SQLAlchemy(app)

tic=time.time()
tig, GR        = chargement_grib()


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

# pour chargement du grib pour le js  a automatiser en fonction de la lat et lng
tig, GR = chargement_grib()
latini=-50      # latitude la plus au nord en premier et latitude nord negative
latfin=-40
longini=350
longfin=360


def vents_encode(latini,latfin,longini,longfin):
    ''' extrait du grib GR les donnees entre ini et fin sur 24 h et l'exporte en json'''
    ilatini=90+latini    # les latitudes Nord doivent être négatives

    ilatfin=90+latfin
    print ()
    U10=GR[0:8,ilatini:ilatfin,longini:longfin].real
    V10=GR[0:8,ilatini:ilatfin,longini:longfin].imag
    numpyData = {"latini":latini,"latfin":latfin,"longini":longini,"longfin":longfin,"u10": U10,"v10":V10}
    a=json.dumps(numpyData, cls=NumpyArrayEncoder)
    #b=jsonify(numpyData)
    return a 



def vents_encode2(latini,latfin,longini,longfin):
    ''' extrait du grib GR les donnees entre ini et fin sur 24 h et l'exporte en json'''
    ilatini=90+latini    # les latitudes Nord doivent être négatives

    ilatfin=90+latfin
    U10=GR[0:8,ilatini:ilatfin,longini:longfin].real
    V10=GR[0:8,ilatini:ilatfin,longini:longfin].imag
     
    u10=[arr.tolist() for arr in U10]
    v10=[arr.tolist() for arr in V10]
    return u10,v10




class user(db.Model):                                              # creation du modele de base de donnée
    id     = db.Column(db.Integer, primary_key=True)
    nom    = db.Column(db.String(100))
    prenom = db.Column(db.String(100))





def f_isochrone2(l2, temps_initial_iso):

    ''' Calcule le nouvel isochrone a partir d'un tableau de points pt2cplx tableau numpy de cplx'''
    ''' deltatemps, tig , U, V sont supposees etre des variables globales'''
    ''' Retourne les nouveaux points el le nouveau temps et implemente le tableau general des isochrones'''
    ''' isochrone 2 comprend une colonne de plus avec la twa en dernier '''
    global isochrone2,TWS2,TWD2,temps_mini2
    numero_iso2           = int(isochrone2[-1][2] + 1)
    print()
    print(' Isochrone Variante N° {} '.format(numero_iso2 ))
    points=isochrone[-l2:,0:2]

#variante 
    points2=isochrone2[-l2:,0:2]  # ici on selectionne -l lignes en partant du bas et les colonnes 0 1 6
    twa2= isochrone2[-l2:,5]      # ici on recupere l'ensemble des twa de l'isochrone precedent

 

#variante
    numero_iso2           = int(isochrone2[-1][2] + 1)
    delta_temps          = intervalles[numero_iso2]  # Ecart de temps entre anciens points et nouveaux en s (inchangé)
    nouveau_temps        = temps_initial_iso + delta_temps     #(inchangé)
    t_iso_formate        = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(temps_initial_iso + delta_temps))
    numero_dernier_point2 = int(isochrone2[-1][4])                   # dernier point isochrone precedent
    numero_premier_point2 = int(isochrone2[-1][4]) - l2               # premier point isochrone precedent
    but2                  = False 
    # on recupere toutes les previsions meteo d'un coup pour l'ensemble des points de depart
    # TWS, TWD = prevision_tableau3(tig, GR, temps_initial_iso, points)
    points_calcul2=np.array([[0,0,0,0,0,0,0]]) # initialisation pour Numpy du brouillard des points calcules (inchangé)




    TWS2, TWD2 =prevision_tableau3(tig, GR, nouveau_temps, points2) # Vitesse vent et direction pour nouveaux points (extraction en double)
# pour chacun des points de l'isochrone 
    if numero_iso2==1:
        penalite=0
    else:    
        penalite=10
    
    for i in range(l2):
       # twa precedente
        twap=twa2[i]
        
        # Calcul des caps a etudier pour chaque point (INCHANGÉ)
        HDG2 = range_cap(dist_cap4(points2[i], A)[1], TWD2[i], angle_objectif, angle_twa_pres, angle_twa_ar)         
        VT2  =polaire2_vect(polaires, TWS2[i], TWD2[i], HDG2)  #Vitesse polaire pour chaque cap
        #Deplacement tenant compte de la penalite
        X12,Y12,Da12,Ca12=deplacement(points2[i][0],points2[i][1],delta_temps,HDG2,TWD2[i],VT2,A,twap,penalite)
        
        L2=len(X12)                                                                            # nombre de ( caps ) points etudies  (INCHANGÉ)
        niso12     = np.ones(L2)*numero_iso2                                                         # numero isochrone(INCHANGÉ)
        npointsm12 = np.ones(L2)*i  +numero_premier_point2 +1    # numero du point mere i = 0 correspond au premier point de l'isochrone precedent(INCHANGÉ)
        npoints12  = np.array(range(L2)) +1                      # numero du point  sans importance sera renumeroté
        X2        = X12.reshape(-1,1)
        Y2         = Y12.reshape(-1,1)
        niso2      = niso12.reshape(-1,1)
        npointsm2  = npointsm12.reshape(-1,1)
        npoints2   = npoints12.reshape(-1,1)
        Da2        = Da12.reshape(-1,1)
        Ca2        = Ca12.reshape(-1,1)
        # maintenant on forme le tableau correspondant à n_pts_x
        n_pts_x22       = np.concatenate((X2,Y2,niso2,npointsm2,npoints2,Da2,Ca2), axis = 1)    # tableau des points pour un point de base
        points_calcul2 = np.concatenate((points_calcul2,n_pts_x22), axis         = 0)           # tableau du brouillard pour tous les points de base 

    points_calcul2 = np.delete(points_calcul2,0,0)                                    # on retire le premier terme de points_calcul
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
    for i in range(points_calcul2.shape[0] - 1, -1, -1):  # ecremage
        if (points_calcul2[i][6]) == (points_calcul2[i - 1][6]):
            points_calcul2 = np.delete(points_calcul2, i, 0)
    longueur2= points_calcul2.shape[0] 
# verification points terre ou mer
    for i in range(points_calcul2.shape[0]- 1, -1, -1):  # ecremage 
        is_on_land = globe.is_land(-points_calcul2[i][1], points_calcul2[i][0])   # point de latitude -y et longitude x
        if (is_on_land==True):
            points_calcul2 = np.delete(points_calcul2, i, 0)
    points_calcul2[:,6]= np.floor(points_calcul2[:,6]/coeff2)       # on retablit le cap en valeur a rechanger en around 0 decimale
    points_calcul2     = points_calcul2[points_calcul2[:,6].argsort(kind='mergesort')] #on trie sur les caps a voir si necessaire !

# VERSION MODIFIEE
# renumerotation sur la colonne 4  le premier numero est le numero dernier point iso precedent +1  
    N=np.array( range( int(numero_dernier_point2) + 1, points_calcul2.shape[0] +int(numero_dernier_point2) + 1,1))  # tableau des indices
    points_calcul2[:,4]=N     # renumerotation
    TWS2, TWD2 =prevision_tableau3(tig, GR, nouveau_temps, points_calcul2) # Vitesse vent et direction pour nouveaux points (extraction en double)
   
# on minore TWS à  2 pour règle VR
    TWS2[TWS2 <2] = 2
    VT2 = polaire3_vect(polaires, TWS2, TWD2, points_calcul2[:,6])
    VT2=0.9*VT2
# calcul des temps vers l arrivee
    D_a2       = points_calcul2[: ,5]               # Distances vers l'arrivee
    T_a2       = 60 * D_a2 / (VT2 + 0.000001)        # Temps vers l'arrivée nb ce temps est en heures
    temps_mini2=(T_a2[np.argmin(T_a2,0)])      # Valeur du temps minimum
# Verification si le but est atteignable dans le temps d'un isochrone    
    if temps_mini2 < delta_temps / 3600:
            but2 = True
    indice2= np.argmin(T_a2,0)  + numero_dernier_point2 + 1     #indice du point de temps minimum
#    ptn_np2=points_calcul[:, 0:2]   #(X,Y)# Constitution du tableau des points retournes en sortie    
    lf2=points_calcul2.shape[0]
# Ajout des points calcules au tableau global des isochrones
    isochrone2 = np.concatenate((isochrone2, points_calcul2[:,0:6]))  # On rajoute ces points a la fin du tableau isochrone 

    print('   {}  {} points capmini {:6.2f} capmaxi {:6.2f} coeff {:6.2f} '.format( t_iso_formate,longueur2,capmini2,capmaxi2,coeff2  ))
   
    return lf2, nouveau_temps, but2, indice2





# ************************************   Fin de la fonction       **********************************************************



def fonction_routeur(xn,yn,x1,y1,t0=time.time()):
    '''x0,y0,x1,y1 depart et arrivee '''
    ''' Le but de la fonction frouteur est a partir de x0 y0 x1 y1 
    de retourner une multipolyline des isochrones'''
    global isochrone,intervalles,TWS,TWD,tig,GR,angle_objectif,temps_mini,A
    global isochrone2,TWS2,TWD2,tig,GR,angle_objectif,temps_mini2,A
   
    
# Definition des variables pour le routage
    tig, GR        = chargement_grib()
    A= x1+y1*1j                         # Arrivee sous forme complexe
    pt1_np=np.array([[xn,yn]])          # isochrone de depart (1 point)
    l=pt1_np.shape[0]                   # longueur de l'isochrone de depart (1)
    l2=pt1_np.shape[0]                   # longueur de l'isochrone de depart (1) le meme que l normal
    temps=t0                            # Definition du temps à l'isochrone de depart par defaut time.time()
    temps2=t0                            # Definition du temps à l'isochrone de depart par defaut time.time()
    angle_objectif = 90                 # amplitude des angle balayes vers l'objectif 
    temps_mini = 0                      # temps entre le dernier isochrone et l'objectif 
# definition des temps des isochrones
    dt1           = np.ones(72) * 600  # intervalles de temps toutes les 10mn pendant une heure puis toutes les heures
    dt2           = np.ones(370) * 3600
    intervalles   = np.concatenate(([t0 - tig], dt1, dt2))
    temps_cumules = np.cumsum(intervalles)
#base
    but = False
    isochrone = np.array([[x0, y0, 0, 0, 0]])# on initialise le tableau isochrone et TWS TWD
    TWS, TWD = prevision_tableau3(tig, GR, t0, pt1_np)   # on initialise le tableau des TWS et TWD variante
      
#variante
    but2 = False
    isochrone2 = np.array([[x0, y0, 0, 0, 0,0]])# on initialise le tableau isochrone et TWS TWD avec une colonne en plus
    TWS2, TWD2 = prevision_tableau3(tig, GR, t0, pt1_np) # prevision au point de depart identique pour les 2
    print ('(336)TWD2',TWD2.shape)


# on imprime les donnees de depart    
    print()
    print('Depart :      Latitude {:6.4f}     \tLongitude {:6.4f}'.format(y0, x0))
    print('Arrivee:      Latitude {:6.4f}     \tLongitude {:6.4f}'.format(y1, x1))
    tig_formate_utc = time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tig))
    tic_formate_local = time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(tic))
    print('Heure UTC du dernier Grib             ',tig_formate_utc)
    print('Heure Locale de depart de la prevision',tic_formate_local)
    print ('Ecart en heures ( = ecart - ecartUTC ) ', (tic-tig)/3600)

 
    vit_vent_n, TWD = prevision(tig, GR, temps, y0,x0)
    temps_formate = time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(temps))
    # Impression des resultats au depart
    print('Date et Heure du grib  en UTC  :', time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tig)))
    print('\nLe {} heure locale Pour latitude {:6.2f} et longitude{:6.2f} '.format(temps_formate, x0, y0))
    print('\tVitesse du vent {:6.3f} Noeuds'.format(vit_vent_n))
    print('\tAngle du vent   {:6.1f} °'.format(TWD))

#********************************************************************************************************************

# on calcule tous les isochrones
    while but2 == False:
        l2,temps2, but2, indice2= f_isochrone2(l2,temps2)

    a2 = int(indice2)                 # indice du point de la route la plus courte
    n2 = int(isochrone2[-1][2])       # nombre d'isochrones

    #extract2=(np.copy(isochrone2[:,3:5]))
    dico2= dict(zip(isochrone2[:,4],isochrone2[:,3]))  #dictionnaire des points et points meres
    route2 = [a2]
    for i in range(n2):
        a2 = int(dico2[a2])
        route2.append(a2)  # route contient les indices successifs des points a emprunter a l'envers
    route2.reverse()
    chemin2 = np.zeros(len(route2) + 1, dtype=complex)  # on initialise le np array de complexes qui va recevoir les donnees
    i2 = 0
    for n2 in (route2):
        chemin2[i2] = isochrone2[n2][0] + isochrone2[n2][1] * 1j
        i2 += 1
    chemin2[i2] = A

    l2 = len(chemin2)
    temps_cum2 = np.copy(temps_cumules[:l2])
    temps_cum2[-1] = temps_cum2[-2] + temps_mini2 * 3600  # le dernier terme est le temps entre le dernier isochrone et l'arrive
    #print ('shape temps cum et temps_cum2.shape',temps_cum2.shape,chemin2.shape)
    #print('temps_cum2',temps_cum2)
    TWS_ch2, TWD_ch2 = prevision_tableau2(GR, temps_cum2, chemin2)# previsions meteo aux differents points pour reconstitution 
   
   
    distance2, cap12 = dist_cap3(chemin2[0:-1], chemin2[1:])    # distance et angle de chaque point au suivant
    #dist = np.append(distance, [0])                         # on rajoute un 0 pour la distance arrivee et l angle arrivee
    HDG_ch2 = np.append(cap12, [0])                           # tableau des caps aux differents points
    TWA_ch2 = twa(HDG_ch2, TWD_ch2)                            # calculs twa sous forme de tableau pour les differents points
    POL_ch2 = polaire3_vect(polaires, TWS_ch2, TWD_ch2, HDG_ch2)# calcul des polaires aux differents points du chemin
    # mise en forme pour concatener
    chx2 =       chemin2.real.reshape((1, -1))
    chy2 =       chemin2.imag.reshape((1, -1))
    temps_pts2 = temps_cum2.reshape((1, -1))
    vitesse2 =   TWS_ch2.reshape((1, -1))
    TWDR2 =       TWD_ch2.reshape((1, -1))
    cap2 =       HDG_ch2.reshape((1, -1))
    twat2 =       TWA_ch2.reshape((1, -1))
    pol2 =       POL_ch2.reshape((1, -1))
    # tabchemin : x,y,vit vent ,TWD,cap vers point suivant twa vers point suivant
    chem2 = np.concatenate((chx2.T, chy2.T, temps_pts2.T, vitesse2.T, TWDR2.T, cap2.T, twat2.T, pol2.T), axis=1)

    temps_cum2 += tig
    route32=[]
    comment2=[]
    for i in range (0,len(chem2),1):
        temps2=time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(chem2[i, 2]))
        # heures=str(((chem[i, 2])- t0)//3600)
        # long=str(-round(chem[i, 0], 2))
        # lat=str(-round(chem[i, 1], 2))
        # tws = str(round(chem[i, 3], 1))
        # twd = str(round(chem[i, 4], 0))
        cap2 = str(round(chem2[i, 5], 0))
        # twaroute = str(round(chem[i, 6], 0))
        # Vt  = str(round(chem[i, 7], 2))
        route32.append([-chem2[i, 1],chem2[i, 0]])   # dans la version leaflet on a le temps en trois
        comment2.append([-chem2[i, 1],chem2[i, 0],chem2[i, 2]+tig,chem2[i, 3],chem2[i, 4],chem2[i, 5],chem2[i, 6],chem2[i, 7]])
    #Confection de la multipolyline pour le trace des isochrones 

        #print('chem2 i 2 ',chem2[i, 2])    
    X2=isochrone2[:,0].reshape(-1,1)
    Y2=isochrone2[:,1].reshape(-1,1)
    N2=isochrone2[:,2].reshape(-1,1)
    points2=np.concatenate((-Y2,X2,N2),1)
    polyline2=np.split(points2[:,0:2],np.where(np.diff(points2[1:,2])==1)[0]+2)
    multipolyline2=[arr.tolist() for arr in polyline2]
    del multipolyline2[0][0]
    # affichage du temps total
    print ('\nHeure de depart v2 ',time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(t0)))
    #print ("temps à l'arrivee en s ",chem[-1, 2])
    print ("Heure d'arrivée v2",time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(chem2[-1, 2])))
    
    duree2 = (temps_cum2[-1] - t0)
    print('temps total2 en s ', duree2)
    j2 = duree2 // (3600 * 24)
    h2 = (duree2-(j2*3600*24))//3600
    mn2 = (duree2 - (j2 * 3600 * 24)-(h2*3600))//60 
    s2=duree2-(j2*3600*24+h2*3600+mn2*60)

    print('Temps total      v2 {:2.0f}j {:2.0f}h {:2.0f}mn {:2.0f}s'.format(j2, h2, mn2 ,s2 ))

    return multipolyline2,route32,comment2










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

@app.route('/windybase')
def windybase():
  return render_template("windybase.html")

@app.route('/numpyhtml')
def numpyhtml():
  return render_template("numpyhtml.html")



@app.route('/resultat',methods = ['POST'])
def resultat():
  resultat1 = request.form                                    # dictionnaire avec les resultats de la requete
                                                              # resultat = request.args dans le cas d'une requete 'GET'
  latdep                 = resultat1['lat']
  longdep                = resultat1['long']
  #frouteur (latdep,longdep,latar,longar) 
  return render_template("resultat.html", total=add(latdep,longdep) , result=request.form)

@app.route('/vents.json')
def jsoni():
  return render_template("vents.json")


# @app.route('/outils.json')
# def outils():
#   return render_template("outils.json")



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

@app.route('/javascript')
def javascript(): 
    global tig, GR
    latini=-50      # latitude la plus au nord en premier et latitude nord negative pour charger le grib pour jzvzscript
    latfin=-40      # Il faudrait mettra une formule pour que la bonne portion de grib soit chargée
    lngini=340
    lngfin=360

    u10,v10=vents_encode2(latini,latfin,lngini,lngfin)   
    l1=list(tab_tws_imoca)
    l2=list(tab_twa_imoca)
    polairesjs=[arr.tolist() for arr in polaires]
    tsimul=time.time()


    #vents2=vents_encode(latini,latfin,longini,longfin)
    return render_template("javascript.html",tig=tig,tsimul=tsimul,latini=latini,lngini=lngini,latfin=latfin,lngfin=lngfin,U10=u10, V10=v10,l1=l1,l2=l2,polairesjs=polairesjs )






@app.route('/outils')
def outilshtml():  
    return render_template("outils.html")    


@app.route('/vents')
def vents():  
    return render_template("vents.html")



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
    
# Extraction de donnees du fichier json
     # Extraction de donnees du fichier json
    with open('courses.json', 'r') as fichier:
        data = json.load(fichier)
    n_course='429'
    bateau=(data[n_course]["bateau"])
    print('\nBateau : ',bateau)
    fichier_polaires='polaires.'+(data[n_course]["polaires"])

    latdep = (data[n_course]["depart"]["lat"])
    lngdep = (data[n_course]["depart"]["lng"])
    latar  = (data[n_course]["bouee_1"]["lat"])
    lngar  = (data[n_course]["bouee_1"]["lng"])
    x0,y0=chaine_to_dec(latdep, lngdep)  # conversion des latitudes et longitudes en tuple
    x1,y1=chaine_to_dec(latar, lngar)
    print ('x0,y0',x0,y0)
    print ('x1,y1',x1,y1)
    latar=y1
    lngar=x1

    t0=time.time() 
    tsimul=time.time()
    print ('(401) temps t0',time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(t0)))

 
# on tient compte des valeurs retournees par get
    latdep        = -float(request.args['latdep'])
    lngdep        = float(request.args['lngdep'])
    x0=lngdep
    y0=latdep


# #Si on veut forcer la position de depart     3 lignes seront à supprimer
#     latitude_d     = '043-17-12-N'
#     longitude_d    = '010-07-49-E'
#     x0,y0=chaine_to_dec(latitude_d, longitude_d)  # conversion des latitudes et longitudes en tuple
    
# #Si on veut forcer la position d'arrivee (reste à tester )
#     latitude_d     = '043-17-12-N'
#     longitude_d    = '010-07-49-E'
#     x1,y1=chaine_to_dec(latitude_d, longitude_d)  # conversion des latitudes et longitudes en tuple
    
  
    # chargement du grib partiel pour utilisation ulterieure en js
    global tig, GR
    latini=-50      # latitude la plus au nord en premier et latitude nord negative pour charger le grib pour jzvzscript
    latfin=-40
    lngini=340
    lngfin=360
    u10,v10=vents_encode2(latini,latfin,lngini,lngfin)   
    l1=list(tab_tws_imoca)   
    l2=list(tab_twa_imoca)   
    polairesjs=[arr.tolist() for arr in polaires]

    # calcul de la route et de la multipolyline des isochrones
    multipolyline,route,comment=fonction_routeur(lngdep,latdep,x1,y1,t0)
    red=[]
    black=[]
    for i in range(len(multipolyline)):
        if (i+1)%6==0:
                black.append(multipolyline[i])
        else:
                red.append(multipolyline[i]) 



    print('tsimul',tsimul)
    return render_template("windleaf.html", multipolyred=red,multipolyblack=black,route=route,comment=comment,l1=l1,l2=l2,polairesjs=polairesjs,lngdep=lngdep,latdep=latdep,lngar=lngar,latar=latar, t0=tsimul ,tig=tig,latini=latini,lngini=lngini,latfin=latfin,lngfin=lngfin,U10=u10, V10=v10 ,result=request.form)


    









if __name__ == "__main__" :
    db.create_all()                 #creation de la base de donnees
    app.debug=True
    app.config['JSON_AS_ASCII']=False
    
    app.run(host='127.0.0.1', port=8080, debug=True)
