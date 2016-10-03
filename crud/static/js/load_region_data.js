
 $(document).ready(function(){
 	var district_val;
 	var sector_val = sector_posted;
 	var cell_val = cell_posted;




	$("#id_fee_type").change(function(){
		var fee_type = $("#id_fee_type").val();
		$("#id_fee_subtype").children("option[value!='']").remove();

		if(fee_type !== ''){
		    $.ajax({
					type:"get",
					url: "/api/subcategory/"+fee_type+"/",
					success:function(choices)
					{
						for(var i=0; i< choices.length; i++){
							$("#id_fee_subtype").append('<option value="'+ choices[i].id +'">'+ choices[i].name +'</option>');

						}
					},
					error: function(request)
					{
						console.log('failed to load fee sub type choices');
					}
				});
		}

	});



	$("#id_district").change(function(){
		district_val = $("#id_district").val();
		$("#id_sector").children("option[value!='']").remove();
		if(district_val !== ''){
		    $.ajax({
					type:"get",
					url: "/api/sectors/"+district_val+'/',
					success:function(sectors)
					{
						for(var i=0; i< sectors.length; i++){
								if (sector_posted === sectors[i].id){
									$("#id_sector").append('<option value="'+ sectors[i].id +'" selected>'+ sectors[i].name +'</option>');
									$("#id_sector").val(sector_posted);
								}
								else{
									$("#id_sector").append('<option value="'+ sectors[i].id +'">'+ sectors[i].name +'</option>');
								}
						}
						$("#id_sector").change();
					},
					error: function(request)
					{
						console.log('failed to load sectors');
					}
				});
		}
		else{
			$("#id_sector").change();
		}

	});


	$("#id_sector").change(function(){
		$("#id_cell").children("option[value!='']").remove();
		sector_val = $("#id_sector").val();
		if(sector_val !== ''){
		    $.ajax({
					type:"get",
					url: "/api/cells/"+sector_val+'/',
					success:function(cells)
					{
						for(var i=0; i< cells.length; i++){
								if (cell_val === cells[i].id){
									$("#id_cell").append('<option value="'+ cells[i].id +'" selected>'+ cells[i].name +'</option>');
									$("#id_cell").val(cell_val);

								}
								else{
									$("#id_cell").append('<option value="'+ cells[i].id +'">'+ cells[i].name +'</option>');
								}
						}
						$("#id_cell").change();
					},
					error: function(request)
					{
						console.log('failed to load cells')
					}
				});
		}
		else{
			$("#id_cell").change();
		}
	});


	$("#id_cell").change(function(){
		$("#id_village").children("option[value!='']").remove();
		cell_val = $(this).val();
		if(cell_val !== ''){
		    $.ajax({
					type:"get",
					url: "/api/villages/"+cell_val+'/',
					success:function(villages)
					{
						for(var i=0; i< villages.length; i++){
								if (village_posted === villages[i].id){
									$("#id_village").append('<option value="'+ villages[i].id +'" selected>'+ villages[i].name +'</option>');
									$("id_village").val(village_posted);
								}
								else{
									$("#id_village").append('<option value="'+ villages[i].id +'">'+ villages[i].name +'</option>');
								}
						}
					},
					error: function(request)
					{
						console.log('failed to load cells')
					}
				});
		}

	});

	$("#id_district").trigger('change');


});