from piston.handler import BaseHandler
#from mytest.models import Note
from django.shortcuts import get_object_or_404
from admin.Common import Common
from datetime import datetime
from django.db.models.query import QuerySet
from property.mappers.SectorMapper import SectorMapper
from PIL import Image


class SectorHandler(BaseHandler):
    allowed_methods = ('GET',)
    
    def read(self,request, sector_name, district_name=None):
        sector = None
        if district_name:
            sector = SectorMapper.getSectorsByDistrictAndName(district_name, sector_name)
        else:
            sector = SectorMapper.getSectorByName(sector_name)
        result = SectorMapper.getSectorGeoData(sector)
        return result
        

class ImageHandler(BaseHandler):
    allowed_methods = ('POST',)
       
    def create(self, request):
        name = request.FILES['image'].name
        image = Image.open(request.FILES["image"])
        image.save('uploads/api/images/'+name)
        return "OK"

class VideoHandler(BaseHandler):
    allowed_methods = ('POST',)
    
    def create(self,request):
        name = request.FILES['video'].name
        with open('uploads/api/videos/'+name, 'wb+') as destination:
            for chunk in request.FILES['video']:
                destination.write(chunk)
        return "OK"

'''
class NoteHandler(BaseHandler):
    allowed_methods = ('GET','POST','PUT','DELETE')
    
    def read(self, request, id=None):
       
        if id is not None:
            note = Note.objects.get(pk=id)            
            return NoteHandler.cleanObjForApi(note)
        else:
           
            notes = Note.objects.all()
            notes_new = []
            for note in notes:
                notes_new.append(note)

            if len(notes) == 0:
                return None
            else:
                return NoteHandler.cleanObjForApi(notes)
    
    def create(self, request):
        POST = request.POST
        title = POST['title']
        body = POST['body']
        user_id = int(POST['user_id'])
        user = PMUser.getUserById(user_id)
        notes = Note.objects.filter(user = user).filter(title=title).filter(body=body)
        if len(notes) > 0:
            return "duplicated"
        else:
            Note.objects.create(user = user, title=title, body=body)
            return "OK"
    
    
    def update(self, request, id):
        PUT = request.PUT
        title = PUT['title']
        body = PUT['body']
        user_id = int(PUT['user_id'])
        user = PMUser.getUserById(user_id)
        
        
        note = Note.objects.get(pk = id)
        note.title=title
        note.body=body
        note.user_id=user_id
        note.user=user
        note.save()
        return "OK"
    
    
    def delete(self, request, id):
        note = get_object_or_404(Note, pk=id)
        note.delete()
        return "Deleted"
    
    
    
    @staticmethod
    def cleanObjForApi(obj):       
        if type(obj) == QuerySet:
            for object in obj:
                for key, value in object.__dict__.iteritems():
                    if type(value) == datetime:
                        value = Common.localize(value)
                        setattr(object, key, value.strftime('%Y-%m-%d'))
                    
        else:
            for key, value in obj.__dict__.iteritems():
                if type(value) == datetime:
                    value = Common.localize(value)
                    setattr(obj, key, value.strftime('%Y-%m-%d'))
        return obj
'''