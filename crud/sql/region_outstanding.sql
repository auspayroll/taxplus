delete from crud_currentoutstanding;


insert into crud_currentoutstanding(balance, overdue, fee_type_id, village_id)
select sum(balance), sum(overdue), fee_type_id, village_id
from crud_accountfee
group by fee_type_id, village_id;


insert into crud_currentoutstanding(balance, overdue, fee_type_id, cell_id)
select sum(balance), sum(overdue), fee_type_id, cell_id
from crud_accountfee
group by fee_type_id, cell_id;


insert into crud_currentoutstanding(balance, overdue, fee_type_id, sector_id)
select sum(balance), sum(overdue), fee_type_id, sector_id
from crud_accountfee
group by fee_type_id, sector_id;


insert into crud_currentoutstanding(balance, overdue, fee_type_id, district_id)
select sum(balance), sum(overdue), fee_type_id, district_id from(
	select t1.balance, t1.overdue, t1.fee_type_id, district_id from (select sector_id, fee_type_id, sum(balance) as balance, sum(overdue) as overdue
	from crud_currentoutstanding group by fee_type_id, sector_id) t1 join property_sector sector on t1.sector_id = sector.id
) t2 group by fee_type_id, district_id;