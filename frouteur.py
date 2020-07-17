

def frouteur(latdep,longdep,latar,longar):
    import folium
    import webbrowser



    #import webbrowser
    # Initialisation carte folium **************************************************************
    m = folium.Map( location=[latdep,longdep],  zoom_start=5)
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

    lat=10
    long=20
    frouteur(lat,long)    