
// fonctions jquery au chargement du document

// classes pour les icones
var LeafletIcon=L.Icon.extend({
    options:{
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    shadowSize: [41, 41],
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34] 
            }
    });

    var greenIcon = new LeafletIcon({ iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png'});
    var blackIcon = new LeafletIcon({ iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-black.png'});    
    var redIcon   = new LeafletIcon({ iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png'});   




$( function() {
    var spinner = $( "#twaspin" ).spinner();
    spinner.spinner( "value", 45 );
  


} );