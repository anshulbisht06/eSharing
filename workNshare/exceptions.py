'''
Created on Apr 9, 2015

@author: ansh
'''
from django.db import IntegrityError


class AlreadyExistsError(IntegrityError):
    pass
