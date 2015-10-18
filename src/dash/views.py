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
from django.http import HttpResponse
from django.shortcuts import render,redirect
import dash.forms
from dash.services import requestToObjects,findObject,updateObject
import logging
from dash.models import Build,Product,Event,Testrun,Deploy,Testpack,Environment,Host
import json
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Max
from django.core import serializers

logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'index.html',{})

def help(request):
    return render(request, 'help.html',{})

@csrf_exempt
def new_build(request):
    ''' Example request: /dash/new_build?Product.name=test%20product&Build.version=1.1.1-234&Build.revision=12
    responds with json of new build
    '''
    
    objects = requestToObjects(dash.models,request)
    
    product = findObject(objects,dash.models.Product)
    product.save()
    
    build = findObject(objects,dash.models.Build)
    build.product = product
    build.save()
    
    return HttpResponse(build.id)

@csrf_exempt
def update_build(request):
    id = request.REQUEST['Build.id']
    build = Build.objects.get(pk=id)
    updateObject(build, request)
    build.save()
    return HttpResponse(build.id)
    
@csrf_exempt
def new_testrun(request):
    
    objects = requestToObjects(dash.models,request)
    
    product = findObject(objects,dash.models.Product)
    product.save()
    
    testpack = findObject(objects,dash.models.Testpack)
    testpack.save()
    
    environment = findObject(objects,dash.models.Environment)
    environment.save()
    
    testrun = findObject(objects,dash.models.Testrun)
    testrun.product = product
    testrun.testpack = testpack
    testrun.environment = environment
    testrun.save()
    
    return HttpResponse(testrun.id)


@csrf_exempt
def update_testrun(request):
    id = request.REQUEST['Testrun.id']
    obj = Testrun.objects.get(pk=id)
    updateObject(obj, request)
    obj.save()
    return HttpResponse(obj.id)

@csrf_exempt
def new_deploy(request):
    objects = requestToObjects(dash.models,request)
    
    product = findObject(objects,dash.models.Product)
    product.save()
    
    environment = findObject(objects,dash.models.Environment)
    environment.save()
    
    host = findObject(objects,dash.models.Host)
    host.save()
    
    deploy = findObject(objects,dash.models.Deploy)
    deploy.product = product
    deploy.environment = environment
    deploy.host = host
    
    deploy.save()
    
    return HttpResponse(deploy.id)

@csrf_exempt
def update_deploy(request):
    id = request.REQUEST['Deploy.id']
    obj = Deploy.objects.get(pk=id)
    updateObject(obj, request)
    obj.save()
    return HttpResponse(obj.id)


def candidate(request):
    products = Product.objects.all()
    events = None
    selectedProduct = None
    selectedVersion = None
    
    try:    
        selectedProduct = request.REQUEST['product']
        selectedVersion = request.REQUEST['version']
        product = Product.objects.get(pk=selectedProduct)
        events = Event.objects.filter(product = product, version = selectedVersion).order_by('start')
        for e in events: 
            if (e.end and e.start):
                e.duration = e.end - e.start
    except KeyError:
        logger.exception('No events')
        logger.debug('No events')
        True
        
    return render(
        request, 'candidate.html',
        {'products' : products, 'events' : events, 'selectedProduct' : selectedProduct, 'selectedVersion' : selectedVersion }
    )
    
def product_versions(request):
    
  product = Product.objects.get(pk = request.REQUEST['product'])
  versions = Event.objects.filter(product = product).order_by('-version').values('version').distinct()
  return HttpResponse(
    json.dumps(list(versions.values_list('version',flat=True) ))
  )

""" Host view """
def host(request):
  
  hosts = Host.objects.all()
  
  try:
    host = Host.objects.get(pk=request.REQUEST['host'])
    
    # Filter of deploys, selecting latest of each product type for the environment
    ids = (
      Deploy.objects.filter(host = host)
      .values('product')
      .annotate(max_id=Max('id'))
      .values_list('max_id',flat=True)
    )
    deploys = Deploy.objects.filter(pk__in=ids)
  except KeyError:
    host = False
    deploys = False
    
  return render(
    request, 'host.html',
    {'deploys' : deploys, 'hosts' : hosts, 'host': host }
  )

""" Environment view """
def environment(request):
  
  environments = Environment.objects.all()
  
  try:
    environment = Environment.objects.get(pk=request.REQUEST['environment'])
    
    # Filter of deploys, selecting latest of each product type for the environment
    ids = (
      Deploy.objects.filter(environment = environment)
      .values('product','host')
      .annotate(max_id=Max('id'))
      .values_list('max_id',flat=True)
    )
    deploys = Deploy.objects.filter(pk__in=ids).order_by('product','host')
  except KeyError:
    environment = False
    deploys = False
    
  return render(
    request, 'environment.html',
    {'deploys' : deploys, 'environments' : environments, 'environment': environment }
  )
  
def pipeline(request):
  
  products = Product.objects.all()
  loop_times = range(101)[1:] # Range for nunPipes selection
  
  ''' How many recent pipelines to show '''
  try:
    numpipes = int(request.REQUEST['numpipes'])
  except KeyError:
    '''Do not show table as no product selected'''
    numpipes = 20
  
  try:    
    product = Product.objects.get(pk=request.REQUEST['product'])
      
  except KeyError:
    '''Do not show table as no product selected'''
    product = False
      
  return render(
    request, 'pipeline.html',
    {'products' : products, 'product' : product, 'loop_times' : loop_times, 'numpipes' : numpipes }
  )

""" 
  Removes old data up_to a certain date
"""
def cleanup(request):
    
    up_to =  request.REQUEST['up_to']
    
    Event.objects.filter(end__lt = up_to).delete()
    Event.objects.filter(start__lt = up_to).filter(end__isnull = True).delete()
    
    # Clean up host, products, environment, testpack records
    # where there is no longer an event
    
    Product.objects.exclude(
        pk__in = Event.objects.values_list('product', flat=True)
    ).delete()
    Host.objects.exclude(
        pk__in = Deploy.objects.values_list('host', flat=True)
    ).delete()
    Environment.objects.exclude(
        pk__in = Testrun.objects.values_list('environment', flat=True)
    ).delete()
    Environment.objects.exclude(
        pk__in = Deploy.objects.values_list('environment', flat=True)
    ).delete()
    Testpack.objects.exclude(
        pk__in = Testrun.objects.values_list('environment', flat=True)
    ).delete()
    
    return HttpResponse("OK", content_type="text/plain")
    
def pipeline_chart(request):
    
  pipes = False
  product = False
  
  ''' How many recent pipelines to show '''
  try:
      numpipes = int(request.REQUEST['numpipes'])
  except KeyError:
      '''Do not show table as no product selected'''
      numpipes = 20
  
  try:    
      product = Product.objects.get(pk=request.REQUEST['product'])
      pipes = getPipes(product,numpipes)
      
  except KeyError:
      '''Do not show table as no product selected'''
      True
      
  return render(
      request, 'pipeline_chart.html',
      {'pipes' : pipes, 'product' : product, }
  )
    
def getPipes(product,numToReturn):
   
  '''Empty class to store data for one product/version'''
  class Pipe:
      pass
  
  recentBuilds = Build.objects.filter(product = product).order_by('-start')[:numToReturn]
  
  pipes = []
  
  
  for build in recentBuilds:
      pipe = Pipe()
      pipe.product = product
      pipe.version = build.version
      logger.debug('Pipe version: '+build.version)
      pipe.events = Event.objects.filter(product = product,version = build.version).order_by('start')
      
      pipes.append(pipe)
      
      
  '''Figure out widths of event bars'''

  maxPipeDuration = None
  
  '''Find longest Pipe time in Epoche'''
  for pipe in pipes:
      mintime = None
      maxtime = None
      
      for event in pipe.events:
          
          '''Images:
          flashing for in progress ( no end time )
          green for succes
          red for failure
          blue for unknown
          '''
          if event.end == None and event.success == None: 
              event.img = 'bluedot_flashing.gif'
          elif event.end == None and event.success == False: 
              event.img = 'reddot_flashing.gif'
          elif event.end == None and event.success == True: 
              event.img = 'greendot_flashing.gif'
          elif event.success == None: 
              event.img = 'bluedot.png'
          elif event.success == True: 
              event.img = 'greendot.png'
          elif event.success == False: 
              event.img = 'reddot.png'
              
                          
          '''If no end time we can assume event is still going on'''
          if event.end == None:
              event.end = datetime.datetime.now()
          
          eventStartEpoche = int(event.start.strftime('%s'))
          eventEndEpoche = int(event.end.strftime('%s'))
          if event.start != None and ( mintime == None or eventStartEpoche < mintime ): 
              mintime = int( eventStartEpoche )
          if event.end != None and ( maxtime == None or eventEndEpoche > maxtime ): 
              maxtime = eventEndEpoche
          
      logger.debug('Pipe mintime: ' + str(mintime))
      logger.debug('Pipe maxtime: ' + str(maxtime))
      pipeDuration = maxtime - mintime
      if mintime != None and maxtime != None and ( maxPipeDuration == None or pipeDuration > maxPipeDuration ): 
          maxPipeDuration = pipeDuration
          
  for p in pipes:
      pipeStartT = int (p.events[0].start.strftime('%s'))
      
      for e in p.events:
          
          '''Epoche formats'''
          eventStartT = int( e.start.strftime('%s') )
          eventEndT = int (e.end.strftime('%s') )
          
          
          e.startPos = float(eventStartT - pipeStartT) / maxPipeDuration  * 500
          e.endPos =  float(eventEndT - pipeStartT) / maxPipeDuration  * 500 - e.startPos
          logger.debug('eventStartT: ' + str(eventStartT) + ' eventEndT: '+ str(eventEndT) + ' maxPipeDuration: ' + str(maxPipeDuration))
          logger.debug('pipeStartT: ' + str(pipeStartT) )
          
  return pipes

