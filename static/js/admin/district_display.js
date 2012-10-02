var sectorLayer;
function init() 
{
	loadMap();
    var selectControl = new OpenLayers.Control.SelectFeature(
        polygonLayer,
        {
        	'hover': true,
        	'multiple': false,
             'callbacks':{
             	'click':function(feature){
             		var points = $("#points").html(); 
					var districts = eval("("+points+")");
					districts = districts['districts'];
					if(districts.length==1){}
					else
					{
						window.location = '/admin/property/district/view_district/?name='+feature.attributes['name'];
					}
             	},
             }
        }
    );
    map.addControl(selectControl);
    selectControl.activate();
	    
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
		feature.attributes = {
			name:name,
		};
		polygonLayer.addFeatures([feature]);
	}
		
			
	if(districts.length>1)
	{
		$("#selectmessage").show();
		polygonLayer.events.on({
            "beforefeatureselected": function(e) {
            	e.feature.style['fillOpacity']=0.5;
            },
            "featureselected": function(e) {
            	e.feature.style['fillOpacity']=0.25;
            },
       });
   }
   else if(districts.length==1)
   {
   		$('#district_title').html("District info:");
		$('#details').show();
   }	
	
    
    if($.trim($('#sectors').html())!="")
    {
    	sectorLayer = new OpenLayers.Layer.Vector("Sector Layer", { renderers: renderer });
    	map.addLayer(sectorLayer);
    	var sectorSelectControl = new OpenLayers.Control.SelectFeature(
            sectorLayer,
            {
            	'hover': true,
            	'multiple': false,
                 'callbacks':{
                 	'click':function(feature){
                 		window.location = '/admin/property/sector/view_sector/?name='+feature.attributes['name'];
                 	},
                 }
            }
        );
    
    	map.addControl(sectorSelectControl);
    	sectorSelectControl.activate();
    	
    	
    	
    	var points = $("#sectors").html(); 
		var sectors = eval("("+points+")");
		sectors = sectors['sectors'];		
		for(i=0; i< sectors.length; i++)
		{
			sector = sectors[i];
			name = sector["name"];
			points = sector["points"]
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
			feature.style={
				label:name, 
				fillColor:color_sector, 
				fillOpacity:0.25, 
				strokeColor:color_sector, 
				strokeWidth: 1,
				fontColor:"#000000",
				labelOutlineColor:"#FFFFFF",
				labelOutlineWidth:3,
			};
			feature.attributes = {
				name:name,
			};
			sectorLayer.addFeatures([feature]);
		}
		sectorLayer.events.on({
            "beforefeatureselected": function(e) {
            	e.feature.style['fillOpacity']=0.5;
            },
            "featureselected": function(e) {
            		e.feature.style['fillOpacity']=0.25;
            },
       });
    }
	var bounds = polygonLayer.getDataExtent();
	map.zoomToExtent(bounds);
}

$(document).ready(function(){	
	$("#showsectors").click(function(){
		if($(this).is(':checked'))
		{
			map.addLayer(sectorLayer);
			var sectorSelectControl = new OpenLayers.Control.SelectFeature(
                sectorLayer,
                {
                	'hover': true,
                	'multiple': false,
                     'callbacks':{
                     	'click':function(feature){
                     		window.location = '/admin/property/sector/view_sector/?name='+feature.attributes['name'];
                     	},
                     }
                }
            );
        
	        map.addControl(sectorSelectControl);
	        sectorSelectControl.activate();
	        sectorLayer.events.on({
	            "beforefeatureselected": function(e) {
	            	e.feature.style['fillOpacity']=0.5;
	            },
	            "featureselected": function(e) {
	            		e.feature.style['fillOpacity']=0.25;
	            },
	       });
	        
        
		}
		else
		{
			map.removeLayer(sectorLayer);
		}
	});
});

