from django.db import models
from datetime import datetime
from django.contrib.gis.db import models
from django.utils import timezone


class importDataPerson(models.Model):
    surname = models.CharField(max_length=100,blank=True)
    given_name = models.CharField(max_length=100,blank=True)
    middle_name = models.CharField(max_length=100,blank=True)
    national_id = models.BigIntegerField(blank=True)

class importDataLand(models.Model):
    upi = models.CharField(max_length=100,blank=True)
    area = models.FloatField(max_length=30,blank=True,default='0')
    is_approved = models.CharField(blank=True,max_length=5)
    short_description = models.CharField(max_length=100,blank=True)
    lease_term = models.CharField(max_length=20,blank=True)
    cell_name = models.CharField(max_length=20,blank=True)
    sector_name = models.CharField(max_length=20,blank=True)
    district_name = models.CharField(max_length=20,blank=True)

class importDataLandOwnership(models.Model):
    land_id = models.ForeignKey(importDataLand)
    person_id = models.ForeignKey(importDataPerson)



class ImportPropertyData(models.Model):
	ogc_fid = models.AutoField(primary_key=True)
	wkb_geometry = models.PolygonField(srid=3857,blank=True, null=True)
	objectid = models.DecimalField(max_digits=9,decimal_places = 0,blank=True, null=True)
	parcels_id = models.DecimalField(max_digits=19,decimal_places = 11,blank=True, null=True)
	province =  models.CharField(max_length=50,blank=True, null=True)
	district =  models.CharField(max_length=50,blank=True, null=True)
	sector =  models.CharField(max_length=50,blank=True, null=True)
	cell =  models.CharField(max_length=50,blank=True, null=True)
	cell_code =  models.CharField(max_length=50,blank=True, null=True)
	village =  models.CharField(max_length=254,blank=True, null=True)
	shape_leng = models.DecimalField(max_digits=19,decimal_places = 11,blank=True, null=True)
	shape_area = models.DecimalField(max_digits=19,decimal_places = 11,blank=True, null=True)
	
	class Meta:
		db_table = 'kiyovu_parcels'


'''
class ImportCellData(models.Model):
	Code = models.CharField(max_length = 255, primary_key = True)
	Libelle = models.CharField(max_length = 255, null=True, blank=True)
	ID_Util_Creation =  models.FloatField(null=True, blank=True)
	DateCreation = models.DateTimeField(null=True, blank=True)
	ID_Util_LastUpdate =  models.FloatField(null=True, blank=True)
	DateLastUpdate = models.DateTimeField(null=True, blank=True)
	class Meta:
		db_table = 'tb00_UACellules'

class ImportDistrictData(models.Model):
	Code = models.CharField(max_length = 4, primary_key = True)
	Libelle = models.CharField(max_length = 50, null=True, blank=True)
	ID_Util_Creation =  models.IntegerField(null=True, blank=True)
	DateCreation = models.DateTimeField(null=True, blank=True)
	ID_Util_LastUpdate =  models.IntegerField(null=True, blank=True)
	DateLastUpdate = models.DateTimeField(null=True, blank=True)
	class Meta:
		db_table = 'tb00_UADistricts'

class ImportVillageData(models.Model):
	Code = models.CharField(max_length = 255, primary_key = True)
	Libelle = models.CharField(max_length = 50, null=True, blank=True)
	ID_Util_Creation =  models.IntegerField(null=True, blank=True)
	DateCreation = models.DateTimeField(null=True, blank=True)
	ID_Util_LastUpdate =  models.IntegerField(null=True, blank=True)
	DateLastUpdate = models.DateTimeField(null=True, blank=True)
	class Meta:
		db_table = 'tb00_UAMidugudus'

class ImportProvinceData(models.Model):
	Code = models.CharField(max_length = 2, primary_key = True)
	Libelle = models.CharField(max_length = 50, null=True, blank=True)
	ID_Util_Creation =  models.IntegerField(null=True, blank=True)
	DateCreation = models.DateTimeField(null=True, blank=True)
	ID_Util_LastUpdate =  models.IntegerField(null=True, blank=True)
	DateLastUpdate = models.DateTimeField(null=True, blank=True)
	class Meta:
		db_table = 'tb00_UAProvinces'

class ImportSectorData(models.Model):
	Code = models.CharField(max_length = 6, primary_key = True)
	Libelle = models.CharField(max_length = 50, null=True, blank=True)
	ID_Util_Creation =  models.IntegerField(null=True, blank=True)
	DateCreation = models.DateTimeField(null=True, blank=True)
	ID_Util_LastUpdate =  models.IntegerField(null=True, blank=True)
	DateLastUpdate = models.DateTimeField(null=True, blank=True)
	class Meta:
		db_table = 'tb00_UASecteurs'

class ImportCitizenData(models.Model):
	ID_Contribuable = models.AutoField(primary_key=True)
	TIN = models.CharField(max_length=20, blank=True, null=True)
	Noms = models.CharField(max_length=50, blank=True, null=True)
	ID_Sexe = models.IntegerField(blank=True, null=True) 
	ID_EtatCivil = models.IntegerField(blank=True, null=True) 
	Photo = models.CharField(max_length=150, blank=True, null=True)
	NumID = models.CharField(max_length=100, blank=True, null=True)
	DateNaiss = models.CharField(max_length=10, blank=True, null=True)
	BP = models.CharField(max_length=50, blank=True, null=True)
	Tel = models.CharField(max_length=50, blank=True, null=True)
	ID_Typcontribuable = models.IntegerField(blank=True, null=True) 
	AffilieTVA = models.IntegerField(blank=True, null=True)
	ID_Naiss_Province = models.CharField(max_length=2, blank=True, null=True)
	ID_Naiss_District = models.CharField(max_length=4, blank=True, null=True)
	ID_Naiss_Secteur = models.CharField(max_length=6, blank=True, null=True)
	ID_Naiss_Cellule = models.CharField(max_length=8, blank=True, null=True)
	ID_Naiss_Mudugudu = models.CharField(max_length=10, blank=True, null=True)
	Naiss_Description = models.CharField(max_length=150, blank=True, null=True)
	ID_InscRC_Province = models.CharField(max_length=2, blank=True, null=True)
	ID_InscRC_District = models.CharField(max_length=4, blank=True, null=True)
	ID_InscRC_Secteur = models.CharField(max_length=6, blank=True, null=True)
	ID_InscRC_Cellule = models.CharField(max_length=8, blank=True, null=True)
	ID_InscRC_Mudugudu = models.CharField(max_length=10, blank=True, null=True)
	InscRC_Description = models.CharField(max_length=150, blank=True, null=True)
	ID_Res_Province = models.CharField(max_length=2, blank=True, null=True)
	ID_Res_District = models.CharField(max_length=4, blank=True, null=True)
	ID_Res_Secteur = models.CharField(max_length=6, blank=True, null=True)
	ID_Res_Cellule = models.CharField(max_length=8, blank=True, null=True)
	ID_Res_Mudugudu = models.CharField(max_length=10, blank=True, null=True)
	Res_Description = models.CharField(max_length=150, blank=True, null=True)
	ID_Secteur = models.CharField(max_length=6, blank=True, null=True)
	Comment = models.CharField(max_length=300, blank=True, null=True)
	ID_Util_Creation = models.IntegerField(blank=True, null=True)
	DateCreation = models.DateTimeField(blank=True, null=True)
	ID_Util_LastUpdate = models.IntegerField(blank=True, null=True)
	DateLastUpdate = models.DateTimeField(blank=True, null=True)

	class Meta:
		db_table = 'tb01_Contribuables'

class ImportFeeData(models.Model):
	ID_Redevance = models.AutoField(primary_key = True)
	ID_Contribuable = models.IntegerField(null=True, blank = True)
	ID_TypRecette = models.IntegerField(null=True, blank = True)
	ID_Periode = models.IntegerField(null=True, blank = True)
	Redevance = models.FloatField(null = True, blank = True)
	DateLimitePayment = models.DateTimeField(null= True, blank = True)
	ID_AutreInfo = models.IntegerField(null=True, blank = True)
	ynRecLocked = models.BooleanField(null=True, blank = True)
	ynFacture = models.BooleanField(null=True, blank = True)
	ID_Facture = models.IntegerField(null=True, blank = True)
	DateFacture = models.DateTimeField(null=True, blank = True)
	Accroissement = models.FloatField(null=True, blank = True)
	IntRetard = models.FloatField(null=True, blank = True)
	TotalDu = models.FloatField(null=True, blank = True)
	ID_Secteur = models.CharField(max_length = 6, null=True, blank=True)
	Comment = models.CharField(max_length = 100, null=True, blank=True)
	ID_Util_Creation = models.IntegerField(null=True, blank=True)
	DateCreation = models.DateTimeField(null=True, blank = True)
	ID_Util_LastUpdate = models.IntegerField(null=True, blank = True)
	DateLastUpdate = models.DateTimeField(null=True, blank = True)
	class Meta:
		db_table = 'tb01_Redevances'

class ImportInvoiceData(models.Model):
	ID_Facture = models.AutoField(primary_key=True)
	ID_Contribuable = models.IntegerField(null=True, blank = True)
	NumFacture = models.CharField(max_length = 15, null=True, blank = True)
	DateFacture = models.DateTimeField(null=True, blank = True)
	ID_AuteurFacture = models.IntegerField(null=True, blank=True)
	MontantRedevances = models.FloatField(null=True, blank = True)
	MontantAccroissements = models.FloatField(null=True, blank=True)
	MontantIntRetards = models.FloatField(null=True, blank=True)
	MontantTotal = models.FloatField(null=True, blank=True)
	DateLimiteValidite = models.DateTimeField(null=True, blank=True)
	ID_FacturePrecedente = models.IntegerField(null=True, blank = True)
	ID_FactureSuivante = models.IntegerField(null=True, blank = True)
	ID_FactureState = models.IntegerField(null=True, blank = True)
	Comment = models.CharField(max_length = 100, null=True, blank = True)
	ID_Secteur = models.CharField(max_length=6, null=True, blank=True)
	ID_Util_Creation = models.IntegerField(null=True, blank=True)
	DateCreation = models.DateTimeField(null=True, blank = True)
	ID_Util_LastUpdate = models.IntegerField(null=True, blank = True)
	DateLastUpdate = models.DateTimeField(null=True, blank = True)
	class Meta:
		db_table = 'tb01_Factures'

class ImportPeriodData(models.Model):
	ID_Periode = models.AutoField(primary_key=True)
	Periode_fr = models.CharField(max_length=50, null=True, blank=True)
	Periode_en = models.CharField(max_length=50, null=True, blank=True)
	DateDebut = models.DateTimeField(null=True, blank=True)
	DateFin = models.DateTimeField(null=True, blank=True)
	ID_Periodicite = models.IntegerField(null=True, blank=True)
	ynActive = models.BooleanField(null=True, blank=True)
	Comment = models.CharField(max_length=200, null=True, blank=True)
	ID_Util_Creation = models.IntegerField(null=True, blank=True)
	DateCreation = models.DateTimeField(null=True, blank=True)
	ID_Util_LastUpdate = models.IntegerField(null=True, blank=True)
	DateLastUpdate = models.DateTimeField(null=True, blank=True)
	class Meta:
		db_table = 'tb01_Periodes'

'''