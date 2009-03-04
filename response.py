# -*- coding: utf-8 -*-
#
# Copyright (c) 2008, 2009 Xigital Solutions
#
# Written by Jim Zhan <jim@xigital.com>
#
# This file is part of SFDC-Python Salesforce python accessor.
#

"""
<result
    xmlns="urn:partner.soap.sforce.com"
    xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<errors>
        <fields>Id</fields>
        <message>Contact ID: id value of incorrect type: fsdfsd</message>
        <statusCode>MALFORMED_ID</statusCode>
</errors>
<id xsi:nil="true"/>
<success>false</success>
</result>

"""
class Error(object):
    """ Map <lxml.objectify.ObjectifiedElement> instance to
        standard Python class. Also take care of the type conversion.
    """
    def __init__(self, error):
        self.statusCode = error.statusCode.text
        self.message = error.message.text
        self.fields = error.fields.text.split(',')


class LoginResult(object):
    """ Map <lxml.objectify.ObjectifiedElement> instance to 
        Python class. Also take care of the type conversion.
        
        @param loginResult: loginResult returned by request.py's login().
        
        @type loginResult: <lxml.objectify.ObjectifiedElement>
    """
    def __init__(self, loginResult):
        self.metadataServerUrl = loginResult.metadataServerUrl.text
        self.passwordExpired = True if loginResult.passwordExpired.text is 'true' else False
        self.serverUrl = loginResult.serverUrl.text
        self.sessionId = loginResult.sessionId.text
        self.userId = loginResult.userId.text
        self.userInfo = object.__new__(self)
        self.userInfo.accessibility = loginResult.userInfo.accessibility
        
