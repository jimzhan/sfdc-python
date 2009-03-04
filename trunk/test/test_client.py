# -*- coding: utf-8 -*-
from sys import path
from os.path import abspath, dirname, join
path.insert(0, abspath(join(dirname(__file__), '..')))
from unittest import TestCase, main
from config import sfdc
from client import Client


class TestClient(TestCase):
    def setUp(self):
        self.client = Client(
            username = sfdc['username'],
            password = sfdc['password']
        )


    def tearDown(self):
        del self.client.loginResult

    def testConvertLead(self):
        pass
    
    def testCreate(self):
        pass
    
    def testDelete(self):
        pass
    
    def testGetDeleted(self):
        pass
    
    def testGetUpdated(self):
        pass
    
    def testInvalidateSessions(self):
        pass
    
    def testLogin(self):
        pass
    
    def testMerge(self):
        pass
    
    def testProcess(self):
        pass
    
    def testQuery(self):
        pass
    
    def testQueryAll(self):
        pass
    
    def testQueryMore(self):
        pass
    
    def testRetrieve(self):
        pass
    
    def testSearch(self):
        pass
    
    def testUndelete(self):
        pass
    
    def testUpdate(self):
        pass
    
    def testUpsert(self):
        pass
    
    def testDescribeGlobal(self):
        pass
    
    def testDescribeLayout(self):
        pass
    
    def testDescribeSObject(self):
        pass
    
    def testDescribeSObjects(self):
        pass
    
    def testDescribeSoftphoneLayout(self):
        pass
    
    def testDescribeTabs(self):
        pass
    
    def emptyRecyclebin(self):
        pass
    
    def getServerTimestamp(self):
        pass
    
    def getUserInfo(self):
        pass
    
    def resetPassword(self):
        pass
    
    def sendEmail(self):
        pass
    
    def setPassword(self):
        pass