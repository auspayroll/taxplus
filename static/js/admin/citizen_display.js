$(document).ready(function () {

    $("#id_status").change(function () {
        if ($("#id_status").val() == 1) {
            $(".deactive_fields").hide();
        }
        else {
            $(".deactive_fields").show();
        }
    });

	// add property to a citizen
	$("#add_property").click(function(){
		if($("#search_error").html()!="Property selected!" || polygonLayer.features.length!=1)
		{
			$("#search_error").html("");
			$("#add_property_error").html("Please search the property first!");	
			return;
		}
		var share = $("#share").val();
		if(!isNaN(share))
		{
			share = parseFloat(share).toFixed(2);
			if(share>=0.0&share<=100.0)
			{
				$("#add_property_error").html("");
				var plot_id = $.trim($("#search_plot_id").html());
				var citizen_id = $.trim($("#citizen_id").html());
				var postData = {"plot_id":plot_id, "citizen_id":citizen_id, "share":share};
				$.ajax({
					type:"get",
					url: "/admin/citizen/ajax/addPropertyToCitizen/",
					data: postData,
					success:function(data)
					{
						if(data=="already exists")
						{
							$("#add_property_error").html("This property already belongs to this citizen!");
						}
						else
						{
							ownerships = data['ownerships'];
						    var str="";
							str +="<div class='log_table'>";
							str += "<table cellpadding='0' cellspacing='0' class='tablesorter' style='width:96%' id='owned_properties_table'>";
							str += "	<thead>";
							str += "			<tr style='border-bottom:1px solid #555;'>";
							str += "				<th class='firstrowfirstcolumn'>No</td>";
							str += "				<th class='firstrow'>Plot ID</td>";
							str += "				<th class='firstrow'>Parcel ID</td>";
							str += "				<th class='firstrow'>Village</td>";
							str += "				<th class='firstrow'>Cell</td>";
							str += "				<th class='firstrow'>Sector</td>";
							str += "				<th class='firstrow'>Share</td>";
							str += "			</tr>";
							str += "		</thead>";
							str += "		<tbody>";
							for(var i=1; i<=ownerships.length; i++)
						    {
						    	ownership = ownerships[i-1];
								str += "<tr><td>"+i+"</td>";
								str += "<td>"+ownership['plot_id']+"</td>";
								str += "<td>"+ownership['parcel_id']+"</td>";
								str += "<td>"+ownership['village']+"</td>";
								str += "<td>"+ownership['cell']+"</td>";
								str += "<td>"+ownership['sector']+"</td>";
								str += "<td>"+ownership['share']+"</td>";
								str += "</tr>";
						    }
							str += "</tbody>";
							str+= "</table>";
							str+= "</div>";
							$("#show_owned_property").html(str);
							$('#add_property_error').html("Property added to this citizen!");
						}
					},
					error: function(request)
					{
						//alert(request.responseText);
					}
				});
				return;		
			}
			else
			{
				$("#add_property_error").html("Please enter a valid share!");
				return;
			}
		}
		$("#add_property_error").html("Please enter a valid share!");
		return;
	});
	
	$("#checkAllBox").click(function () {

	    if ($(this).is(':checked')) {
	        $(".multi_pay_checkbox").prop('checked', true)
	    }
	    else {
	        $(".multi_pay_checkbox").prop('checked', false)
	    }
	});

    $("#pay_multiple_btn").click(function () {
        if ($(".multi_pay_checkbox:checked").length > 0) {
            //validate all selected fees are the same type and belong to the same business / subbusiness 
            ids = new Array;
            mark = '';
            validate = true;
            $(".multi_pay_checkbox:checked").each(function () {
                new_mark = $("#mark_" + $(this).val()).val();
                if (mark == '') {
                    mark = new_mark;
                }
                else if (mark != new_mark) {
                    validate = false;
                }

                ids.push($(this).val());
            });

            if (validate) {
                window.location = '/admin/tax/tax/paymultiple_taxes/?type=fee&id=' + ids.join(',');
            }
            else {
                alert("Invalid list of fees selected. You can only pay multiple fees of the same type and belong to the same tax payer.");

            }
        }
        else {
            alert("Please select tax/fee items to pay");
        }

    });
	
    $("#view_epay_multiple_btn").click(function () {
        if ($(".multi_pay_checkbox:checked").length > 0) {
            //validate all selected fees are the same type and belong to the same business / subbusiness 
            ids = new Array;
            mark = '';
            validate = true;
            $(".multi_pay_checkbox:checked").each(function () {
                new_mark = $("#mark_" + $(this).val()).val();
                if (mark == '') {
                    mark = new_mark;
                }
                else if (mark != new_mark) {
                    validate = false;
                }

                ids.push($(this).val());
            });

            if (validate) {
                window.location = '/admin/tax/tax/generate_multipayepayinvoice/?type=fee&id=' + ids.join(',');
            }
            else {
                alert("Invalid list of fees selected. You can only pay multiple fees of the same type and belong to the same tax payer.");

            }
        }
        else {
            alert("Please select tax/fee items to pay");
        }

    });

	
	
	// look for a property and display it on the map according to the entered information
	$("#search_property").click(function(){
		plot_id = $.trim($("#id_plot_id").val());
		parcel_id = $.trim($("#id_parcel_id").val());
		village = $.trim($("#id_village").val());
		cell = $.trim($("#id_cell").val());
		sector = $.trim($("#id_sector").val());
		search_conditions="";
		
		if(plot_id==""&&parcel_id==""&&village==""&&cell==""&&sector=="")
		{
			$("#search_error").html("Please enter plot ID or address");
			return false;
		}
		else if(plot_id!="")
		{
			search_conditions="plot_id="+plot_id;
		}
		else
		{
			if(parcel_id == ""){$("#search_error").html("Please enter parcel ID.");return;}
			if(isNaN(parcel_id)){$("#search_error").html("Please enter a valid parcel ID.");return;}
			if(village == ""){$("#search_error").html("Please enter village.");return;}
			if(cell == ""){$("#search_error").html("Please enter cell.");return;}
			if(sector == ""){$("#search_error").html("Please select a sector.");return;}
			search_conditions = "parcel_id="+parcel_id+"&village="+village+"&cell="+cell+"&sector="+sector;
		}
			
			
		$.ajax({
			type:"get",
			url: "/admin/citizen/ajax/searchSingleProperty/",
			data: search_conditions,
			success:function(data)
			{
				if(data==""){return;}
				else
				{
					if(data=="No property found!"||data=="Multiple properties found!")
					{
						$("#search_error").html(data);
						return;
					}
					else
					{
					    props = $.parseJSON(data);
						properties = props['properties'];
						if(properties.length>0)
						{
							// remove existing property and popup on the map
							for(s=0;s<polygonLayer.features.length;s++)
							{
								feature = polygonLayer.features[s];
								if(feature.popup!=null)
								{
									feature.popup.hide();	
								}
							}
							polygonLayer.removeFeatures(polygonLayer.features);
							
							// inform user that the a property is found
							$("#search_error").html("Property selected!");
							
							property = properties[0];
							plot_id = property['plot_id'];
							$("#search_plot_id").html(plot_id);
							address = property['parcel_id'] + " " + property['village']+ ", "+property['cell']+", "+property['sector'];
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
							feature.style={label:'Property searched',fillColor:color_sector, fillOpacity:0.2, strokeColor:color_sector, strokeWidth: 1,fontColor:color_sector,};
							
							
							
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
						    map.addPopup(popup);
						    
						    
						    var selectControl = new OpenLayers.Control.SelectFeature(
								polygonLayer, {
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
							
							polygonLayer.addFeatures([feature]);
							var bounds = polygonLayer.getDataExtent();
							map.zoomToExtent(bounds);
						}
					}	
				}
			},
			error: function(request)
			{
				//alert(request.responseText);
			}
		});	
		
		
		
		

	});
});















