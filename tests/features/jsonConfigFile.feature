Feature: Read and parse a JSON config file

    Scenario: readJsonConfig
        # Read the list of servers to be notified about
        # Only a single server tested at present, not sure how to test a list
        Given I have the file name "test.rF2_serverNotify.json"
        When the JSON file is read
        Then I see the result "F1_1979_Official_Server_1"
        Then I see the interval 30

    Scenario: ServerIsIdle
        Given I have the file name "test.rF2_serverNotify.json"
        When the JSON file is read
        # Set the (fake) server status:
        And the server "F1_1979_Official_Server_1" is "Idle"
        Then I see the status "F1_1979_Official_Server_1" is "Idle"

    Scenario: ServerDefaultIsIdle
        # The status is Idle initially
        Given I have the file name "test.rF2_serverNotify.json"
        When the JSON file is read
        Then I see the status "F1_1979_Official_Server_2" is "Idle"

    Scenario: ServerIsActive
        Given I have the file name "test.rF2_serverNotify.json"
        When the JSON file is read
        # Set the (fake) server status:
        And the server "F1_1979_Official_Server_1" is "Active"
        Then I see the status "F1_1979_Official_Server_1" is "Active"
 