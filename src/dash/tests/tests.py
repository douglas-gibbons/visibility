'''
   Copyright 2013 Douglas Gibbons

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

from django.test import TestCase
from django.utils import unittest    
from django.test.client import Client
from django.contrib.auth.models import User
from dash.models import Build

import logging
import json

logger = logging.getLogger(__name__)


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class TestHelper(unittest.TestCase):
                                
    def setUp(self):
        self.client = Client()
    
    def testNewBuild(self):
        randomString = User.objects.make_random_password()
        
        response = self.client.get('/dash/new_build?Product.name='+randomString+
                                   '&Build.version=1.1.1-234&Build.revision=12&Build.start=2013-05-08T13:34:34Z')
        
        self.assertEqual(response.status_code, 200)
        
        logger.debug('Response content:' + str(response.content))
        
        id = response.content
        logger.debug('Got an id of '+str(id))
        
        build = Build.objects.get(pk=id)
        self.assertEqual(build.product.name, randomString, 'Incorrect product name')
 
               
        response = self.client.get('/dash/new_build?Product.name='+randomString+'&Build.version=1.1.1-234&Build.revision=12')
        self.assertEqual(response.status_code, 200, 'Could not create a similar entry using same product name')

    def testUpdateBuild(self):
        
        randomString = User.objects.make_random_password()
        dateTimeString = '2013-05-08T14:00:00Z'

        '''Create build'''
        response = self.client.get('/dash/new_build?Product.name='+randomString+
                                   '&Build.version=1.1.1-234&Build.revision=12&Build.start='+dateTimeString)
        self.assertEqual(response.status_code, 200)
        id = response.content

        response = self.client.get('/dash/update_build?Build.id='+str(id)+'&Build.end='+dateTimeString)
        self.assertEqual(response.status_code, 200)
        newId = response.content
        '''Check we get back the same id'''
        self.assertEqual(id,newId)
        
        build = Build.objects.get(pk=id)
        
        '''Check end date has updated to same as start date'''
        self.assertEqual(build.start,build.end)
    