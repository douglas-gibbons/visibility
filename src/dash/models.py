'''
   Copyright 2013 Douglas Gibons

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
from django.db import models
import logging

logger = logging.getLogger(__name__)


class Product(models.Model):
    name = models.CharField(max_length = 128, primary_key = True)

class Host(models.Model):
    name = models.CharField(max_length = 128, primary_key = True)
    
class Environment(models.Model):
    name = models.CharField(max_length = 128, primary_key = True)

class Testpack(models.Model):
    name = models.CharField(max_length = 128, primary_key = True)

class Event(models.Model):
    
    start = models.DateTimeField('Start Time and Date',null=True)
    end = models.DateTimeField('End Time and Date',null=True)
    version = models.CharField('Version number. e.g. 1.2.3-45678',max_length = 128,null=True)
    product = models.ForeignKey(Product,null=True)
    success = models.NullBooleanField(null=True)
    
    def getParentType(self):
        '''Try to find out the parent type
        returns:
            Text name of model'''
        try:
            self.build
            return "Build"
        except Build.DoesNotExist:
            #logger.debug('Type is not Build')
            True
        try:
            self.testrun
            return "Testrun"
        except Testrun.DoesNotExist:
            #logger.debug('Type is not Testrun')
            True
        try:
            self.deploy
            return "Deploy"
        except Deploy.DoesNotExist:
            #logger.debug('Type is not Deploy')
            True
        
        return None
  
class Build(Event):
    vcs_location = models.CharField('URL or other locator to source code',max_length = 512,null=True)
    revision = models.IntegerField('Version control system revision number',null=True)
    builder = models.CharField('Builder can be URL to Jenkins build or comment etc',max_length = 512,null=True)

class Testrun(Event):
    testpack = models.ForeignKey(Testpack,null=True)
    test_location = models.CharField('Test Location can be URL to Jenkins job etc',max_length = 512,null=True)
    environment = models.ForeignKey(Environment,null=True)
    
''' Deployment to an environment '''
class Deploy(Event):
    environment = models.ForeignKey(Environment,null=True)
    host = models.ForeignKey(Host,null=True)
