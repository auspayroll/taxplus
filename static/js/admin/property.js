function init() 
{
    if ($("div#map") != null) {
        loadMap();
    }
    polygon = new OpenLayers.Control.DrawFeature(
		polygonLayer,
		OpenLayers.Handler.Polygon,
		{
			handlerOptions: {holeModifier: "altKey"},
		}
	);
	polygon.events.register("featureadded", '', controlFeatureHandler);
	function controlFeatureHandler(data)
	{
		getCoordinates();
		polygon.deactivate();
	}
	map.addControl(polygon);
}
   
function getCoordinates()
{
	str="";
	points = polygonLayer.features[0].geometry.getVertices();
	for(i=0;i<points.length;i++)
	{
		if(i>0){str=str+"#";}
		str=str+points[i].x+","+points[i].y;
	}
	$("#id_boundary").html(str);
	if(points.length>=3)
	{
		$("#boundary_error").html("Boundary added!");		
		$('html').ajaxSend(function(event, xhr, settings) {
		    function getCookie(name) {
		        var cookieValue = null;		
		        if (document.cookie && document.cookie != '') {
		            var cookies = document.cookie.split(';');
		            for (var i = 0; i < cookies.length; i++) {
		                var cookie = jQuery.trim(cookies[i]);
		                // Does this cookie string begin with the name we want?
		                if (cookie.substring(0, name.length + 1) == (name + '=')) {
		                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
		                    break;
		                }
		            }
		        }
		        return cookieValue;
		    }
		    if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
		        // Only send the token to relative URLs i.e. locally.
		        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
		    }
		});
		
		
		$.ajax({
				type:"post",
				url: "/admin/ajax/getPropertySector/",
				data: { boundary:$("#id_boundary").html()},
				success:function(data)
				{
					if(data=="")
					{
						$("div#error").html("It is not within any sector! ");
						$("#uniform-id_district").children('span').html("");
						$("#uniform-id_sector").children('span').html("");
						$("#uniform-id_cell").children('span').html("");
						$("#uniform-id_village").children('span').html("");
					}
					else
					{
						district_id = data['district_id'];
						district_name = data['district_name'];
						sector_name = data['sector_name'];
						sector_id = data['sector_id'];
						cells = data['cells']
						
						$("#uniform-id_district").children('span').html(district_name);
						$("#id_sector").append("<option selected='selected' value='"+ sector_id +"'>"+ sector_name +"</option>");
						$("#uniform-id_sector").children('span').html(sector_name);
						
						$("#id_cell option[value!='']").remove();
						for(var i=0;i<cells.length;i++)
						{
							cell = cells[i];
							$("#id_cell").append("<option value='"+ cell['id'] +"'>" + cell['name'] + "</option");
						}
                        $("#id_cell").prop('disabled',false);
					}
					return;
				},
				error: function(request)
				{
					//document.write(request.responseText);
					//alert(request.responseText);
				}
			}
		)
	}
	else
	{
		$("#boundary_error").html("Invalid boundary!");
	}
}

function refreshMap()
{
	map.removeControl(polygon);
	map.removeLayer(polygonLayer);
	polygon.destroy();
	polygonLayer.destroy();
	$("#id_boundary").html("");
	$("#boundary_error").html("");
	polygonLayer = new OpenLayers.Layer.Vector("Vector Layer", { renderers: renderer });
	map.addLayer(polygonLayer);
	polygon = new OpenLayers.Control.DrawFeature(
		polygonLayer,
		OpenLayers.Handler.Polygon,
		{
			handlerOptions: {holeModifier: "altKey"},
		}
	);
	
	polygon.events.register("featureadded", '', controlFeatureHandler);
	
	function controlFeatureHandler(data)
	{
		//deal with some data storing
		//candraw = false;
		getCoordinates();
		polygon.deactivate();
	}
	map.addControl(polygon);
}
	    
function toggle() {
	if($("div#error").html()!="Property added successfully!")
	{
		$("div#error").html("");
	}
	else
	{
		$("#id_district option[value!='']").remove();
		
		$("#id_sector option[value!='']").remove();
		$("#id_cell option[value!='']").remove();
		$("#id_village option[value!='']").remove();
		
		$("#uniform-id_district span").html("----------");
		$("#uniform-id_sector span").html("----------");
		$("#uniform-id_cell span").html("----------");
		$("#uniform-id_village span").html("----------");
		
		$("#id_parcel_id").val("");
		$("#id_is_leasing").prop('checked',false);
		$("#uniform-id_is_leasing span").removeClass('checked');
	}
	
	
	
	
	if(polygon!=null)
	{
		if(!polygon.active)
		{
			if($("#id_boundary").html()=='')
			{polygon.activate();}
			else
			{
				refreshMap();
				polygon.activate();	
			}
		}
		else 
		{
			refreshMap();
			polygon.activate();
		}				
	}
}

function check_property_registration_form()
{
	parcel_id=$.trim($("#id_parcel_id").val());
	village=$.trim($("#id_village").val());
	cell=$.trim($("#id_cell").val());
	sector = $.trim($("#id_sector").val());
	
	if($("#uniform-id_is_leasing").children('span').hasClass('checked'))
	{
		$("#id_is_leasing").attr('checked',true);		
	}
	else
	{
		$("#id_is_leasing").attr('checked',false);
	}

	if(sector==''){
		$("#error").html('Please add a boundary for property.');
		return false;
	}
	if(cell==""){
		$("#error").html('Please select a cell.');
		return false;
	}
	if(village==""){
		$("#error").html('Please select a village.');
		return false;
	}
	if(parcel_id==''){
		$("#error").html('Please enter parcel ID.');
		return false;		  
	}
	if($("#id_boundary").html()!="")
	{
		string=$("#id_boundary").html();
		points=string.split('#');
		if(points.length<2)
		{	
				$("#error").html("Please add a valid boundary!");
				return false;
		}
	}

	
	$('html').ajaxSend(function(event, xhr, settings) {
	    function getCookie(name) {
	        var cookieValue = null;
	        if (document.cookie && document.cookie != '') {
	            var cookies = document.cookie.split(';');
	            for (var i = 0; i < cookies.length; i++) {
	                var cookie = jQuery.trim(cookies[i]);
	                // Does this cookie string begin with the name we want?
	                if (cookie.substring(0, name.length + 1) == (name + '=')) {
	                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
	                    break;
	                }
	            }
	        }
	        return cookieValue;
	    }
	    if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
	        // Only send the token to relative URLs i.e. locally.
	        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
	    }
	});
	
	
	$.ajax({
			type:"post",
			url: "/admin/ajax/add_property/",
			data: {parcel_id: $("#id_parcel_id").val(), village: $("#id_village").val(), cell: $("#id_cell").val(), sector:$("#id_sector").val(), is_leasing:$("#id_is_leasing").is(':checked'),boundary:$("#id_boundary").html()},
			success:function(data)
			{
				if(data=="OK")
				{
					$("div#error").html("Property added successfully!");
					toggle();
					return;	
				}
				else if(data=="This plot already exists!")
				{
					$("div#error").html(data);
					return;
				}
				else
				{
					$("div#error").html("It is not within any sector!");
					return;
				}
				
			},
			error: function(request)
			{
				//document.write(request.responseText);
				//alert(request.responseText);
			}
		}
	)

	
	return true;
}
   
function checkPropertyConditions()
{
	upi =  $.trim($("#id_upi").val());
	parcel_id =  $.trim($("#id_parcel_id").val());
	//village =  $.trim($("#id_village").val());
	cell =  $.trim($("#id_cell").val());
	sector =  $.trim($("#id_sector").val());
	if(upi!="")
	{
		return true;
	}
	else
	{
		//if((parcel_id=="")&(village=="")&(cell=="")&(sector==""))
		if((parcel_id=="")&(cell=="")&(sector==""))
		{
			$("#search_error").html("No property details entered!");
			return false;
		}
		if(isNaN(parcel_id))
		{
			$("#search_error").html("Plot/Parcel ID is invalid.");
			return false;
		}
		if((parcel_id!="")&(cell!="")&(sector!=""))
		{
			return true;
		}
		else
		{
			$("#search_error").html("Please enter parcel ID, cell and sector. Alternatively, you can enter UPI only.");
			return false;
		}
	}
}

function showPropertyOnMap()
{
	var points=$("#points").html();
	points=eval("("+points+')');
		
	popup_message ="Hello";
	popup_message = "<div>"+popup_message+"</div>";
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
      	popup_message,
      	anchor,
      	false
      	);
    feature.popup = popup;
	polygonLayer.addFeatures([feature]);
    map.addPopup(popup);
}


