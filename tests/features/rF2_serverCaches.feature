Feature: List of rFactor 2 servers is held explicitly in a cache.
    The data from those servers is also cached.
    Valve commands are:
    * Get names of all servers (reasonably quick)
    * Get address of a named server (reasonably quick but there are a lot of them)
    * Get details of server (reasonably quick but there are a lot of them)
    In addition we have a list of names of favourite servers.
    
    Functions:
    Refresh cache of names of all servers
    Refresh address cache for a list of named servers
    Refresh details cache for a list of named servers
    From the caches:
      Get names of all servers
      Get next name of a server (generator)
      Get addresses of a list of named servers 
      Get details of a list of named servers 
      Get list of names of favourite servers
      for testing: select fake caches



    Scenario: FakeCacheNames
        #Given I have the file name "test.rF2_serverNotify"
        When the caches are faked
        When the names of all servers are read
        Then I see "F1_1979_Official_Server_1" "F1_1979_Official_Server_2"

    Scenario: FakeCacheNextName
        When the caches are faked
        When I ask for the next server name
        Then I see "F1_1979_Official_Server_1"
        When I ask for the next server name
        Then I see "F1_1979_Official_Server_2"
        
    Scenario: FakeCacheAddresses
        When the caches are faked
        When I ask for the address for "F1_1979_Official_Server_1" is "46.9.118.148"
        And I see the port for "F1_1979_Official_Server_1" is 62299
        When I ask for the address for "F1_1979_Official_Server_2" is "46.9.118.149"
        And I see the port for "F1_1979_Official_Server_2" is 64399
        When I ask for the address for "NoSuchServer" is "ServerNotFound"
        And I see the port for "NoSuchServer" is 0

    Scenario: RefreshNamesCache
        When the names are read
        When I ask for the next server name
        Then what I see is not "F1_1979_Official_Server_1"

    Scenario: RefreshAddressesCache
        When the addresses are read
        When I ask for the next server name
        #Then what I see is not "F1_1979_Official_Server_1"


