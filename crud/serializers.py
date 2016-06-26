from rest_framework import serializers
from crud.models import Property, Account, District, Sector, Cell, Village, \
	Business, Citizen, Category, CategoryChoice, Rate, AccountFee


class TestSerializer(serializers.Serializer):
	pk = serializers.IntegerField(read_only=True)
	upi = serializers.CharField(max_length=100)
	test = serializers.CharField(write_only=True)

	def create(self, validated_data):
		"""
		Create and return a new `Snippet` instance, given the validated data.
		"""
		class Dummy:
			pass
		d = Dummy()
		d.pk = None
		d.upi = None
		return d

	def update(self, instance, validated_data):
		"""
		Update and return an existing `Snippet` instance, given the validated data.
		"""
		instance.title = validated_data.get('title', instance.title)
		instance.code = validated_data.get('code', instance.code)
		instance.linenos = validated_data.get('linenos', instance.linenos)
		instance.language = validated_data.get('language', instance.language)
		instance.style = validated_data.get('style', instance.style)
		instance.save()
		return instance


"""
class PropertySerializer(serializers.ModelSerializer):
	class Meta:
		model = Property
		fields = ('id', 'upi')
"""


class AccountFeeSerializer(serializers.ModelSerializer):
	class Meta:
		model  = AccountFee
		fields = ('account', 'fee_type', 'fee_subtype', 'from_date', 'auto', 'amount', 
			'due_days', 'period', 'sector', 'cell', 'village')

	account = serializers.PrimaryKeyRelatedField(label='Account Number', queryset=Account.objects.all(), style={'base_template': 'input.html'})
	fee_type = serializers.PrimaryKeyRelatedField(queryset=CategoryChoice.objects.filter(category__code='fee_type'))
	fee_subtype = serializers.PrimaryKeyRelatedField(label='Category', queryset=CategoryChoice.objects.filter(category__code__in=['land_use', 'cleaning_rate']))
	sector = serializers.PrimaryKeyRelatedField(required=False, label='Sector Id', queryset=Sector.objects.all(), style={'base_template': 'input.html'})
	cell = serializers.PrimaryKeyRelatedField(required=False, label='Cell Id', queryset=Cell.objects.all(), style={'base_template': 'input.html'})
	village = serializers.PrimaryKeyRelatedField(required=False, label='Village Id', queryset=Village.objects.all(), style={'base_template': 'input.html'})

class RateSerializer(serializers.ModelSerializer):
	class Meta:
		model  = Rate
		fields = ('category', 'sub_category', 'amount', 'date_from', 
			'date_to', 'village', 'village_id', 'sub_category_name',
			'category_name',
			'cell', 'sector')

	category = serializers.PrimaryKeyRelatedField(queryset=CategoryChoice.objects.filter(category__code='fee_type'))
	sub_category = serializers.PrimaryKeyRelatedField( queryset=CategoryChoice.objects.filter(category__code__in=['land_use', 'cleaning_rate']))
	category_name = serializers.ReadOnlyField(source='category.name')
	sub_category_name = serializers.ReadOnlyField(source='sub_category.name')
	village = serializers.ReadOnlyField(source='village.name')
	village_id = serializers.ReadOnlyField(source='village.id')
	cell = serializers.ReadOnlyField(source='cell.name')
	sector = serializers.ReadOnlyField(source='sector.name')

class CategorySerializer(serializers.ModelSerializer):
	class Meta:
		model  = Category
		fields = ('code', 'name')

class CategoryChoiceSerializer(serializers.ModelSerializer):
	class Meta:
		model  = CategoryChoice
		fields = ('code', 'name', 'category')


class CitizenSerializer(serializers.ModelSerializer):
	class Meta:
		model  = Citizen
		fields = ('id', 'citizen_id', 'first_name', 'middle_name', 'last_name', 'date_of_birth', 
			'phone_1', 'phone_2', 'email', 'address', 'gender', 'created', 'photo')



class BusinessSerializer(serializers.ModelSerializer):
	class Meta:
		model  = Business
		fields = ('id', 'name', 'tin', 'date_started', 'address', 'phone1', 
			'phone2', 'email', 'vat_register', )


class DistrictSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = District
		fields = ('id', 'name', 'code')


class SectorSerializer(serializers.ModelSerializer):
	class Meta:
		model = Sector
		fields = ('id', 'name', 'code', 'district', 'district_name', 'district_url')

	district = serializers.SlugRelatedField(slug_field='code', queryset=District.objects.all(),
		style={'base_template': 'input.html'}, label='District code')

	district_name = serializers.ReadOnlyField(source='district.name')

	district_url = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='district-detail',
        source='district.pk'
    )



class CellSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Cell
		fields = ('id', 'name', 'code', 'sector', 'sector_code', 'sector_url')

	sector_code = serializers.SlugRelatedField(slug_field='code', queryset=Sector.objects.all(),
		style={'base_template': 'input.html'}, label='Sector code', source='sector')

	sector = serializers.ReadOnlyField(source='sector.name')

	sector_url = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='sector-detail',
        source='sector.pk'
    )



class VillageSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Village
		fields = ('id', 'name', 'code', 'cell_code', 'cell', 'cell_url')

	cell_code = serializers.SlugRelatedField(slug_field='code', queryset=Cell.objects.all(),
		style={'base_template': 'input.html'}, source='cell')

	cell_url = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='cell-detail',
        source='cell.pk'
    )

	cell = serializers.ReadOnlyField(source='cell.name')



class PropertySerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Property
		fields = ('id', 'upi', 'sector', 'cell', 'village')


class AccountSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Account
		fields = ('id', 'name', 'start_date', 'tin', 'citizen_id', 'phone', 'email', 
			'principle_total', 'principle_paid', 'interest_total', 'interest_paid',
			'penalty_total', 'penalty_paid', 'overdue', 'balance')

		read_only_fields = ('principle_total', 'principle_paid', 'interest_total', 'interest_paid',
			'penalty_total', 'penalty_paid', 'overdue', 'balance')





