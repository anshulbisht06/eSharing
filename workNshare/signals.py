'''
Created on Apr 9, 2015

@author: ansh
'''
from django.dispatch import Signal


follower_created = Signal(providing_args=['follower'])
follower_removed = Signal(providing_args=['follower'])
following_created = Signal(providing_args=['following'])
following_removed = Signal(providing_args=['following'])
