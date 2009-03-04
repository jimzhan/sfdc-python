# -*- coding: utf-8 -*-
#
# Copyright (c) 2008, 2009 Xigital Solutions
#
# Written by Jim Zhan <jim@xigital.com>
#
# This file is part of SFDC-Python Salesforce python accessor.
#
from copy import deepcopy
from gzip import GzipFile
from lxml import etree
from datetime import date, datetime
from decimal import Decimal
from StringIO import StringIO
from util import Singleton
from config import sfdc, http, header, namespace

__author__ = 'Jim Zhan'
__email__ = 'jim@xigital.com'

__xml__ = ('''
<soap:Envelope
    xmlns="%s"
    xmlns:sobject="%s"
    xmlns:soap="%s"
    xmlns:xsd="%s"
    xmlns:xsi="%s">
<soap:Header /><soap:Body /></soap:Envelope>''' % (
    namespace.partner,
    namespace.sobject,
    namespace.soap,
    namespace.xsd,
    namespace.xsi
)).strip()


############################## COMMON ##############################
class Node(object):
    """ XML node class, all elements/headers must inherit from me.
        *NOTE* Python's data types will be automatically converted
        Salesforce's data types in string correspondingly.
        
        @param tag: Node's tag name.
        @param text: Text value of the returned Element.
        
        @type tag: string
        @type text: string
        
        @return XML node. <lxml.etree.Element> instance can be
            accessed via its 'xml' attribute.
    """
    def __init__(self, tag, text=None, nsmap=None, attrib=None):
        self.debug = sfdc.debug
        if isinstance(nsmap, dict):
            tag = '{%s}%s' % (nsmap.values()[0], tag)
            self.xml = etree.Element(tag, nsmap=nsmap, attrib=attrib)
        else:
            self.xml = etree.Element(tag, attrib=attrib)

        if isinstance(text, bool):
            self.xml.text = 'true' if text else 'false'
        elif isinstance(text, (int, long, float, Decimal)):
            self.xml.text = str(text)
        elif isinstance(text, date):
            self.xml.text = text.strftime(sfdc.datefmt)
        elif isinstance(text, datetime):
            self.xml.text = text.strftime(sfdc.datetimefmt)
        elif text is not None:
            self.xml.text = str(text)


    def __str__(self):
        """ Returns XML node in string.
        
            @return XML node in string format. This is mainly for
                debug purpose. To use the content in XML request,
                use L{__repr__()} instead.
        """
        return etree.tostring(self.xml, pretty_print=self.debug)


    def __repr__(self):
        """ Returns XML node in string without any redundant character.
        
            @return XML node in string format. This is mainly for
                XML request. To debug the generated XML node
                use L{__str__()} instead.
        """
        return etree.tostring(self.xml)

############################## Headers ##############################
class SessionHeader(Node):
    """ Specifies the session ID returned from the login server
        after a successful login(). This session ID is used in
        all subsequent calls. This is a Singleton class.
    
        @param sessionId: Session ID returned by the login()
            call to be used for subsequent call authentication.
        
        @type sessionId: string
        
        @return SessionHeader node. <lxml.etree.Element> instance can be accessed
            via its "xml" attribute.        
    """
    def __init__(self, sessionId):
        Node.__init__(self, 'SessionHeader')
        self.xml.append(Node('sessionId', sessionId).xml)
        self.sessionId = sessionId


class AssignmentRuleHeader(Node):
    """ The AssignmentRuleHeader must be specified in the
        create() or update() call of a Case or Lead for the
        specified assignment rule to be applied, and it must
        be specified in the update() call of an Account for
        the territory assignment rules to be applied.

        @param assignmentRuleId: ID of a specific assignment rule to
            run for the Case or Lead.
        @param useDefaultRule: If true for a Case or Lead, uses
            the default (active) assignment rule for a Case or Lead.
            If specified, do not specify an assignmentRuleId.
            If true for an Account, all territory assignment rules
            are applied, and if false, no territory assignment rules are applied.

        @type assignmentRuleId: SFDC ID
        @type useDefaultRule: Boolean
        
        @return AssignmentRuleHeader node. <lxml.etree.Element> instance
            can be accessed via its "xml" attribute.
    """
    def __init__(self, assignmentRuleId=None, useDefaultRule=None):
        Node.__init__(self, 'AssignmentRuleHeader')
        self.xml.extend((
            Node('assignmentRuleId', assignmentRuleId).xml,
            Node('useDefaultRule', useDefaultRule).xml
        ))


class CallOption(Node):
    """ Specifies the options needed to work with a specific client.
        This header is only available for use with the Partner WSDL.

        @param client: A string that identifies a client.
        @param defaultNamespace: A string that identifies a developer
            namespace prefix. Use this field to resolve field names
            in managed packages without having to fully specify the
            C{fieldName} everywhere.

        @type client: string
        @type defaultNamespace: string
        
        @return CallOptions node. <lxml.etree.Element> instance
            can be accessed via its "xml" attribute.
    """
    def __init__(self, client=None, defaultNamespace=None):
        Node.__init__(self, 'CallOptions')
        self.xml.extend((
            Node('client', client).xml,
            Node('defaultNamespace', defaultNamespace).xml
        ))


class EmailHeader(Node):
    """ The Salesforce user interface allows you to specify whether
        or not to send an email when these events occur:
        - Create a new C{Case} or C{Task}
        - Create a C{CaseComment}
        - Convert C{Case} email to a C{Contact}
        - New C{User} email notification
        - A L{resetPassword()} call
        Involved methods:
         - L{create()}
         - L{delete()}
         - L{resetPassword()},
         - L{update()}
         - L{upsert()}
        
        @param triggerAutoResponseEmail: Indicates whether to trigger
            auto-response rules(C{true}) or not (C{false}), for leads
            cases. In the Salesforce user interface, this email can be
            automatically triggered by a number of events, for example
            creating a case or resetting a user password. If this value
            is set to C{true}, when a C{Case} is created, if there is
            an email address for the contact specified in C{ContactId},
            the email is sent to that address. If not, the email is sent
            to the address specified in C{SuppliedEmail}.
        @param triggerOtherEmail: Indicates whether to trigger email
            outside the organisation (C{true}) or not (C{false}).
            In Salesforce user interface, this email can be automatically
            triggered by creating, editing, or deleting a contact for a case.
        @param triggerUserEmail: Indicates whether to trigger email that
            is sent to users in the organisation (C{true}) or not (C{false}).
            In the Salesforce user interface, this email can be automatically
            triggered by a number of events; resetting a password, creating
            a new user, adding comments to a case, or creating or modifying
            a task.

        @type triggerAutoResponseEmail: boolean
        @type triggerOtherEmail: boolean
        @type triggerUserEmail: boolean
        
        @return EmailHeader node. <lxml.etree.Element> instance
            can be accessed via its "xml" attribute.
    """
    def __init__(self, triggerAutoResponseEmail=None,
                 triggerOtherEmail=None,
                 triggerUserEmail=None):
        Node.__init__(self, 'EmailHeader')
        self.xml.extend((
            Node('triggerAutoResponseEmail', triggerAutoResponseEmail).xml,
            Node('triggerOtherEmail', triggerOtherEmail).xml,
            Node('triggerUserEmail', triggerUserEmail).xml
        ))


class LocaleOption(Node):
    """ Specifies the language of the labels returned.
        Involved methods: L{describeSObject()}, L{describeSObjects()}

        @param language: Specifies the language of the labels returned.
            The value must be a valide user locale (language and country),
            such as de_DE or en_GB. For more information on locales, see
            U{the LanguageLocaleKey field on the CategoryNodeLocalization object.
            <http://www.salesforce.com/us/developer/docs/api/Content/sforce_api_objects_categorynodelocalization.htm#locale_description>}
            
        @type language: string
        
        @return LocaleOptions node. <lxml.etree.Element> instance
            can be accessed via its "xml" attribute.
    """
    def __init__(self, language=None):
        Node.__init__(self, 'LocaleOptions')
        self.xml.append(Node('language', language).xml)


class LoginScopeHeader(Node):
    """ Specifies your organization ID so that you can authenticate
        Self-Service users for your organization using the existing
        L{C{login()}}.

        @param organizationId: The ID of the organisation against
            which you will authenticate Self-Service users.
        @param portalId: Specify only if user is a Customer Porta user.
            The ID of the portal for this organisation. ID is availabe
            in the Salesforce user interface.
            - Select B{Setup} | B{Customize} | B{Customer Portal} | B{Settings}
            - Select a Customer Portal name, and on the Customer Portal
              detail page, the URL of the Customer Portal displays.
              The Portal ID is in the URL.

        @type organizationId: SFDC ID
        @type portalID: SFDC ID
        
        @return LoginScopeHeader node. <lxml.etree.Element> instance
            can be accessed via its "xml" attribute.
    """
    def __init__(self, organizationId=None, portalId=None):
        Node.__init__(self, 'LoginScopeHeader')
        self.xml.extend((
            Node('organizationId', organizationId).xml,
            Node('portalId', portalId).xml,
        ))
        

class MruHeader(Node):
    """ In API version 7.0 and later, the L{C{create()}}, L{C{update()}},
        and L{C{upsert()}} calls do not update the list of most recently
        used (MRU) items in the Recent Items section of the sidebar in the
        Salesforce user interface unless this header is used. Be advised
        that using this header to update the Recent Items list
        may negatively impact performance.
        Involved methods:
            - L{C{create()}}
            - L{C{merge()}}
            - L{C{query()}}
            - L{C{retrieve()}}
            - L{C{update()}}
            - L{C{upsert()}}

        @param updateMru: Indicates whether to update the list of most
            recently used items (C{true}) or not (C{false}).

        @type updateMru: boolean
        
        @return MruHeader node. <lxml.etree.Element> instance
            can be accessed via its "xml" attribute.
    """
    def __init__(self, updateMru=False):
        Node.__init__(self, 'MruHeader', updateMru)
            

class QueryOption(Node):
    """ Specifies the batch size for queries. Batches that are larger or
        smaller than the specified size may be used, in order to maximize
        performance.
        Involved methods:
            - L{C{query()}}
            - L{C{queryMore()}}
            - L{C{retrieve()}}

        @param batchSize: Batch size for the numbver of records returned
            in a L{C{query()}} or L{C{queryMore()}} call. Child objects
            count toward to the number of records for the batch size.
            The default is 500; the minimum is 200, and the maximum is 2,000.

        @type batchSize: integer
        
        @return QueryOptions node. <lxml.etree.Element> instance
            can be accessed via its "xml" attribute.
    """
    def __init__(self, batchSize=500):
        Node.__init__(self, 'QueryOptions')
        self.xml.append(Node('batchSize', batchSize).xml)


class UserTerritoryDeleteHeader(Node):
    """ Specify a user to whom open opportunities are assigned when the
        current owner is removed from a territory. If this header is not
        used or the value of its element is null, the opportunities are
        transferred to the forecast manager in the territory above, if
        one exists. If one does not exist, the user being removed from
        the territory keeps the opportunities. Involved method: L{C{delete()}}.

        @param transferToUserId: The ID of the user to whom open opportunities
            in that user's territory will be assigned when an opportunity's
            owner (user) is removed from a territory.

        @type transferToUserId: SFDC ID
        
        @return UserTerritoryDeleteHeader node. <lxml.etree.Element> instance
            can be accessed via its "xml" attribute.
    """
    def __init__(self, transferToUserId):
        Node.__init__(self, 'UserTerritoryDeleteHeader')
        self.xml.append(Node('transferToUserId', transferToUserId).xml)


############################## Specified Request ##############################
class ProcessSubmitRequest(Node):
    """ Construct a ProcessSubmitRequest lxml element instance
        for client.py#Client#process().
    
        @param objectId: The object to submit for approval,
            for example, an Account, Contact, or custom object.
        @param nextApproverIds:	If the process requires
            specification of the next approval, the ID of
            the user to be assigned the next request.
        @param comment:	The comment to add to the history step
            associated with this request.

        @type objectId: SFDC Id.
        @type nextApproverIds: SFDC Id/SFDC Id array.
        @type comment: string

        @return: ProcessSubmitRequest lxml element instance.
    """
    def __init__(self, objectId, nextApproverIds=None, comment=None):
        processType = {
            '{%s}type' % namespace.xsi: 'ProcessSubmitRequest'
        }
        Node.__init__(self, 'actions', attrib=processType)
        self.xml.append(Node('objectid', objectId).xml)
        if comment:
            self.xml.append(Node('comments', comments).xml)

        if nextApproverIds:
            if isinstance(nextApproverIds, (tuple, list)):
                self.xml.extend(
                    [Node('nextApproverIds', item).xml for item in nextApproverIds]
                )
            else:
                self.xml.append(Node('nextApproverIds', nextApproverIds).xml)


class ProcessWorkitemRequest(Node):
    """ Construct a ProcessWorkitemRequest lxml element instance
        for client.py#Client#process().
        
        @param action: For processing an item after being
            submitted for approval, a string representing
            the kind of action to take: Approve, Reject,
            or Remove. Only system administrators can specify
            Remove. If the Allow submitters to recall approval
            requests option is selected for the approval process,
            the submitter can also specify Remove.
        @param nextApproverIds:	If the process requires
            specification of the next approval, the ID
            of the user to be assigned the next request.
        @param comment:	The comment to add to the history
            step associated with this request.
        @param workitemId: The ID of the ProcessInstanceWorkitem
            that is being approved, rejected, or removed.

        @type action: string.
        @type nextApproverIds: SFDC Id/SFDC Id array.
        @type comment: string.
        @type workitemId: SFDC Id.

        @return: ProcessResult object.
    """
    def __init__(self, action, workitemId, nextApproverIds=None, comment=None):
        processType = {
            '{%s}type' % namespace.xsi: 'ProcessWorkitemRequest'
        }
        Node.__init__(self, 'actions', attrib=processType)
        self.xml.extend((
            Node('action', action).xml,
            Node('workitemId', workitemId).xml
        ))
        if comment:
            self.xml.append(Node('comments', comments).xml)
        if nextApproverIds:
            if isinstance(nextApproverIds, (tuple, list)):
                self.xml.extend(
                    [Node('nextApproverIds', item).xml for item in nextApproverIds]
                )
            else:
                self.xml.append(Node('nextApproverIds', nextApproverIds).xml)            
        
############################## Complex Types ##############################
class SObject(Node):
    nsmap = {'sobject': namespace.sobject}
    """ Create a sObject node, this is also a <util.Record> like class
        which represent key-value pairs via SObject's attribute/value.
    
        @param recordType: Record type, this element must be places
            at the top of each sObject record.
        @param root: Root name of this sObject, belongs to partner's
            namespace in general, default is "sObjects".
        @param params: Key-value pairs dictionary, represents the
            fieldname-value pairs of this sObject.
        
        @type recordType: string
        @type root: string
        @type params: dictionary
        
        @return: Inherited from Node, lxml.etree.Element instance
            can be retrieve from its "xml" attribute.
    """
    def __init__(self, recordType, root='sObjects', **params):
        Node.__init__(self, root)
        recordType = recordType.capitalize()
        kids = [Node('type', recordType, nsmap=SObject.nsmap).xml]
        for key, value in params.items():
            if key is not 'type':
                kids.append(Node(key, value, nsmap=SObject.nsmap).xml)
        self.xml.extend(kids)


class LeadConvert(Node):
    """ LeacConvert complex object. For Salesforce's CORE call convertLead().
        This is also a <util.Record> like class which represent key-value pairs
        via SObject's attribute/value.
    
        @param leadId: ID of the Lead to convert. Required.
        @param convertedStatus: Valid LeadStatus value for a converted lead. Required.
        @param doNotCreateOpportunity: Specifies whether to create an Opportunity
            during lead conversion (false, the default) or not (true). Set this
            flag to true only if you do not want to create an opportunity from the lead.
            An opportunity is created by default.
        @param opportunityName: Name of the opportunity to create. If no name is
            specified, then this value defaults to the company name of the lead.
            The maximum length of this field is 80 characters. If doNotCreateOpportunity
            argument is true, then no Opportunity is created and this field must be left
            blank; otherwise, an error is returned.
        @param overwriteLeadSource: Specifies whether to overwrite the LeadSource
            field on the target Contact object with the contents of the LeadSource
            field in the source Lead object (true), or not (false, the default).
            To set this field to true, the client application must specify a
            contactId for the target contact.
        @param ownerId: Specifies the ID of the person to own any newly created account,
            contact, and opportunity. If the client application does not specify this
            value, then the owner of the new object will be the owner of the lead.
            Not applicable when merging with existing objects￑if an ownerId is specified,
            the API does not overwrite the ownerId field in an existing account or contact.
        @param sendNotificationEmail: Specifies whether to send a notification email to the
            owner specified in the ownerId (true) or not (false, the default).
        @param accountId: ID of the Account into which the lead will be merged. Required
            only when updating an existing account, including person accounts. If no
            accountID is specified, then the API creates a new account. To create a new
            account, the client application must be logged in with sufficient access rights.
            To merge a lead into an existing account, the client application must be logged
            in with read/write access to the specified account. The account name and other
            existing data are not overwritten.
        @param contactId: ID of the Contact into which the lead will be merged
            (this contact must be associated with the specified accountId, and
            an accountId must be specified). Required only when updating an existing contact.
            If no contactID is specified, then the API creates a new contact that is implicitly
            associated with the Account. To create a new contact, the client application must
            be logged in with sufficient access rights. To merge a lead into an existing contact,
            the client application must be logged in with read/write access to the specified
            contact. The contact name and other existing data are not overwritten
            (unless overwriteLeadSource is set to true, in which case only the LeadSource
            field is overwritten).
            ***NOTE*** If you are converting a lead into a person account, do not specify the
            contactId or an error will result. Specify only the accountId of the person account.
            
        @type leadId: SFDC ID
        @type convertedStatus: string
        @type doNotCreateOpportunity: boolean
        @type opportunityName: string
        @type overwriteLeadSource: boolean
        @type ownerId: SFDC ID
        @type sendNotificationEmail: boolean
        @type accountId: SFDC ID
        @type contactId: SFDC ID
        
        @return: Inherited from Node, lxml.etree.Element instance
            can be retrieve from its "xml" attribute.        
    
    """
    def __init__(self, leadId, convertedStatus,
                 doNotCreateOpportunity=False, opportunityName=None,
                 overwriteLeadSource=False, ownerId=None,
                 sendNotificationEmail=False, accountId=None, contactId=None):
        
        Node.__init__(self, 'leadConverts')
        self.xml.extend((
            Node('leadId', leadId).xml,
            Node('convertedStatus', convertedStatus).xml,
            Node('doNotCreateOpportunity', doNotCreateOpportunity).xml,
            Node('opportunityName', opportunityName).xml,
            Node('overwriteLeadSource', overwriteLeadSource).xml,
            Node('ownerId', ownerId).xml,
            Node('sendNotificationEmail', sendNotificationEmail).xml,
            Node('accountId', accountId).xml,
            Node('contactId', contactId).xml
        ))


class BaseEmail(Node):
    """ Base email object which will be used in both single and mass email.

        @param bccSender: Indicates whether the email sender receives a
            copy of the email that is sent. For a mass mail, the sender
            is only copied on the first email sent.
        @param saveAsActivity: Optional. The default value is true,
            meaning the email is saved as an activity. This argument
            only applies if the recipient list is based on targetObjectId
            or targetObjectIds. If HTML email tracking is enabled for the
            organization, you will be able to track open rates.
        @param useSignature: Indicates whether the email includes an
            email signature if the user has one configured. The default
            is true, meaning if the user has a signature it is included
            in the email unless you specify false.
        @param emailPriority: Optional. The priority of the email:
                - Highest
                - High
                - Normal
                - Low
                - Lowest
            The default is Normal.
        @param replyTo: Optional. The email address that receives the
            message when a recipient replies.
        @param subject: Optional. The email subject line. If you are
            using an email template and attempt to override the subject
            line, an error message is returned.
        @param templateId: The ID of the template to be merged to create
            this email.
        @param sendDisplayName: Optional. The name that appears on the
            From line of the email.

        @type bccSender: boolean
        @type saveAsActivity: boolean
        @type useSignature: boolean
        @type emailPriority: picklist (string)
        @type replyTo: string
        @type subject: string
        @type templateId: SFDC ID (string)
        @type senderDisplayName: string
    """
    def __init__(self, tag='Email', bccSender=False,
                 saveAsActivity=True, useSignature=True,
                 emailPriority='Normal', replyTo=None,
                 subject=None, templateId=None,
                 senderDisplayName=None):
        Node.__init__(self, tag)
        self.xml.extend((
            Node('bccSender', bccSender).xml,
            Node('saveAsActivity', saveAsActivity).xml,
            Node('useSignature', useSignature).xml,
            Node('emailPriority', emailPriority).xml,
            Node('replyTo', replyTo).xml,
            Node('subject', subject).xml,
            Node('templateId', templateId).xml,
            Node('senderDisplayName', senderDisplayName).xml
        ))



class SingleEmailMessage(BaseEmail):
    """ Single email message based on BaseEmail.

        @param bccAddresses: Optional. An array of blind carbon copy
            (BCC) addresses. The maximum allowed is five. This argument
            is allowed only when a template is not used. All emails
            must have a recipient value in at least one of the following:
                - toAddresses
                - ccAddresses
                - bccAddresses
                - targetObjectId
                - targetObjectIds
            * NOTE * If the BCC COMPLIANCE option is set at the
            organization level, the user cannot add BCC addresses on
            standard messages. The following error code is returned:
            BCC_NOT_ALLOWED_IF_BCC_COMPLIANCE_ENABLED.
        @param ccAddresses: Optional. An array of carbon copy (CC)
            addresses. The maximum allowed is five. This argument is
            allowed only when a template is not used.
        @param charset: Optional. The character set for the email. If
            this value is null, the user's default value is used.
        @param documentAttachments: Optional. An array listing the ID
            of each Document you want to attach to the email. You can
            attach multiple documents as long as the total size of all
            attachments does not exceed 10 MB.
        @param fileAttachments: Optional. An array listing the file
            names of the binary and text files you want to attach to
            the email. You can attach multiple files as long as the
            total size of all attachments does not exceed 10 MB.
        @param htmlBody: Optional. The HTML version of the email,
            specified by the sender. The value is encoded according
            to the specification associated with the organization.
        @param plainTextBody: Optional. The text version of the email,
            specified by the sender.
        @param targetObjectId: Optional. The object ID of the contact,
            lead, or user the email will be sent to. The object ID you
            enter sets the context and ensures that merge fields in the
            template contain the correct data.
            * NOTE * Do not enter the object IDs of records that have
            the Email Opt Out option selected.
            All emails must have a recipient value in at least one of
            the following:
                - toAddresses
                - ccAddresses
                - bccAddresses
                - targetObjectId
                - targetObjectIds
        @param toAddresses: Optional. An array of email address you
            are sending the email to. The maximum allowed is ten. This
            argument is allowed only when a template is not used.
        @param whatId: Optional. If you specify a contact for the
            targetObjectId field, you can specify a whatId as well.
            This helps to further ensure that merge fields in the
            template contain the correct data. The value must be one
            of the following types:
                - Account
                - Asset
                - Campaign
                - Case
                - Contract
                - Opportunity
                - Order
                - Product
                - Solution
                - Custom

        @type bccAddresses: string array
        @type ccAddresses: string array
        @type charset: string
        @type documentAttachments: SFDC ID array (string array)
        @type fileAttachments: <EmailFileAttachment> array
        @type htmlBody: string
        @type plainTextBody: string
        @type targetObjectId: SFDC ID (string)
        @type toAddresses: string array
        @type whatId: SFDC ID (string)
    """
    def __init__(self, bccAddresses=None, ccAddresses=None,
                 charset=None, documentAttachments=None,
                 fileAttachments=None, htmlBody=' ',
                 plainTextBody=' ', targetObjectId=None,
                 toAddresses=None, whatId=None):
        BaseEmail.__init__(self, tag='SingleEmailMessage')

        if isinstance(fileAttachments, (tuple, list)):
            items = [item.xml for item in fileAttachments]
            files = Node('fileAttachments')
            files.xml.extend(items)
        else:
            files = Node('fileAttachments', fileAttachments) \
                if fileAttachments else Node('fileAttachments')
 
        if isinstance(documentAttachments, (tuple, list)):
            items = [item.xml for item in documentAttachments]
            docs = Node('documentAttachments')
            docs.xml.extend(items)
        else:
            docs = Node('documentAttachments', documentAttachments) \
                if documentAttachments else Node('documentAttachments')

        self.xml.extend([
            Node('bccAddresses', bccAddresses).xml,
            Node('ccAddresses', ccAddresses).xml,
            Node('charset', charset).xml,
            docs.xml,
            files.xml,
            Node('htmlBody', htmlBody).xml,
            Node('plainTextBody', plainTextBody).xml,
            Node('targetObjectId', targetObjectId).xml,
            Node('toAddresses', toAddresses).xml,
            Node('whatId', whatId).xml
        ])


class MassEmailMessage(BaseEmail):
    """ Mass email message based on BaseEmail.

        @param description: A value used internally to identify the object
            in the mass email queue.
        @param targetObjectIds: An array of object IDs of the contacts,
            leads, or users the email will be sent to. The object IDs you
            enter set the context and ensure that merge fields in the
            template contain the correct data. The objects must be of the
            same type (either all contacts, all leads, or all users).
            You can list up to 250 IDs per email. If you specify a value
            for the targetObjectIds field, optionally specify a whatId as
            well to set the email context to a user, contact, or lead.
            This ensures that merge fields in the template contain the
            correct data.
            * NOTE * Do not enter the object IDs or records that have
            the Email Opt Out option selectd.
            All emails must have a recipient value in at least one of
            the following:
                - toAddresses
                - ccAddresses
                - bccAddresses
                - targetObjectId
                - targetObjectIds
        @param whatIds: Optional. If you specify an array of contacts
            for the targetObjectIds field, you can specify an array of
            whatIds as well. This helps to further ensure that merge
            fields in the template contain the correct data. The values
            must be one of the following types:
                - Contract
                - Case
                - Opportunity
                - Product
            If you specify whatIds, specify one for each targetObjectId;
            otherwise, you will receive an INVALID_ID_FIELD error.

        @type description: string
        @type targetObjectIds: SFDC ID array (string array)
        @type whatIds: SFDC ID array (string array)
    """
    def __init__(self, targetObjectIds, whatIds=None, description=None):
        BaseEmail.__init__(self, 'MassEmailMessage')
        self.xml.extend([
            Node('targetObjectIds', targetObjectIds).xml,
            Node('whatIds', whatIds).xml,
            Node('description', description).xml
        ])


class EmailFileAttachment(Node):
    """ Specify attachments passed in as part of the request.

        @param fileName: The name of the file to attach.
        @para body: The attachment itself.

        @type fileName: string
        @type body: base64
    """
    def __init__(self, fileName, body):
        Node.__init__(self, 'EmailFileAttachment')
        self.xml.extend((
            Node('fileName', fileName).xml,
            Node('body', body).xml
        ))

############################## Email ##############################
class Email(Node):
    """ Base email message, for inheritance only.

        @param bccSender: Indicates whether the email sender
            receives a copy of the email that is sent.
        @param saveAsActivity: The default value is True.
            meaning the email is saved as an activity.
            This argument only applies if the recipient
            list is based on targetObjectId or targetObjectIds.
            If HTML email tracking is enabled for the organization,
            you will be able to track open rates.
        @param useSignature: Indicates whether the email includes
            an email signature if the user has one configured.
            The default is True, meaning if the use has a
            signature it is included in the email unless you
            specify False.
        @param emailPriority: Highest/High/Normal/Low/Lowest,
            the default value is Normal.
        @param replyTo: The email address that receives the message
            when a recipient replies.
        @param subject: The email subject line. If you are using an
            email template and attempt to override the subject line,
            an error message is returned.
        @param templateId: The ID of the template to be merged to
            create this email.
        @param senderDisplayName: The name that appears on the
            From line of the email.

        @type bccSender: string
        @type saveAsActivity: boolean
        @type useSignature: boolean
        @type emailPriority: string
        @type replyTo: string
        @type subject: string
        @type templateId: SFDC ID
        @type senderDisplayName: string

        @return: Constructed email message instance.
    """
    def __init__(self, tag='email', bccSender=None,
                 saveAsActivity=True, useSignature=True,
                 emailPriority='Normal', replyTo=None,
                 subject=None, templateId=None,
                 senderDisplayName=None):

        Node.__init__(self, tag)
        priority = emailPriority if emailPriority \
                   in ('Highest', 'High', 'Normal', 'Low', 'Lowest') \
                   else 'Normal'
        self.xml.extend((
            Node('bccSender', bccSender).xml,
            Node('saveAsActivity', saveAsActivity).xml,
            Node('useSignature', useSignature).xml,
            Node('emailPriority', Priority).xml,
            Node('replyTo', replyTo).xml,
            Node('templateId', templateId).xml,
            Node('senderDisplayName', senderDisplayName).xml
        ))


class SingleEmailMessage(Email):
    """ Single email message, contains the arguments it uses
        in addition to the base email arguments.

        TODO: ATTACHEMENTS

        @param bccAddresses: An array of blind carbon copy addresses.
            This argument is allowed only when a template is not used.
        @param ccAddresses: An array of carbon copy addresses.
            The maximum allowed is five. This argument is allowed only
            when a template is not used.
        @param charset: the character set for the email. If this value
            is null, the user's default value is used.
        @param documentAttachments: An array listing the ID of each
            Document you want to attach to the email. You can attach
            multiple documents as long as the sive of all attachments
            does not exceed 10MB.
        @param fileAttachments: An array listing the file names of
            binary and text files you want to attach to the email.
            You can attach multiple files as long as the total size
            of all attachments does not exceed 10MB.
        @param htmlBody: The HTML version of the email, specified by
            the sender. The value is encoded according to the specification
            associated with the organization.
        @param plainTextBody: The text version of the email, specified
            by the sender.
        @param targetObjectId: The object ID of the contact, lead, or
            user the email will be sent to. The object ID you enter sets
            the context and ensures that merge fields in the template
            contain the correct data.
        @param toAddresses: An array of email address you are sending
            the email to, The maximum allowed is ten. This argument is
            allowed only when a template is not used.
        @param whatId: If you specify a contact for the targetObjectId
            field, you can specify a whatId as well. This help to further
            ensures that merge fields in the template contain the correct
            data.

        @type bccAddresses: string array
        @type ccAddresses: string array
        @type charset: string
        @type documentAttachments: SFDC ID
        @type fileAttachments: EmailFileAttachment
        @type htmlBody: string
        @type plainTextBody: string
        @type targetObjectId: SFDC ID
        @type whatId: SFDC ID

        @return: SingleEmailMessage (lxml.etree.Element)
    """
    def __init__(self, bccSender=None, saveAsActivity=True,
                 useSignature=True, emailPriority='Normal',
                 replyTo=None, subject=None,
                 templateId=None, senderDisplayName=None,
                 bccAddresses=None, ccAddresses=None,
                 charset=None, documentAttachments=None,
                 fileAttachments=None, htmlBody=' ',
                 plainTextBody=' ', targetObjectId=None,
                 whatId=None):

        Email.__init__(self, 'SingleEmailMessage',
            bccSender, saveAsActivity,
            useSignature, emailPriority,
            replyTo, subject,
            templateId, senderDisplayName
        )
        bccAddresses = ','.join(bccAddresses) \
                       if bccAddresses else None
        ccAddresses = ','.join(ccAddresses) \
                      if ccAddresses else None
        self.xml.extend((
            Node('bccAddresses', bccAddresses).xml,
            Node('ccAddresses', ccAddresses).xml,
            Node('charset', charset).xml,
            Node('htmlBody', htmlBody).xml,
            Node('plainTextBody', plainTextBody).xml,
            Node('targetObjectId', targetObjectId).xml,
            Node('whatId', whatId).xml
        ))
        
############################## XML Requests ##############################
class Request(object):
    """ Base class of all XML requests. Initialise the empty XML etree
        with action's body, body content is to be appended.

        @param action: Request action name.

        @type action: string

        @return: XML request constructor, <lxml.etree._ElementTree> instance
            can be accessed by its "xml" attribute.
    """
    def __init__(self, action):
        self.xml = etree.parse(StringIO(__xml__))
        self.body = etree.Element(action)
        self.xml.getroot()[-1].append(self.body)
        self.headers = deepcopy(header)
        self.name = action
        self.response = '%sResponse' % action
        self.encoding = sfdc.encoding
        self.compressType = http.compresstype
        self.method = http.method
        self.debug = sfdc.debug


    def addSoapHeader(self, header, namespace=namespace.partner):
        """ Append a node to SOAP Header.

            @param header: Header element to be appended, etree.Element's
                instance.
            @param namespace: Which namespace should be used for this header,
                default is None, means that it should use the default partner
                namespace, which is "urn:partner.soap.sforce.com".

            @type header: string
            @type namespace: string
        """
        self.xml.getroot()[0].append(header)


    def setSoapHeader(self, header, node, namespace=namespace.partner):
        """ Set a node to SOAP Header.

            @param header: Header's name.
            @param node: Header element to be set, etree.Element's instance.
            @param namespace: Which namespace should be used for this header,
                default is None, means that it should use the default partner
                namespace, which is "urn:partner.soap.sforce.com".

            @type header: string
            @type node: lxml.etree.Element
            @type namespace: string
        """
        element = self.xml.find('//{%s}%s' % (namespace, header))
        if element:
            self.xml.replace(element, node)
        else:
            self.addSoapHeader(node)


    def compress(self, data):
        """ Compress the raw data.

            @param data: Raw XML data in string format.

            @type data: string

            @return: Compressed raw XML data in string format.
        """
        buffer = StringIO()
        zdata = GzipFile(
            mode = 'wb',
            fileobj = buffer,
            compresslevel = http.compresslevel
        )
        zdata.write(data)
        zdata.close()
        return buffer.getvalue()


    def decompress(self, data):
        """ Decompress the compressed data.

            @param data: Compressed raw XML data. 

            @type data: <gzip.GzipFile>

            @return: Decompressed raw XML data in string format.
        """
        zdata = GzipFile(fileobj=StringIO(data))
        return zdata.read()


    def __str__(self):
        """ Constructed XML message, mainly for debug. """
        return etree.tostring(
            self.xml,
            xml_declaration = True,
            encoding = self.encoding,
            pretty_print = self.debug
        )


    def __repr__(self):
        """ Constructed XML message, used to request from server. """
        data = etree.tostring(
            self.xml,
            xml_declaration = True,
            encoding = self.encoding
        )
        if self.debug:
            self.headers['Accept-Encoding'] = 'identity'
            if self.headers.has_key('Content-Encoding'):
                del self.headers['Content-Encoding']
        else:
            data = self.compress(data)
            self.headers['Accept-Encoding'] = self.compressType
            self.headers['Content-Encoding'] = self.compressType   

        self.headers['Content-Length'] = len(data)
        return data


class AuthenticatedRequest(Request):
    """XML request constructor for authenticated users.
        session is actually a shadow copy from template.py
        so that the sessionId can be shared globally.

        @param action: Authenticated request action name.
        @param sessionId: Authenticated session id from Salesforce.com

        @type action: string
        @type sessionId: string

        @return: XML request constructor, <lxml.etree._ElementTree> instance
            can be accessed by its "xml" attribute.
    """
    def __init__(self, sessionId, action):
        Request.__init__(self, action)
        sessionHeader = SessionHeader(sessionId).xml
        self.setSoapHeader('SessionHeader', sessionHeader)


if __name__ == '__main__':
    pass
