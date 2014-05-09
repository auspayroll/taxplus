from django.conf.urls import *
from piston.resource import Resource
from api.handlers import *
from api.CORSResource import CORSResource

#note_handler = CORSResource(NoteHandler)
image_handler = CORSResource(ImageHandler)
video_handler = CORSResource(VideoHandler)
sector_handler = CORSResource(SectorHandler)



urlpatterns = patterns('',
    #url(r'^note/add/$', note_handler, { 'emitter_format': 'xml' }),
    #url(r'^note/(?P<id>(\d+))/$', note_handler, { 'emitter_format': 'xml' }),
    #url(r'^notes/', note_handler, { 'emitter_format': 'xml' }),
    url(r'^image/add/$', image_handler, { 'emitter_format': 'xml' }),
    url(r'^video/add/$', video_handler, { 'emitter_format': 'xml' }),
    
    url(r'^sector/(?P<sector_name>(\w+))/$', sector_handler, { 'emitter_format': 'xml' }),
    url(r'^sector/(?P<sector_name>(\w+))/(?P<district_name>(\w+))/$', sector_handler, { 'emitter_format': 'xml' }),
)