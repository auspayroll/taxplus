from django.utils import simplejson
from property.models import Property, Ownership


class PropertyMapper:    
          
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get all properties
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
    @staticmethod
    def getAllProperties():
        return Property.objects.all()
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get property by plot ID
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
    @staticmethod
    def getPropertyByPlotId(plotid):
        property = Property.objects.filter(plotid = plotid)
        if not property:
            return None
        else:
            return property[0]
    
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get property by conditions
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
    @staticmethod
    def getPropertiesByConditions(conditions):
        properties = None
        count = 0
        for key, value in conditions.iteritems():
            if key == 'plotid' and value:
                properties = Property.objects.filter(plotid = value)
                count = count + 1
            if key == 'suburb' and value:
                if count > 0:
                    properties = properties.filter(suburb__iexact = value)
                else:
                    properties = Property.objects.filter(suburb__iexact = value)
                count = count + 1
            if key == 'streetname' and value:
                if count > 0:
                    properties = properties.filter(streetname__iexact = value)
                else:
                    properties = Property.objects.filter(streetname__iexact = value)
                count = count + 1
            if key == 'streetno' and value:
                if count > 0:
                    properties = properties.filter(streetno__iexact = value)
                else:
                    properties = Property.objects.filter(streetno__iexact = value)
                count = count + 1
            if key == 'citizen' and value and properties:
                ownerships = Ownership.objects.filter(citizen = citizen).filter(property__in = properties)
                if len(ownerships) == 0:
                    return None
                else:
                    properties_new = []
                    for ownership in ownerships:
                            properties_new.append(ownership.property)
                    return properties_new
        return properties
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get Geographic data of property or peroperties.
    1) The returned data is of Json format
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
    @staticmethod
    def getPropertyGeoData(properties):
        data = {}
        properties_new = []
        
        # convert properties into list type
        if type(properties) != list:
            properties_new.append(properties)
        else:
            properties_new = properties
            
        properties = []
    
        # return json  
        for property in properties_new:
            points_json = []
            property_json = {}
            boundary=property.boundary
            str1=str(boundary.polygon.wkt)
            str1=str1.replace('POLYGON', '').replace('((', '').replace('))', '')[1:]
            points = str1.split(', ')
            for point in points:
                point_json={}
                point_parts = point.split(' ')
                point_x_parts=point_parts[0].replace(' ','').split('.')
                point_x=point_x_parts[0]+'.'+point_x_parts[1][:5]
                point_y_parts=point_parts[1].replace(' ','').split('.')
                point_y=point_y_parts[0]+'.'+point_y_parts[1][:5]
                point_json['x']=point_x
                point_json['y']=point_y
                points_json.append(point_json)
            property_json['points']=points_json
            property_json['plotid']=property.plotid
            property_json['streetno']=property.streetno
            property_json['streetname']=property.streetname
            property_json['suburb']=property.suburb
            properties.append(property_json)            
        data['properties'] = properties
        return simplejson.dumps(data)
            