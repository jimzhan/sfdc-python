# -*- coding: utf-8 -*-
#
# Copyright (c) 2008, 2009 Xigital Solutions
#
# Written by Jim Zhan <jim@xigital.com>
#
# This file is part of SFDC-Python Salesforce python accessor.
# 

class Base(Exception):
    """ Basic Salesforce error Exception class. """
    def __init__(self, code, message):
        Exception.__init__(self, message)
        self.code = code.strip()
        self.message = message.strip()


    def __str__(self):
        return '%s: %s' % (self.code, self.message)

    
    def __repr__(self):
        return '%s: %s' % (self.code, self.message)


    def __unicode__(self):
        return '%s: %s' % (self.code, self.message)


class SessionExpired(Base):
    """ For any authenticated request with expired/invalid sessionId. """


class LoginFault(Base):
    """ An error occurred during the login() call. """


class SFDCError(Base):
    """ All unexpected errors returned by Salesforce """


class UnimplementedError(Exception):
    """ For those unimplemented methods """


############################## Standard SFDC Fault ##############################
"""
class ApiQueryFault(Base):
    ''' The row and column numbers where the problem occurred. '''
    pass


class InvalidSObject(Base):
    ''' An invalid sObject in a describeSObject(), describeSObjects(),
        create(), update(), retrieve(), or query() call.
    '''
    pass


class InvalidField(Base):
    ''' An invalid field in a retrieve() or query() call. '''
    pass


class MalformedQuery(Base):
    ''' A problem in the queryString passed in a query() call.
    '''
    pass


class InvalidQuery(Base):
    ''' A problem in the queryLocator passed in a queryMore() call.
    '''
    pass


class MalformedSearch(Base):
    ''' A problem in the search passed in a search() call.
    '''
    pass


class InvalidId(Base):
    ''' A specified ID was invalid in a setPassword() or resetPassword() call.
    '''
    pass


class UnexpectedError(Base):
    ''' An unexpected error occurred. The error is not associated with any other API fault.
    '''
    pass
"""

############################## Exception Codes ##############################
exceptions = {
    'API_CURRENTLY_DISABLED': 'Because of a system problem, API functionality is temporarily unavailable.',
    'API_DISABLED_FOR_ORG': 'API access has not been enabled for the organization. Contact salesforce.com to enable API access.', 
    'CANT_ADD_STANDARD_PORTAL_USER_TO_TERRITORY': 'A user with a standard portal license cannot be added to a territory.', 
    'CIRCULAR_OBJECT_GRAPH': 'The request failed because it contained a circular object reference.',
    'CLIENT_NOT_ACCESSIBLE_FOR_USER': 'The current user does not have permission to access the specified client.', 
    'CLIENT_REQUIRE_UPDATE_FOR_USER': 'The current user is required to use a newer version of the specified client, and will have access until the client is updated.', 
    'DUPLICATE_VALUE': 'You cannot supply a duplicate value for a field that must be unique. For example, you may have submitted two copies of the same sessionId in a invalidateSessions() call.', 
    'EMAIL_BATCH_SIZE_LIMIT_EXCEEDED': 'A method tried to process more email records than the maximum batch size.',
    'EMAIL_TO_CASE_INVALID_ROUTING': 'An email to case record has been submitted for processing but the feature is not enabled.',
    'EMAIL_TO_CASE_LIMIT_EXCEEDED': 'The daily converted email limit for the Email-to-Case feature has been exceeded.',
    'EMAIL_TO_CASE_NOT_ENABLED': 'The Email-to-Case feature has not been enabled.',
    'EXCEEDED_ID_LIMIT': 'Too many IDs were specified in a call. For example, more than 2000 IDs were requested in a retrieve() call, or more than 200 session IDs were specified in a logout() call.',
    'EXCEEDED_LEAD_CONVERT_LIMIT': 'Too many IDs were sent to a convertLead() call.',
    'EXCEEDED_MAX_SIZE_REQUEST': 'The size of the message sent to the API exceeded 50 MB.',
    'EXCEEDED_MAX_TYPES_LIMIT': 'The number of object types to describe is too large.',
    'EXCEEDED_QUOTA': 'The size limit for organization data storage was exceeded during a create() call.',
    'FUNCTIONALITY_NOT_ENABLED': 'Functionality has been temporarily disabled. Other calls may continue to work.',
    'INACTIVE_OWNER_OR_USER': 'The user or record owner is not active.',
    'INACTIVE_PORTAL': 'The referenced portal is inactive.',
    'INSUFFICIENT_ACCESS': 'The user does not have sufficient access to perform the operation.',
    'INVALID_ASSIGNMENT_RULE': 'An invalid AssignmentRuleHeader value was specified.',
    'INVALID_BATCH_SIZE': 'The query options have an invalid batch size value.',
    'INVALID_CLIENT': 'The client is invalid.',
    'INVALID_CROSS_REFERENCE_KEY': 'An invalid foreign key cannot be set on a field.',
    'INVALID_FIELD': 'The specified field name is invalid.',
    'INVALID_FILTER_LANGUAGE': 'The specified language cannot be used as a filter.',
    'INVALID_FILTER_VALUE': 'A SOQL query with LIKE or NOT LIKE specified an invalid character, for example, an incorrectly placed asterisk (*). Correct the query and resubmit.',
    'INVALID_ID_FIELD': 'The specified ID is correctly formatted, but is not valid, for example, it is an ID of the wrong type, or the object it identifies no longer exists.',
    'INVALID_LOCATOR': 'The locator is invalid.',
    'INVALID_LOGIN': 'The login() credentials are not valid, or the maximum number of logins have been exceeded. Contact your administrator for more information.',
    'INVALID_NEW_PASSWORD': 'The new password does not conform with the password policies of the organization.',
    'INVALID_OPERATION': 'The client application tried to submit an object that is already in process as part of workflow approval or processing.',
    'INVALID_OPERATION_WITH_EXPIRED_PASSWORD': 'Due to password expiration, a valid password must be set using setPassword() before the call can be invoked.',
    'INVALID_QUERY_FILTER_OPERATOR': 'An invalid operator was used in the query() filter clause, at least for that field.',
    'INVALID_QUERY_LOCATOR': 'An invalid queryLocator parameter was specified in a queryMore() call.',
    'INVALID_QUERY_SCOPE': 'The specified search scope is invalid.',
    'INVALID_REPLICATION_DATE': 'The date for replication is out of the allowed range, such as before the organization was created.',
    'INVALID_SEARCH': 'The search() call has invalid syntax or grammar. See Salesforce Object Search Language (SOSL).',
    'INVALID_SEARCH_SCOPE': 'The specified search scope is invalid.',
    'INVALID_SESSION_ID': 'The specified sessionId is malformed (incorrect length or format) or has expired. Log in again to start a new session.',
    'INVALID_SOAP_HEADER': 'There is an error in the SOAP header. If you are migrating from an earlier version of the API, be advised that the SaveOptions header cannot be used with API version 6.0 or later. Use AssignmentRuleHeader instead.',
    'INVALID_SSO_GATEWAY_URL': 'The URL provided to configure the Single Sign-On gateway was not a valid URL.',
    'INVALID_TYPE': 'The specified sObject type is invalid.',
    'INVALID_TYPE_FOR_OPERATION': 'The specified sObject type is invalid for the specified operation.',
    'LIMIT_EXCEEDED': 'An array is too long. For example, there are too many BCC addresses, targets, or email messagess.',
    'LOGIN_DURING_RESTRICTED_DOMAIN': 'The user is not allowed to log in from this IP address.',
    'LOGIN_DURING_RESTRICTED_TIME': 'The user is not allowed to log in during this time period.',
    'MALFORMED_ID': 'An invalid ID string was specified. For information about IDs, see ID Field Type.',
    'MALFORMED_QUERY': 'An invalid query string was specified. For example, the query string was longer than 10,000 characters.',
    'MALFORMED_SEARCH': 'An invalid search string was specified. For example, the search string was longer than 10,000 characters.',
    'MISSING_ARGUMENT': 'A required argument is missing.',
    'NOT_MODIFIED': 'The describe call response has not changed since the specified date.',
    'NO_SOFTPHONE_LAYOUT': 'If an organization has the CTI feature enabled, but no softphone layout has been defined, this exception is returned if a describe call is issued. This is most often caused because no call center has been defined: during call center definition, a default softphone layout is created. If an organization does not have the CTI feature enabled, FUNCTIONALITY_NOT_ENABLED is returned instead.',
    'NUMBER_OUTSIDE_VALID_RANGE': 'The number specified is outside the valid range for the field.',
    'OPERATION_TOO_LARGE': 'The query has returned too many results. Some queries, for example those on objects that use a polymorphic foreign key like Task, if run by a user without the "View All Data" permission, would require sharing rule checking if many records were returned. Such queries return this exception because the operation requires too many resources. To correct, add filters to the query to narrow the scope, or use filters such as date ranges to break the query up into a series of smaller queries.',
    'ORG_LOCKED': 'The organization has been locked. You must contact salesforce.com to unlock the organization.',
    'ORG_NOT_OWNED_BY_INSTANCE': 'The user tried to log in to the wrong server instance. Choose another server instance or log in at https://www.salesforce.com. You can use http instead of https.',
    'PASSWORD_LOCKOUT': 'The user has exceeded the allowed number of login attempts. The user must contact his or her administrator to regain login access.',
    'PORTAL_NO_ACCESS': 'Access to the specified portal is not available.',
    'QUERY_TIMEOUT': 'The query has timed out. For more information, see Salesforce Object Query Language (SOQL).',
    'QUERY_TOO_COMPLICATED': 'SOQL query is either selecting too many fields or there are too many filter conditions. Try reducing the number of formula fields referenced in the query.',
    'REQUEST_LIMIT_EXCEEDED': 'Exceeded either the concurrent request limit or the request rate limit for your organization. For details, see API Usage Metering.',
    'REQUEST_RUNNING_TOO_LONG': 'A request has taken too long to be processed.',
    'SERVER_UNAVAILABLE': 'A server that is necessary for this call is currently unavailable. Other types of requests might still work.',
    'SSO_SERVICE_DOWN': 'The service was unavailable, and an authentication call to the organization’s specified Single Sign-On server failed.',
    'TOO_MANY_APEX_REQUESTS': 'Too many Apex requests have been issued. If this persists, contact Salesforce Customer Support.',
    'TRIAL_EXPIRED': 'The trial period for the organization has expired. A representative from the organization must contact salesforce.com to re-enable the organization.',
    'UNSUPPORTED_API_VERSION': 'A method call was made that does not exist in the accessed API version, for example, trying to use upsert() (new in 8.0) against version 5.0.',
    'UNSUPPORTED_CLIENT': 'This version of the client is no longer supported.',
}
############################## Status Codes ##############################
status = {
    'ALREADY_IN_PROCESS': 'You cannot submit a record that is already in an approval process. You must wait for the previous approval process to complete before resubmitting a request with this record.',
    'ASSIGNEE_TYPE_REQUIRED': 'You must designate an assignee for any workflow task (ProcessInstance, ProcessInstanceStep, or ProcessInstanceWorkitem).',
    'BAD_CUSTOM_ENTITY_PARENT_DOMAIN': 'The changes you are trying to make cannot be completed because changes to the associated master-detail relationships cannot be made.',
    'BCC_NOT_ALLOWED_IF_BCC_COMPLIANCE_ENABLED': "Your client applicationblind carbon-copied an email address on an email even though the organization's Compliance BCC Email option is enabled. This option specifies a particular email address that automatically receives a copy of all outgoing email. When this option is enabled, you cannot BCC any other email address. To disable the option, log in to the Salesforce app and select Setup | Security Controls | Compliance BCC Email.",
    'BCC_SELF_NOT_ALLOWED_IF_BCC_COMPLIANCE_ENABLED': "Your client application blind carbon copied the logged-in user's email address on an email even though the organization's BCC COMPLIANCE option is set to true. This option specifies a particular email address that automatically receives a copy of all outgoing email. When this option is enabled, you cannot BCC any other email address. To disable the option, log in to the Salesforce app and select Setup | Security Controls | Compliance BCC Email.",
    'CANNOT_CHANGE_FIELD_TYPE_OF_APEX_REFERENCED_FIELD': 'You cannot change the type of a field that is referenced in an Apex script.',
    'CANNOT_CREATE_ANOTHER_MANAGED_PACKAGE': 'You can only create one managed package in an organization.',
    'CANNOT_DEACTIVATE_DIVISION': "You cannot deactivate Divisions if an assignment rule references divisions or if a user's DefaultDivision field is not set to null.",
    'CANNOT_DELETE_LAST_DATED_CONVERSION_RATE': 'You must have at least one DatedConversionRate record if dated conversions are enabled.',
    'CANNOT_DELETE_MANAGED_OBJECT': 'You cannot modify components that are included in a managed package.',
    'CANNOT_DISABLE_LAST_ADMIN': 'You must have at least one active administrator user.',
    'CANNOT_ENABLE_IP_RESTRICT_REQUESTS': 'If you exceed the limit of five IP ranges specified in a profile, you cannot enable restriction of login by IP addresses. Reduce the number of specified ranges in the profile and try the request again.',
    'CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY': 'You do not have permission to create, update, or activate the specified record.',
    'CANNOT_MODIFY_MANAGED_OBJECT': 'You cannot modify components that are included in a managed package.',
    'CANNOT_RENAME_APEX_REFERENCED_FIELD': 'You cannot rename a field that is referenced in an Apex script.',
    'CANNOT_RENAME_APEX_REFERENCED_OBJECT': 'You cannot rename an object that is referenced in an Apex script.',
    'CANNOT_REPARENT_RECORD': 'You cannot define a new parent record for the specified record.',
    'CANNOT_RESOLVE_NAME': 'A sendEmail() call could not resolve an object name.',
    'CANNOT_UPDATE_CONVERTED_LEAD': 'A converted lead could not be updated.',
    'CANT_DISABLE_CORP_CURRENCY': 'You cannot disable the corporate currency for an organization. To disable a currency that is set as the corporate currency, first use the Salesforce user interface to change the corporate currency to a different currency, and then disable the original currency.',
    'CANT_UNSET_CORP_CURRENCY': 'You cannot change the corporate currency for an organization from the API. Use the Salesforce user interface to change the corporate currency.',
    'CHILD_SHARE_FAILS_PARENT': 'You cannot change the owner of or define sharing rules for a record that is a child of another record if you do not also have the appropriate permissions on the parent. For example, you cannot change the owner of a a contact record if you cannot edit its parent account record.',
    'CIRCULAR_DEPENDENCY': 'You cannot create a circular dependency between metadata objects in your organization. For example, public group A cannot include public group B, if public group B already includes public group A.',
    'CUSTOM_CLOB_FIELD_LIMIT_EXCEEDED': 'You cannot exceed the maximum size for a CLOB field.',
    'CUSTOM_ENTITY_OR_FIELD_LIMIT': 'You have reached the maximum number of custom objects or custom fields for your organization.',
    'CUSTOM_FIELD_INDEX_LIMIT_EXCEEDED': 'You have reached the maximum number of indexes on a field for your organization.',
    'CUSTOM_INDEX_EXISTS': 'You can create only one custom index per field.',
    'CUSTOM_LINK_LIMIT_EXCEEDED': 'You have reached the maximum number of custom links for your organization.',
    'CUSTOM_TAB_LIMIT_EXCEEDED': 'You have reached the maximum number of custom tabs for your organization.',
    'DELETE_FAILED': 'You cannot delete a record because it is in use by another object.',
    'DEPENDENCY_EXISTS': 'You cannot perform the requested operation because of an existing dependency on the specified object or field.',
    'DUPLICATE_CASE_SOLUTION': 'You cannot create a relationship between the specified case and solution because it already exists.',
    'DUPLICATE_CUSTOM_ENTITY_DEFINITION': 'Custom object or custom field IDs must be unique.',
    'DUPLICATE_CUSTOM_TAB_MOTIF': 'You cannot create a custom object or custom field with a duplicate master name.',
    'DUPLICATE_DEVELOPER_NAME': 'You cannot create a custom object or custom field with a duplicate developer name.',
    'DUPLICATE_EXTERNAL_ID': 'A user-specified external ID matches more than one record in Salesforce during an upsert() call.',
    'DUPLICATE_MASTER_LABEL': 'You cannot create a custom object or custom field with a duplicate master name.',
    'DUPLICATE_USERNAME': 'A create(), update(), or upsert() call failed because of a duplicate user name.',
    'DUPLICATE_VALUE': 'You cannot supply a duplicate value for a field that must be unique. For example, you may have submitted two copies of the same sessionId in a invalidateSessions() call.',
    'EMAIL_NOT_PROCESSED_DUE_TO_PRIOR_ERROR': 'Because of an error earlier in the call, the current email was not processed.',
    'EMPTY_SCONTROL_FILE_NAME': 'The Scontrol file name was empty, but the binary was nonempty.',
    'ENTITY_FAILED_IFLASTMODIFIED_ON_UPDATE': 'You cannot update a record if the date inLastModifiedDate is later than the current date.',
    'ENTITY_IS_ARCHIVED': 'You cannot access a record if it has been archived.',
    'ENTITY_IS_DELETED': 'You cannot reference an object that has been deleted. Note that this status code only occurs in version 10.0 of the API and later. Previous releases of the API use INVALID_ID_FIELD for this error.',
    'ENTITY_IS_LOCKED': 'You cannot edit a locked object during a workflow processing operation.',
    'ERROR_IN_MAILER': 'An email address is invalid, or another error occurred during an email-related transaction.',
    'FAILED_ACTIVATION': 'The activation of a Contract or Order failed.',
    'FIELD_CUSTOM_VALIDATION_EXCEPTION': 'You cannot define a custom validation formula that violates a field integrity rule.',
    'FIELD_INTEGRITY_EXCEPTION': 'You cannot violate field integrity rules.',
    'HTML_FILE_UPLOAD_NOT_ALLOWED': 'Your attempt to upload an HTML file failed. HTML attachments and documents, including HTML attachments to a Solution, cannot be uploaded if the Disallow HTML documents and attachments checkbox is selected in Setup | Security Controls | HTML Documents and Attachments Settings.',
    'IMAGE_TOO_LARGE': 'The image exceeds the maximum width, height, and file size.',
    'INACTIVE_OWNER_OR_USER': 'The owner of the specified item is an inactive user. To reference this item, either reactivate the owner or reassign ownership to another active user.',
    'INSUFFICIENT_ACCESS_ON_CROSS_REFERENCE_ENTITY': 'An operation affects an object that is cross-referenced by the specified object, but the logged-in user does not have sufficient permissions on the cross-referenced object. For example, if the logged in user attempts to modify an account record, that user might not have permission to approve, reject, or reassign a ProcessInstanceWorkitem that is submitted after that action.',
    'INSUFFICIENT_ACCESS_OR_READONLY': 'You cannot perform the specified action because you do not have sufficient permissions.',
    'INVALID_ACCESS_LEVEL': 'You cannot define a new sharing rule if it provides less access than the specified organization-wide default.',
    'INVALID_ARGUMENT_TYPE': 'You supplied an argument that is of the wrong type for the operation being attempted.',
    'INVALID_ASSIGNEE_TYPE': 'You specified an assignee type that is not a valid integer between one and six.',
    'INVALID_ASSIGNMENT_RULE': 'You specified an assignment rule that is invalid or that is not defined in the organization.',
    'INVALID_BATCH_OPERATION': 'The specified batch operation is invalid.',
    'INVALID_CREDIT_CARD_INFO': 'The specified credit card information is not valid.',
    'INVALID_CROSS_REFERENCE_KEY': 'The specified value in a relationship field is not valid, or data is not of the expected type.',
    'INVALID_CROSS_REFERENCE_TYPE_FOR_FIELD': 'The specified cross reference type is not valid for the specified field.',
    'INVALID_CURRENCY_CONV_RATE': 'You must specify a positive, non-zero value for the currency conversion rate.',
    'INVALID_CURRENCY_CORP_RATE': 'You cannot modify the corporate currency conversion rate.',
    'INVALID_CURRENCY_ISO': 'The specified currency ISO code is not valid. For more information, see IsoCode.',
    'INVALID_EMAIL_ADDRESS': 'A specified email address is invalid.',
    'INVALID_EMPTY_KEY_OWNER': 'You cannot set the value for owner to null.',
    'INVALID_FIELD': 'You specified an invalid field name in an update() or upsert() call.',
    'INVALID_FIELD_FOR_INSERT_UPDATE': 'You cannot combine a person account record type change with any other field update.',
    'INVALID_FIELD_WHEN_USING_TEMPLATE': 'You cannot use an email template with an invalid field name.',
    'INVALID_FILTER_ACTION': 'The specified filter action cannot be used with the specified object. For example, an alert is not a valid filter action for a Task.',
    'INVALID_ID_FIELD': 'The specified ID field (ID, ownerId), or cross-reference field is invalid.',
    'INVALID_INET_ADDRESS': 'A specified Inet address is not valid.',
    'INVALID_LINEITEM_CLONE_STATE': 'You cannot clone a Pricebook2 or PricebookEntry record if those objects are not active.',
    'INVALID_MASTER_OR_TRANSLATED_SOLUTION': 'The solution is invalid. For example, this error can occur if you try to associate a translated solution with a master solution when another translated solution in the same language is already associated with the master solution.',
    'INVALID_OPERATION': 'There is no applicable approval process for the specified object.',
    'INVALID_OPERATOR': 'The specified operator is not applicable for the field type when used as a workflow filter.',
    'INVALID_OR_NULL_FOR_RESTRICTED_PICKLIST': 'You specified an invalid or null value for a restricted picklist.',
    'INVALID_PARTNER_NETWORK_STATUS': 'The specified partner network status is invalid for the specified template field.',
    'INVALID_PERSON_ACCOUNT_OPERATION': 'You cannot delete a person account.',
    'INVALID_SAVE_AS_ACTIVITY_FLAG': 'You must specify true or false for the Save_as_Activity flag.',
    'INVALID_SESSION_ID': 'The specified sessionId is malformed (incorrect length or format) or has expired. Log in again to start a new session.',
    'INVALID_STATUS': 'The specified organization status change is not valid.',
    'INVALID_TYPE': 'The specified type is not valid for the specified object.',
    'INVALID_TYPE_FOR_OPERATION': 'The specified type is not valid for the specified operation.',
    'INVALID_TYPE_ON_FIELD_IN_RECORD': "The specified value is not valid for the specified field's type.",
    'IP_RANGE_LIMIT_EXCEEDED': 'The specified IP address is outside the IP range specified for the organization.',
    'LAST_MODIFIED_SINCE_TOO_OLD': 'The LastModifedbyDate specified is too old. Retry the request without this filter.',
    'LICENSE_LIMIT_EXCEEDED': 'You have exceeded the number of licenses assigned to your organization.',
    'LIMIT_EXCEEDED': 'You have exceeded a limit. The limit may be on a field size or value, license, or other component.',
    'LOGIN_CHALLENGE_ISSUED': "An email containing a security token was sent to the user's email address because he or she logged in from an IP address that is not included in their organization's list of trusted IP addresses. The user cannot log in until he or she adds the security token to the end of his or her password.",
    'LOGIN_CHALLENGE_PENDING': "The user logged in from an IP address that is not included in their organization's list of trusted IP addresses, but a security token has not yet been issued.",
    'LOGIN_MUST_USE_SECURITY_TOKEN': 'The user must add a security token to the end of his or her password to log in.',
    'MALFORMED_ID': 'An ID must be either 15 characters, or 18 characters with a valid case-insensitive extension. There is also an exception code of the same name.',
    'MANAGER_NOT_DEFINED': 'A manager has not been defined for the specified approval process.',
    'MASSMAIL_RETRY_LIMIT_EXCEEDED': 'A mass mail retry failed because your organization has exceeded its mass mail retry limit.',
    'MASS_MAIL_LIMIT_EXCEEDED': 'The organization has exceeded its daily limit for mass email. Mass email messages cannot be sent again until the next day.',
    'MAXIMUM_CCEMAILS_EXCEEDED': 'You have exceeded the maximum number of specified CC addresses in a workflow alert.',
    'MAXIMUM_DASHBOARD_COMPONENTS_EXCEEDED': 'You have exceeded the document size limit for a dashboard.',
    'MAXIMUM_HIERARCHY_LEVELS_REACHED': 'You have reached the maximum number of levels in a hierarchy.',
    'MAXIMUM_SIZE_OF_ATTACHMENT': 'You have exceeded the maximum size of an attachment.',
    'MAXIMUM_SIZE_OF_DOCUMENT': 'You have exceeded the maximum size of a document.',
    'MAX_ACTIONS_PER_RULE_EXCEEDED': 'You have exceeded the maximum number of actions per rule.',
    'MAX_ACTIVE_RULES_EXCEEDED': 'You have exceeded the maximum number of active rules.',
    'MAX_APPROVAL_STEPS_EXCEEDED': 'You have exceeded the maximum number of approval steps for an approval process.',
    'MAX_FORMULAS_PER_RULE_EXCEEDED': 'You have exceeded the maximum number of formulas per rule.',
    'MAX_RULES_EXCEEDED': 'You have exceeded the maximum number of rules for an object.',
    'MAX_RULE_ENTRIES_EXCEEDED': 'You have exceeded the maximum number of entries for a rule.',
    'MAX_TASK_DESCRIPTION_EXCEEEDED': 'The task description is too long.',
    'MAX_TM_RULES_EXCEEDED': 'You have exceeded the maximum number of rules per Territory.',
    'MAX_TM_RULE_ITEMS_EXCEEDED': 'You have exceeded the maximum number of rule criteria per rule for a Territory.',
    'MERGE_FAILED': 'A merge operation failed.',
    'MISSING_ARGUMENT': 'You did not specify a required argument.',
    'NONUNIQUE_SHIPPING_ADDRESS': 'You cannot insert a reduction order item if the original order shipping address is different from the shipping address of other items in the reduction order.',
    'NO_APPLICABLE_PROCESS': 'A process() request failed because the record submitted does not satisfy the entry criteria of any workflow process for which the user has permission.',
    'NO_ATTACHMENT_PERMISSION': 'Your organization does not permit email attachments.',
    'NO_MASS_MAIL_PERMISSION': 'You do not have permission to send the specified email. You must have "Mass Email" if you are sending mass mail or "Send Email" if you are sending individual email.',
    'NUMBER_OUTSIDE_VALID_RANGE': 'The number specified is outside the valid range of values.',
    'NUM_HISTORY_FIELDS_BY_SOBJECT_EXCEEDED': 'The number of history fields specified for the sObject exceeds the allowed limit.',
    'OPTED_OUT_OF_MASS_MAIL': 'An email cannot be sent because the specified User has opted out of mass mail.',
    'PACKAGE_LICENSE_REQUIRED': 'The logged-in user cannot access an object that is in a licensed package if the logged-in user does not have a license for the package.',
    'PORTAL_USER_ALREADY_EXISTS_FOR_CONTACT': 'A create()User operation failed because you cannot create a second portal user under a Contact.',
    'PRIVATE_CONTACT_ON_ASSET': 'You cannot have a private contact on an asset.',
    'RECORD_IN_USE_BY_WORKFLOW': 'You cannot access a record if it is currently in use by a workflow process.',
    'REQUEST_RUNNING_TOO_LONG': 'A request that has been running too long may be cancelled.',
    'REQUIRED_FIELD_MISSING': 'A call requires a field that was not specified.',
    'SELF_REFERENCE_FROM_TRIGGER': 'You cannot recursively update or delete the same object from an Apex trigger',
    'SHARE_NEEDED_FOR_CHILD_OWNER': 'You cannot delete a sharing rule for a parent record if its child record needs it.',
    'STANDARD_PRICE_NOT_DEFINED': 'Custom prices cannot be defined without corresponding standard prices.',
    'STORAGE_LIMIT_EXCEEDED': "You have exceeded your organization's storage limit.",
    'STRING_TOO_LONG': 'The specified string exceeds the maximum allowed length.',
    'TABSET_LIMIT_EXCEEDED': 'You have exceeded the number of tabs allowed for a tabset.',
    'TEMPLATE_NOT_ACTIVE': 'The template specified is unavailable. Specify another template or make the template available for use.',
    'TERRITORY_REALIGN_IN_PROGRESS': 'An operation cannot be performed because a territory realignment is in progress.',
    'TEXT_DATA_OUTSIDE_SUPPORTED_CHARSET': 'The specified text uses a character set that is not supported.',
    'TOO_MANY_APEX_REQUESTS': 'Too many Apex requests have been sent to Salesforce. This error is transient. Resend your request after a short wait.',
    'TOO_MANY_ENUM_VALUE': 'A request failed because too many values were passed in for a multi-select picklist. You can select a maximum of 100 values for a multi-select picklist.',
    'TRANSFER_REQUIRES_READ': 'You cannot assign the record to the specified User because the user does not have read permission.',
    'UNABLE_TO_LOCK_ROW': 'A deadlock or timeout condition has been detected.',
    'UNAVAILABLE_RECORDTYPE_EXCEPTION': 'The appropriate default record type could not be found.',
    'UNDELETE_FAILED': 'An object could not be undeleted because it does not exist or has not been deleted.',
    'UNKNOWN_EXCEPTION': 'The system encountered an internal error. Please report this problem to salesforce.com.',
    'UNSPECIFIED_EMAIL_ADDRESS': 'The specified user does not have an email address.',
    'UNSUPPORTED_APEX_TRIGGER_OPERATON': 'You cannot save recurring events with an Apex trigger.',
    'WEBLINK_SIZE_LIMIT_EXCEEDED': 'The size of a WebLink URL or JavaScript code exceeds the limit.',
}
