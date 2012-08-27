from django.forms import ModelForm
from django import forms
from property.models import Property, Boundary
from django.contrib.gis.geos import Point, GEOSGeometry, Polygon
from django.forms import model_to_dict
from log.models import Log

class PropertyCreationForm(ModelForm):
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
        Log.objects.createLog(request.session.get('user'),property, None, None,"add")        
        return property