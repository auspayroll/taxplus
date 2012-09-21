from django.db.models.query import QuerySet

class PropertyCommonMapper:
    @staticmethod
    def getGeoData(object_or_objects):
        objects = []
        if type(object_or_objects) == list or type(object_or_objects) == QuerySet:
            objects = list(object_or_objects)
        else:
            objects.append(object_or_objects)
        objects_json=[]
        for object in objects:
            object_json={}
            boundary = object.boundary
            points_json = []
            str1=str(boundary.polygon.wkt)
            str1=str1.replace('POLYGON', '').replace('((', '').replace('))', '')[1:]
            points = str1.split(', ')
            poly = ''
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
            object_json['points'] =  points_json
            object_json['name'] = str(object.name)
            objects_json.append(object_json)
        return objects_json
                