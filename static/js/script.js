

const options = {
    // Required: API key
   // key: 'PsLAtXpsPTZexBwUkO7Mx5I', // REPLACE WITH YOUR KEY !!!
    key: 'ydO74Xuxv2WWOEShDpel1kaiae8zCnLO',
    // Put additional console output

    //key: 'ql9GMEGFJjsQ4zhfsZXV4ELo2D09AsDV',
    //verbose: true,

    // Optional: Initial state of the map
    lat: 50.4,
    lon: 1,
    zoom: 10,
};

// Initialize Windy API
windyInit(options, windyAPI => {
    // windyAPI is ready, and contain 'map', 'store',
    // 'picker' and other usefull stuff
    //import map from '@windy/map';
    const { map } = windyAPI;
    // .map is instance of Leaflet map
    //var map = L.map('map').setView([51.505, -0.09], 13);
    L.popup()
        .setLatLng([50.4, 14.3])
        .setContent('Hello World +1492')
        .openOn(map);
    L.marker([51.5, -0.09]).addTo(map)
        
});
