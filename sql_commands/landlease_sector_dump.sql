
select region.sector, coalesce(sums.fees,0) as fee_count, coalesce(sums.amount,0) as fee_amount, coalesce(sums.remaining_amount,0) as principle_overdue, 
coalesce(sums.interest,0) as interest, coalesce(sums.penalty,0) as penalty
from ( 
	select property_sector.id as sector_id, property_sector.name as sector 
	from property_sector
	join property_district on property_sector.district_id = property_district.id 
	where property_district.name = 'Kicukiro' 
	
) region left outer join

( 
	select property_sector.id as sector_id, sum(jtax_fee.remaining_amount) as remaining_amount, sum(jtax_fee.interest) as interest, sum(jtax_fee.penalty) as penalty,
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
	group by property_sector.id

) sums on region.sector_id = sums.sector_id 
order by region.sector

