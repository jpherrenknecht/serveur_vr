
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



    $.get("courses.json", function(data)       // courses json est dans le repertoire principal
        {
   const obj= JSON.parse(data);
   nomcourse= obj[course]["nom"]
   console.log('Nom de la course :'+ nomcourse)
   bateau=obj[course]["bateau"]
   console.log('Bateau :'+ bateau)
    });


    $( function()
     {

        var spinnertwa= $( "#spinner_twa" ).spinner()
            spinnertwa.spinner({ min :-180 , max :+180  , stop:function(e,ui){var twa= spinnertwa.spinner("value"); console.log(spinnertwa.spinner("value")); }   });
            spinnertwa.spinner("value", 45); 
            


        var spinnerhdg= $( "#spinner_hdg" ).spinner()
            spinnerhdg.spinner({  min :0 , max :360 });
            spinnerhdg.spinner("value", 60); 
        // $("#nomcourse").innerHTML="<h2>"+nomcourse+"</h2>"
        //$("#spinner_twa").on("spinstop", function(){ alert($(this).spinner('value'));  } );

       // $("#spinner_twa").on("spinstop", function(){ alert($(this).spinner('value'));  } );  // fonctionne 
       //document.getElementById('nomcourse').innerHTML="<h2>"+nomcourse+"</h2>"



    } );