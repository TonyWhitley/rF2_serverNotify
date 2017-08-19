Feature: Scan a set of fake rFactor 2 servers and send a notification
    if someone joins a server that had no drivers.
    Server names can use regular expressions

    Replaced by JSON file
    """
    Scenario: ReadTestConfigFile
        # Read the list of servers to be notified about
        # Only a single server tested at present, not sure how to test a list
        Given I have the file name "test.rF2_serverNotify"
        When the text file is read
        Then I see the result "F1_1979_Official_Server_1"

    Scenario: ServerIsIdle
        Given I have the file name "test.rF2_serverNotify"
        When the text file is read
        # Set the (fake) server status:
        And the server "F1_1979_Official_Server_1" is "Idle"
        Then I see the status "F1_1979_Official_Server_1" is "Idle"

    Scenario: ServerDefaultIsIdle
        # The status is Idle initially
        Given I have the file name "test.rF2_serverNotify"
        When the text file is read
        Then I see the status "F1_1979_Official_Server_2" is "Idle"

    Scenario: ServerIsActive
        Given I have the file name "test.rF2_serverNotify"
        When the text file is read
        # Set the (fake) server status:
        And the server "F1_1979_Official_Server_1" is "Active"
        Then I see the status "F1_1979_Official_Server_1" is "Active"
    """
