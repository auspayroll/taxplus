update jtax_fee as f set amount = (pf.amount - pf.fine_amount), remaining_amount = 0, is_paid = True from jtax_payfee as pf 
where f.id = pf.fee_id and f.i_status='active' and pf.i_status='active' and f.is_paid = False;


update jtax_propertytaxitem as f set amount = (pf.amount - pf.fine_amount), remaining_amount = 0, is_paid = True from jtax_payfixedassettax as pf 
where f.id = pf.property_tax_item_id and f.i_status='active' and pf.i_status='active' and f.is_paid = False;


update jtax_rentalincometax as f set amount = (pf.amount - pf.fine_amount), remaining_amount = 0, is_paid = True from jtax_payrentalincometax as pf 
where f.id = pf.rental_income_tax_id and f.i_status='active' and pf.i_status='active' and f.is_paid = False;

update jtax_tradinglicensetax as f set amount = (pf.amount - pf.fine_amount), remaining_amount = 0, is_paid = True from jtax_paytradinglicensetax as pf 
where f.id = pf.trading_license_tax_id and f.i_status='active' and pf.i_status='active' and f.is_paid = False;


update jtax_tradinglicensetax as f set i_status='inactive' where i_status='active' and is_paid = False and (select count(*) from jtax_tradinglicensetax as pf 
where f.business_id = pf.business_id and pf.i_status='active' and f.due_date=pf.due_date and pf.is_paid = True) > 0;

update jtax_tradinglicensetax set i_status = 'inactive' where period_from > period_to;

update jtax_fee as f set i_status = 'inactive' from asset_business b where f.business_id = b.id 
and f.i_status = 'active' and b.date_started >= f.period_to;
