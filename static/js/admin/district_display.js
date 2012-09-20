var lon=30.05979;
var lat=-1.94479;
var zoom = 18;
var polygon;
var renderer;
var map;
var polygonLayer;
var newLayer;
var apiKey = "AqTGBsziZHIJYYxgivLBf0hVdrAk9mWO5cQcb8Yux8sW5M8c8opEC2lZqKR1ZZXf";
 	
//Initialise the 'map' object
function init() 
{
	map_div = document.getElementById("map");
 	if(map_div==null)
 	{
 		return;
 	}
 	renderer = OpenLayers.Util.getParameters(window.location.href).renderer;
 	renderer = (renderer) ? [renderer] : OpenLayers.Layer.Vector.prototype.renderers;
 	
 	
   	map = new OpenLayers.Map 
   	("map", {controls:
    	[
            new OpenLayers.Control.Navigation(),
            new OpenLayers.Control.PanZoomBar(),
            new OpenLayers.Control.Permalink(),
            new OpenLayers.Control.ScaleLine({geodesic: true}),
            new OpenLayers.Control.Permalink('permalink'),
            new OpenLayers.Control.MousePosition(),                    
            new OpenLayers.Control.Attribution()
        ],
        maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
        maxResolution: 156543.0339,
        numZoomLevels: 19,
        units: 'm',
        projection: new OpenLayers.Projection("EPSG:900913"),
        displayProjection: new OpenLayers.Projection("EPSG:4326")
        });
	
	
		
	
        // This is the layer that uses the locally stored tiles
        //newLayer = new OpenLayers.Layer.OSM("Local Tiles");
        
	    var gsat = new OpenLayers.Layer.Google("Google Satellite",{type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 19});
    	map.addLayer(gsat);
	    
	    newLayer = new OpenLayers.Layer.OSM("Local Tiles", map_url+"/osm/${z}/${x}/${y}.png", {numZoomLevels: 19});
	    newLayer.tileOptions={crossOriginKeyword: null};
	    map.addLayer(newLayer);
	    
    	 var aerial = new OpenLayers.Layer.Bing({
            name: "Aerial",
            key: apiKey,
            type: "Aerial",
            numZoomLevels: 19
        });	    
	    map.addLayer(aerial);
		polygonLayer = new OpenLayers.Layer.Vector("Polygon Layer", { renderers: renderer });
		map.addLayer(polygonLayer);
		map.addControl(new OpenLayers.Control.LayerSwitcher());
	    
	    if( ! map.getCenter() ){
	        var lonLat = new OpenLayers.LonLat(lon, lat).transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject());
	    	map.setCenter (lonLat, zoom);
	    }
	    
	    var points = $("#points").html(); 
		var districts = eval("("+points+")");
		districts = districts['districts'];		
		for(i=0; i< districts.length; i++)
		{
			district = districts[i];
			name = district["name"];
			points = district["points"]
			var polygon_points = [];
			for( j=0;j<points.length;j++)
			{
				point=points[j];
				x = point['x'];
				y = point['y'];
				p = new OpenLayers.Geometry.Point(x,y);
		  		polygon_points.push(p);
			}
			var ring = new OpenLayers.Geometry.LinearRing(polygon_points);
			var polygon_obj= new OpenLayers.Geometry.Polygon([ring]);
			var feature = new OpenLayers.Feature.Vector(polygon_obj,{});
			var label = $("div#displaytext").html();
			feature.style={
				label:name, 
				fillColor:color_district, 
				fillOpacity:0.25, 
				strokeColor:color_district, 
				strokeWidth: 1,
				fontColor:"#000000",
				labelOutlineColor:"#FFFFFF",
				labelOutlineWidth:3,
			};
			polygonLayer.addFeatures([feature]);
		}
		var bounds = polygonLayer.getDataExtent();
		map.zoomToExtent(bounds);
}

$(document).ready(function(){	
	$("#tabs").tabs();
	$('.dropdown_list').mouseleave(function(){
		$(this).fadeOut();
	});
	$('li[id^="li_"]').mouseover(function(){
		$(this).css("cursor","pointer");
		$(this).css("background-color","red");
	});
	$('li[id^="li_"]').mouseleave(function(){
		$(this).css("background-color","#cccccc");
	});
});

