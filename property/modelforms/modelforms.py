from django.forms import ModelForm
from django import forms
from property.models import Property, Boundary, District, Sector, Council
from django.contrib.gis.geos import Point, GEOSGeometry, Polygon
from django.forms import model_to_dict
from log.models import Log
from property.mappers.DistrictMapper import DistrictMapper
from property.mappers.CouncilMapper import CouncilMapper

class PropertyCreationForm(ModelForm):
    """
    Consider the boundary of a property as a polygon, then boundary textfield stores the coordinators of polygon vertices
    """
    boundary = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Property
        fields = ("plotid", "streetno", "streetname", "suburb")
    def save(self,request):
        ## create polygan
        plist=[]
        boundary=self.cleaned_data["boundary"]
        points = boundary.split('#')
        for point in points:
            parts = point.split(',')
            point_x=parts[0]
            point_y=parts[1]
            plist.append(GEOSGeometry('POINT(%s %s)' %(point_x, point_y)))
        plist.append(plist[0])
        polygon = Polygon(plist)
        boundary = Boundary.objects.create(polygon=polygon, type = "manual", i_status="active")
        property = forms.ModelForm.save(self, False)
        property.boundary = boundary
        property.i_status="active"
        property.save()
        new_data = model_to_dict(property)
        Log.objects.createLog(request,object=property,action="add",plotid=self.cleaned_data["plotid"])        
        return property




class CouncilCreationForm(ModelForm):
    """
    Consider the boundary of a district as a polygon, then boundary textfield stores the coordinators of polygon vertices
    """
        
    boundary = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Council
        fields = ("name","address",)
        

class SectorCreationForm(ModelForm):
    """
    Consider the boundary of a district as a polygon, then boundary textfield stores the coordinators of polygon vertices
    """
    districts = [(d.id, d.name) for d in DistrictMapper.getAllDistricts()]
    #councils = [(c.id, c.name) for c in CouncilMapper.getAllCouncils()]
    boundary = forms.CharField(widget=forms.Textarea)
    district = forms.ChoiceField(widget = forms.Select(),required = True, choices = districts)
    #council = forms.ChoiceField(widget = forms.Select(),required = True, choices = councils)  
    class Meta:
        model = Sector
        fields = ("name","council")
    def __init__(self, request, *args, **kwargs):
        super(SectorCreationForm, self).__init__(*args, **kwargs)
        councils = None
        user = request.session.get('user')
        if user.superuser:
            councils = [(c.id, c.name) for c in CouncilMapper.getAllCouncils()]
        else:
            councils = [(user.council.id, user.council.name)]
        self.fields['council'] = forms.ChoiceField(widget = forms.Select(),required = True, choices = councils)

  




class DistrictCreationForm(ModelForm):
    """
    Consider the boundary of a district as a polygon, then boundary textfield stores the coordinators of polygon vertices
    """
    boundary = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = District
        fields = ("name",)
    def save(self,request):
        ## create polygan
        plist=[]
        boundary=self.cleaned_data["boundary"]
        points = boundary.split('#')
        for point in points:
            parts = point.split(',')
            point_x=parts[0]
            point_y=parts[1]
            plist.append(GEOSGeometry('POINT(%s %s)' %(point_x, point_y)))
        plist.append(plist[0])
        polygon = Polygon(plist)
        boundary = Boundary.objects.create(polygon=polygon, type = "manual", i_status="active")
        district = forms.ModelForm.save(self, False)
        district.boundary = boundary
        district.i_status="active"
        district.save()
        new_data = model_to_dict(district)
        Log.objects.createLog(request,object=district,action="add")        
        return district

