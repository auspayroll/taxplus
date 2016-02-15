
 $(document).ready(function(){
	if(localStorage.getItem("sectors")) {
	    data = JSON.parse(localStorage.getItem("sectors"));
	} else {
	    $.ajax({
				type:"get",
				url: "/static/sectors.json",
				success:function(sectors)
				{
					localStorage.setItem("sectors", JSON.stringify(sectors));
				},
				error: function(request)
				{
					console.log('failed to load sectors')
				}
			});
	}

	if(localStorage.getItem("cells")) {
	    data = JSON.parse(localStorage.getItem("cells"));
	} else {
	    $.ajax({
				type:"get",
				url: "/static/cells.json",
				success:function(cells)
				{
					localStorage.setItem("cells", JSON.stringify(cells));
				},
				error: function(request)
				{
					console.log('failed to load cells')
				}
			});
	}

	if(localStorage.getItem("villages")) {
	    data = JSON.parse(localStorage.getItem("villages"));
	} else {
	    $.ajax({
				type:"get",
				url: "/static/villages.json",
				success:function(villages)
				{
					localStorage.setItem("villages", JSON.stringify(villages));
				},
				error: function(request)
				{
					console.log('failed to load villages')
				}
			});
	}

	$("#id_district").change(function(){
		var district_val = $("#id_district").val();
		$("#id_sector").children("option[value!='']").remove();
		if(district_val !== ''){
			var sectors = JSON.parse(localStorage.getItem('sectors'));
			for(var i=0; i< sectors.length; i++){
				if(Number(district_val) === sectors[i]['district_id']){
					if (sector_posted === sectors[i].id){
						$("#id_sector").append('<option value="'+ sectors[i].id +'" selected>'+ sectors[i].name +'</option>');
					}
					else{
						$("#id_sector").append('<option value="'+ sectors[i].id +'">'+ sectors[i].name +'</option>');
					}
				}
			}
			//$("#search_table #id_pay_village").trigger("chosen:updated");
		}
		$("#id_sector").change();
	}).trigger('change');


	$("#id_sector").change(function(){
		var sector_val = $("#id_sector").val();
		$("#id_cell").children("option[value!='']").remove();
		if(sector_val !== ''){
			var cells = JSON.parse(localStorage.getItem('cells'));
			for(var i=0; i< cells.length; i++){
				if(Number(sector_val) === cells[i]['sector_id']){
					if (cell_posted === cells[i].id){
						$("#id_cell").append('<option value="'+ cells[i].id +'" selected>'+ cells[i].name +'</option>');
					}
					else{
						$("#id_cell").append('<option value="'+ cells[i].id +'">'+ cells[i].name +'</option>');
					}
				}
			}
		}
		$("#id_cell").change();
	}).trigger('change');


	$("#id_cell").change(function(){
		var cell_val = $("#id_cell").val();
		$("#id_village").children("option[value!='']").remove();
		if(cell_val !== ''){
			var villages = JSON.parse(localStorage.getItem('villages'));
			for(var i=0; i< villages.length; i++){
				if(Number(cell_val) === villages[i]['cell_id']){
					if (village_posted === villages[i].id){
						$("#id_village").append('<option value="'+ villages[i].id +'" selected>'+ villages[i].name +'</option>');
					}
					else{
						$("#id_village").append('<option value="'+ villages[i].id +'">'+ villages[i].name +'</option>');
					}
				}
			}
		}
	}).trigger('change');


});