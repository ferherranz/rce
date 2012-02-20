#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Service.py
#       
#       Copyright 2011 dominique hunziker <dominique.hunziker@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#       
#       

# Decorator imports
from functools import wraps

# Django imports
from piston.handler import AnonymousBaseHandler
from piston.utils import rc
from django.http import HttpResponseBadRequest, HttpResponseServerError

# File processing
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
import cStringIO

# Import used to setup ROS environment
import setupROS
# Do not import packages which need a functioning ROS environment before here

# Communication interface to the ROS adminstration
import roslib
paths = roslib.packages.find_resource('Administration', 'DjangoInterface.py')

if len(paths) != 1:
    print('Could not uniquely identify the ROS interface.')
    exit(-1)

import imp
DjangoInterface = imp.load_source('DjangoInterface', paths[0])

def exceptionHandler(f):
    """ This decorator should be used on the Handler methods to simplify
        the error handling.
    """
    @wraps(f)
    def wrapper(*args, **kw):
        try:
            return f(*args, **kw)
        except DjangoInterface.InternalError as e:
            return HttpResponseServerError(str(e), content_type='text/plain')
        except DjangoInterface.InvalidRequest as e:
            return HttpResponseBadRequest(str(e), content_type='text/plain')
        except DjangoInterface.FatalError as e:
            return HttpResponseServerError(str(e), content_type='text/plain')
    
    return wrapper

class _ConversionError(Exception):
    """ General Exception class which is used for conversion of input files.
    """
    pass

class ServiceHandler(AnonymousBaseHandler):
    """ This class provides the methodes to handle requests to the ROS
        service API without an environment ID and without a task ID.
    """
    allowed_methods = ('GET', 'POST')
    
    @exceptionHandler
    def read(self, request):
        """ Handle 'GET' request.
            This type of request should be used to gather information
            on the ROS Service.
        """
        return DjangoInterface.readService()
    
#   def update(self, request):
#       """ Handle 'PUT'
#       """
    
#   def delete(self, request):
#       """ Handle 'DELETE'
#       """
    
    @exceptionHandler
    def create(self, request):
        """ Handle 'POST' request.
            This type of request should be used to create a new ROS
            environment. If the POST['data'] contains an ID field with
            a valid environment ID only the requested nodes are added
            to the given environment.
        """
        try:
            envID = request.POST['ID']
        except KeyError:
            envID = None
        
        try:
            data = str(request.POST['data'])
        except KeyError:
            data = None
        
        try:
            binary = _convertFILESToStringIO(request.FILES)
        except _ConversionError:	# Raised by _getStringIO if dict request.FILES
            return rc.BAD_REQUEST	#   contains objects which are not of type UploadedFile
        
        return DjangoInterface.createEnvironment(envID=envID, data=data, files=binary)

class EnvironmentHandler(AnonymousBaseHandler):
    """ This class provides the methodes to handle requests to the ROS
        service API with an environment ID and without a task ID.
    """
    allowed_methods = ('GET', 'DELETE', 'POST')
    
    @exceptionHandler
    def read(self, request, envID):
        """ Handle 'GET' request.
            This type of request should be used to gather information
            on the ROS environment matching the environment ID.
        """
        return DjangoInterface.readEnvironment(envID=envID)
    
#   def update(self, request, envID):
#       """ Handle 'PUT'
#       """
    
    @exceptionHandler
    def delete(self, request, envID):
        """ Handle 'DELETE' request.
            This type of request should be used to delete an environment.
            With this request all nodes and running tasks in the specified
            environment are deleted.
        """
        DjangoInterface.deleteEnvironment(envID=envID)
        
        return rc.DELETED
    
    @exceptionHandler
    def create(self, request, envID):
        """ Handle 'POST' request.
            This type of request should be used to create a new task in
            the ROS environment envID. If request.POST contains an 'ID'
            field with a valid task ID only the sent data in
            request.POST['data'] is added to the given task. If the task
            is already running or completed a BAD_REQUEST is returned.
            As soon as the function encounters the field 'data' in
            request.POST the task is launched.
        """
        try:
            taskID = request.POST['ID']
        except KeyError:
            taskID = None
        
        try:
            data = str(request.POST['data'])
        except KeyError:
            data = None
        
        try:
            binary = _convertFILESToStringIO(request.FILES)
        except _ConversionError:	# Raised by _getStringIO if dict request.FILES
            return rc.BAD_REQUEST	#   contains objects which are not of type UploadedFile
        
        return DjangoInterface.createTask(envID=envID, taskID=taskID, data=data, files=binary)

class TaskHandler(AnonymousBaseHandler):
    """ This class provides the methodes to handle requests to the ROS
        service API with an environment ID and with a task ID.
    """
    allowed_methods = ('GET', 'DELETE')
    
    @exceptionHandler
    def read(self, request, envID, taskID):
        """ Handle 'GET' request.
            This type of request should be used to gather information
            on the Task matching the task ID in the ROS environment
            matching the envrironment ID.
        """
        (data, files) = DjangoInterface.readTask(envID=envID, taskID=taskID)
        
        ### ??? ###
        ### 
        ### ToDo:	What should be done with the files ???
        ### 
        
        return data
    
#   def update(self, request, envID, taskID):
#       """ Handle 'PUT'
#       """
    
    @exceptionHandler
    def delete(self, request, envID, taskID):
        """ Handle 'DELETE' request.
        """
        DjangoInterface.deleteTask(envID=envID, taskID=taskID)
        
        return rc.DELETED
    
#   def create(self, request, envID, taskID):
#       """ Handle 'POST'
#       """

def _convertFILESToStringIO(FILES):
    """ Converts the given FILES into a dictionary containing StringIO
        objects representing the files.
        
        Important:  If there are files which have the same key only one
                    will be passed on!
    """
    stringIOs = {}
    
    for key in FILES:
        fileObj = FILES[key]
        
        if isinstance(fileObj, InMemoryUploadedFile):
            strObj = fileObj.file
        elif isinstance(fileObj, TemporaryUploadedFile):
            strObj = cStringIO.StringIO()
            strObj.write(fileObj.read())
        else:
            raise _ConversionError('Given fileObj is not a valid instance of django.core.file.uploadedfile.UploadedFile')
        
        stringIOs[key] = strObj
    
    return stringIOs