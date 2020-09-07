"use strict";

function id(t) {
    return document.getElementById(t);
}

var R = 300;
var polar_data = null;
var pg = id("polar_graph");
var c = pg.getContext("2d");
var boat_speeds = [];
var options = 0;

var wind_speed = 10;
var up_vmg = 0;
var down_vmg = 0;
var up_twa = 0;
var down_twa = 0;
var twa = 0;
var p_canvas = null;

var colors = ["#ff0000", "#00ff00", "#0000ff", "#ff2000", "#00a000", "#b00000", "#d77900"]

function cancel_event(e) {
    e = e || window.event;
    if (!e.target) {
        return false; //IE shit
    }
    if (e.target.tagName == "INPUT") {
        return true;
    }
    if (e.preventDefault) {
        e.preventDefault();
    }
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    e.cancelBubble = true;
    return false;
}

function show_speed(evt) {
    if (evt) {
        var pos = getMousePos(id("polar_graph"), evt);
        twa = Math.round(Math.atan2(pos.x, R + 20 - pos.y) * 180 / Math.PI);
    }
    var bs = get_boat_speed(twa, wind_speed * 1.852);
    id("twa").innerHTML = twa + "&deg;";
    id("bs").innerHTML = (Math.round(bs[0] * 100) / 100) + " kts";
    id("vmg").innerHTML = Math.abs(Math.round(bs[0] * Math.cos(twa * Math.PI / 180) * 100) / 100) + " kts";
    id("sail").innerHTML = sails[bs[1]];
}

function foil_c(twa, ws) {
    var ct = 0;
    var cv = 0;

    if (twa <= 70) {
        return 1;
    } else if (twa < 80) {
        ct = (twa - 70) / 10;
    } else if (twa < 160) {
        ct = 1;
    } else if (twa < 170) {
        ct = (170 - twa) / 10;
    } else {
        return 1;
    }

    if (ws <= 11) {
        return 1;
    } else if (ws < 16) {
        cv = (ws - 11) / 5;
    } else if (ws < 35) {
        cv = 1;
    } else if (ws < 40) {
        cv = (40 - ws) / 5;
    } else {
        return 1;
    }

    return 1 + 0.04 * ct * cv;
}

function get_boat_speed(twa, ws) {
    if (!polar_data) return[0, 0];
    if (twa > 180) twa = 360 - twa;
    twa = Math.round(twa);
    if (ws >= 129) ws = 129;
    var ws1 = Math.floor(ws);
    var frac = ws - Math.floor(ws);
    var offset = 4 * (130 * twa + ws1);
    var bs = ((polar_data[offset + 1] << 8) | (polar_data[offset + 2])) / 100;
    var bs1 = ((polar_data[offset + 5] << 8) | (polar_data[offset + 6])) / 100;
    var sail = polar_data[offset];
	var retbs =  bs + frac * (bs1 - bs);
	if (options & 16) {
		retbs *= foil_c(twa, ws/1.852);
	}
	if (options & 256) {
		retbs *= 1.003;
	}
    return[retbs, sail];
}

function extract_polars(img) {
    if (!p_canvas) p_canvas = document.createElement('CANVAS');
    p_canvas.width = 130;
    p_canvas.height = 181;
    var c = p_canvas.getContext("2d");
    c.drawImage(img, 0, 0, 130, 181);
    polar_data = c.getImageData(0, 0, 130, 181).data;
    plot_polars(wind_speed);
}

function load_polars() {
    var polar_img = new Image();
    polar_img.onload = function() {
        extract_polars(this);
    };
    polar_img.src = "ideal_" + ((options >> 5) &  7) + ".png?1";
}

function radial(a, r) {
    var ra = (a - 90) * Math.PI / 180;
    c.moveTo(0, 0);
    c.lineTo(Math.cos(ra) * (R + 5), Math.sin(ra) * (R + 5));
    c.fillText(a, Math.cos(ra) * (R + r), Math.sin(ra) * (R + r));
}

function plot_scale() {
    c.lineWidth = 0.4;
    c.textBaseline = "middle";
    c.beginPath();
    c.translate(0.5, R + 20.5);
    for (var i = 1; i <= 5; i++) {
        c.arc(0, 0, R * i / 5, -Math.PI / 2, Math.PI / 2, false);
    }
    for (var i = 0; i <= 180; i += 15) {
        radial(i, 10);
    }
    c.stroke();
}

function calc_vmg(bs, i) {
    var vmg = bs * Math.cos(i * Math.PI / 180);
    if (vmg > up_vmg) {
        up_vmg = vmg;
        up_twa = i;
    } else if (vmg < down_vmg) {
        down_vmg = vmg;
        down_twa = i;
    }
}

function plot_polars(ws) {
    var i;
    var last_sail = -1;
    var bss = [];
    up_vmg = 0;
    down_vmg = 0;
    id("ws").value = ws;
    ws *= 1.852;
    plot_scale();
    c.lineWidth = 1;
    c.save();
    c.beginPath();
    c.moveTo(0, 0);
    for (i = 0; i <= 180; i++) {
        boat_speeds[i] = bss = get_boat_speed(i, ws);
        calc_vmg(bss[0], i);
        c.lineTo(0, -bss[0] * R / maxbs);
        if (bss[1] !== last_sail) {
            c.stroke();
            c.strokeStyle = colors[last_sail = bss[1]];
            c.beginPath();
            c.lineTo(0, -bss[0] * R / maxbs);
        }
        c.rotate(Math.PI / 180);
    }
    c.stroke();
    c.restore();
    c.beginPath();
    c.fillStyle = "red";
    radial(up_twa, maxbs);
    radial(down_twa, maxbs);
    c.strokeStyle = "red";
    c.stroke();
    id("up_twa").innerHTML = up_twa + "&deg;";
    id("up_vmg").innerHTML = (Math.round(up_vmg * 100) / 100) + " kts";
    id("down_twa").innerHTML = down_twa + "&deg;";
    id("down_vmg").innerHTML = -(Math.round(down_vmg * 100) / 100) + " kts";
    show_speed();
}

function set_speed(delta, is_abs) {
    if (is_abs) wind_speed = delta;
    else wind_speed = +parseInt(Math.round((parseFloat(wind_speed) + delta) * 100)) / 100;

    if (wind_speed <= 1) wind_speed = 1;
    if (wind_speed >= 70) wind_speed = 70;
    pg.width = pg.width;
    plot_polars(wind_speed);
}

function getMousePos(canvas, evt) {
    var rect = canvas.getBoundingClientRect();
    return {
        x: evt.clientX - rect.left,
        y: evt.clientY - rect.top
    };
}

function toggle_options(opt) {
    pg.width = pg.width;
	options ^= opt;
    load_polars();
}

id("polar_graph").addEventListener('mousemove', function(evt) {
    show_speed(evt);
    return true;
},
false);

id("polar_graph").addEventListener('touchmove', function(evt) {
    show_speed(evt.touches[0]);
    return cancel_event(evt);
},
false);

id("polar_graph").addEventListener('touchstart', function(evt) {
    show_speed(evt.touches[0]);
    return cancel_event(evt);
},
false);

//if (localStorage && localStorage['polar_ws']) {
//    wind_speed = parseFloat(localStorage['polar_ws']);
//}

var w = [];
if (w = window.location.search.match(/wind=([0-9\.]+)/)) {
	wind_speed = w[1];
}

var opt = [];
if (opt = window.location.search.match(/opt=(\d+)/)) {
    options=opt[1];
	if (options & 16) 
	    id("op16").checked = true;
	if (options & 32) 
	    id("op32").checked = true;
	if (options & 64) 
	    id("op64").checked = true;
	if (options & 128) 
	    id("op128").checked = true;
	if (options & (128+64+32+16))  {
	    id("op256").checked = true;
		options |= 256;
	}
}
///if (window.location.search.match(/pro=0/)) {
    load_polars();
//    id("psb").checked = false;
//} else {
  //  load_polars(7);
//}