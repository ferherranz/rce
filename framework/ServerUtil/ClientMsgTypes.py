#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       ClientMsgTypes.py
#       
#       This file is part of the RoboEarth Cloud Engine framework.
#       
#       This file was originally created for RoboEearth - http://www.roboearth.org/
#       The research leading to these results has received funding from the European Union 
#       Seventh Framework Programme FP7/2007-2013 under grant agreement no248942 RoboEarth.
#       
#       Copyright 2012 RoboEarth
#       
#       Licensed under the Apache License, Version 2.0 (the "License");
#       you may not use this file except in compliance with the License.
#       You may obtain a copy of the License at
#       
#       http://www.apache.org/licenses/LICENSE-2.0
#       
#       Unless required by applicable law or agreed to in writing, software
#       distributed under the License is distributed on an "AS IS" BASIS,
#       WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#       See the License for the specific language governing permissions and
#       limitations under the License.
#       
#       \author/s: 
#       
#       

""" Message Types of RCE Client Protocol:
        
        IN      Initialize the connection
        
        CC      Create a container
        CS      Update on container status
        DC      Destroy a container
        
        CN      Change a ROS component (Node, Parameter, Interface)
        IR      register/unregister from an Interface
        
        DM      ROS Message
"""

INIT = 'IN' # not used in the current release

CREATE_CONTAINER = 'CC'
CONTAINER_STATUS = 'CS'
DESTROY_CONTAINER = 'DC'

CONFIGURE_COMPONENT = 'CN'
INTERFACE_REGISTRATION = 'IR'

DATA_MESSAGE = 'DM'