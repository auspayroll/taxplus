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
	resultLayer = new OpenLayers.Layer.Vector("Result Layer",{
		styleMap: new OpenLayers.StyleMap({'default':{
				strokeColor: "#00FF00",
				strokeOpacity: 1,
				strokeWidth: 2,
				fillColor: "#FF5500",
				fillOpacity: 0.5,
				pointRadius: 0,
				//pointerEvents: "visiblePainted",
				// label with \n linebreaks
				label : " ${parcel_id} ",
                    
				fontColor: "white",
				fontSize: "13",
				fontFamily: "Courier New, monospace",
				fontWeight: "normal",
				labelAlign: "cm",
				labelXOffset: "0",
				labelYOffset: "0",
				labelOutlineColor: "#fff",
				labelOutlineWidth: 0
			}}),
	
	}); 
	map.addLayer(resultLayer);

	
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
			upi = property['upi'];
			if(upi==undefined)
			{
				continue;
			}
			//plot_id = property['plot_id'];
			address = '';

			if(property['village']==undefined)
			{
				address = property['parcel_id']+ ", " + property['cell'] + ", " +property['sector'];
			}
			else
			{
				address = property['parcel_id']+ " "+property['village']+", " + property['cell'] + ", " +property['sector'];
			}

			
			property_popup_message = "<div>UPI: "+upi+"<br>Address: "+address+"</div>";
			points=property['points'];
			var polygon_points = [];

			if(points==undefined||points.length==0)
			{
				continue;
			}
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
			var feature = new OpenLayers.Feature.Vector(polygon_obj,{parcel_id:(i+1)});
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
    // This is very important
	var bounds = resultLayer.getDataExtent();
    map.zoomToExtent(bounds);
		
}







$(document).ready(function(){
	$("#printcurrent").click(function(){
		window.print();
	});
	
	
	
	$("#printall").click(function(){
		$.ajax({
				type:"get",
				url: "/admin/report/ajax/properties_with_unpaid_tax_for_printing/",
				success:function(data)
				{
					properties = data['properties'];
					str = "";
					str += "<table border='1' cellpadding='2' cellspacing ='0' style='margin-left:auto; text-align:left;margin-right:auto;'>";
					str +=	"	<tr>";
					str +=	"		<th>UPI</th>";
					str +=	"		<th>Address</th>";
					str +=	"		<th>Citizen Names</th>";
					str +=	"		<th>Citizen Ids</th>";
					str +=	"		<th>Business Names</th>";
					str +=	"		<th>Phone</th>";
					str +=	"		<th>Email</th>";
					str +=	"		<th>Due Taxes</th>";
					str +=	"	</tr>";
					
					for(i=0; i<properties.length; i++)
					{
						property = properties[i];
						str+= "<tr>";
						str+="<td>"+property['upi']+"</td>";
						str+="<td>"+property["address"]+"</td>";
						str+="<td>"+property["citizen_names"]+"</td>";
						str+="<td>"+property["citizen_ids"]+"</td>";
						str+="<td>"+property["business_names"]+"</td>";
						str+="<td>"+property["phones"]+"</td>";
						str+="<td>"+property["emails"]+"</td>";
						str+="<td>"+property["tax_types"]+"</td>";
						str+="</tr>";
					}
					str += "</table>";
					$("#properties_in_all_pages").html($("#graph_title_section").html() + "<br><br>" + str);
					$("#properties_in_all_pages").printElement();
				},
				error: function(request)
				{
					//document.write(request.responseText);
					//alert(request.responseText);
				}
			});
	});
});

