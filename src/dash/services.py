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
import re
import logging
import inspect
import sys
import datetime
from django.db import models


logger = logging.getLogger(__name__)

def updateObject(obj,request):
    '''Updates the given object with data from the request'''
    module = sys.modules[obj.__module__]
    
    '''Get all objects from the request - overkill, but we have this code, so lets use it'''
    logger.debug('Working with module: '+str(module))
    
    objects = requestToObjects(module,request)
    
    '''Get the new build object, populated with our new build data'''
    buildAdditional = findObject(objects,obj.__class__)
    


    for name,value in vars(buildAdditional).iteritems():
        if value == None: continue
        logger.debug('Adding element from request; Name: '+str(name) + ' Value: '+str(value))

        if (name == 'start' or name == 'end') and value.lower() == 'now':
            q = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.debug('Setting DateTimeField to '+str(q))

        setattr(obj,name,value)
    
    return obj
    
    
def requestToObjects(module,request):
    '''
        Creates objects from the given request.
        
        For example ?Mouse.name=tiny&Mouse.size=2&Cat.name=fred&Cat.claws=sharp
        Creates these objects:
            Mouse(name=tiny,size=2)
            Cat(name=fred,claws=sharp)
        
        Sub classes - that's up to you to assemble as we do not know the hierarchy you want
        
        Does not save the objects
        
        Args:
            module:
                module in which the models are such as dash.models
            request: 
                HTTP request
        
        Returns: 
            list of objects
    '''
    objects = list()

    for p,q in request.REQUEST.iteritems():
        
        words = re.split('\.',p)
        logger.debug(words)
        field = words.pop()
        className = '.'.join(words)
        logger.debug('Found in request: Class Name: ' + className + ' Field: '+ field + ' Value: ' + q)
        
        klass = getattr(module,className)
        
        '''Check to see if we  have an object of that type and create if needed'''
        myObj = False
        for object in objects:
            if isinstance(object,klass):
                myObj = object
                break
        if (myObj == False):
            
            '''Need to be careful about creating objects - some are lists of unique items'''
            myObj = klass()
            
            logger.debug('Created object of type '+myObj.__class__.__name__)
            objects.append(myObj)
            
        if (field == 'start' or field == 'end') and q.lower() == 'now':
            q = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.debug('Setting DateTimeField to '+str(q))
            
        '''Set the field value to the object'''
        setattr(myObj,field,q)
    
    return objects

def findObject(objects,klass):
    '''Find an object of the given class in the list of objects or create a new one'''
    
    for object in objects:
        if (isinstance(object,klass)):
            logger.debug('Found an existing object of type '+object.__class__.__name__)
            return object
    
    newObj = klass()
    logger.debug('Created new object of type '+newObj.__class__.__name__)
    return newObj
        