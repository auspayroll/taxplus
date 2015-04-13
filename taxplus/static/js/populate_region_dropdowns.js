$(document).ready(function(){

	var regions;
	var district_val;
	var sector_val;
	var cell_val;
	var village_val;

	$.ajax({
	  dataType: "json",
	  async:false,
	  cache:true,
	  url: "/static/region.json",
	  success: function(data){
	  	regions = data;
	  },

	  error: function( jqXHR, textStatus, errorThrown ){
	  	console.log(errorThrown); }
	});

	sector_val = $("#search_table #id_sector").val();
	cell_val = $("#search_table #id_cell").val();
	village_val = $("#search_table #id_village").val();


	$("#search_table #id_district").change(function(){
		district_val = $("#search_table #id_district").val();
		$("#search_table #id_sector").val('');
		$("#search_table #id_sector").children().remove();
		$("#search_table #id_sector").append('<option selected="selected" value="">--------</option>');

		if(district_val !==''){
			$("#search_table #id_sector").prop('disabled',false);
			var sectors_dict = regions[district_val]['s'];
			var sectors = [];
			for(var s in sectors_dict){
				sectors.push([s, sectors_dict[s]['n']]);
			}
			sectors.sort();
			var sector_val = $("#search_table #id_sector").val();
			$("#search_table #id_sector").children("option[value!='']").remove();
			for(var i=0; i<sectors.length; i++)
			{
				var sector = sectors[i];
				$("#search_table #id_sector").append('<option value="'+ sector[0] +'">'+ sector[1] +'</option>');
			}
			$("#search_table #id_sector").trigger("chosen:updated");
			$("#search_table #id_sector").prop('disabled',false);
		}
		else{
			$("#search_table #id_sector").prop('disabled',true);
		}

		$("#search_table #id_sector").change();
		$("#search_table #id_sector").trigger("chosen:updated");
	});


	$("#search_table #id_sector").change(function(){
		sector_val = $("#search_table #id_sector").val();
		$("#search_table #id_cell").val('');
		$("#search_table #id_cell").children().remove();
		$("#search_table #id_cell").append('<option selected="selected" value="">--------</option>');

		if(sector_val !== ''){
			$("#search_table #id_cell").prop('disabled',false);
			var cells_dict = regions[district_val]['s'][sector_val]['c'];
			var cells = [];
			for(var c in cells_dict){
				cells.push([c, cells_dict[c]['n']]);
			}
			cells.sort();
			var cell_val = $("#search_table #id_cell").val();
			$("#search_table #id_cell").children("option[value!='']").remove();
			for(var i=0; i<cells.length; i++)
			{
				var cell = cells[i];
				$("#search_table #id_cell").append('<option value="'+ cell[0] +'">'+ cell[1] +'</option>');
			}
			$("#search_table #id_cell").trigger("chosen:updated");
			$("#search_table #id_cell").prop('disabled',false);

		}
		else{
			$("#search_table #id_cell").prop('disabled',true);
		}
		$("#search_table #id_cell").change();
		$("#search_table #id_cell").trigger("chosen:updated");
	});


	$("#search_table #id_cell").change(function(){
		cell_val = $("#search_table #id_cell").val();
		$("#search_table #id_village").val('');
		$("#search_table #id_village").children().remove();
		$("#search_table #id_village").append('<option selected="selected" value="">--------</option>');

		if(cell_val !== ''){
			$("#search_table #id_village").prop('disabled',false);
			var villages = regions[district_val]['s'][sector_val]['c'][cell_val]['v'];
			villages.sort();
			village_val = $("#search_table #id_village").val();
			$("#search_table #id_village").children("option[value!='']").remove();
			for(var i=0; i<villages.length; i++)
			{
				var village = villages[i];
				if(village_val == village[0]){
					$("#search_table #id_village").append('<option selected="selected" value="'+ village[0] +'">'+ village[1] +'</option>');
				}
				else{
					$("#search_table #id_village").append('<option value="'+ village[0] +'">'+ village[1] +'</option>');
				}
			}
			$("#search_table #id_village").trigger("chosen:updated");
			$("#search_table #id_village").prop('disabled',false);
		}
		else{
			$("#search_table #id_village").prop('disabled',true);
		}


		$("#search_table #id_village").trigger("chosen:updated");
		$("#search_table #id_village").change();
	});

});


