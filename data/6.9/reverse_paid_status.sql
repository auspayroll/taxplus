update jtax_setting set valid_from = '2011-01-01' where valid_from = '2013-01-01' and valid_to is null;

update jtax_fee f set is_paid = False where is_paid=True and i_status='active' and (select count(*) from jtax_payfee where fee_id = f.id and i_status ='active') = 0;

update jtax_propertytaxitem f set is_paid = False where is_paid=True and i_status='active' and (select count(*) from jtax_payfixedassettax where property_tax_item_id = f.id and i_status ='active') = 0;

update jtax_rentalincometax f set is_paid = False where is_paid=True and i_status='active' and (select count(*) from jtax_payrentalincometax where rental_income_tax_id = f.id and i_status ='active') = 0;

update jtax_tradinglicensetax f set is_paid = False where is_paid=True and i_status='active' and (select count(*) from jtax_paytradinglicensetax where trading_license_tax_id = f.id and i_status ='active') = 0;