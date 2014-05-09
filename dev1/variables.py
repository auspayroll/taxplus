from django import forms
from django.utils.safestring import mark_safe
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Put all the global variables here.
Thanks for cooperation!  :)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

SUPPORT_EMAIL = 'peterd@surroundpix.com.au'
SUPPORT_PHONE = '1300303240'

#SMS details:
SMS_USER = 'pmrw'
SMS_PW = 'pmrw2013'

MAX_UPLOAD_SIZE = 20971520
FORM_UPLOAD_FILE_TYPES = ('.pdf','.doc','.docx','xls')

tax_exempt_reasons = (
	('Government Building','Government Building'),
	('Church','Church'),
	('Charitable Activity','Charitable Activity'),
	('Foreign Diplomatic Mission','Foreign Diplomatic Mission'),
	('Other','Other'),
)

miscellaneous_fee_types = (
    ('Public Cemetary Fee','Public Cemetary Fee'),
    ('Parking Fees','Parking Fees'),
    ('Public Parking Fees','Public Parking Fees'),
    ('Parking Fees on Boats','Parking Fees on Boats'),
    ('Civil Marriage Fee','Civil Marriage Fee'),
    ('Immovable Property Fees','Immovable Property Fees'),
    ('Official Certificates and Documents','Official Certificates and Documents'),
    ('Authorisation to Make Bricks or Roof Tiles','Authorisation to Make Bricks or Roof Tiles'),
    ('Billboard','Billboard'),
)

pending_payment_reasons = (
	('Legacy Data',	'Legacy Data'),
						   					   
)


citizen_deactivate_reasons = (
	('deceased','Deceased'),
	('double entry','Double Entry'),
	('expat','Expat'),
)
languages = (
	('English','English'),
	('Kinyarwanda','Kinyarwanda'),
	('French','French'),
)

status_choices = (
	('active','active'), 
    ('inactive','inactive'),
)

boundary_types = (
    ('official','official'), 
    ('manual','manual')
)

location_types = (
    ('property','property'),			
    ('sector','sector'), 
    ('district','district'),
    ('council','council'),
    ('province','province'),
)


currency_types = (
    ('RWF','Rwandan Franks'),
    ('AUD','Australian Dollars'),
    ('USD','American Dollars')
)

value_accepted = (
    ('NO','Reject Declared Value'),
    ('RV','Needs to Be Reviewed'),
    ('YE','Accept Declared Value')
)

declare_value_statuses = {
	('To be reviewed','To be reviewed'),
    ('Accepted','Accepted'),
    ('Rejected','Rejected')
}

assign_value_status = {
	('To be reviewed','To be reviewed'),
    ('Accepted','Accepted'),
    ('Rejected','Rejected')
}


media_types = (
    ('IMG','Image File'),
    ('OD','Offical Document'),
    ('SD','Supporting Document'),
    ('OT','Other')

)

on_hold = (
    ('T','Stop Process for Manual Review'),
    ('N','Not on Hold')
)
region_types = (
    ('Rural Area','Rural Area'),
    ('Town','Town'),
	('Kigali','Kigali'),
)

land_use_types_class = {
	'RES':('Residential',),
	'COM':('Commercial/Trading Centre', 'Commercial'),
	'IND':('Industrial', 'Industries'),
	'AGR':('Agricultural', 'Agricultural(>35 ha)', 'Agricultural(2-35 ha)', 'Agricultural(>2 ha)'),
	'QRY':('Quarry Purpose', 'Quarries Exploitation'),
	'FOR':('Forestry', 'Forestry'),
	'CUL':('Cultural (other)', 'Cultural (others)'),
	'CUN':('Cultural (non profit)', 'Cultural (no profit)'),
	'RUR':('Rural', 'Rural Area'),
	'URB':('Urban','Urban Area'),
}

fixed_asset_land_uses = ('RES', 'COM', 'IND', 'AGR', 'QRY')

land_use_types = (
    ('Residential','Residential'),
    ('Commercial','Commercial'),
	('Industrial','Industrial'),
	('Agricultural','Agricultural'),
	('Quarry Purpose','Quarry Purpose'),
)

land_lease_types = (
    ('Urban Area','Urban Area'),
    ('Trading Centre','Trading Centre'),
	('Rural Area','Rural Area'),
	('Agriculture','Agriculture (>2 hectares)'),
	('Quarries Exploitation','Quarries Exploitation'),
)

tax_types = (
    ('Fixed asset tax','Fixed asset tax'),
    ('Rental income tax','Rental income tax'),
	('Trading license tax','Trading license tax'),
)
fee_types = (
	('land_lease','Land lease fee'),
	#('market','Market fee'),
	('cleaning','Cleaning fee'),
)
tax_and_fee_types = (
	('fixed_asset','Fixed asset tax'),
    ('rental_income','Rental income tax'),
	('trading_license','Trading license tax'),
	('land_lease_fee','Land lease fee'),
	('market_fee','Market fee'),
	('cleaning_fee','Cleaning fee'),
	('misc_fee','Other Miscellaneous fees'),

)
tax_and_fee_invoice_prefixes = (
	('FA','fixed_asset'),
    ('RI','rental_income'),
	('TL','trading_license'),
	('LF','land_lease_fee'),
	('MF','market_fee'),
	('CF','cleaning_fee'),
	('MC','misc_fee'),

)

all_tax_types = (
	('all','All'),
	('fixed_asset','Fixed asset tax'),
    ('rental_income','Rental income tax'),
	('trading_license','Trading license tax'),
	('land_lease_fee','Land lease fee'),
	#('market_fee','Market fee'),
	('cleaning_fee','Cleaning fee'),
)

banks = (
  ('BK','Bank of Kigali'),
  ('BNR','Nation Bank of Rwanda'),
  ('FBR','Fina Bank Rwanda'),
  ('KCB','KCB Rwanda'),
  ('EBR','Equity Bank Rwanda'),
  ('EB','Ecobank'),
  ('CSO','Council Sector Office'),
  ('BP','Banque Populaire Du Rwanda'),
  ('N/A', 'N/A - Exempt'),
)

vehicle_types = (
  ('motorcycle','Motorcycle'),
  ('vehicle','Vehicle'),
  ('motorboat','Motor Boat'),
)

'''
owner_types = (
  ('citizen','Citizen'),
  ('business','Business'),
)

asset_types = (
  ('property','Property'),
  ('business','Business'),
  ('shop','Shop'),
  ('office','Office'),
  ('stall','Stall'),
  ('vehicle','Vehicle'),
  ('billboard','Billboard'),
)
'''

gender_types = (
	('Male','Male'),
	('Female','Female'),
	('Unknown','Unknown'),
)


def getFullBankName(bank):
	for c in banks:
		if c[0] == str(bank):
			return c[1]

def getKeyByValue(list,value):
	for i in list:
		if i[1] == value:
			return i[0]

def getValueByKey(list,key):
	for i in list:
		if i[0] == key:
			return i[1]

class HorizontalRadioRenderer(forms.RadioSelect.renderer):
  def render(self):
    return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))


#declare some hardcoded values for tax calculation
FIXED_ASSET_RESIDENTIAL_DEDUCTION = 3000000
FIXED_ASSET_TAX_RATE = 0.001
FIXED_ASSET_DUE_DATE = '03-31'
FIXED_ASSET_TAX_LATE_FEE_INTEREST = 0.015
FIXED_ASSET_TAX_LATE_FEE_SURCHARGE = 0.1
FIXED_ASSET_TAX_LATE_FEE_SURCHARGE_MAX = 1000000

RENTAL_INCOME_DUE_DATE = '03-31'

FEE_LATE_FEE_INTEREST = 0.015
FEE_LATE_FEE_SURCHARGE = 0.1
FEE_LATE_FEE_SURCHARGE_MAX = 10000
FEE_MONTHLY_DUE_DATE = '5'

business_yearly_turnover_tax = (
	('','--- Select yearly turnover ---'),								
	('60000','Up to 40,000000 Rwf'),
	('90000','From 40,000,001 to 60,000,000'),
	('150000','From 60,000,001 to 150,000,000'),
	('250000','Above 150 Million Rwf'),
)

area_types = (
	('Rural Area','Rural Area'),
	('Trading Centre','Trading Centre'),
	('City of Kigali','City of Kigali'),
)

business_activity = {

}

media_tags = {
	('Ownership','Ownership'),
	('Asset','Asset'),
	('Declared Value','Declared Value'),
	('Tax','Tax'),
	('Payment','Payment'),
}

business_types = {
	('Tailor','Tailor'),
	('Other businesses','Other Businesses'),
	('No premises','No premises (No cleaning fee)'),
}

activities = (
			  ('small',(('rural',4000), ('town',6000), ('kigali',8000))),
			  ('motorcycle',(('rural',4000), ('town',6000), ('kigali',8000))),
			  ('machine',(('rural',20000), ('town',30000), ('kigali',40000))),
			  ('car',(('rural',40000), ('town',40000), ('kigali',40000))),
			  ('boat',(('rural',20000), ('town',20000), ('kigali',20000))),
			  ('other',(('rural',20000), ('town',30000), ('kigali',40000)))
			)

activity_description = { 'small':'A) Vendors without shops, small scale technicians', 
						'motorcycle':'B) Transport of people and goods on motorcycles', 
						'machine':'C) Traders and technicians who use machines',
						'car':'D) All other vehicles besides bicycles, eg. cars',
						'boat':'E) For transport activities by motor boat',
						'other':'F) Other profit orientated activity' }