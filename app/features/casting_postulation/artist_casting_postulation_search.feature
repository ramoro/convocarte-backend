Feature: Artist Casting Postulation Search
    As an artist, 
    I want to be able to search my list of postulations 
    o I can keep track of them and the projects each one belongs to.

  Scenario: Successful search of submitted postulation
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And there is a project with name "Matrix 4" with an associated role called "Neo"
    And there is a casting call published for that project opening the role "Neo" with unlimited spots
    | field                     | value                      |
    | title                     | Searching Neo For Matrix 4 |
    | remuneration_type         | Remunerado |
    And I postulate for the open role "Neo" within the published casting
    When I try to search for my postulations
    Then the system will show me the submitted postulation

  Scenario: Unsuccessful search of a submitted Postulation for an open role within an ended casting
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And there is a project with name "Matrix 4" with an associated role called "Neo"
    And there is a casting call published for that project opening the role "Neo" with unlimited spots
    | field                     | value                      |
    | title                     | Searching Neo For Matrix 4 |
    | remuneration_type         | Remunerado |
    And the casting is finished
    And I postulate for the open role "Neo" within the published casting
    When I try to search for my postulations
    Then the system will not show me the submitted postulation