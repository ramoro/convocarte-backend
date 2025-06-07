Feature: Casting Postulation Creation
  As an artist 
  I want to be able to apply for one or more roles within a casting 
  So that I can be considered for the project

  Scenario: Successful Postulation for an open role within a casting
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
    When I postulate for the open role "Neo" within the published casting
    Then a postulation for that casting call and that open role should be succesfully created in the system

  Scenario: Unsuccessful Postulation for an open role within an ended casting
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
    When I postulate for the open role "Neo" within the published casting
    Then the postulation should not be created for the user
    And the user should be notified that the casting has already finished

  Scenario: Unsuccessful Postulation for an open role within a paused casting
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
    And the casting is paused
    When I postulate for the open role "Neo" within the published casting
    Then the postulation should not be created for the user
    And the user should be notified that the casting is paused

  Scenario: Unsuccessful Postulation for an open role with full spots
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And there is a project with name "Matrix 4" with an associated role called "Neo"
    And there is a casting call published for that project opening the role "Neo" with 50 spots
    | field                     | value                      |
    | title                     | Searching Neo For Matrix 4 |
    | remuneration_type         | Remunerado |
    And the open role "Neo" has all its 50 spots full
    When I postulate for the open role "Neo" within the published casting
    Then the postulation should not be created for the user
    And the user should be notified that the open role for this casting call is full

  Scenario: Unsuccessful Postulation for an open role for which the user has already applied
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
    When I postulate for the open role "Neo" within the published casting
    Then the postulation should not be created for the user
    And the user should be notified that they has already postulated for that role