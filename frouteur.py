
import time
from uploadgrib import *
from fonctions_vr import *


def frouteur(d,ar,tig,GR,t=time.time()):

    '''d et ar depart et arrivee sous forme de tupple ,
     tig instant initial du grib , GR valeurs du grib '''
    import folium
    import webbrowser
   


    


    # Initialisation carte folium **************************************************************
    lat1=-(d[1]+ar[1])/2                    # Point pour centrer la carte folium
    long1= (d[0]+ ar[0])/2
    m = folium.Map( location=[lat1,long1],  zoom_start=5)
    folium.LatLngPopup().add_to(m)   # popup lat long
    #*******************************************************************************************
    filecarte='map.html'
    filepath = 'templates/'+filecarte
    m.save(filepath)
    webbrowser.open( filepath)

    return None







if __name__ == '__main__':
    import folium
    import webbrowser
    import time

    # initialisation des variables
    angle_objectif = 90
    dico = {}
    indice = 0
    t_v_ar_h = 0
    nouveau_temps = 0
    tic = time.time()
    # t = time.localtime()
    # print('t',t)
    # 
    # print('instant',instant)

    # filename = chargement_grib()
    # tig, GR = ouverture_fichier(filename)
    # temps = instant
    (filenamehdf5,dategrib,tig )= filename()
    # Depart ou position actuelle 
    latitude_d = '043-38-42-N'
    longitude_d = '059-25-36-W'

    #todo Arrivee cap Lizard
    latitude_a = '049-15-00-N'
    longitude_a = '005-10-00-W'
    d  = chaine_to_dec(latitude_d, longitude_d)  # conversion des latitudes et longitudes en tuple
    ar = chaine_to_dec(latitude_a, longitude_a)
    
    D = cplx(d)  # transformation des tuples des points en complexes
    A = cplx(ar)

    

    # Initialisation du tableau des points d'isochrones
    # 0: x du point (longitude), 1: y du point (latitude) , 2: N° isochrone , 3: N° du pt mere ,
    # 4: N° du pt , 5: Distance a l'arrivee , 6: Cap vers l'arrivee
    isochrone = [[D.real, D.imag, 0, 0, 0, dist_cap(D, A)[0], dist_cap(D, A)[1]]]

    dt1 = np.ones(36) * 3600  # intervalles de temps toutes les 10mn pendant une heure puis toutes les heures
    dt2 = np.ones(378) * 3600

    intervalles = np.concatenate(([tic - tig], dt1, dt2))
    temps_cumules = np.cumsum(intervalles)

    
    print('Depart : Latitude {:6.4f}  Longitude {:6.4f}'.format(d[1], d[0]))
    print('Arrivee: Latitude {:4.2f}  Longitude {:4.2f}'.format(ar[1], ar[0]))
    tig_formate_utc = time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tig))
    print('tig_formate_utc',tig_formate_utc)
    print('temps instantane',time.time())

    print ('ecart', (tic-tig)/3600)








    #lancement de la fonction
    frouteur(d,ar,tig,GR)    