from datetime import datetime
import time
import os
from dateutil import tz
basedir = os.path.abspath(os.path.dirname(__file__))
#local = tz.gettz() # Local time
#ET = tz.gettz('Europe/Paris') # European time


def datemoinsunjour(date):
    '''date est sous la forme yyyymmdd par ex 20201102'''
    '''renvoie le jour precedent sous lameme forme '''
    year=int(date[0:4])
    month=int(date[4:6])
    day=int(date [6:8])
    datejour=datetime(year, month, day ,0,0,0)
    djs=time.mktime(datejour.timetuple())-24*3600   # moins un jour
    datem1 = time.strftime("%Y%m%d", time.localtime(djs))
    return datem1


print('\n')
print('\n')
print ('Exemples')
#temps instantanés
t = time.localtime()    #retour sous forme tuple
utc = time.gmtime()     #retour sous forme tuple
# peut etre utilise par 
print ('exemple heure : t[3]',t[3])
print ('temps en s',time.time())

print ('t',t)
print('utc',utc)

#decalage horaire 
print ('\nDecalage en heures', t[3]-utc[3])

#construction d'une date
heure_grib=6
dategrib =datetime(utc[0] , utc[1] , utc[2] , int(heure_grib),0, 0)
print ('\nDategrib : ',dategrib)

# transformation de cette date en s 
t1=time.mktime(dategrib.timetuple())
print ('t1',t1 )

t3 = time.localtime(t1)##retour sous forme tuple
print ('t3',t3)   
t4 = time.gmtime(t1)##retour sous forme tuple avec deux heures en moins mais ce n'est qu'un formatage
print ('t4',t4)   



# pour mon grib 
# je constitue la presentation de l'heure du grib
dategrib =datetime(utc[0] , utc[1] , utc[2] , int(heure_grib),0, 0)
print ('\nDategrib : ',dategrib)

# je peux la transformer en secondes mais ce sont des secondes locales
tig=time.mktime(dategrib.timetuple())
print ('tig en local ',tig )

# si je les transforme en date 
t5 = time.localtime(tig)
print('tig sous forme tuple',t5)
tig_formate_utc = time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tig))
print('tig_formate_utc',tig_formate_utc)


tig_formate_local = time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(tig))
print('tig_formate_local',tig_formate_local)

print()

# ecart en secondes entre le tempts instantané et le temps du grib


tic=time.time()                                    # temps instantane en secondes locales
# date et heure simulation chargement grib************************************
datejour            = datetime(2020,11,20, 11,6,0)                  # en heures locales
# *************************************************************************************
dateessai=datejour
dateessai_sec        = time.mktime(dateessai.timetuple())  
dateessai_sec=tic           # transformation en secondes
dateessai_tuple      = time.gmtime(dateessai_sec)                      # transformation en tuple utc
# verification
dateessai_formate = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(dateessai_sec))
tic_formate    = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(tic))
dateessai_formatcourt=time.strftime("%Y%m%d", time.localtime(dateessai_sec))
dateessai_formatcourt_utc=time.strftime("%Y%m%d", time.gmtime(dateessai_sec))
tic_formatcourt=time.strftime("%Y%m%d", time.localtime(tic))
print ('date formatee ',dateessai_formate)
print(tic_formate)
print('dateessaiformatcourt',dateessai_formatcourt)
print('dateessaiformatcourt_utc',dateessai_formatcourt_utc)

print(tic_formatcourt)
print(dateessai_tuple)