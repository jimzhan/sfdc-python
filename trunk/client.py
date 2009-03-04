# -*- coding: utf-8 -*-
#
# Copyright (c) 2008, 2009 Xigital Solutions
#
# Written by Jim Zhan <jim@xigital.com>
#
# This file is part of SFDC-Python Salesforce python accessor.
#
import util
from urlparse import urlparse
from lxml import etree, objectify
from httplib import HTTPSConnection
from config import http, sfdc, namespace
from error import LoginFault, SessionExpired, SFDCError
from request import AuthenticatedRequest, EmailHeader, \
        LeadConvert, Node, ProcessSubmitRequest, \
        ProcessWorkitemRequest, QueryOption, Request, \
        SObject


__author__ = 'Jim Zhan'
__email__ = 'jim@xigital.com'


def makeConnection(serverUrl=sfdc.address):
    protocol, host, path, params, query, fragment = urlparse(serverUrl)
    connection = HTTPSConnection(host)
    connection.debuglevel = http.debuglevel if sfdc.debug else 0
    setattr(connection, 'path', path)
    return connection


class Client(object):
    """ Salesforce's SOAP Client. Initialised with blank
        sessionId & serverUrl (should be returned by login()).
    """
    def __init__(self):
        self.sessionId = None
        self.serverUrl = None
        self.connection = makeConnection()
        

    def __del__(self):
        if hasattr(self.connection, 'close'):
            self.connection.close()    


    def useSession(self, loginResult):
        """ Use loginResult which returned by login() to 
            update the serverUrl and setup the sessionId.
        
            @param loginResult: <response.LoginResult>
        """
        if hasattr(self.connection, 'close'):
            self.connection.close()
        self.connection = makeConnection(loginResult.serverUrl.pyval)
        self.loginResult = loginResult
        self.sessionId = loginResult.sessionId.pyval


    def send(self, request, forList=False):
        """ Actually talk to Salesforce's server, get & parse
            the response content.
            
            @param request: XML request.
            @param forList: Indicates whether this request
                is constructed by list, if so, response will
                be resolved as a list correspondingly.
                
            @type request: <soap.Request> or <soap.AuthenticatedRequest>
            @type forList: boolean
            
            @return: Parsed response body returned by _parse()
                <lxml.objectify.ObjectifiedElement>.
        """
        self.connection.request(
            request.method,
            self.connection.path,
            body = repr(request),
            headers = request.headers
        )
        response = self.connection.getresponse()
        return self._parse(request, response, forList)


    def _parse(self, request, response, forList):
        """ Parse response data. Also take care of 
            compressed data (if debug is False).
            
            @param request: XML request.
            @param response: Raw data returned from Salesforce.
            @param forList: Indicates whether this request
                is constructed by list, if so, response will
                be resolved as a list correspondingly.
                
            @type request: <soap.Request> or <soap.AuthenticatedRequest>
            @type response: string
            @type forList: boolean
            
            @return: Parsed response body <lxml.objectify.ObjectifiedElement>.
        """
        if response.getheader('Content-Encoding') == request.compressType:
            data = request.decompress(response.read())
        else:
            data = response.read()
        xml = objectify.fromstring(data)
        if sfdc.debug: print etree.tostring(xml)
        # see if there's any Fault node first.
        if hasattr(xml.Body, 'Fault'):
            code = xml.find('//faultcode')
            message = code.getnext()
            faultcode = code.text.replace('sf:', '')
            faultstring = message.text.replace('%s:' % faultcode, '')

            if faultcode == 'INVALID_SESSION_ID':
                raise SessionExpired(faultcode, faultstring)
            elif faultcode.find('LOGIN') is not -1:
                raise LoginFault(faultcode, faultstring)
            else:
                raise SFDCError(faultcode, faultstring)

        # regular response body.
        body = '//{%s}%s' % (namespace.partner, request.response)
        kids = xml.find(body).getchildren()
        return kids if forList else kids[0]


    def _append(self, parent, params, tag=None):
        """ Append node(s) to request's body and also
            indicate if the result is array or not.

            @param parent: Parent node.
            @param params: Parameters, to be constructed.
            @param tag: Node's tag name.

            @type parent: lxml Element
            @type params: single lxml Element | lxml Element array
            @type tag: string

            @return: Tuple which contain parent Element
                and a boolean value which indicate that
                if the request is in array or a single
                Element.
        """
        if isinstance(params, (tuple, list)):
            if tag:
                nodes = [Node(tag, item).xml for item in params]
            else:
                nodes = [item.xml for item in params]

            if hasattr(parent, 'body'):
                parent.body.extend(nodes)
            else:
                parent.extend(nodes)
            return (parent, True)

        node = Node(tag, params).xml if tag else params.xml
        if hasattr(parent, 'body'):
            parent.body.append(node)
        else:
            parent.append(node)
        return (parent, False)


    def convertLead(self, leadConverts):
        ''' Converts a Lead into an Account, Contact, or (optionally) an Opportunity.
        
            @param leadConverts: Array of LeadConvert.

            @type leadConverts: <soap.LeadConvert> instances array.
            
            @return: An array of LeadConvertResult objects. Single LeadConvertResult
                will be returned if the parameter is a <request.LeadConvert> instance.

                accountId (String/ID): ID of the new Account (if a new account was specified)
                    or the ID of the Account specified when convertLead() was invoked.
                contactId (String/ID): ID of the new Contact (if a new contact was specified)
                    or the ID of the Contact specified when convertLead() was invoked.
                leadId (String/ID): ID of the converted Lead.
                opportunityId (String/ID): ID of the new Opportunity. If one was created when
                    convertedLead() was invoked.
                success (Boolean): Indicates whether the convertLead() call succeeded for this object.
                errors (Erros array): If an error occurred during the create() call, an array of
                    one or more Error objects providing the error code and description.

            @raise UnexpectedError: An unexpected error occurred. The error is not associated with
                    any other API fault.
        '''
        request = AuthenticatedRequest(self.sessionId, 'convertLead')
        request, forList = self._append(request, leadConverts)
        return self.send(request, forList=forList)
    
    
    def create(self, sObjects):
        """ Adds one or more new individual objects to your organization's data.

            @param sObjects: Array of one or more sObject to create(). Limit: 200.
                
            @return: An array of SaveResult objects, single SaveResult will be
                returned if the parameter is a <request.SObject> instance.

                id (String/ID): ID of the sObject that you attempted to create().
                    If this field is empty, then the object was not created.
                success (Boolean): Indicates whether the create() call succeeded.
                errors (Error array): If an error occurred during create() call, an
                    array of one or more Error objects providing the error code and
                    description.

            @raise InvalidSObject: An invalid sObject in a call.
            @raise UnexpectedError: An unexpected error occurred. The error is not associated
                    with any other API fault.
        """
        request = AuthenticatedRequest(self.sessionId, 'create')
        request, forList = self._append(request, sObjects)
        result = self.send(request, forList=forList)
        return result
    

    def delete(self, ids):
        """ Deletes one or more individual objects from your organization's data.

            @param ids: Array of one or more IDs assiciated with
                    the objects to delete. Limit: 200.
                    
            @type ids: SFDC ID array

            @return: An array of DeleteResult objects. Single DeleteResult will
                be returned if the parameter is a SFDC ID (string).

                id (String/ID): ID of an sObject that you attempted to delete.
                success (Boolean): Indicates whether the delete() call succeeded.
                errors (Error array): If an error occurred during the delete call, an
                    array of one or more Error objects providing the error code and
                    description.

            @raise InvalidSObject: An invalid sObject in a call.
            @raise UnexpectedError: An unexpected error occurred. The error is not associated
                    with any other API fault.            
        """
        request = AuthenticatedRequest(self.sessionId, 'delete')
        request, forList = self._append(request, ids, tag='ids')
        return self.send(request, forList=forList)


    def getDeleted(self, sObjectType, starDate, endDate):
        """Retrieves the list of individual objects that have been deleted within
            the given timespan for the specified object.

            @param sObjectType: Object type.
            @param startDate: Starting date/time (Coordinated Universal Time (UTC)
                - not local - timezone) of the timespan for which retrieve the data.
                The API ignores the seconds portion of the specified DateTime value.
            @param endDate: Ending date/time (Coordinated Universal Time (UTC)
                - not local - timezone) of the timespan for which to retrieve the data.
                The API ignores the seconds portion of the specified DateTime value.
                    
            @type sObjectType: string
            @type startDate: datetime
            @type endDate: datetime

            @return: a GetDeletedResult object that contains an array of DeletedRecord.
                earliestDateAvailable (DateTime): For the object type of the getDeleted() call,
                    the timestamp (UTC) of the last physically deleted object.
                deletedRecords (Array): Array of deleted records which satisfy the start
                    and end dates specified in the call.
                latestDateCovered (DateTime): The timstamp (UTC) of the earliest process
                    within the range of the startDate and endDate specified in the call that
                    did not complete.

            @raise InvalidSObject: An invalid sObject in a call.
            @raise UnexpectedError: An unexpected error occurred. The error is not associated
                    with any other API fault.            
        """
        request = AuthenticatedRequest(self.sessionId, 'getDeleted')
        request.body.extend((
            Node('sObjectType', sObjectType).xml,
            Node('startDate', startDate).xml,
            Node('endDate', endDate).xml
        ))
        return self.send(request, forList=True)

    
    def getUpdated(self, sObjectType, startDate, endDate):
        """ Retrieves the list of individual objects that have been udpated (added or changed)
            within the given timespan for the specified object.

            @param sObjectType: Object type.
            @param startDate: Starting date/time (UTC) of the timespan for which to
                    retrieve the data.
            @param endDate: Ending date/time (UTC) of the timespan for which to retrieve
                    the data.
                    
            @type sObjectType: string
            @type startDate: datetime
            @type endDate: datetime

            @return: a GetUpdatedResult object that contains information about each record
                that was inserted or updated within the given timespan.
                id (ID array): Array of IDs of each object that has been updated.
                latestDateCovered (DateTime): The timstamp (UTC) of the earliest process
                    within the range of startDate and endDate that did not complete.

            @raise InvalidSObject: An invalid sObject in a call.
            @raise UnexpectedError: An unexpected error occurred. The error is not associated
                with any other API fault.            
        """
        request = AuthenticatedRequest(self.sessionId, 'getUpdated')
        request.body.extend((
            Node('sObjectType', sObjectType).xml,
            Node('startDate', startDate).xml,
            Node('endDate', endDate).xml
        ))
        return self.send(request, forList=True)

    
    def invalidateSessions(self, sessionIds):
        """ Ends one or more sessions specified by a sessionId.
        
            @param sessionIds: Session IDs that you wanna invalidate.
            
            @type sessionIds: string array OR string
            
            @return: An array of LogoutResult objects. If the parameter is a
                sessionId (string), a single LogoutResult will be returned.
            
            @raise UnexpectedError:: An unexpected error occurred. The error is not
                associated with any other API fault.
        """
        request = AuthenticatedRequest(self.sessionId, 'invalidateSessions')
        request, forList = self._append(request, sessionIds, tag='sessionIds')
        return self.send(request, forList=forList)

    
    def login(self, username=None, password=None):
        """Logs in to the login server and starts a client session.

            @param username: Login username.
            @param password: Login password associated with the specified username.

            @type username: string
            @type password: string

            @return: A LoginResult object.
                <LoginResult>
                    metadataServerUrl (String): URL of the endpoint that will process subsequent
                        metadata API calls. Your client application needs to set the endpoint.
                    passwordExpired (Boolean): Indicates whether the password used during the login
                        attempt is expired.
                    serverUrl (String): URL of the endpoint that will process subsequent API calls.
                    sessionId (String/ID): Unique ID associated with this session. Your client application
                        needs to set this value in the session header.
                    userId (String/ID): ID of user associated  with the specified username and password.
                    userInfo (GetUserInfoResult): User information fields.

            @raise LoginFault: An error occurred during the call.
            @raise UnexpectedError: An unexpected error occurred. The error is not associated
                with any other API fault.                
        """
        if getattr(self, 'loginResult', None):
            return self.loginResult
        request = Request('login')
        request.body.extend((
            Node('username', username).xml,
            Node('password', password).xml
        ))
        self.useSession(self.send(request))
        return self.loginResult
    
    
    def merge(self, masterRecord, recordToMergeIds):
        """Merge up three records into one.

            @param masterRecord: Required. Must provied the ID of the object that
                other records will be merged into. Optionally, provide the fields to
                be updated and their values.
            @param recordToMergeIds: Required. Minimum of one, maximum of two.
            
            @type masterRecord: sObject
            @type recordToMergeIds: SFDC ID array

            @return: A mergeResult object.
                Id (String/ID): ID of the master record, the record into which the other
                    records were merged.
                mergedRecordIds (ID array): ID of the records that were merged into the
                    master record. If successful, the values will match mergeRequest.recordToMergeIds.
                success (Boolean): Indicates whether the merge was successful.
                updatedRelatedIds (ID array): ID of all related records that were moved
                    (re-parented) as a result of the merge, and that are viewable by the
                    user sending the merge call.
                errors (Error array): If an error occurred during the call, an array of one
                    or more Error objects providing the error code and description.

            @raise InvalidSObject: An invalid sObject in a call.
            @raise UnexpectedError: An unexpected error occurred. The error is not associated
                with any other API fault.
            @raise InvalidIdFault: A specified ID was invalid in the call.
        """
        request = AuthenticatedRequest(self.sessionId, 'merge')
        mergeRequest = Node('request').xml
        mergeRequest.append(masterRecord.xml)
        mergeRequest, forList = self._append(
            mergeRequest,
            recordToMergeIds,
            tag = 'recordToMergeIds'
        )
        return self.send(request, forList)
    
    
    def process(self, processType):
        """Submits an array of approval instances for approval,
            or processes an array of approval instances to be
            approved, rejected, or removed.

            @param proccessType: can be either:
                ProcessSubmitRequest:
                    objectId (String/ID): The object to submit for approval.
                    nextApproverIds (ID array): If the process requires specification
                        of the next approval, the ID of the user to be assigned the next
                        request.
                    comment (String): The comment to add to the history step associated
                        with this request.
                ProcessWorkitemRequest:
                    action (String): For processing an item after being submitted for
                        approval, a string representing the kind of action to take:
                            Approve, Reject, Remove.
                        Only system administrators can specify Remove except the
                        'Allow submitters to recall approval request' is selected.
                    nextApproverIds (ID array): If the process requires specification
                        of the new approval, the ID of the user to be assigned the next
                        request.
                    comment (String): The comment to add to the history step associated
                        with this request.
                    workitemId (String/ID): The ID of the ProcessInstanceWorkitem that
                        is being approved, rejected, or removed.
                        
            @type processType: string

            @return: a ProcessResult object, which has the following properties, depending
                on the type of call (submit for approval or process object already submitted
                to for approval)
                actorIds (ID array): IDs of the users who are currently assigned to this
                    approval step.
                entityId (String/ID): The object being processed.
                errors (Error array): The set of errors returned if the request failed.
                instanceId (String/ID): The ID of ProcessInstance assocaited with the object
                    submitted for processing.
                instanceStatus (String): The status of the current process instance (not
                    an individual object but the entire process instance). Valid values:
                        Approved, Rejected, Removed, Pending
                newWorkItemIds (ID array): Case-insensitive IDs that point to ProcessInstanceWorkitem
                    objects (the set of new workflow items created)
                success (Boolean): true if processing or approval completed successfully.

            @raise ALREADY_IN_PROCESS: You cannot submit a record that is ready in an approval
                process. You must wait for the previous approval process to complete
                before resubmitting a request with this record.
            @raise NO_APPLICABLE_PROCESS: A process() request failed because the record submitted
                does not satisfy the entry criteria of any workflow process for which the
                user has permission.
        """
        request = AuthenticatedRequest(self.sessionId, 'process')
        request.body.append(processType.xml)
        return self.send(request)

    
    def query(self, queryString, batchSize=500):
        """ Executes a query against the specified object and returns data that
            matches the specified criteria.

            @param queryString: Query string that specifies the object to query.
            @param batchSize: Batch size for the number of records should be
                returned. Default is 500.
                
            @type queryString: string
            @type batchSize: integer

            @return: A QueryResult object.
                queryLocator (String): A specialised string, similar to ID. Used in
                    queryMore() for retrieving subsequent sets of objects from the query
                    result, if applicable. Represent a server-side cursor.
                done (Boolean): Indicates whether additional rows need to be retrieved
                    from the query results (false) using queryMore(), or not (true).
                    Your client application can use this value as loop condition while
                    iterating through the query results.
                records (sObject array): Array of sObjects representing individual objects
                    of the specified object and containing data defined in the field list
                    specified in the queryString.
                size (Integer): Your client applition can use this value to determine
                    whether the query retrieved any rows (size > 0) or not (size = 0).
                    Total number of rows retrieved in the query.

            @raise MalformedQuery: A problem in the queryString passed in a query() call.
            @raise InvalidSObject: An invalid sObject in a call.
            @raise InvalidField: An invalid field in the call.
            @raise UnexpectedError: An unexpected error occurred. The error is not associated
                with any other API fault.
        """
        request = AuthenticatedRequest(self.sessionId, 'query')
        request.setSoapHeader('QueryOptions', QueryOption(batchSize).xml)
        request.body.append(Node('queryString', queryString).xml)
        return self.send(request, forList=True)
    
    
    def queryAll(self, queryString):
        """ Retrieves data from specified objects, whether or not they have been deleted.

            @param queryString: Query string that specifies the object to query,
                the fields to return, and any conditions for including a specific
                object in the query.
                
            @type queryString: string

            @return: A QueryResult object, which has the following properties.
                queryLocator (String): A specialised string, similar to ID. Used in queryMore()
                    for retrieving subsequent sets of objects from the query result, if applicable.
                    Represents a server-side cursor.
                done (Boolean): Indicates whether additional rows need to be retrieved from the
                    query results (false) using queryMore(), or not (true). Your client application
                    can use this value as a loop condition while iterating through the query results.
                records (sObject array): Array of sObjects representing individual objects of the
                    specified object and containing data defined in the field list specified in the
                    queryString.
                size (Integer): Your client application can use this value to determine whether
                    the query retrieved any rows (size > 0) or not (size = 0). Total number of
                    rows retrieved in the query.

            @raise MalformedQuery: A problem in the queryString passed in a query() call.
            @raise InvalidSObject: An invalid sObject in a call.
            @raise InvalidField: An invalid field in the call.
            @raise UnexpectedError: An unexpected error occurred. The error is not associated
                with any other API fault.                    
        """
        request = AuthenticatedRequest(self.sessionId, 'queryAll')
        request.body.append(Node('queryString', queryString).xml)
        return self.send(request, forList=True)
    
    
    def queryMore(self, queryLocator):
        """ Retrieves the next batch of objects from a query().

            @param queryLocator: Represents the server-side cursor that tracks the
                current processing location in the query result set.
            
            @type queryLocator: string

            @return: A QueryResult object, which has the following properties.
                queryLocator (String): A specialised string, similar to ID. Used in queryMore()
                    for retrieving subsequent sets of objects from the query result, if applicable.
                    Represents a server-side cursor.
                done (Boolean): Indicates whether additional rows need to be retrieved from the
                    query results (false) using queryMore(), or not (true). Your client application
                    can use this value as a loop condition while iterating through the query results.
                records (sObject array): Array of sObjects representing individual objects of the
                    specified object and containing data defined in the field list specified in the
                    queryString.
                size (Integer): Your client application can use this value to determine whether
                    the query retrieved any rows (size > 0) or not (size = 0). Total number of
                    rows retrieved in the query.

            @raise InvalidQueryLocator: A problem in the queryLocator passed in a queryMore() call.
            @raise UnexceptedError: An unexpected error occurred. The error is not associated
                with any other API fault.
        """
        request = AuthenticatedRequest(self.sessionId, 'queryMore')
        request.body.append(Node('queryLocator', queryLocator).xml)
        return self.send(request, forList=True)

    
    def retrieve(self, fieldList, sObjectType, ids):
        """ Retrieves one or more objects based on the specified objects IDs.

            @param fieldList: List of one or more fields in the specified object,
                separated by commas. You must specify valid field names and must have
                read-level permissions to each specifed field. The fieldList deinfes the
                ordering of fields in the result.
            @param sObjectType: Object from which to retrieve data. The specified value must be
                a valid object for your organization. ***NOTE*** param name change to 'fromSObject'
                due to Python is using 'from' as its keyword.
            @param ids: Array of one or more IDs of the objects to retrieve. You can pass
                maximum of 2000 object IDs to the call.
                    
            @type fieldList: string array
            @type sObjectType: string
            @type ids: SFDC ID array

            @return: sObject array, single sObject will be returned if
                the parameter "ids" is a SFDC ID (string).
                Array of one or more sObjects representing individual objects of the specified
                object. The number of sObjects returned in the array matches the number of object
                IDs passed into the call. If you do not have access to an object or if a passed ID
                is invalid, the array return null for the object.

            @raise InvalidSObject: An invalid sObject in a call.
            @raise InvalidField: An invalid field in the call.
            @raise UnexpectedError: An unexpected error occurred. The error is not associated
                with any other API fault.
        """
        request = AuthenticatedRequest(self.sessionId, 'retrieve')
        request.body.extend((
            Node('fieldList', ','.join(fieldList)).xml,
            Node('sObjectType', sObjectType).xml
        ))
        request, forList = self._append(request, ids, tag='ids')
        return self.send(request, forList=forList)
    
    
    def search(self, search):
        """ Executes a text search in your organization's data.

            @param search: Search string that specifies the text expression to search for,
                the scope of fields to search, the list of objects and fields to retrieve,
                and the maximum number of objects to return.
                
            @type search: string

            @return: A SearchResult object.
                searchRecords: Array of SearchRecord objects.

            @raise InvalidField: An invalid field in the call.
            @raise InvalidSObject: An invalid sObject in the call.
            @raise MalformedSearch: A problem in the search passed in the call.
            @raise UnexpectedError: An unexpected error occurred. The error is not associated
                with any other API fault.
        """
        request = AuthenticatedRequest(self.sessionId, 'search')
        request.body.append(Node('searchString', searchString).xml)
        return self.send(request)


    def undelete(self, ids):
        """ Undeletes objects from the recycle bin.

            @param ids: IDs of the objects to be restored.
            
            @type ids: SFDC ID array

            @return: An UndeleteResult object, single UndeleteResult will 
                be returned if the parameter is a SFDC ID (string).

                Id (String/ID): ID of the record being undeleted.
                success (Boolean): Indicates whether the undelete was successful.
                errors (Error array): If an error during the call, an array of one
                    or more Error objects providing the error code and description.

            @raise UnexpectedError: An unexpected error occurred. The error is not
                assoicated with any other API fault.
        """
        request = AuthenticatedRequest(self.sessionId, 'undelete')
        request, forList = self._append(request, ids, tag='ids')
        return self.send(request, forList=forList)

    
    def update(self, sObjects):
        """ Updates one or more existing objects in your organization's data.

            @param sObjects (sObject array): Array of one or more objects (maximum of 200) to update.
            
            @type sObjects: soap.SObject array

            @return: An array of SaveResult objects. Each element in the SaveResult array
                corresponds to the sObject[] array passed as the sObjects parameter in the
                call. For example, the object returned in the first index in the SaveResult
                array matches the object specified in the first index of the sObject[] array.
                * NOTE * Single SaveResult will be returned if the parameter is a
                <request.SObject> instance.

            @raise InvalidSObject: An invalid sObject in a call.
            @raise UnexpectedError: An unexpected error occurred. The error is not associated
                with any other API fault.                
        """
        request = AuthenticatedRequest(self.sessionId, 'update')
        request, forList = self._append(request, sObjects)
        return self.send(request, forList=forList)


    def upsert(self, externalIDFieldName, sObjects):
        """ Create new objects and updates existing objects; uses a custom field to
            determine the presence of existing objects. In most cases, we recommand
            that you use upsert instead of create() to vaoid creating unwanted duplicate
            records (idempotent).

            @param ExternalIDFieldName: Contains the name of the field on this object
                with the external ID field attribute for custom objects or the idLookup
                field property for standard objects. The idLookup field property is usually
                on a field that is the object's ID field or name field, but there are
                exceptions, so check for the presence of the property in the object you
                wish to upsert().
            @param sObjects: Array of one or more objects (maximum of 200) to
                create or update.
                
            @type ExternalIDFieldName: string
            @type sObjects: soap.SObject array

            @return: An array of UpsertResult objects. Each element in the array corresponds
                to the sObject[] array passed as the sObject parameter in the upsert() call.
                For example, the object returned in the first index in the UpsertResult array
                matches the object specified in the first index of the sObject[] array.
                * NOTE * Single UpsertResult will be returned if parameter "sObjects"
                if a SFDC ID (string).

            @raise InvalidSObject: An invalid sObject in a call.
            @raise UnexpectedError: An unexpected error occurred. The error is not associated
                    with any other API fault.
        """
        request = AuthenticatedRequest(self.sessionId, 'upsert')
        request.body.append(Node('externalIDFieldName').xml)
        request, forList = self._append(request, sObjects)
        return self.send(request, forList=forList)


############################## Describer ##############################
    def describeGlobal(self):
        """ Retrieves a list of available objects for your organizations's data.

            @returns a DescribeGlobalResult object.
                encoding (String): Specifies how an organization's data is encoded, such as
                    UTF-8 or ISO-8859-1.
                maxBatchSize (Integer): Maximum number of records allowed in the call.
                types (String array): List of available objects for your organization.

            @raise UnexpectedError: An unexpected error occurred. The error is not associated
                with any other API fault.            
        """
        request = AuthenticatedRequest(self.sessionId, 'describeGlobal')
        return self.send(request)
    

    def describeLayout(self, sObjectType, recordTypeIds=None):
        """ Retrieves metadata about page layouts for the specified object type.

            @param sObjectType: The specified value must be a valid object for your
                    organization.
            @param recordTypeIds: Optional parameter restricts the layout data returned
                to the specified record types. To retrieve the layout for the master record
                type, specify the value 012000000000000AAA for the recordTypeId regardless
                of the object. This value is returned in the recordTypeInfos for the master
                record type in the DescribeSObjectResult.
                ***Note*** that a SOQL query returns a null value, not 012000000000000AAA.
                    
            @type sObjectType: string
            @type recordTypeIds: SFDC ID array

            @return: a DescribeLayoutResult object containing top-level record type information
                about the passed-in sObjectType, as well as a mapping of record types to layout.
                Your client application ca traverse this object to retrieve detailed metadata
                about the layout.

            @raise InvalidSObject: An invalid sObject in a call.
            @raise UnexpectedError: An unexpected error occurred. The error is not associated
                with any other API fault.
        """
        elements = [Node('sObjectType', sObjectType).xml]
        if recordTypeIds:
            elements.extend(
                [Node('recordTypeId', item).xml for item in recordTypeIds]
            )
        request = AuthenticatedRequest(self.sessionId, 'describeLayout')
        request.body.extend(elements)
        return self.send(request)

    
    def describeSObject(self, sObjectType):
        """ Describes metadata (field list and object properties) for the specified object.

            @param sObjectType: sObject type.
            
            @type sObjectType: string

            @returns A DescribeSObjectResult object.
                Details: http://www.salesforce.com/us/developer/docs/api/Content/sforce_api_calls_describesobjects_describesobjectresult.htm#topic-title

            @raise InvalidSObject: An invalid sObject in a call.
            @raise UnexpectedError: An unexpected error occurred. The error is not associated
                with any other API fault.
        """
        request = AuthenticatedRequest(self.sessionId, 'describeSObject')
        request.body.append(Node('sObjectType', sObjectType).xml)
        return self.send(request)
    
    
    def describeSObjects(self, sObjectTypes):
        """ An array-based version of describeSObject(); describes metadata (field list and
            object properties) for the specified object or array of objects.
            
            @param sObjectTypes: List of Object types.
            
            @type sObjectTypes: string array

            @return: List of DescribeSObjectResult objects. A Single DescribeSObjectResult
                will be returned if the parameter is a SFDC ID (string).
                Details: http://www.salesforce.com/us/developer/docs/api/Content/sforce_api_calls_describesobjects_describesobjectresult.htm#topic-title

            @raise InvalidSObject: An invalid sObject in a call.
            @raise UnexpectedError: An unexpected error occurred. The error is not associated
                with any other API fault.
        """
        request = AuthenticatedRequest(self.sessionId, 'describeSObjects')
        request, forList = self._append(request, sObjectTypes, tag='sObjectType')
        return self.send(request, forList=forList)


    def describeSoftphoneLayout(self):
        """ Retrieves layout information for a Salesforce Call Center SoftPhone.
        
            @return: The response is a DescribeSoftphoneLayoutResult object.
                CallType (String): A set of attributes that associated with each
                    allowed call type. A call type may be Inbound, Outbound, or Interna
                id (SFDC ID): ID of layout. Note that layout objects are not exposed via the API.
                name (string): Name of the call type: Inbound, Outbound, or Internal.
                
                Each describeSoftphoneLayoutResult object contains one or more call types:
                infoFields (may be more than one)(name): The name of an information field
                    in the SoftPhone layout that does not correspond to a Salesforce object.
                    For example, caller ID may be specified in an information field.
                    Information fields hold static information about the call type.
                name (string): Name of the layout.
                Sections (string): A set of object names and the corresponding item name
                    in the SoftPhone layout, one section for each object in a call type.
                    
                Each call type returned in a describeSoftphoneLayoutResult object contains
                one section for each call type. Each section contains object-item pairs:
                entityApiName (string): The name of an object in the Salesforce application
                    that corresponds to an item displayed in the SoftPhone layout, for example,
                    a set of accounts or cases.
                itemApiName (string): The name of a record in the Salesforce application that
                    corresponds to an item displayed in the SoftPhone layout, for example, the Acme account.

        """
        request = AuthenticatedRequest(self.sessionId, 'describeSoftphoneLayout')
        return self.send(request)

    
    def describeTabs(self):
        """ The describeTabs call returns information about the standard and custom
            apps available to the logged-in user. An app is a group of tabs that
            works as a unit to provide application funcationality.
          
            @return: a DescribeTabSetResult object, of which DescribeTab is a property.
                label (String): The display label of this standard or custom app.
                    This value changes when tabs are renamed in the Salesforce user
                    interface.
                logoUrl (String): A fully qualified URL to the logo image associated
                    with the standard or custom app.
                namespace (String): If this is a custom app, and a set of tabs in the
                    custom app was installed as part of a managed package, the value
                    of this attribute is the developer namespace prefix that the creator
                    of the package chose when the Developer Edition organization was
                    enabled to allow publishing a managed package. This attribute identifies
                    elements of a Force.com AppExchange package.
                selected (Boolean): If true, then this standard or custom app is the user's
                    currently selected app.
                tabs (DescribeTab): An array of tabs that displayed for the specified
                    standard app or custom app.
                    DescribeTab:
                        custom (Boolean): true if this is a custom tab.
                        iconUrl (String): The URL for the main 32 x 32 pixel icon for a tab.
                            This icon appears next to the heading at the top of most pages.
                        label (String): The display label for this tab.
                        miniIconUrl (String): The URL for the 16 x 16 pixel icon that represent
                            a tab. This icon appears in related lists and other locations.
                        sobjectName (string): The name of the sObject that is primarily displayed
                            on this tab (for tabs that display a particular SObject).
                        url (String): A fully qualified URL for viewing this tab.
            
        """
        request = AuthenticatedRequest(self.sessionId, 'describeTabs')
        return self.send(request, forList=True)
    
    
############################## Utility ##############################
    def emptyRecyclebin(self, ids):
        """ Delete records from the recycle bin immediately.

            @param ids: Array of one or more IDs associated
                with the records to delete from the recycle bin.
                Maximum number of records is 200.

            @type ids: SFDC Id/SFDC Id array.

            @return: An array of EmptyRecycleBinResult objects.
                Each element in the array corresponds to the ID[]
                array passed as the parameter in the emptyRecycleBin()
                call. For example, the object returned in the first
                index in the DeleteResult array matches the object
                specified in the first index of the ID[] array.
        """
        request = AuthenticatedRequest(self.sessionId, 'emptyRecycleBin')
        request, forList = self._append(request, ids, tag='ids')
        return self.send(request, forList=forList)

    
    def getServerTimestamp(self):
        """ Retrieves the current system timestamp (UTC) from the API.

            @return: a GetServerTimestampResult object.
                timestamp (DateTime): System timestamp of the API when the call was executed.

            @raise UnexpectedError: An unexpected error occurred. The error is not associated
                with any other API fault.
        """
        request = AuthenticatedRequest(self.sessionId, 'getServerTimestamp')
        response = self.send(request)
        return util.getTime(response.timestamp.pyval)


    def getUserInfo(self):
        """ Retrieves personal information for the user associated with the current session.

            @return: a GetUserInfoResult object.
                details: http://www.salesforce.com/us/developer/docs/api/Content/sforce_api_calls_getuserinfo_getuserinforesult.htm#topic-title

            @raise UnexpectedError: An unexpected error occurred. The error is not associated
                with any other API fault.            
        """
        request = AuthenticatedRequest(self.sessionId, 'getUserInfo')
        return self.send(request)

    
    def resetPassword(self, userId):
        """ Changes a user's password to a temporary, system-generated value.

            @param userId: ID of the User or SelfServiceUswer whose password you want to reset.
            
            @type userId: SFDC ID

            @return: New password generated by the API. Once the user logs in with this
                password, they will be asked to provide a new password. This password is
                temporary, meaning that it cannot be resued once the user has set his or
                her new password.

            @raise InvalidId: A specified ID was invalid in the call.            
            @raise UnexpectedError: An unexpected error occurred. The error is not associated
                with any other API fault.
        """
        request = AuthenticatedRequest(self.sessionId, 'resetPassword')
        request.body.append(Node('userId', userId).xml)
        emailHeader = EmailHeader(triggerUserEmail=True).xml
        request.setSoapHeader('EmailHeader', emailHeader)
        response = self.send(request)
        return response.password
    

    def sendEmail(self, base, messages):
        """ Immediately sends an email message.

            @param base (BaseEmail):
                bccSender (Boolean): Indicates whether the email sender receives a
                    copy of the email that is sent. For a mass email, the sender is
                    only copied on the first email sent.
                saveAsActivity (Boolean): Optional. The default value is true.
                    This argument only applies if the recipient list is based on
                    targetObjectId or targetObjectIds. If HTML email tracking is
                    enabled for the organization, you will be able to track open rates.
                useSignature (Boolean): Indicates whether the email includes an
                    email signature if the user has one configured. The default
                    is true, meaning if the user has a signature it is included
                    in the email unless you specify false.
                emailPriority (Picklist/String): Optional, Highest/High/Normal(default)/Low/Lowest.
                replyTo (String): Optional. The email address that receives the message
                    when a recipient replies.
                subject (String): Optional. The email subject line. If you are using
                    an email template and attempt to override the subject one, an error
                    message is returned.
                templateId (ID/String): The ID of the template to be merged to create this email.
                senderDisplayName (String): Optional. The name that appears on the from
                    line of the email.
            @param messages:
                SingleEmailMessage:
                    bccAddresses (String array): Optional. An array of blind
                        carbon copy addresses. The maximum allowed is five.
                        This argument is allowed only when a template is not used.
                        ***NOTE*** All emails must have a recipient value in at least
                        one of the following: toAddresses/ccAddresses/bccAddresses
                        targetObjectId/targetObjectIds.
                    ccAddresses (String array): Optional. An array of carbon
                        copy addresses. The maximum allowed is five. This argument
                        is allowed only when a template is not used.
                    charset (String): Optional. The character set for the email.
                        If this value is null, the user's default value is used.
                    documentAttachments (ID array): Optional. An array listing the
                        ID of each Document you want to attach to the email. You
                        can attach multiple documents as long as the total size
                        of all attachments does not exceed 10MB.
                    fileAttachments (EmailFileAttachment array): Optional. An array
                        listing the file names of the binary and text files you want
                        to attach to the email. You can attach multiple files as long
                        as the total size of all attachments does not exceed 10MB.
                    htmlBody (String): Optional. The HTML version of the email, specified
                        by the sender. The value is encoded accroding to the specification
                        associated with the organization.
                    plainTextBody (String): Optional. The text version of the email,
                        specified by the sender.
                    targetObjectId (ID/String): Optional. The object ID of the contact,
                        lead, or user the email will be sent to. The object ID you enter
                        sets the context and ensures that merge fields in the template
                        contain the correct data. DO NOT enter the object IDs of records
                        that have the 'Email Opt Out' option selected.
                        ***NOTE*** All emails must have a recipient value in at least one
                        of the following: toAddresses/ccAddresses/bccAddresses/targetObjectId/targetObjectIds.
                        toAddresses (String array): Optional. An array of email address
                        you are sending the email to. The maximum allowed is ten. This
                        argument is allowed only when a template is not used.
                        ***NOTE*** All emails must have a recipient value in at least one
                        of the following: toAddresses/ccAddresses/bccAddresses/targetObjectId/targetObjectIds.
                    whatId (ID/String): Optional. If you specify a contact for the targetObjectId
                        field, you can specify a whatId as well. This helps to further ensure
                        that merge fields in the template contain the correct data. The value
                        must be one of the following Types:
                        Account/Asset/Campaign/Case/Contract/Opportunity/Order/Product/Solution/Custom

                MassEmailMessage:
                    targetObjectIds (ID array): An array of object IDs of the contats,
                        leads, or users the email will be sent to. The object IDs you enter
                        set the context and ensure that merge fields in the template contain
                        the correct data. The objects must be of the same type (either all
                        contacts, all leads, or all users). You can list up to 250 IDs per
                        email. If you specify a value for the targetObjectIds field, optionally
                        specify a whatId as well to set the email context to a user, contact,
                        or lead. This ensures that merge fields in the template contain the
                        correct data. DO NOT enter the object IDs of records that have the
                        'Email Opt Out' option selected.
                        ***NOTE*** All emails must have a recipient value in at least one
                        of the following: toAddresses/ccAddresses/bccAddresses/targetObjectId/targetObjectIds.
                    whatIds (ID array): Optional. If you specify an array of contacts for
                        the targetObjectIds field, you can specify an array of whatIds as well.
                        This helps to further ensure that merge fields in the template contain
                        the correct data. The value must be one of the following types:
                            Contract/Case/Opportunity/Product
                        If you specify whatIds, specify one for each targetObjectId; otherwise,
                        you will receive an INVALID_ID_FIELD error.

                EmailFieldAttachment:
                    setFileName (String): The following table contains the arguments that
                        the EmailFileAttachment uses in the SingleEmailMessage object to
                        specify attachments passed in as part of the request, as opposed
                        to existing an Document passed in using the documentAttachtments
                        argument.
                    setBody (Base64): The attachment itself.

            @return: A list of SendEmailResult objects.
                success (Boolean): Indicates whether the email was successfully accepted for
                    delivery by the message transfer agent.
                SendEmailError (Error array): If an error occurred during the call, a SendEmailError
                    object is returned.

            @raise BCC_NOT_ALLOWED_IF_BCC_COMPLIANCE_ENABLED:
            @raise BCC_SELF_NOT_ALLOWED_IF_BCC_COMPLIANCE_ENABLED:
            @raise EMAIL_NOT_PROCESSED_DUE_TO_PRIOR_ERROR:
            @raise ERROR_IN_MAILER:
            @raise INSUFFICIENT_ACCESS_ON_CROSS_REFERENCE_ENTITY:
            @raise INVALID_EMAIL_ADDRESS:
            @raise INVALID_ID_FIELD:
            @raise INVALID_SAVE_AS_ACTIVITY_FLAG:
            @raise LIMIT_EXCEEDED:
            @raise MALFORMED_ID:
            @raise MASS_MAIL_LIMIT_EXCEEDED:
            @raise NO_MASS_MAIL_PERMISSION:
            @raise REQUIRED_FIELD_MISSING:
            @raise TEMPLATE_NOT_ACTIVE:
        """
        raise UnimplementedError
    
    

    def setPassword(self, userId, password):
        """ Sets the specified user's password to the specified value.

            @param userId: ID of the User or SelfServiceUser whose password
                want to reset.
            @param password: New password to use for the specified user.
            
            @type userId: SFDC ID
            @type password: string
            
            @return: True. Otherwise a related exception will be raised.

            @raise InvalidId: A specified ID was invalid in the call.            
            @raise UnexpectedError: An unexpected error occurred. The error is not associated
                with any other API fault.
        """
        request = AuthenticatedRequest(self.sessionId, 'setPassword')
        request.body.extend((
            Node('userId', userId).xml,
            Node('password', password).xml
        ))
        response = self.send(request)
        return response.pyval in (u'', '', None)


if __name__ == '__main__':
    admin = {
        'username': sfdc.username,
        'password': sfdc.password + sfdc.token
    }
    client = Client()
    client.login(**admin)
    print client.describeGlobal().maxBatchSize
