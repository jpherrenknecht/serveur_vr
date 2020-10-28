
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
#tig, GR = chargement_grib()
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
    #les latitudes et longitudes sont en coordonnees leaflet positives au nord la latitude initiale est la plus petite (plus au sud )
    # on les transforme en indices grib
    ilatini=90 -latini    #ilatini est l'indice de grib dans GR
    ilatfin=90-latfin
    # pour les longitudes longini est la plus a l'ouest 

    if (longini <longfin) :
        U10=GR[0:12,ilatini:ilatfin,longini:longfin].real
        V10=GR[0:12,ilatini:ilatfin,longini:longfin].imag
    else :
        fin = 360-longini         # sert a determiner la coupe a la fin 
        debut =longfin+1
        U10=np.concatenate((GR[0:12,ilatini:ilatfin,-fin:].real,GR[0:12,ilatini:ilatfin,:debut].real),axis=2)
        V10=np.concatenate((GR[0:12,ilatini:ilatfin,-fin:].imag,GR[0:12,ilatini:ilatfin,:debut].imag),axis=2)
    u10=[arr.tolist() for arr in U10]
    v10=[arr.tolist() for arr in V10]
    return u10,v10




class user(db.Model):                                              # creation du modele de base de donnée
    id     = db.Column(db.Integer, primary_key=True)
    nom    = db.Column(db.String(100))
    prenom = db.Column(db.String(100))


#*******************************************************************************************************
#*******************************************************************************************************

def f_isochrone2(l, temps_initial_iso):

    ''' Calcule le nouvel isochrone a partir d'un tableau de points pt2cplx tableau numpy de cplx'''
    ''' deltatemps, tig , U, V sont supposees etre des variables globales'''
    ''' Retourne les nouveaux points el le nouveau temps et implemente le tableau general des isochrones'''
    ''' isochrone 2 comprend une colonne de plus avec la twa en dernier '''
    global isochrone,TWS,TWD,temps_mini

    nb_points_ini=200
    
    
    numero_iso           = int(isochrone[-1][2] + 1)

    if (numero_iso<48):
        nb_points=nb_points_ini
    else:
        nb_points=50 

    print()
    print(' Isochrone Variante N° {} '.format(numero_iso ))
  

#variante 
    points=isochrone[-l:,0:2]  # ici on selectionne -l lignes en partant du bas et les colonnes 0 1 6
    twa= isochrone[-l:,5]      # ici on recupere l'ensemble des twa de l'isochrone precedent

   
#variante
    numero_iso           = int(isochrone[-1][2] + 1)
    delta_temps          = intervalles[numero_iso]  # Ecart de temps entre anciens points et nouveaux en s (inchangé)
    nouveau_temps        = temps_initial_iso + delta_temps     #(inchangé)
    t_iso_formate        = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(temps_initial_iso + delta_temps))
    numero_dernier_point = int(isochrone[-1][4])                   # dernier point isochrone precedent
    numero_premier_point = int(isochrone[-1][4]) - l               # premier point isochrone precedent
    but                  = False 
    # on recupere toutes les previsions meteo d'un coup pour l'ensemble des points de depart
    # TWS, TWD = prevision_tableau3(tig, GR, temps_initial_iso, points)
    points_calcul=np.array([[0,0,0,0,0,0,0]]) # initialisation pour Numpy du brouillard des points calcules (inchangé)

    TWS, TWD =prevision_tableau3(tig, GR, nouveau_temps, points) # Vitesse vent et direction pour nouveaux points (extraction en double)
# pour chacun des points de l'isochrone 
    if numero_iso==1:
        penalite=0
    else:    
        penalite=0
    
    for i in range(l):

      #VARIANTE
     # twa precedente
        twap=twa[i]
        # ici c'est nouveau
        
        # Calcul des caps a etudier pour chaque point (INCHANGÉ)
        HDG = range_cap(dist_cap4(points[i], A)[1], TWD[i], angle_objectif, angle_twa_pres, angle_twa_ar)  

        VT  =polaire2_vectv2(polaires,tab_twa, tab_tws, TWS[i], TWD[i], HDG)  #Vitesse polaire pour chaque cap
        #print ('delta_temps',delta_temps)
        
        X1,Y1,Da1,Ca1=deplacement2(points[i][0],points[i][1],delta_temps,HDG,TWD[i],VT,A,twap,penalite)

        L=len(X1)                                                                            # nombre de ( caps ) points etudies  (INCHANGÉ)
        niso1     = np.ones(L)*numero_iso                                                         # numero isochrone(INCHANGÉ)
        npointsm1 = np.ones(L)*i  +numero_premier_point +1    # numero du point mere i = 0 correspond au premier point de l'isochrone precedent(INCHANGÉ)
        npoints1  = np.array(range(L)) +1                      # numero du point  sans importance sera renumeroté
        X        = X1.reshape(-1,1)
        Y         = Y1.reshape(-1,1)
        niso      = niso1.reshape(-1,1)
        npointsm  = npointsm1.reshape(-1,1)
        npoints   = npoints1.reshape(-1,1)
        Da        = Da1.reshape(-1,1)
        Ca        = Ca1.reshape(-1,1)
        # maintenant on forme le tableau correspondant à n_pts_x
        n_pts_x2       = np.concatenate((X,Y,niso,npointsm,npoints,Da,Ca), axis = 1)    # tableau des points pour un point de base
        points_calcul = np.concatenate((points_calcul,n_pts_x2), axis         = 0)           # tableau du brouillard pour tous les points de base 





#VERSION MODIFIEE

    points_calcul = np.delete(points_calcul,0,0)                                    # on retire le premier terme de points_calcul
    points_calcul = points_calcul[points_calcul[: ,6].argsort(kind = 'mergesort')]   # tri stable sur 6eme colonne (caps vers arrivee)
    k=0                                                                             # on regroupe les  caps 359 et 1
    while (((points_calcul[k][6]-points_calcul[k-1][6])<-330)and (k<points_calcul.shape[0]-1)):
        points_calcul[k][6]+=360
        k+=1
    points_calcul= points_calcul[points_calcul[:,6].argsort(kind='mergesort')]   # les caps en 361 sont replaces a la fin 
    capmini = points_calcul[0][6]
    capmaxi = points_calcul[-1][6]
    coeff   = nb_points/ (capmaxi-capmini)  # coefficient pour ecremer et garder 50 points


#VERSION MODIFIEE
#ecremage arrondi et tri
    points_calcul[:,6]=np.around(points_calcul[:,6]*coeff,0)                   # La colonne 6 est arrondie  
    points_calcul     = points_calcul[points_calcul[:,5].argsort(kind='mergesort')] # On trie sur les distances 
    points_calcul     = points_calcul[points_calcul[:,6].argsort(kind='mergesort')] # On trie sur les caps mais l'ordre des distances est respecté
# ecremage proprement dit
    for i in range(points_calcul.shape[0] - 1, -1, -1):  # ecremage
        if (points_calcul[i][6]) == (points_calcul[i - 1][6]):
            points_calcul = np.delete(points_calcul, i, 0)
    
# verification points terre ou mer
    for i in range(points_calcul.shape[0]- 1, -1, -1):  # ecremage 
        is_on_land = globe.is_land(-points_calcul[i][1], points_calcul[i][0])   # point de latitude -y et longitude x
        if (is_on_land==True):
            points_calcul = np.delete(points_calcul, i, 0)
    points_calcul[:,6]= np.floor(points_calcul[:,6]/coeff)       # on retablit le cap en valeur a rechanger en around 0 decimale
    points_calcul     = points_calcul[points_calcul[:,6].argsort(kind='mergesort')] #on trie sur les caps a voir si necessaire !

# VERSION MODIFIEE
# renumerotation sur la colonne 4  le premier numero est le numero dernier point iso precedent +1  
    N=np.array( range( int(numero_dernier_point) + 1, points_calcul.shape[0] +int(numero_dernier_point) + 1,1))  # tableau des indices
    points_calcul[:,4]=N     # renumerotation
    TWS, TWD =prevision_tableau3(tig, GR, nouveau_temps, points_calcul) # Vitesse vent et direction pour nouveaux points (extraction en double)
   
# on minore TWS à  2 pour règle VR
    TWS[TWS <2] = 2
    VT = polaire3_vect(polaires,tab_twa, tab_tws, TWS, TWD, points_calcul[:,6])
    VT=0.9*VT
# calcul des temps vers l arrivee
    D_a       = points_calcul[: ,5]               # Distances vers l'arrivee
    T_a       = 60 * D_a / (VT + 0.000001)        # Temps vers l'arrivée nb ce temps est en heures
    temps_mini=(T_a[np.argmin(T_a,0)])      # Valeur du temps minimum
# Verification si le but est atteignable dans le temps d'un isochrone    
    if temps_mini < delta_temps / 3600:
            but = True
    indice= np.argmin(T_a,0)  + numero_dernier_point + 1     #indice du point de temps minimum
#    ptn_np2=points_calcul[:, 0:2]   #(X,Y)# Constitution du tableau des points retournes en sortie    
    lf=points_calcul.shape[0]
# Ajout des points calcules au tableau global des isochrones
    isochrone = np.concatenate((isochrone, points_calcul[:,0:6]))  # On rajoute ces points a la fin du tableau isochrone 

    print('   {}  {} points capmini {:6.2f} capmaxi {:6.2f} coeff {:6.2f} '.format( t_iso_formate,lf,capmini,capmaxi,coeff  ))
   
    return lf, nouveau_temps, but, indice



#*******************************************************************************************************
# ************************************   Fin de la fonction       **********************************************************



def fonction_routeur(course,latdep,lngdep,arrivee,t0=time.time()):
    '''x0,y0,x1,y1 depart et arrivee '''
    ''' Le but de la fonction frouteur est a partir de x0 y0 x1 y1 
    de retourner une multipolyline des isochrones'''
    ''' ex d'initialisation : course,depart,arrivee =    457,"bouee_2","arrivee"    '''


    global isochrone,intervalles,TWS,TWD,tig,GR,angle_objectif,angle_twa_pres,angle_twa_ar,temps_mini,A,polaires,tab_twa,tab_tws
    tig, GR        = chargement_grib()

    with open('courses.json', 'r') as fichier:
        data1 = json.load(fichier)
    print ('course',course)
    bateau=  (data1[course]["bateau"])
    # latdep = (data1[course][depart]["lat"])
    # lngdep = (data1[course][depart]["lng"])
    latar  = (data1[course][arrivee]["lat"])
    lngar  = (data1[course][arrivee]["lng"])
    print('\nBateau : ',bateau)

    print ('Depart :',latdep, lngdep,' ')
    print ('Arrivee :',latar, lngar,' ')
    print()

    with open('polars.json', 'r') as fichier:
        data2 = json.load(fichier)
    
    angle_twa_pres=data2[bateau]["pres_mini"]
    angle_twa_ar= data2[bateau]["var_mini"]
    l1=data2[bateau]["tab_tws"]
    l2=data2[bateau]["tab_twa"]
    polairesj1=data2[bateau]["polaires"]
    tab_tws=np.array(l1)
    tab_twa=np.array(l2)
    polaires=np.array(polairesj1)

    #x0,y0=chaine_to_dec(latdep, lngdep)  # conversion des latitudes et longitudes en tuple
    x0,y0=lngdep,latdep
    x1,y1=chaine_to_dec(latar, lngar)
    print ('x0,y0',x0,y0)
    print ('x1,y1',x1,y1)



# Initialisation des variables pour le routage
    
    A= x1+y1*1j                         # Arrivee sous forme complexe
    pt1_np=np.array([[x0,y0]])          # isochrone de depart (1 point)
    l=pt1_np.shape[0]                   # longueur de l'isochrone de depart (1)
          
    temps=t0                            # Definition du temps à l'isochrone de depart par defaut time.time()
   
    angle_objectif = 90                 # amplitude des angle balayes vers l'objectif 
    temps_mini = 0                      # initialisation temps entre le dernier isochrone et l'objectif
    but = False
    isochrone = np.array([[x0, y0, 0, 0, 0,0]])# on initialise le tableau isochrone et TWS TWD avec une colonne en plus
    TWS, TWD = prevision_tableau3(tig, GR, t0, pt1_np) # prevision au point de depart identique pour les 2

# definition des temps des isochrones
    dt1           = np.ones(48) * 600  # intervalles de temps toutes les 10mn pendant une heure puis toutes les heures
    dt2           = np.ones(370) * 3600
    intervalles   = np.concatenate(([t0 - tig], dt1, dt2))
    temps_cumules = np.cumsum(intervalles)




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

#********************************************************************************************************************

# on calcule tous les isochrones
   

    while but == False:
        l,temps, but, indice= f_isochrone2(l,temps)



#********************************************************************************************************************
#********************************************************************************************************************




#VARIANTE


    a = int(indice)                 # indice du point de la route la plus courte
    n = int(isochrone[-1][2])       # nombre d'isochrones

    #extract2=(np.copy(isochrone2[:,3:5]))
    dico= dict(zip(isochrone[:,4],isochrone[:,3]))  #dictionnaire des points et points meres
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




#VARIANTE

    l = len(chemin)
    temps_cum = np.copy(temps_cumules[:l])
    temps_cum[-1] = temps_cum[-2] + temps_mini * 3600  # le dernier terme est le temps entre le dernier isochrone et l'arrive
   

    #print ('shape temps cum et temps_cum2.shape',temps_cum2.shape,chemin2.shape)
    #print('temps_cum2',temps_cum2)
    TWS_ch, TWD_ch = prevision_tableau2(GR, temps_cum, chemin)# previsions meteo aux differents points pour reconstitution 
   
   
    distance, cap1 = dist_cap3(chemin[0:-1], chemin[1:])    # distance et angle de chaque point au suivant
    #dist = np.append(distance, [0])                         # on rajoute un 0 pour la distance arrivee et l angle arrivee
    HDG_ch = np.append(cap1, [0])                           # tableau des caps aux differents points
    TWA_ch = twa(HDG_ch, TWD_ch)                            # calculs twa sous forme de tableau pour les differents points
    POL_ch = polaire3_vect(polaires,tab_twa, tab_tws, TWS_ch, TWD_ch, HDG_ch)# calcul des polaires aux differents points du chemin


    # mise en forme pour concatener
    chx =       chemin.real.reshape((1, -1))
    chy =       chemin.imag.reshape((1, -1))
    temps_pts = temps_cum.reshape((1, -1))
    vitesse =   TWS_ch.reshape((1, -1))
    TWDR =       TWD_ch.reshape((1, -1))
    cap =       HDG_ch.reshape((1, -1))
    twat =       TWA_ch.reshape((1, -1))
    pol =       POL_ch.reshape((1, -1))
    # tabchemin : x,y,vit vent ,TWD,cap vers point suivant twa vers point suivant
    chem = np.concatenate((chx.T, chy.T, temps_pts.T, vitesse.T, TWDR.T, cap.T, twat.T, pol.T), axis=1)

    temps_cum += tig
#VERIFICATION
    # print('430 chem version base', chem[-1])
    # print('431 chem version variante', chem2[-1])




#VARIANTE
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
    # affichage du temps total
    print ('\nHeure de depart v2 ',time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(t0)))
    #print ("temps à l'arrivee en s ",chem[-1, 2])
    print ("Heure d'arrivée v2",time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(chem[-1, 2])))
    
    duree = (temps_cum[-1] - t0)
    #print('temps total2 en s ', duree2)
    j = duree // (3600 * 24)
    h = (duree-(j*3600*24))//3600
    mn = (duree - (j * 3600 * 24)-(h*3600))//60 
    s=duree-(j*3600*24+h*3600+mn*60)

#print('temps total  {}h {}mn'.format(duree/3600,(duree-duree//3600))/60)
    print('Temps total      v {:2.0f}j {:2.0f}h {:2.0f}mn {:2.0f}s'.format(j, h, mn ,s ))


    return multipolyline,route3,comment,x0,y0,x1,y1,l1,l2,polairesj1












##partie serveur web


@app.route('/')
def index():
  return render_template('index.html')

@app.route('/dom')
def dom():
  return render_template('dom.html')

@app.route('/leafletbase')
def leafletbase():
  return render_template("leafletbase.html")

@app.route('/windybase')
def windybase():
  return render_template("windybase.html")


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


@app.route('/javascript')
def javascript(): 
    global tig, GR
    latini=-50      # latitude la plus au nord en premier et latitude nord negative pour charger le grib pour jzvzscript
    latfin=-35      # Il faudrait mettra une formule pour que la bonne portion de grib soit chargée
    lngini=330
    lngfin=360

    u10,v10=vents_encode2(latini,latfin,lngini,lngfin)   
    l1=[1,2]
    l2=[2,5]
    polairesjs=[10,20]
    tsimul=time.time()


    #vents2=vents_encode(latini,latfin,longini,longfin)
    return render_template("javascript.html",tig=tig,tsimul=tsimul,latini=latini,lngini=lngini,latfin=latfin,lngfin=lngfin,U10=u10, V10=v10,l1=l1,l2=l2,polairesjs=polairesjs )




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



    multipolyline,route,comment=fonction_routeur(course,latdep,lngdep,arrivee,t0)
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
    
    # valeurs par defaut si pas de retour de dashboard
  
    course="438.1"
    depart="depart"
    arrivee="arrivee"
    t1=time.time() 
    tsimul=time.time()

    try:
        (request.args['latdep'])
        latdep = -float(request.args['latdep'])
        lngdep = float(request.args['lngdep'])
        course = request.args['race']
        #print('on est dans try')
     
    except :   
        with open('courses.json', 'r') as fichier:
            data1 = json.load(fichier)
        # print ('course',course)
        # bateau=  (data1[course]["bateau"])
        latdep = (data1[course][depart]["lat"])
        lngdep = (data1[course][depart]["lng"])
        #print('on est dans except')
    
    print ('latdep lngdep ',latdep,lngdep )  
  
    # chargement du grib partiel pour utilisation ulterieure en js
    global tig, GR
    latini=(math.floor(-latdep)+10)    # latitude la plus au nord en premier et latitude nord negative pour charger le grib pour javascript
    latfin=(latini -20)
    lngini=(math.floor(lngdep)-20)%360
    lngfin=(lngini+40)%360
    
    u10,v10=vents_encode2(latini,latfin,lngini,lngfin)   
    #provisoire

    print ('(586)latdep lngdep dans main.py',latdep,lngdep)
    print('(587)latini latfin lngini lngfin dans main.py',latini,latfin,lngini,lngfin)
    # calcul de la route et de la multipolyline des isochrones
   
    multipolyline,route,comment,x0,y0,x1,y1,l1,l2,polairesjs=fonction_routeur(course,latdep,lngdep,arrivee,tsimul)
    latar=y1
    lngar=x1
    red=[]
    black=[]
    for i in range(len(multipolyline)):
        if (i+1)%6==0:
                black.append(multipolyline[i])
        else:
                red.append(multipolyline[i]) 

    print('tsimul',tsimul)
    print ('course',course)
    return render_template("windleaf.html", multipolyred=red,multipolyblack=black,route=route,comment=comment,l1=l1,l2=l2,polairesjs=polairesjs,lngdep=lngdep,latdep=latdep,lngar=lngar,latar=latar, t0=tsimul,tig=tig,latini=latini,lngini=lngini,latfin=latfin,lngfin=lngfin,U10=u10, V10=v10 ,result=request.form)



if __name__ == "__main__" :
    db.create_all()                 #creation de la base de donnees
    app.debug=True
    app.config['JSON_AS_ASCII']=False
    
    app.run(host='127.0.0.1', port=8080, debug=True)
