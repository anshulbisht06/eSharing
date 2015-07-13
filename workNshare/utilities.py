'''
Created on Apr 2, 2015

@author: ansh
'''
from django.db.models import FileField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
import datetime
'''
calculate age from DoB
'''
def age(birth_date, on=None):
    birth_date=datetime.datetime.strptime(birth_date,'%Y-%m-%d')
    if on is None:
        on = datetime.date.today()
    was_earlier = (on.month, on.day) < (birth_date.month, birth_date.day)
    return on.year - birth_date.year - (was_earlier)



'''
    Restricted version of FileField, optional parameters :
        content_types - list containing allowed content_types.
        max_upload_size - indicates maximum file size allowed for upload.
'''
class ContentTypeRestrictedFileField(FileField):
    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types")
        self.max_upload_size = kwargs.pop("max_upload_size")

        super(ContentTypeRestrictedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):        
        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)
        
        file = data.file
        try:
            content_type = file.content_type
            if content_type in self.content_types:
                if file._size > self.max_upload_size:
                    raise forms.ValidationError(_('Please keep size of under %s. Current size of file %s') % (filesizeformat(self.max_upload_size), filesizeformat(file._size)))
            else:
                raise forms.ValidationError(_('File-type not supported.'))
        except AttributeError:
            pass        
            
        return data
