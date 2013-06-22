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

from django.core.urlresolvers import resolve
from django import template
from django.template import RequestContext

register = template.Library()

"""Output "active" if this is the current active page"""
@register.simple_tag
def active(request, pathName):

    if resolve(request.path).url_name == pathName:
        return 'active'
    return 'nonactive'