
select region.sector, region.cell, region.village, coalesce(sums.amount,0) as fee_amount, coalesce(sums.remaining_amount,0) as principle_overdue, 
coalesce(sums.interest,0) as interest, coalesce(sums.penalty,0) as penalty, coalesce(sums.fees,0) as fee_count
from ( 
	select property_village.id as village_id, property_village.name as village, 
	property_sector.id as sector_id, property_sector.name as sector, 
	property_cell.name as cell, property_cell.id as cell_id
	from property_village join property_cell on property_village.cell_id = property_cell.id
	join property_sector on property_cell.sector_id = property_sector.id
	join property_district on property_sector.district_id = property_district.id 
	where property_district.name = 'Kicukiro' 
	
) region left outer join

( 
	select property_village.id as village_id, sum(jtax_fee.remaining_amount) as remaining_amount, sum(jtax_fee.interest) as interest, sum(jtax_fee.penalty) as penalty,
	count(*) as fees, sum(jtax_fee.amount) as amount
	from property_village join property_cell on property_village.cell_id = property_cell.id
	join property_sector on property_cell.sector_id = property_sector.id
	join property_district on property_sector.district_id = property_district.id
	left outer join property_property on property_property.village_id = property_village.id
	left outer join jtax_fee on jtax_fee.property_id = property_property.id
	left outer join taxplus_categorychoice on jtax_fee.category_id = taxplus_categorychoice.id
	where property_district.name = 'Kicukiro' 
	and taxplus_categorychoice.code = 'land_lease'
	and jtax_fee.status_id = 1
	group by property_sector.id, property_cell.id, property_village.id

) sums on region.village_id = sums.village_id 
order by region.sector, region.cell, region.village

