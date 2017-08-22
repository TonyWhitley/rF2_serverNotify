Feature: Read and parse the text file of AI driver namnes

    Scenario: MatchDriverName
        Given I have the drivers file name "drivers.txt"
        When the drivers file is read
        And the filter is "Albin Warnelov #12"
        Then I see the driver status "AI"

    Scenario: MatchDriverNameAJ
        Given I have the drivers file name "drivers.txt"
        When the drivers file is read
        And the filter is "A J Foyt"
        Then I see the driver status "AI"

    Scenario: DontMatchDriverName
        Given I have the drivers file name "drivers.txt"
        When the drivers file is read
        And the filter is "Seven Smiles"
        Then I see the driver status "Human"

