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
	feature.style={label:label, fillColor:color_sector, fillOpacity:0.2, strokeColor:color_sector, strokeWidth: 1,fontColor:color_sector,};
	polygonLayer.addFeatures([feature]);
	var bounds = polygonLayer.getDataExtent();
	map.zoomToExtent(bounds);
}
