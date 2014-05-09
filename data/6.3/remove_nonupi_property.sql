update property_property set status_id = 2 where cell_id is null and boundary_id is null and status_id =1 and id not in 
(select distinct(property_id) from jtax_propertytaxitem where i_status='active' and is_paid = True) and id not in 
(select distinct(property_id) from jtax_rentalincometax where i_status='active' and is_paid = True) and id not in 
(select distinct(property_id) from jtax_fee where fee_type='land_lease' and i_status='active' and is_paid = True);


update jtax_fee set i_status = 'inactive' where i_status='active' and fee_type = 'land_lease' and is_paid =False and property_id in (select id from property_property
WHERE status_id != 1 or is_land_lease = False);
update jtax_propertytaxitem set i_status = 'inactive' where i_status='active' and  is_paid =False and property_id in (select id from property_property
WHERE status_id != 1);
update jtax_rentalincometax set i_status = 'inactive' where i_status='active' and  is_paid =False and property_id in (select id from property_property
WHERE status_id != 1 or is_leasing = False);


update jtax_propertytaxitem set i_status='inactive' 
WHERE i_status = 'active' and is_paid=False and id  IN (SELECT id
              FROM (SELECT id,
                             row_number() over (partition BY property_id, due_date, is_paid, i_status  ORDER BY id desc) AS rnum
                     FROM jtax_propertytaxitem where is_paid = False) t
              WHERE t.rnum > 1) ;

update jtax_rentalincometax set i_status='inactive' 
WHERE i_status = 'active' and is_paid=False and id  IN (SELECT id
              FROM (SELECT id,
                             row_number() over (partition BY property_id, due_date, is_paid, i_status  ORDER BY id desc) AS rnum
                     FROM jtax_rentalincometax where is_paid = False) t
              WHERE t.rnum > 1) ;


update jtax_tradinglicensetax set i_status='inactive' 
WHERE i_status = 'active' and is_paid=False and id  IN (SELECT id
              FROM (SELECT id,
                             row_number() over (partition BY business_id, subbusiness_id, due_date, is_paid, i_status  ORDER BY id) AS rnum
                     FROM jtax_tradinglicensetax where is_paid = False) t
              WHERE t.rnum > 1) ;

update jtax_fee set i_status='inactive' 
WHERE i_status = 'active' and is_paid=False and id  IN (SELECT id
              FROM (SELECT id,
                             row_number() over (partition BY fee_type, business_id, subbusiness_id, property_id, due_date, is_paid, i_status  ORDER BY id) AS rnum
                     FROM jtax_fee where is_paid = False) t
              WHERE t.rnum > 1) ;

			  

