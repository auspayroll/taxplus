function init()
{
	$(document).ready(function(){
		$('#addPermissions').mouseover(function(){
			$(this).css('cursor','pointer');
		});
		
		$('#addPermissions').click(function(){
			var selectedOptions = $('#id_permissions_all option:selected');
			if (selectedOptions.length == 0) {
	            alert("Nothing to move.");
	        }
	        $('#id_permissions_selected').append($(selectedOptions).clone());
	        $(selectedOptions).remove();
		});
		
		$('#deletePermissions').mouseover(function(){
			$(this).css('cursor','pointer');
		});
		
		$('#deletePermissions').click(function(){
			var selectedOptions = $('#id_permissions_selected option:selected');
			if (selectedOptions.length == 0) {
	            alert("Nothing to move.");
	        }
	        $('#id_permissions_all').append($(selectedOptions).clone());
	        $(selectedOptions).remove();
		});		
	});
}


$(function(){		
		$(".currency").keyup(function(){
			var val = $(this).val().replace(/,/gi,'');
			if(val.indexOf('.') > -1){
				return;
			}
			val = parseFloat(val);
			if(!isNaN(val)){
				if(val < 0 ){
					$(this).val('0');
				}
				else {
					val = val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
					$(this).val(val);
				}
			}

		});
});
