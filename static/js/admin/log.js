function check_log_search_form()
{
	userid=$.trim($("#id_userid").val());
	plotid=$.trim($("#id_plotid").val());
	transactionid=$.trim($("#id_transactionid").val());
	
	if(userid==''){
		reset_log_search_form_error_fields();
		$("#userid_error").html(' Please enter user id.');
		return false;		  
	}
	if(userid!='' && isNaN(userid)){
		reset_log_search_form_error_fields();
		$("#userid_error").html(' Please enter a valid user id.');
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
	$("#id_userid").html('');
	$("#id_plotid").html('');
	$("#id_transactionid").html('');
}
