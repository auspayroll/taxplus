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
	loadMap();
    var points=$("#points").html();
	points=eval("("+points+')');
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
	feature.style={label:label, fillColor:color_house, fillOpacity:0.2, strokeColor:color_house, strokeWidth: 1,fontColor:color_house,};
	polygonLayer.addFeatures([feature]);
	var bounds = polygonLayer.getDataExtent();
	map.zoomToExtent(bounds);
}

$(document).ready(function(){	
	$('li[id^="li_"]').mouseover(function(){
		$(this).css("cursor","pointer");
		$(this).css("background-color","red");
	});
	$('li[id^="li_"]').mouseleave(function(){
		$(this).css("background-color","#cccccc");
	});
});

