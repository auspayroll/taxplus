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

function check_search_conditions()
{
	plotid = $.trim($("#id_new_plotid").val());
	citizenid = $.trim($("#id_new_citizenid").val());
	transactionid = $.trim($("#id_new_transactionid").val());
	if(plotid!=""&&isNaN(plotid))
	{
		$("#log_error").html("Please enter a valid plot ID.");
		return false;
	}
	if(citizenid!=""&&isNaN(citizenid))
	{
		$("#log_error").html("Please enter a valid citizen ID.");
		return false;
	}
	if(transactionid!=""&&isNaN(transactionid))
	{
		$("#log_error").html("Please enter a valid transaction ID.");
		return false;
	}
	return true;
}
