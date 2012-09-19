
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Put all the global variables here.
Thanks for cooperation!  :)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

status_choices = (
    ('deleted','deleted'), 
    ('active','active'), 
    ('inactive','inactive')
)

boundary_types = (
    ('official','official'), 
    ('manual','manual')
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