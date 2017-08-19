Feature: Create and access a list of rFactor 2 servers.
    Fake server lists were to run tests quicker
    but now the list is saved in a JSON file that's
    less necessary.  It does cope with changes in real world
    server addresses.

    Scenario: FakeServers
        Given I have the file name "test.rF2_serverNotify"
        When the servers are faked
        Then I see the address for "F1_1979_Official_Server_1" is "46.9.118.148"
        And I see the port for "F1_1979_Official_Server_1" is 62299
        Then I see the address for "F1_1979_Official_Server_2" is "46.9.118.149"
        And I see the port for "F1_1979_Official_Server_2" is 64399
        Then I see the address for "NoSuchServer" is "ServerNotFound"
        And I see the port for "NoSuchServer" is 0

    Scenario: WriteFakeServers
        When the servers are faked
        And the fake servers file is written
        And the fake servers file is read
        Then the servers match the fake servers
"""
        
    Scenario: WriteRealServers
        #This takes a few minutes
        When the servers are read
        And the servers file is written

    Scenario: ReformatServersFile
        #Only used after changing the json.dumps call
        When the servers file is set up
        And the servers file is read
        And the servers file is written
"""

    Scenario: ReadServers
        Given I have the file name "test.rF2_serverNotify"
        When the servers file is set up
        And the servers file is read
        #When the servers are read
        Then I see the address for "F1_1979_Official_Server_1" is "46.9.118.148"
        And I see the port for "F1_1979_Official_Server_1" is 62299
        And I see the address for "RSVRsig-racing.boards.net" is "86.163.28.215"
        And I see the port for "RSVRsig-racing.boards.net" is 64299
        
        Then I see the address for "F1_1979_Official_Server_2" is "ServerNotFound"
        And I see the port for "F1_1979_Official_Server_2" is 0
        Then I see the address for "NoSuchServer" is "ServerNotFound"
        And I see the port for "NoSuchServer" is 0
