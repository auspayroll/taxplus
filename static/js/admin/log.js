function check_log_search_form()
{
	username=$.trim($("#id_username").val());
	plotid=$.trim($("#id_plotid").val());
	transactionid=$.trim($("#id_transactionid").val());
	
	if(username==''){
		reset_log_search_form_error_fields();
		$("#username_error").html(' Please enter username.');
		return false;		  
	}
	if(plotid!='' && isNaN(plotid)){
		reset_log_search_form_error_fields();
		$("#plotid_error").html(' Please enter a valid plot id.');
		return false;		  
	}
	if(transactionid!='' && isNaN(transactionid)){
		reset_log_search_form_error_fields();
		$("#transactionid_error").html(' Please enter a valid transaction id.');
		return false;		  
	}	
}
function reset_log_search_form_error_fields()
{
	$("#id_username").html('');
	$("#id_plotid").html('');
	$("#id_transactionid").html('');
}
