# on va charger uniquement le premier fichier


import numpy as np
import json
from json import JSONEncoder
from uploadgrib import *

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

global tig,GR
tig, GR = chargement_grib()
latini=40
latfin=45
longini=350
longfin=360

# U10=GR[0:8,latini:latfin,longini:longfin].real
# V10=GR[0:8,latini:latfin,longini:longfin].imag
# numpyData = {"latini":latini,"latfin":latfin,"longini":longini,"longfin":longfin,"u10": U10,"v10":V10}
# b=json.dumps(numpyData, cls=NumpyArrayEncoder)


def vents_encode(latini,latfin,longini,longfin):
    ''' extrait du grib GR les donnees entre ini et fin sur 24 h et l'exporte en json'''
    U10=GR[0:8,latini:latfin,longini:longfin].real
    V10=GR[0:8,latini:latfin,longini:longfin].imag
    numpyData = {"latini":latini,"latfin":latfin,"longini":longini,"longfin":longfin,"u10": U10,"v10":V10}
    a=json.dumps(numpyData, cls=NumpyArrayEncoder)
    return a 


a=vents_encode(latini,latfin,longini,longfin)


print(a)

#print (numpyData)

# with open("templates/vents.json", "w") as write_file:
#     json.dump(numpyData, write_file, cls=NumpyArrayEncoder)

# encodedNumpyData = json.dumps(numpyData, cls=NumpyArrayEncoder)  # use dump() to write array into file
# print("Printing JSON serialized NumPy array")
# print(encodedNumpyData)





# # les gribs complets sont disponibles en heure d'ete à
# # 13h(gfs06) - 19(gfs12) -  01(gfs18) - 07 h (gfs00)
# # les gribs complets sont disponibles en heure d'hiver à
# # 12h(gfs06) - 18(gfs12) -  00(gfs18) - 06 h (gfs00)

# # renvoie le chemin absolu du repertoire courant ici /home/jphe/PycharmProjects/VR_version2
# basedir = os.path.abspath(os.path.dirname(__file__))


# # leftlon, rightlon, toplat, bottomlat = 0, 360, 90, -90

# # t = time.localtime()
# # utc = time.gmtime()
# # decalage_h = t[3] - utc[3]
# # heures = [0,6,12,18]
# # heure_grib = heures[((utc[3] + 19) // 6) % 4]  # heure du grib

# # dategrib_tpl=datetime(utc[0] , utc[1] , utc[2] , int(heure_grib),0, 0)
# # tig=time.mktime(dategrib_tpl.timetuple())+decalage_h*3600    #temps initial du grib en sec locales 
# # dategrib= str(dategrib_tpl) 
# # date=dategrib[0:10].replace("-","")
# # strhour=dategrib[11:13]
# # iprev = ()
# # for a in range(0, 3, 3):  # Construit le tuple des indexs des fichiers maxi 387
# #     iprev += (str(int(a / 100)) + str(int((a % 100) / 10)) + str(a % 10),)
# # GR = np.zeros((len(iprev), 181, 360),
# #                 dtype=complex)  # initialise le np array de complexes qui recoit les donnees
# # for indexprev in range(len(iprev)):  # recuperation des fichiers de 0 a 384 h
# #     prev = iprev[indexprev]

# # url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t" + strhour + "z.pgrb2.1p00.f" + \
# #                   prev + "&lev_10_m_above_ground=on&all_var=on&leftlon=" \
# #                   + str(leftlon) + "&rightlon=" + str(rightlon) + "&toplat=" + str(toplat) + "&bottomlat=" + str(
# #                 bottomlat) + "&dir=%2Fgfs." + date + "%2F" + strhour
# # print('url',url)                

# # nom_fichier = "grib_" + date + "_" + strhour + "_" + prev
# # urlretrieve(url, nom_fichier)  # recuperation des fichiers provisoires

# # print(' Enregistrement prévision {} + {} heures effectué: '.format(dategrib,prev))  # destine a suivre le chargement des previsions


# # ds = xr.open_dataset(nom_fichier, engine='cfgrib')
# # print (ds.variables)
# # print(ds.variables['u10'].data)

# # u10=2.492996

# # v10=1.077
# # vcplx=u10+v10*1j

# # vit_vent_n = np.abs(vcplx) * 1.94384
# # angle_vent = (270 - np.angle(vcplx, deg=True)) % 360


# #print (' Vitesse et angle ', vit_vent_n,angle_vent)


# # prevision par fonction

# #chargement_grib()
# tig, GR = chargement_grib()
# tic = time.time()

# print()
# print ('tig en s ',tig)
# print ('tic en s ',tic)
# print ('Ecart', (tic-tig)/3600,'h')

# tig_formate_utc = time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tig))
# tic_formate_local = time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(tic))
# print('\n Date et Heure UTC du dernier Grib             ',tig_formate_utc) 
# print(' Date et Heure locales                         ',tic_formate_local) 



# # Depart
# latitude_d = '045-00-00-N'
# longitude_d = '003-00-00-W'
# d = chaine_to_dec(latitude_d, longitude_d)  # co
# print ('latitude et longitude',d)



# # prevision avec date donnee    

# print ('\nPrévision à date et heure données \
#         \n---------------------------------')
# print('\nLatitude {:6.2f} et Longitude{:6.2f} '.format( d[1], d[0]))
# dateprev=datetime(2020 , 9 , 20, 17 ,  0)   # attention a remplir en heure locale ppour avoir la correspondance avec le gib UTC
# print ('\nDateprev : ',dateprev , ' local')
# # je peux la transformer en secondes mais ce sont des secondes locales
# dateprev_s=time.mktime(dateprev.timetuple())
# print ('dateprev_s en local ',dateprev_s )
# dateprev_formate_local = time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(dateprev_s))
# print('dateprev_formate_local',dateprev_formate_local)

# # prevision proprement dite
# vit_vent_n, angle_vent = prevision(tig, GR,dateprev_s, d[1], d[0])
# #  print('\nLe {} heure Locale Pour latitude {:6.2f} et longitude{:6.2f} '.format(dateprev_formate_local, d[1], d[0]))
# print('\tAngle du vent   {:6.1f} °'.format(angle_vent))
# print('\tVitesse du vent {:6.3f} Noeuds'.format(vit_vent_n))
# print()


# def prevision_entiers( GR, dt_h, latitude, longitude):
#     '''dt_h heure par rappport au debut du grib '''
#     res_cpx=GR[dt_h//3,int(latitude+90),int(longitude%360)]
#     vit_vent_n = np.abs(res_cpx) * 1.94384
#     angle_vent = (270 - np.angle(res_cpx, deg=True)) % 360
#     return vit_vent_n, angle_vent

# dt_h=3 
# vit_vent_n, angle_vent=prevision_entiers(GR, dt_h,d[1], d[0])

# print('\tAngle du vent   {:6.1f} °'.format(angle_vent))
# print('\tVitesse du vent {:6.3f} Noeuds'.format(vit_vent_n))


# # for dt_h in range(0,24,3):
# #     vit_vent, angle_vent=prevision_entiers(GR, dt_h,d[1], d[0])
# #     json=
# #     print (vit_vent)



# U10=GR.real
# V10=GR.imag


# print (U10[0,1,0])
# print (V10[0,1,0])


