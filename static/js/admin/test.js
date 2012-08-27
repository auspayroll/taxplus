var obj = [];
					var results = data.split("####");
					var polygons = results[0].split('%');
					var table_data = results[1];
					if(table_data =="NOPROPERTY")
					{
						$('#search_results tr:last').after("<tr><td class='firstcolumn' colspan='6'><strong>No results were found, please try again.</strong></td></tr>");
					}
					property_objects=[];
					var po = new Array();
					var properties = table_data.split('#');
					for(i=0;i<properties.length;i++)
					{	
						property = properties[i];
						property_parts = property.split(':');
						plotid = property_parts[0];
						address = property_parts[1];
						$('#search_results tr:last').after("<tr><td class='firstcolumn'>"+plotid+"</td><td>"+address+"</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>");
						popup_string = "Plot ID: "+plotid+"  address: "+address;
						po[i] = popup_string;
					}
					//alert(po[0]);
					//alert(popup_string);