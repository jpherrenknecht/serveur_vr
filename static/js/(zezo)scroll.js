"use strict";

var mousex = 0;
var mousey = 0;
var grabx = 0;
var graby = 0;
var moved = 0;

var canvas = null;
var boat_data = null;
var track_canvas = null;
var container = null;
var tiles = null;
var winds = null;
var iso = null;
var dragobj = null;
var span_lat = null;
var span_lon = null;
var span_dd1 = null;
var span_dd2 = null;
var span_info = null;
var span_wind = null;
var wind_info = null;
var wi_top = 27;
var help_div = null;
var is_ie = 0;
var is_mac = 0;
var use_transform = undefined;
var update_info = 0;
var show_tracks = false;
// var updating_tracks = false;

var width = 0;
var height = 0;

var popup = null;

var wind_tile_size = 720;
var zoom_levels = [8, 16, 32, 64, 128, 256, 512];

function id(i)
{ 
	return document.getElementById(i); 
}

function debug_status(text) {
	var div = id("debug_div");
	if (div) {
		div.innerHTML = text;
	}
}

function px(x) {
	return Math.round(x) + 'px';
}

function do_scroll() {
	if (use_transform !== undefined) {
		var x = px(scroll_x);
		var y = px(scroll_y);
		canvas.style[use_transform] = "translate(" + x + "," + y + ")";
	} else {
		canvas.style.left=px(Math.floor(scroll_x+0.5));
		canvas.style.top=px(Math.floor(scroll_y+0.5));
	}
}


function getMouseXY(e)
{
	e = e || window.event;
	if (e && e.type != 'keydown') {
		if (e.pageX || e.pageY) {
			mousex = e.pageX;
			mousey = e.pageY;
		} else if (e.clientX || e.clientY) {
			mousex = e.clientX + document.body.scrollLeft + document.documentElement.scrollLeft;
			mousey = e.clientY + document.body.scrollTop + document.documentElement.scrollTop;
		}
	}

}

function boat_q(e,obj)
{
    var characterCode;
    if(e && e.which){
        characterCode = e.which;
    }
    else{
        e = window.event;
        characterCode = e.keyCode;
    }
    if(characterCode == 13){
        replace_div('boat=' + obj.value);
    }
    return true;
}


function minmax18 (obj)
{
    if (obj.style.height !== '') {
        obj.style.height = '';
    } else {
                obj.style.height = '18px';
        }
        return false;
}


function dec2dm(ind)
{
	var integer,rest;
	ind = Math.abs(ind);
	integer = Math.floor(ind);
	rest = Math.floor(((ind - integer) * 60)*10)/10;
	return String(integer) + '&deg;' + (rest < 9?'0':'') + String(rest) + (rest.toString().indexOf('.') < 0 ? '.0': '');
}

function xy2ll(xi, yi)
{
	var x, y, newx, newy;

	x = xi || width / 2;
	y = yi || height / 2;

	newy = (90 * scale - (y - scroll_y)) / scale;
	newx = (x - scroll_x) / scale;

	if (newx > 180) {
		newx -= 360;
	} else if (newx < -180) {
		newx += 360;
	}
	return [newx, newy];
}

function update_wind(pos) {
	var a = get_interp_wind(pos[0],90-pos[1],(wind_time==0)?grib_steps:"current_wind");
	wind_info.style.top = px(-scroll_y + mousey - wi_top);
	wind_info.style.left = px(-scroll_x + mousex + 7 - 150 * (pos[0] < boat_lon));
	var speed = (Math.round(a[0]*100/1.852)/100).toString();
	var pp = speed.indexOf('.');
	if (pp < 0) {
		speed += '.00';
	} else if (pp > speed.length - 3) {
		speed += '0';
	}	
	span_wind.innerHTML = a[1] + '&deg;&nbsp;' + speed + 'kt';
}

function update_lat_lon(e)
{
    getMouseXY(e);
    var pos = xy2ll(mousex, mousey);
	if (span_wind !== null) {
		update_wind(pos);
	}
	if (mobile) {
		pos = xy2ll(width/2, height/2);
	}
	if(span_lat !== null) {
		span_lon.innerHTML = dec2dm(pos[0]) + (pos[0] > 0 ? '\u2032E': '\u2032W ');
		span_lat.innerHTML = (Math.abs(pos[1]) < 10?' ':'') + dec2dm(pos[1]) + (pos[1] > 0 ? '\u2032N': '\u2032S ');
		if (span_dd1 !== null) span_dd1.innerHTML = crsdist(boat_lat,boat_lon,pos[1],pos[0]);
		if (span_dd1 !== null) span_dd2.innerHTML = crsdist(pos[1],pos[0],goal_lat,goal_lon);
    }
	if (!dragobj) {
//		setTimeout(function() {update_tracks(pos[1], pos[0]);}, 0);
		update_tracks(pos[1], pos[0]);
	}
	return true;
}

function show_polars() {
	var pos;
	if (mobile) {
		pos = xy2ll();
	} else {
		pos = xy2ll(mousex,mousey);
	}
	var wi = get_interp_wind(pos[0],90-pos[1], grib_steps);

	var win = window.open("polars.html?opt=" + pro_options + "wind=" + (wi[0] / 1.852), 'vor_polars');
//	var win = window.open("http://sail.zezo.org/vor/polars.html" + (use_pro?"":"?pro=0"), 'vor_polars');
	win.focus();
}

function mouse_over(e) {
	if (!update_info) {
		return;
	}
	getMouseXY(e);
	if (wind_info) {
		wind_info.style.display='block';
	}
}

function mouse_out(e) {
	var rt = e.toElement || e.relatedTarget;
	while (rt && rt != container && rt.nodeName != 'HTML') {
		rt = rt.parentNode;
	}	
	if (rt == container) {
		 return;
	}
	if (dragobj) {
		drop(e);
		return cancel_event(e);
	}
	if (wind_info) {
		wind_info.style.display='none';
	}
}

function cancel_update() {
	update_info = 0;
	if (!mobile) 
		removeDocListener("mousemove",update_lat_lon);
	if (wind_info && !dragobj) {
		wind_info.style.display='none';
	}
}

function resume_update() {
	update_info = 1;
	if (!mobile)
		addDocListener("mousemove",update_lat_lon);
	if (wind_info) {
		update_lat_lon();
		wind_info.style.display='block';
	}
}

function replace_div(q)
{
	var opt = pro_options;
	canvas.style.cursor = "wait";
//	document.body.style.cursor='wait';
	window.location.replace('chart.pl?sid=' + session_id + '&o=' + opt +
		'&wind=' + (wind_time) + '&' + q);
}	

function set_days(ndays)
{
	var pos = xy2ll();
	days = ndays;
	id('new_nav').style.cursor = 'wait';
	replace_div('days=' + days);
}

function select_zoom(obj) {
	zoom_bar(8 << obj.selectedIndex);
}

function set_algo(algo) {
	popup.style.display="none";
	replace_div("algo="+algo);
}

function zoom(newscale, xi, yi)
{
	var pos = xy2ll(xi, yi);
	id('new_nav').style.cursor = "wait";
	replace_div('clon=' + pos[0] + '&clat=' + pos[1] + '&scale=' + newscale);
}
function zoom_bar(s)
{
	zoom(s, width / 2, height / 2);
}

function zoom_in(x, y) 
{
	var i = zoom_levels.indexOf(scale);
	if (i < 6 && i >= 0) {
		zoom(zoom_levels[i + 1], x, y);
	}	
}

function zoom_out(x, y)
{
	var i = zoom_levels.indexOf(scale);
	if (i > 0) {
		zoom(zoom_levels[i - 1], x, y);
	}
}

function over(e, o)
{
	e = e || window.event;
	o.className = 'menuitem selectedmenuitem';
	return cancel_mo(e);
}

function out(e,o)
{
	e = e || window.event;
	o.className = 'menuitem';
	return cancel_mo(e);
}

function in_pos(obj, offset)
// display menu at mouse pointer taking care of borders
{
	if (mousex < width - obj.offsetWidth - offset) {
		obj.style.left = (mousex + offset) + 'px';
	} else {
		obj.style.left = (mousex - offset - obj.offsetWidth) + 'px';
	}
	if (mousey < height - obj.offsetHeight) {
		obj.style.top = mousey + 'px';
	} else {
		obj.style.top = (mousey - offset - obj.offsetHeight) + 'px';
	}
}

function show_context(e)
{	
	return show_popup(e, "cmenu");
}

function show_algo(e)
{
	mousex = id("algo").offsetLeft;
	return show_popup(e, "amenu");
}


function ie_mouseup() {
	document.body.onmouseup = null;
	document.body.onmousedown = hide_popup;
}

function hide_popup()
{
	if (popup) {
		popup.style.display="none";
	}
	document.body.onmousedown=null;
	popup = null;
	resume_update();
	return false;
}

function show_popup(e, element)
{
	popup = id(element);
	popup.style.display="block";
	in_pos(popup,0);
	if (is_ie) {
		document.body.onmouseup = ie_mouseup;
	} else {
		document.body.onmousedown = hide_popup;
	}
	cancel_update();
	return cancel_event(e);
}

function make_visible()
{
	this.style.visibility="visible";
}

function load_image(x,y,layer,tile_size, in_image)
{
	var canvas_wind = (layer == winds && w_canvas_c != null);
	var extra_url = '';
	var lon, lat, baseurl, image;
	lon = x * tile_size / scale;
	lat = y * tile_size / scale;
	if (lon >= 360 || lon <-360) {
		return;
	}
	if (lon < 0) {
		lon = 360 + lon;
	}
	if (!in_image) {	
		image = document.createElement(canvas_wind?'CANVAS':'IMG');
		image.style.position="absolute";
		image.style.display="block";
		if (!canvas_wind) {
			image.style.visibility="hidden";
			image.onload = make_visible;
			image.style.width=tile_size + 'px';
			image.style.height=tile_size + 'px';
		} else {
			image.width = tile_size;
			image.height = tile_size;
		}
		image.style.left = px(image.xpos = tile_size * x);
		image.style.top = px(image.ypos = tile_size * y);
		layer.appendChild(image);
	} else {
		image = in_image;
	}
	if (layer == tiles) {
		baseurl = "http://i.zezo.org/tilest_"+scale+"/";
	} else if (layer === iso) {
		baseurl = "http://i.zezo.org/iso/" + iso_id + '_';
	} else {
		if (canvas_wind) {
			plot_winds(image, (in_image === null)?0:1);
			return;
		}
		baseurl = "http://i.zezo.org/winds/" + wind_time + "/" + scale + "/";
/* DST
		var wind_diff = 0;
		var hour = new Date().getUTCHours();
		if(hour == 6 || hour == 18) {
			wind_diff = 12;
			extra_url = '?12';
		}
		baseurl = "http://i.zezo.org/winds/" + (wind_time + wind_diff) + "/" + scale + "/";
*/
	}
	image.src = baseurl + lon+"_" + lat + ".png" + extra_url;
}
	
function fill(layer,tile_size,replace)
{
	var i,x,y,vp_top,vp_bottom,vp_left,vp_right,grid,count,obj,border;
	grid = [];

	vp_left = Math.floor(-scroll_x/tile_size);
	vp_right = Math.floor((-scroll_x + width)/tile_size);

	vp_top = Math.floor(-scroll_y/tile_size);
	vp_bottom = Math.floor((height - scroll_y)/tile_size);

	if (vp_top < 0) { 
		vp_top = 0;
	}

	if (vp_bottom >= 180*scale/tile_size) {
		vp_bottom = 180*scale/tile_size -1;
	}
	
	for (x = vp_left; x<= vp_right; x++){
		grid[x]=[];
		for (y = vp_top; y<= vp_bottom; y++) {
			if (layer === tiles || layer == winds || ( x >= iso_minx && x < iso_maxx && y >= iso_miny && y < iso_maxy)) {
				grid[x][y] = 1;
			}
		}
	}
	
	for (i = layer.childNodes.length - 1; i >= 0; i--) {
		obj = layer.childNodes[i]; 
		if (obj && (obj.nodeName === "CANVAS" || obj.nodeName === "IMG")) {	
			x = Math.floor(obj.offsetLeft/tile_size);
			y = Math.floor(obj.offsetTop/tile_size);
			if ( grid[x] && grid[x][y]) {
				grid[x][y] = obj;
			} else {
				layer.removeChild(obj);
			}
		}
	}


	for (x = vp_left; x<= vp_right; x++){
		for (y = vp_top; y<= vp_bottom; y++) {
			if (replace && grid[x][y] !== 1) {
				load_image(x,y,layer,tile_size,grid[x][y]);
			} else if(grid[x][y] === 1) {
				load_image(x,y,layer,tile_size,null);
			} // else it is there and correct
		}
	}
}

function cleanup_layer(layer)
{
	var i,obj;
	for (i = layer.childNodes.length - 1; i >= 0; i--) {
		obj = layer.childNodes[i];
		if (obj.tagName==='IMG' || obj.tagName ==='CANVAS') {	
			 layer.removeChild(obj);
		}
	}
}

function show_canvas_wind() {
	winds.style.display="block";
	fill(winds,wind_tile_size,true);
}

function store_option(option, value) {
	if (sessionStorage) {
		localStorage[option] = value;
		sessionStorage[option] = value;
	}
}

function wind_display(type) {
	if (wind_style == type) {
		return;
	}
	wind_style = type;
	if (type == 0) {
		cleanup_layer(winds);
	} else {
		if (w_canvas_c) {
			show_canvas_wind();
		} else { 
			fill(winds,wind_tile_size,true);
		}
	}
	body_color();
	store_option("wind_type",type);
}
		
function show_wind(h)
{
	if (wind_time == h) {
		return;
	}
	wind_time = h;
	winds.style.display='block';
	if (w_canvas_c) {
		load_wind(wind_time);
	} else {
		fill(winds,wind_tile_size,true);
	}
	id("hours")[wind_time/3].selected=true;
}

function next_wind() {
	if (wind_time < 384) {
		show_wind(wind_time + 3);
	}
}

function prev_wind() {
	if (wind_time >= 3) {
		show_wind(wind_time - 3);
	} 
}

function handle_key(e)
{ 
	var characterCode;
	var t;
	if(e && e.which){ 
		characterCode = e.which;
		t = e.target.nodeName;
	}
	else{
		e = window.event;
		t = e.srcElement.nodeName;
		characterCode = e.keyCode;
	}
	if (t == 'INPUT' || (t == 'SELECT' && characterCode >= 37 && characterCode <= 40)) {
		return;
	}
	if (characterCode > 48 && characterCode <58) {
		set_days(characterCode - 48);
		return true;
	} 
	switch(characterCode){ 
		case 37: do_drag(width/4,0);
		break;
		case 38: do_drag(0,height/4);
		break;
		case 39: do_drag(-width/4,0);
		break;
		case 40: do_drag(0,-height/4);
		break;
		case 61:
		case 107:
		case 187: if (mousex && mousey) {
					zoom_in((width / 2 + mousex) / 2,(height / 2 + mousey) / 2);
				} else {
					zoom_in(width / 2, height / 2);
		}
			break;
		case 45: 
		case 109: 
		case 173: // ff 
		case 189: if (mousex && mousey) {
				zoom_out(width-mousex,height-mousey);
			} else {
				zoom_out(width / 2, height / 2);
		}
		break;
		case 48: show_wind(0);
		break;
		case 188: prev_wind();
		break;
		case 190: next_wind();
		break;
	}
	return false;
}

function fill_layers()
{
		fill(tiles,720);
		fill(iso,360);
		if (wind_style > 0 && (!w_canvas_c || wind_array["current_wind"])) { // old-style or no wind data yet
			winds.style.display="block";
			fill(winds,wind_tile_size);
		}
}

function toggle_options(i) {
	var pos = xy2ll();
	pro_options ^= i;
	replace_div('clon=' + pos[0] + '&clat=' + pos[1]);
}

function full_options(i) {
	var pos = xy2ll();
	if (i) {
		pro_options &= 10;
	} else {
		pro_options  |= 244;
	}
	replace_div('clon=' + pos[0] + '&clat=' + pos[1]);
}

function toggle_gates(e) {
	var pos = xy2ll();
	ignore_gates = !ignore_gates;
	replace_div('clon=' + pos[0] + '&clat=' + pos[1]);
}


function drop(e)
{
	if (!e) {
		e = window.event;
	}
//	console.log(e.type);
	if (dragobj) {
		if (e.type === "touchend") {	
			dragobj.ontouchmove = null;
			dragobj.ontouchend = null;
	 	} else {
			dragobj.onmousemove = null;
			dragobj.onmouseup = null;
		}
		dragobj.style.cursor = 'default';
		dragobj = null;
	}
	do_scroll();
	fill_layers();
	init_tracks();
	resume_update();
	return false;
}

function wheel(e)
{
	var delta = 0;
	if (!e) {
		e = window.event;
	}
	getMouseXY(e);
	if (mousex > 2000 || mousey > 2000) { //FF2
		mousex = width/2;
		mousey = height/2;
	}
	if (e.wheelDelta) { /* IE/Opera. */
		delta = e.wheelDelta/80;
	} else if (e.detail) {
		delta = -e.detail/3;
	}
	cancel_event(e);
	return delta;
}

function wheel_zoom(e) {
	var delta = wheel(e);
	if (delta >= 1 ) {	
		zoom_in((width / 2 + mousex) / 2,(height / 2 + mousey) / 2);
	} else if (delta <= 1) {
		zoom_out(width-mousex,height-mousey);
	}
	return false;
}

function wheel_wind(e) {
	var delta = wheel(e);
	if (delta > 0) {
		next_wind();
	} else { 
		prev_wind();
	}
	return false;
}

function resize(no_fill)
{	
	width = Math.floor(container.offsetWidth/2) * 2;
	height = Math.floor(container.offsetHeight/2) * 2;
	if (mobile) {
		var crosshair = id("crosshair");
		crosshair.style.top = px(height/2-100);
		crosshair.style.left = px(width/2-100);
		crosshair.style.visibility="visible";
	}
	if (no_fill)
		return;
	init_tracks();
	fill_layers();
}

function recenter()
{
	scroll_x += width / 2;
	scroll_y += height / 2;

	if (scroll_x >= 270*scale) {
		scroll_x = 270*scale;
	} else if (scroll_x < -(270*scale-width)) {
		scroll_x = -(270*scale-width);
	}
	if (scroll_y >= 0) {
		scroll_y = 0;
	} else if (scroll_y < -(180*scale-height)) {
		scroll_y = -(180*scale-height);
	}
	do_scroll();	
}

function gc_dir(lat, lon, dlat, dlon) {
	var a = crsdist_num(lat, lon, dlat, dlon);
	return Math.round(a[0] * 180/Math.PI);
}

function adjust_speed(lat,bss) {
	if (lat >= -60) 
		return;
	if (lat <= -61) 
		bss[0] /= 4;
	else 
		bss[0] *= (0.75 + (lat + 60) / 2);
}

function plot_track(c, steps, color, type,  dlat, dlon) {
	var angle = gc_dir(boat_lat, boat_lon, dlat, dlon);
		
	var pos = [boat_lon * Math.PI/180, boat_lat * Math.PI/180];  // in radians
	var i, x, y, lat, lon, wind;
	var thick_steps = 36;

	var wind = get_interp_wind(boat_lon, 90-boat_lat, grib_steps + 1);
	
	var twa = wind[1] - angle;
	var	bss = get_boat_speed((360 + angle - wind[1])%360, wind[0]);
	var sail = bss[1];
//	adjust_speed(boat_lat,bss);
	
//	if (steps <= 216 - grib_steps && type === "gc") {
//		steps -= grib_steps;
//	}

	if (type === "") {
		span_wind.innerHTML += '<br><span style="white-space: nowrap; font-weight: bold"><span style="color: red;"> HDG:&nbsp;' + angle + '</span><span style="color:green"> TWA:&nbsp;' + angle_diff(0,twa) + '</span></span>';
	}
	if (type !== "gc") {
		c.lineWidth = 1.5;
	} else {
		c.lineWidth = 1;
	}

	c.strokeStyle = color;

	c.beginPath();
	c.moveTo(boat_lon * scale,(90-boat_lat) * scale);

//	debug_status((360 + angle - wind[1])%360 + ' ' + wind[0] + ' ' + bss);

	for (i = grib_steps + 1 ; i <= steps; i++) {
		pos = gc_destination(pos[0],pos[1], angle * Math.PI/180, bss[0]/6);

		lon = pos[0] * 180/Math.PI;
		lat = pos[1] * 180/Math.PI;

		if (boat_lon > 90 && lon < -90) 
			lon += 360;

		x = lon * scale;
		y = (90-lat) * scale;

		c.lineTo(x, y);

		if (!(i%6)) {
			c.arc(x, y, i%18?1.6:2.5,  (angle + 90)/180 * Math.PI, (angle+449)/180 * Math.PI,0);
			c.moveTo(x, y);
		} else if (scale >= 256 && type !== "gc") {
			c.strokeRect(x-0.75,y-0.75,1.5,1.5);
		}
		if (type === "gc") {
			var a = gc_dir(lat, lon, dlat, dlon);
			if (angle_diff(a, angle) > 90) {
				break;
			} else {
				angle = a;
			}
		}

		wind = get_interp_wind(lon, 90 - lat, i + 1);
		if (wind[0] < 0) {
			break;
		}

		if (type === "twa") 
			angle = (wind[1] - twa) % 360;

		bss = get_boat_speed((360 + angle - wind[1])%360, wind[0]);
//		adjust_speed(lat,bss);
		if (sail != bss[1] && type !== "gc") {
			sail = bss[1];
			c.strokeRect(x-3, y-3, 6, 6);
		}
		if (i == thick_steps && type !== "gc") {
			c.stroke();
			c.lineWidth = 1;
			c.beginPath();
			c.moveTo(x,y);
		}
	}
	c.stroke();
	return i;
}

function update_tracks(dlat, dlon) {
	var steps;
	if (!show_tracks) 
		return;
	track_canvas.width = width;
	var c = track_canvas.getContext("2d");
	c.translate(Math.floor(scroll_x+0.5),Math.floor(scroll_y+0.5));
	steps = plot_track(c, 144 + grib_steps, "blue", "gc", dlat, dlon); // gc
	plot_track(c, steps,  "green", "twa", dlat, dlon); // twa
	plot_track(c, steps, "red",  "", dlat, dlon); // heading
}


function init_tracks() {
	if (!show_tracks) 
		return;
	track_canvas.style.display="block";
	track_canvas.style.left=px(-Math.floor(scroll_x+0.5));
	track_canvas.style.top=px(-Math.floor(scroll_y+0.5));
	track_canvas.width = width;
	track_canvas.height = height;
}

function toggle_tracks() {
	show_tracks = !show_tracks;
	store_option("plot_track", show_tracks);

	if (show_tracks) {
		id("track_icon").src="img/icon_track_red.png";
		if (!polar_data)  {
			load_polars((pro_options >> 5) & 7);
			load_array_winds();
		}	
		wi_top = 45;
		init_tracks();
		update_lat_lon();
	}
	else {
		id("track_icon").src="img/icon_track_gray.png";
		track_canvas.style.display="none";
		wi_top = 27;
	}
}

function set_touch_pos(a,b,c,d) {
        mousex = width/2;
        mousey = height/2;
        set_pos(a,b,c,d);
}

function set_pos(is_dest,is_xy,lon,lat)
{
	var pos, cpos; 
	cpos = xy2ll();
	if (is_xy) {
		if(!lon || !lat) {
			pos = xy2ll(mousex,mousey);
		} else {
		 	pos = xy2ll(lon,lat);
		}
	} else {
		pos = [lon,lat];
	}
	if (is_dest) {
		replace_div('tlon='+pos[0]+'&tlat='+pos[1]+'&clon='+cpos[0]+'&clat='+cpos[1]);
	} else {
		replace_div('lon='+pos[0]+'&lat='+pos[1]+'&clon='+cpos[0]+'&clat='+cpos[1]);
	}
}

function smart_recenter() {
		scroll_x = width/2 * (1 - 0.85 * Math.sin(boat_heading * Math.PI/180)) - scale * boat_lon;
		scroll_y = height/2 * (1 + 0.85 * Math.cos(boat_heading * Math.PI/180)) + scale * (boat_lat - 90);
}

function find_boat() {
	smart_recenter();
	var pos = xy2ll(0,0);
	replace_div('clon='+pos[0]+'&clat='+pos[1]);
}

function check_transform() {
	var properties = [
		'transform',
		'WebkitTransform',
		'msTransform',
		'MozTransform',
		'OTransform'
	];
	var p;
	while (p = properties.shift()) {
		if (typeof canvas.style[p] != 'undefined') {
			return p;
		}
	}
}
	
function check_browser() {
	if(navigator.appName === "Microsoft Internet Explorer") {
		is_ie=1;
		if(!Array.indexOf){
			Array.prototype.indexOf = function(obj){
				for(var i=0; i<this.length; i++){
		 			if(this[i] == obj){
						return i;
					}
				}
				return -1;
			};
		}
	} else if (navigator.userAgent.indexOf('Mac OS') > 0) {
		is_mac = 1;
	}
}

function body_color() {
	var color;
	if (wind_style <=1 ) {
		color="#E0F0ff";
	} else { 
		color="white";
	}
	document.body.style.backgroundColor = color;
}

function load_config() {
	if (sessionStorage) {
	var wt = sessionStorage.wind_type || localStorage.wind_type;
	if (wt) {
			wind_style = parseInt(wt);
		}
	} else {
		wind_style = 1;
	}
	body_color();
}

function load_track_config() {
	var sw = sessionStorage["plot_track"] || localStorage["plot_track"];
	if (!sw || sw === "true") {
		toggle_tracks();
	} 
}

function init()
{
	load_config();


	container = id("vp_container");
	canvas = id('vp_canvas');
	track_canvas = id('track_canvas');
	winds = id('winds_layer');
	boat_data = id('boat_data');

	if (init_wind()) {
		span_wind = id("wind_data");
		wind_info = id("wind_info");
	}

	check_browser();
	use_transform = check_transform();
	tiles = id('tile_layer');
	iso = id('iso_layer');
	span_lat = id('span_lat');
	span_lon = id('span_lon');
	span_dd1 = id('span_dd1');
	span_dd2 = id('span_dd2');
	help_div = id('help_div');
	document.body.onresize=resize;
	addListener(canvas,"DOMMouseScroll",wheel_zoom);
	addListener(canvas, "mousewheel",wheel_zoom);
	addListener(container, "mouseout",mouse_out);
	addListener(container, "mouseover",mouse_over);
	if (is_ie) {
		addDocListener("contextmenu",show_context);
	} else {
		addDocListener("contextmenu",cancel_event);
	}
	addDocListener("keydown", handle_key);
	addListener(canvas,"touchstart", grab);
	addListener(canvas,"touchcancel", drop);
	document.onselectstart = function() {return false;};
	document.ondragstart = function() {return false;};
	if (!is_ie) {
		canvas.focus();
	}

    if (boat_data !== null) {
            boat_data.style.display = 'block';
            minmax18(boat_data);
    }

	resize(true);
	recenter();
    id('new_nav').style.cursor = 'default';
	canvas.style.cursor = 'default';
//	document.body.style.cursor = 'default';
	fill_layers();
	if (w_canvas_c) {
		load_track_config();
	}		
	resume_update();
}

function updi(event,info,wi)
{
	if (dragobj) {
		return;
	}
	var w = wi||'200px';
	getMouseXY(event);
	if(help_div === null) {
		return;
	}	
	help_div.innerHTML = info;
	help_div.style.width = w;
	help_div.style.display = 'block';
	in_pos(help_div,12);
	help_div.style.zIndex=20;
}

function cleari()
{
	help_div.style.display = 'none';
}

function do_drag(dx,dy) {
	scroll_x += dx;
	scroll_y += dy;
	if (scroll_x >= 360*scale) { 
		scroll_x = 360*scale;
	} else if (scroll_x < -(360*scale-width)) {
		scroll_x = -(360*scale-width);
	}
	if (scroll_y >= 0) { 
		scroll_y = 0; 
	} else if (scroll_y < -(180*scale-height)) {
		scroll_y = -(180*scale-height);
	}
	if (!mobile)
		fill_layers(); 
	do_scroll();
	update_lat_lon(null);
}

function drag(e) 
{
	if (dragobj) {
		if (e && e.type === "touchmove") {
			if (e.touches.length == 1) {
				e = e.touches[0];
			} else {
				return true;
			}
		}
		getMouseXY(e);
		do_drag(mousex - grabx, mousey - graby);
		grabx = mousex;
		graby = mousey;
		moved = 1;
	}
	return false; 
}

function grab(e)
{
	if (popup !== null) {
		return true;
	}
	moved = 0;
	if (e.type === "touchstart") {
		if (e.touches.length == 1 && e.touches[0].target.className !== 'abs' && popup == null) {
			var touch = e.touches[0]; // Get the information for finger #1
			getMouseXY(touch);
			dragobj = canvas;
			dragobj.ontouchmove = drag;
			dragobj.ontouchend = drop;
			dragobj.ontouchcancel = drop;
			grabx = mousex;
			graby = mousey;
		} else {
			dragobj.ontouchmove = null;
			return true;
		}
	} else {
		var button = e.button || e.which;
		update_lat_lon(e);
		if (button == 1) {
			if (is_mac && e.ctrlKey) {
				return show_context(e);
			}
			if (e.shiftKey||e.ctrlKey||e.altKey) {
				if (e.shiftKey) {
					set_pos(0,1);
				} else {
					set_pos(1,1);
				}
			} else { // button 1, no modifiers
				dragobj = canvas;
				cancel_update();
				dragobj.onmousemove = drag;
				dragobj.onmouseup = drop;
				dragobj.style.cursor = 'move';
				grabx = mousex;
				graby = mousey;
				return true;
			}
		} else if (button == 2) {
				return show_context(e);
		}
	}
	return cancel_event(e);
}
