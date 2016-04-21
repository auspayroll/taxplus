delete from crud_currentoutstanding;


insert into crud_currentoutstanding(balance, overdue, fee_type_id, village_id, accounts)
select sum(balance), sum(overdue), fee_type_id, village_id, count(*)
from crud_accountfee where closed is null
group by fee_type_id, village_id;


insert into crud_currentoutstanding(balance, overdue, fee_type_id, cell_id, accounts)
select sum(balance), sum(overdue), fee_type_id, cell_id, count(*)
from crud_accountfee where closed is null
group by fee_type_id, cell_id;


insert into crud_currentoutstanding(balance, overdue, fee_type_id, sector_id, accounts)
select sum(balance), sum(overdue), fee_type_id, sector_id, count(*)
from crud_accountfee where closed is null
group by fee_type_id, sector_id;


insert into crud_currentoutstanding(balance, overdue, fee_type_id, district_id, accounts)
select sum(balance), sum(overdue), fee_type_id, district_id, count(*)
from crud_accountfee where closed is null
group by fee_type_id, district_id;