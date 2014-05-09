/*
Old import data for property ownership across Districts have misplaced Citizen ID into Foreign Identity Number column.
This SQL:

- Copy foreign Identity Number over to Citizen ID column , exclude the invalid citizen id
( Citizen ID format: ignore the first number, then it 's YOB, then gender (7: female, 8: male) )

- Update YOB and Gender as well
*/

update citizen_citizen set gender = 
CASE WHEN substring(foreign_identity_number from 6 for 1) = '8' THEN 'Male' ELSE 'Female' END ,
year_of_birth = substring(foreign_identity_number from 2 for 4),
citizen_id = replace(foreign_identity_number,'"','') ,
foreign_identity_number = ''
WHERE  citizen_id = '' and foreign_identity_number is not null 
and substring(foreign_identity_number from 1 for 1) = '1' and substring(foreign_identity_number from 6 for 1) in ('7','8') ;