 $(document).ready(function(){

	/* initialize form */
	var init_district_val = $("#search_table #id_district").val();
	if(init_district_val != ''){
		$("#search_table #id_district").change();
	}



	$("#search_table #id_district").change(function(){
		var district_val = $("#search_table #id_district").val();
		if(district_val === ''){
			$("#search_table #id_sector").val('');
			$("#search_table #id_sector").children("option[value!='']").remove();
			$("#search_table #id_sector").prop('disabled',true);
		}
		else{
			$.ajax({
				type:"get",
				url: "/admin/ajax/getObjectsByParentId/?object_type=district&object_id="+district_val,
				success:function(sectors)
				{
					var sector_val = $("#search_table #id_sector").val();
					$("#search_table #id_sector").children("option[value!='']").remove();
					for(var i=0; i<sectors.length; i++)
					{
						var sector = sectors[i];
						if(sector_val == sector[0]){
							$("#search_table #id_sector").append('<option selected="selected" value="'+ sector[0] +'">'+ sector[1] +'</option>');
						}
						else{
							$("#search_table #id_sector").append('<option value="'+ sector[0] +'">'+ sector[1] +'</option>');
						}
					}
					$("#search_table #id_sector").trigger("chosen:updated");
					$("#search_table #id_sector").prop('disabled',false);
				},
				error: function(request)
				{
	                $("#search_table #id_sector").prop('disabled','disabled');
	                $("#search_table #id_cell").prop('disabled','disabled');
	                $("#search_table #id_village").prop('disabled','disabled');
				}
			});
		}
		$("#search_table #id_sector").change();
	});


	$("#search_table #id_sector").change(function(){
		var sector_val = $("#search_table #id_sector").val();
		if(sector_val === ''){
			$("#search_table #id_cell").val('');
			$("#search_table #id_cell").children("option[value!='']").remove();
			$("#search_table #id_cell").prop('disabled',true);
		}
		else{
			$.ajax({
				type:"get",
				url: "/admin/ajax/getObjectsByParentId/?object_type=sector&object_id="+sector_val,
				success:function(cells)
				{
					var cell_val = $("#search_table #id_cell").val();
					$("#search_table #id_cell").children("option[value!='']").remove();
					for(var i=0; i<cells.length; i++)
					{
						var cell = cells[i];
						if(cell_val == cell[0]){
							$("#search_table #id_cell").append('<option selected="selected" value="'+ cell[0] +'">'+ cell[1] +'</option>');
						}
						else{
							$("#search_table #id_cell").append('<option value="'+ cell[0] +'">'+ cell[1] +'</option>');
						}
					}
					$("#search_table #id_cell").trigger("chosen:updated");
					$("#search_table #id_cell").prop('disabled',false);
				},
				error: function(request){}
			});
		}
		$("#search_table #id_cell").change();
	});


	$("#search_table #id_cell").change(function(){
		var cell_val = $("#search_table #id_cell").val();
		if(cell_val === ''){
			$("#search_table #id_village").val('');
			$("#search_table #id_village").children("option[value!='']").remove();
			$("#search_table #id_village").prop('disabled',true);
		}
		else{
			$.ajax({
				type:"get",
				url: "/admin/ajax/getObjectsByParentId/?object_type=cell&object_id="+cell_val,
				success:function(villages)
				{
					var village_val = $("#search_table #id_village").val();
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
				},
				error: function(request){}
			});
		}
		$("#search_table #id_village").change();
	});









});