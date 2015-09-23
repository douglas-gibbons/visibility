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
from django.conf.urls import patterns, url

from dash import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^help$', views.help, name='help'),
    #url(r'^new_build$', views.new_build, name='new_build'),
    #url(r'^update_build$', views.update_build, name='update_build'),
    url(r'^new_build$', views.new_build, name='new_build'),
    url(r'^update_build$', views.update_build, name='update_build'),
    url(r'^new_testrun$', views.new_testrun, name='new_testrun'),
    url(r'^update_testrun$', views.update_testrun, name='update_testrun'),
    url(r'^new_deploy$', views.new_deploy, name='new_deploy'),
    url(r'^update_deploy$', views.update_deploy, name='update_deploy'),
    
    url(r'^pipeline_chart$', views.pipeline_chart, name='pipeline_chart'),  # Ajax request on pipeline_page
    url(r'^pipeline$', views.pipeline, name='pipeline'),
    url(r'^environment$', views.environment, name='environment'),
    url(r'^host$', views.host, name='host'),

    url(r'^candidate$', views.candidate, name='candidate'),
    url(r'^product_versions$', views.product_versions, name='product_versions'), # Ajax request on pipeline_page

)