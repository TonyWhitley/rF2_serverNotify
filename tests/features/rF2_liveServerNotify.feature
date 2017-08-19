Feature: Scan a set of real rFactor 2 servers and send a notification
    if someone joins a server that had no drivers.
    Server names can use regular expressions

    Scenario: RealServerIsIdle
        Given I have the file name "test.rF2_serverNotify.json"
        When the JSON file is read
        When the servers file is set up
        And the servers file is read
        # read the server status:
        And the server "F1_1979_Official_Server_1" is read
        Then I see the status "F1_1979_Official_Server_1" is "Active"
