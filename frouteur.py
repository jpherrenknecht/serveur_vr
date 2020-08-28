
import time
from uploadgrib import *
from fonctions_vr import *
import folium
import webbrowser
from global_land_mask import globe
from uploadgrib import *
from polaires.polaires_ultime import *



def f_isochrone(points, temps_initial_iso):
    ''' Calcule le nouvel isochrone a partir d'un tableau de points pt2cplx tableau numpy de cplx'''
    ''' deltatemps, tig , U, V sont supposees etre des variables globales'''
    ''' Retourne les nouveaux points el le nouveau temps et implemente le tableau general des isochrones'''

    global isochrone
    numero_iso           = int(isochrone[-1][2] + 1)
    delta_temps          = intervalles[numero_iso]  # Ecart de temps entre anciens points et nouveaux en s
    nouveau_temps = temps_initial_iso + delta_temps
    t_iso_formate        = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(temps_initial_iso + delta_temps))
    numero_dernier_point = int(isochrone[-1][4])                   # dernier point isochrone precedent
    numero_premier_point = int(isochrone[-1][4]) - points.shape[0]   # premier point isochrone precedent
   
    but                  = False   
    
    # on recupere toutes les previsions meteo d'un coup pour l'ensemble des points de depart
    TWS, TWD = prevision_tableau3(tig, GR, temps_initial_iso, points)
   
    # pour chaque point de l'isochrone precedent  donnés en entrée (isochrone précédent)
    points_calcul2=np.array([[0,0,0,0,0,0,0]]) # initialisation pour Numpy du brouillard des points de l'isochrone

    for i in range(points.shape[0]):
        HDG = range_cap(dist_cap4(points[i], A)[1], TWD[i], angle_objectif, angle_twa_pres, angle_twa_ar)  # Calcul des caps a etudier
        VT = polaire2_vect(polaires, TWS[i], TWD[i], HDG)
        X1,Y1,Da1,Ca1=deplacement_x_y_tab_ar(points[i][0],points[i][1],delta_temps,HDG,VT,A) #coordonnees des nouveaux points calcules sous forme X,Y
        L=len(X1)
        niso1= np.ones(L)*numero_iso   #len(X1) doit pouvoir etre evite 3 fois
        npointsm1=np.ones(L)*i  +numero_premier_point +1    # numero du point mere i= 0 correspond au premier point de l'isochrone precedent
        npoints1=np.array(range(L)) +1           # numero du point  sans importance sera renumeroté
        X=X1.reshape(-1,1)
        Y=Y1.reshape(-1,1)
        niso=niso1.reshape(-1,1)
        npointsm=npointsm1.reshape(-1,1)
        npoints=npoints1.reshape(-1,1)
        Da=Da1.reshape(-1,1)
        Ca=Ca1.reshape(-1,1)
        # maintenant on forme le tableau correspondant à n_pts_x
        n_pts_x2     = np.concatenate((X,Y,niso,npointsm,npoints,Da,Ca), axis=1)    # tableau des points pour un point de base
        points_calcul2= np.concatenate((points_calcul2,n_pts_x2), axis=0)           # tableau du brouillard des points 
        
       
#Version Numpy    
    points_calcul2=np.delete(points_calcul2,0,0)                                    # on retire le premier terme de points_calcul2
    points_calcul2= points_calcul2[points_calcul2[:,6].argsort(kind='mergesort')]   # tri stable sur 6eme colonne
 
    k=0
    while (((points_calcul2[k][6]-points_calcul2[k-1][6])<-357)and (k<points_calcul2.shape[0]-1)):
        points_calcul2[k][6]+=360
        k+=1
    points_calcul2= points_calcul2[points_calcul2[:,6].argsort(kind='mergesort')]
    capmini2=points_calcul2[0][6]
    capmaxi2=points_calcul2[-1][6]
   
   
    coeff2 = 49/ (capmaxi2-capmini2)  # coefficient pour ecremer et garder 50 points
   
    
#ecremage arrondi et tri

    points_calcul2[:,6]=np.around(points_calcul2[:,6]*coeff2,0)   # le calcul est fait sur la colonne sans boucle variante around
    points_calcul2= points_calcul2[points_calcul2[:,5].argsort(kind='mergesort')] #on trie sur les distances 
    points_calcul2= points_calcul2[points_calcul2[:,6].argsort(kind='mergesort')] #on trie sur les caps mais l'ordre des distances est respecté
   


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
    points_calcul2[:,6]=np.floor(points_calcul2[:,6]/coeff2)       # on retablit le cap en valeur a rechanger en around 0 decimale
    points_calcul2= points_calcul2[points_calcul2[:,6].argsort(kind='mergesort')] #on trie sur les caps a voir si necessaire !
    # renumerotation sur la colonne 4  le premier numero est le numero dernier point iso precedent +1  
    N=np.array( range( int(numero_dernier_point) + 1, points_calcul2.shape[0] +int(numero_dernier_point) + 1,1))  # tableau des indices
    points_calcul2[:,4]=N     # renumerotation
    TWS, TWD =prevision_tableau3(tig, GR, nouveau_temps, points_calcul2) # Vitesse vent et direction pour nouveaux points (extraction en double)
    VT = polaire3_vect(polaires, TWS, TWD, points_calcul2[:,6])
   

    # calcul des temps vers l arrivee
    D_a = points_calcul2[:,5]               # Distances vers l'arrivee
    T_a = 60 * D_a / (VT + 0.000001)        # Temps vers l'arrivée nb ce temps est en heures
    temps_mini=(T_a[np.argmin(T_a,0)])      # Valeur du temps minimum
    
    if temps_mini < delta_temps / 3600:
            but = True
    indice2= np.argmin(T_a,0)  + numero_dernier_point + 1     #indice du point de temps minimum
    ptn_np2=points_calcul2[:, 0:2]   #(X,Y)
  
    trace_iso2=np.concatenate((-points_calcul2[:,1].reshape(-1,1),points_calcul2[:,0].reshape(-1,1)),axis=1)  #(-Y,X)
    isochrone = np.concatenate((isochrone, points_calcul2))  # On rajoute ces points a la fin du tableau isochrone
       
    print(' Isochrone calculé N° {}  {}  {} points  '.format(numero_iso, t_iso_formate,longueur  ))

    return ptn_np2, nouveau_temps, but, indice2,trace_iso2





def frouteur(x0,y0,x1,y1,t0=time.time()):
    '''d et ar depart et arrivee sous forme de tupple ,'''
    ''' Le but de la fonction frouteur est a partir de x0 y0 x1 y1 
    de retourner une multipolyline des isochrones'''

    #on commence par charger le grib
    
    tig, GR        = chargement_grib()

    pt1_np=np.array([[x0,y0]])
    temps=t0

    but = False
    while but == False:
        pt1_np, temps, but, indice,trace_iso = f_isochrone(pt1_np, temps)  
    # trace iso 



    return None







if __name__ == '__main__':
    import folium
    import webbrowser
    import time


    tic=time.time()

# initialisation des variables
    angle_objectif = 90
    indice = 0
    t_v_ar_h = 0
    nouveau_temps = 0
    tig, GR        = chargement_grib()
   
       
    x0,y0=(-73.62,-40.46)
    t0=time.time()    
    x1,y1=(-3.89,-47.65)
    A= x1+y1*1j
    pt1_np=np.array([[x0,y0]])
    but = False

    # definition des temps des isochrones
    dt1           = np.ones(72) * 600  # intervalles de temps toutes les 10mn pendant une heure puis toutes les heures
    dt2           = np.ones(370) * 3600
    intervalles   = np.concatenate(([t0 - tig], dt1, dt2))
    temps_cumules = np.cumsum(intervalles)
    # on initialise l'isochrone de depart avec le depart et le temps au depart
    pt1_np=np.array([[x0,y0]])
   
# Initialisation du tableau des points d'isochrones
    # 0: x du point (longitude), 1: y du point (latitude) , 2: N° isochrone , 3: N° du pt mere ,
    # 4: N° du pt , 5: Distance a l'arrivee , 6: Cap vers l'arrivee
    isochrone = [[x0, y0, 0, 0, 0, dist_cap(x0+y0*1j, x1+y1*1j)[0], dist_cap(x0+y0*1j, x1+y1*1j)[1]]]

# impression des donnees au point de depart
    print()
    print('Depart :      Latitude {:6.4f}     \tLongitude {:6.4f}'.format(y0, x0))
    print('Arrivee:      Latitude {:6.4f}     \tLongitude {:6.4f}'.format(y1, x1))
    tig_formate_utc = time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tig))
    tic_formate_local = time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(tic))
    print('Heure UTC du dernier Grib             ',tig_formate_utc)
    print('Heure Locale de depart de la prevision',tic_formate_local)
    print ('Ecart en heures ( = ecart - ecartUTC ) ', (tic-tig)/3600)
    print() 








#lancement de la fonction
    frouteur(x0,y0,x1,y1)
    print (isochrone[0:10])

    #   ****************************************Controle du temps d'execution **********************************
tac = time.time()
print('\nDuree d\'execution:  {:4.2f} s'.format(tac - tic))
