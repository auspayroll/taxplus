/* ONLY RUN ONCE */

insert into asset_ownership(asset_property_id,  owner_citizen_id, share, i_status, date_started, date_created)
select property_id, citizen_id, share, i_status, startdate, CURRENT_TIMESTAMP from property_ownership;