var resultLayer;
var property_str; 	
function init() 
{
 	loadMap();
	polygon = new OpenLayers.Control.DrawFeature(
		polygonLayer,
		OpenLayers.Handler.Polygon,
		{
			handlerOptions: {holeModifier: "altKey"},
		}
	);
	map.addControl(polygon);     
	polygon.events.register("featureadded", '', controlFeatureHandler); 
	resultLayer = new OpenLayers.Layer.Vector("Result Layer"); 
	map.addLayer(resultLayer);

	



	// draw properties on the map
	if($("#cellgeodata").html()!="")
	{
		return;
		var geodata = $.trim($("#geodata").html());
		if(geodata != "")
		{
			geodata = $.parseJSON(geodata);	
		}
		else
		{
			return;
		}
		var properties = geodata['properties'];
		for(i=0;i<properties.length;i++)
		{
			property=properties[i];
			plot_id = property['plot_id'];
			address = property['parcel_id']+ " "+property['village']+", " + property['cell'] + ", " +property['sector'];
			property_popup_message = "<div>Plot ID: "+plot_id+"<br>Address: "+address+"</div>";
			points=property['points'];
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
			var anchor = {'size': new OpenLayers.Size(0,0), 'offset': new OpenLayers.Pixel(0, 0)};
	        popup = new OpenLayers.Popup.FramedCloud(
	          	"",
	          	feature.geometry.getBounds().getCenterLonLat(),
	          	new OpenLayers.Size(100,100),
	          	property_popup_message,
	          	anchor,
	          	false
	          	);
		    feature.popup = popup;
			resultLayer.addFeatures([feature]);
		    map.addPopup(popup);
		}
		polygonLayer.removeFeatures(polygonLayer.features);
		
		
		
		// popup effects
		for(s=0;s<resultLayer.features.length;s++)
		{
			resultLayer.features[s].popup.hide();
		}
		
		var selectControl = new OpenLayers.Control.SelectFeature(
			resultLayer, {
				hover: true,
				onBeforeSelect: function(feature) {
					feature.popup.show();   
				        return true;
				},
		    	onUnselect: function(feature) {
			       feature.popup.hide();
			       return true;
		    	}
			}
		);
			
		map.addControl(selectControl);
		selectControl.activate();
		 	
	}

	map.addControl(new OpenLayers.Control.LayerSwitcher());			
    if( ! map.getCenter() ){
        var lonLat = new OpenLayers.LonLat(lon, lat).transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject());
    	map.setCenter (lonLat, zoom);
    }
	function controlFeatureHandler(data)
	{
		getCoordinates();
		polygon.deactivate();			
	}






















	// draw properties on the map
	if($("#geodata").html()!="")
	{
		var geodata = $.trim($("#geodata").html());
		if(geodata != "")
		{
			geodata = $.parseJSON(geodata);	
		}
		else
		{
			return;
		}
		var properties = geodata['properties'];
		for(i=0;i<properties.length;i++)
		{
			property=properties[i];
			plot_id = property['plot_id'];
			address = property['parcel_id']+ " "+property['village']+", " + property['cell'] + ", " +property['sector'];
			property_popup_message = "<div>Plot ID: "+plot_id+"<br>Address: "+address+"</div>";
			points=property['points'];
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
			var anchor = {'size': new OpenLayers.Size(0,0), 'offset': new OpenLayers.Pixel(0, 0)};
	        popup = new OpenLayers.Popup.FramedCloud(
	          	"",
	          	feature.geometry.getBounds().getCenterLonLat(),
	          	new OpenLayers.Size(100,100),
	          	property_popup_message,
	          	anchor,
	          	false
	          	);
		    feature.popup = popup;
			resultLayer.addFeatures([feature]);
		    map.addPopup(popup);
		}
		polygonLayer.removeFeatures(polygonLayer.features);
		
		
		
		// popup effects
		for(s=0;s<resultLayer.features.length;s++)
		{
			resultLayer.features[s].popup.hide();
		}
		
		var selectControl = new OpenLayers.Control.SelectFeature(
			resultLayer, {
				hover: true,
				onBeforeSelect: function(feature) {
					feature.popup.show();   
				        return true;
				},
		    	onUnselect: function(feature) {
			       feature.popup.hide();
			       return true;
		    	}
			}
		);
			
		map.addControl(selectControl);
		selectControl.activate();
		 	
	}

	map.addControl(new OpenLayers.Control.LayerSwitcher());			
    if( ! map.getCenter() ){
        var lonLat = new OpenLayers.LonLat(lon, lat).transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject());
    	map.setCenter (lonLat, zoom);
    }
	function controlFeatureHandler(data)
	{
		getCoordinates();
		polygon.deactivate();			
	}
		
}

function keyword_search()
{
	var condition_count = 0;
	var querystring ="";
	var ids = Array("id_citizen_id","id_plot_id","id_sector","id_cell","id_village","id_parcel_id");
	var descs = Array("", "", "", "", "","Parcel ID");
	
	// Check number value valid or not, and whether value is entered
	for(var i=0;i<ids.length;i++)
	{
		var id = ids[i];
		var desc = descs[i];
		var value = $("#"+id).val();
		if(value!="")
		{
			if(desc!=""&&isNaN(value))
			{
				$("#keyword_error").html(desc+" is invalid!");
				return false;
			}
			else
			{
				condition_count++;
			}
		}
	}
	if(condition_count==0)
	{
		$("#keyword_error").html("Please enter search conditions!");
		return false;
	}
	return true;
}


function initilizeListEvents()
{
	$('li[id^="li_"]').mouseover(function(){
		$(this).css("cursor","pointer");
		$(this).css("background-color","red");
	});
	$('li[id^="li_"]').mouseleave(function(){
		$(this).css("background-color","#cccccc");
	});
	$('li[id^="li_"]').click(function(){
		id = $(this).attr("id");
		parts = id.split("_");
		search_field = parts[1];
		$("#id_"+search_field).val($(this).html());
	});
}


$(document).ready(function(){	
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
	
	$('input[id^="id_"]').keyup(function(){
		search_field = $(this).attr("id").replace("id_","");
		if(search_field!="sector"&&search_field!="cell"&&search_field!="village"){return;}
		if($.trim($(this).val())=="")
		{
			$('#'+search_field+"_dropdown_list").html('');
			$('#'+search_field+"_dropdown_list").fadeOut();
			return;
		}
		else
		{
			value = $.trim($(this).val());
			querystring = search_field+"="+value;
			$.ajax({
				type:"get",
				url: "/admin/ajax/search_property_field/",
				data: querystring,
				success:function(data)
				{
					if(data==""){return;}
					else
					{
						str="<ul>";
						for(i=0;i<data.length;i++)
						{
							str=str+"<li id='li_"+search_field+"_"+i+"'>"+ data[i] + "</li>";										
						}
						str=str+"</ul>";
						$('#'+search_field+'_dropdown_list').html(str);
						$('#'+search_field+'_dropdown_list').show();
						initilizeListEvents();
					}
				},
				error: function(request)
				{
					alert(request.responseText);
				}
			});
		}
	});
});

