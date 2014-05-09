update jtax_propertytaxitem set due_date = '2012-03-31' where due_date = '2012-04-01';
update jtax_propertytaxitem set due_date = '2013-03-31' where due_date = '2013-04-01';

update jtax_rentalincometax set due_date = '2012-03-31' where due_date = '2012-04-01';
update jtax_rentalincometax set due_date = '2013-03-31' where due_date = '2013-04-01';

update jtax_tradinglicensetax set due_date = '2012-03-31' where due_date = '2012-04-01';
update jtax_tradinglicensetax set due_date = '2013-03-31' where due_date = '2013-04-01';

update jtax_propertytaxitem set period_to = '2013-12-31 23:59:59' where period_to > '2013-12-31 23:59:59';

update jtax_rentalincometax set period_to = '2013-12-31 23:59:59' where period_to > '2013-12-31 23:59:59';

update jtax_tradinglicensetax set period_to = '2013-12-31 23:59:59' where period_to > '2013-12-31 23:59:59';

