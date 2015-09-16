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
import logging
from django.core.management.base import BaseCommand
import httplib,urllib
import datetime
import random
import time
import threading

''' Pretends to be a whole pipeline; adding builds,deploys,testruns in real time'''

logger = logging.getLogger(__name__)

        
class Dummy(BaseCommand):
    
    def nowString(self):
        '''Could just return the text "now" instead''' 
        # return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return 'now'
    
    def sleepRandom(self):
        minTime = 0 # seconds
        maxTime = 30
        t = random.randrange(minTime, maxTime, 1)
        logger.debug('Sleeping for '+str(t)+' seconds')
        time.sleep(t) 
    
    def getUrl(self,url,dict):
        hostname='localhost'
        port=8000
        conn = httplib.HTTPConnection(hostname,port)
        
        params = urllib.urlencode(dict)
        
        logger.debug('Getting '+url)
        conn.request("GET",url + '?' + params)
        response = conn.getresponse()
        id = response.read()
        
        logger.debug('Got back ID '+str(id))
        
        return id
    
    
    def createBuild(self,productName,version):
        '''Build'''
        
        url = '/dash/new_build'
        dict = {
            'Product.name' : productName,
            'Build.version' : version,
            'Build.revision' : '1000',
            'Build.start' : self.nowString()
            }
        
        id = self.getUrl(url,dict)
        return id

    def updateBuild(self,id,success):
        
        self.sleepRandom()
        
        url = '/dash/update_build'
        dict = {
            'Build.id' : str(id),
            'Build.success' : success,
            'Build.end' : self.nowString()
        }
        self.getUrl(url,dict)
    
    def createDeploy(self,productName,version,environment):
        ''' Deploy '''
        logger.debug('Deploying '+version)
        
        url = '/dash/new_deploy'
        dict = {
         'Product.name' : productName,
         'Deploy.version' : version,
         'Environment.name' : environment,
         'Deploy.start' : self.nowString()
        }
        id = self.getUrl(url,dict)
        return id
    
    def updateDeploy(self,id,success):
        url = '/dash/update_deploy'
        dict = {
            'Deploy.id' : str(id),
            'Deploy.success' : '1' ,
            'Deploy.end' : self.nowString()
        }
        id = self.getUrl(url,dict)
        
    def createTest(self,productName,version,success):
        '''Fail now and again'''


        ''' Test '''
        logger.debug('Testing '+version)
        
        url = '/dash/new_testrun'
        dict = {
            'Product.name' : productName,
            'Testpack.name' : 'Sanity',
            'Testrun.version' : version,
            'Environment.name' : 'Testing',
            'Testrun.success' : success,
            'Testrun.start' : self.nowString()
        }
        id = self.getUrl(url,dict)     
        return id
    
    def updateTest(self,id,success):
        
        url = '/dash/update_testrun'
        dict = {
            'Testrun.id' : str(id),
            'Testrun.success' : success,
            'Testrun.end' : self.nowString()
        }
        id = self.getUrl(url,dict)
    
    def delivery(self,productName):
        
        for i in range(30):
            
            success = 1
            version = '1.0-'+str(i)
            '''Build'''
            logger.debug('Building version '+version)
            
            '''Building'''
            id = self.createBuild(productName,version)
            self.sleepRandom()
            self.updateBuild(id,success)
            
            '''Deploying'''
            id = self.createDeploy(productName,version,"Test")
            self.sleepRandom()
            self.updateDeploy(id,success)
            
            '''Testing'''
            id = self.createTest(productName,version,success)
            self.sleepRandom()
    
            self.sleepRandom()
    
            '''Was the testing success? Lets add a random element'''
            if random.randrange(0, 3, 1) == 1:
                self.updateTest(id,'')
            else:
                self.updateTest(id,1)
                '''Deploying'''
                id = self.createDeploy(productName,version,"Staging")
                self.sleepRandom()
                self.updateDeploy(id,success)
                self.sleepRandom()
                id = self.createDeploy(productName,version,"Production")
                self.sleepRandom()
                self.updateDeploy(id,success)
                
            


    def run(self):
      
      threads = []
      for product in ['UI', 'API', 'DB', 'Reports', 'Security']:
          # self.delivery(product)
          t = threading.Thread(target=self.delivery, args=(product,))
          threads.append(t)
          t.start()
      