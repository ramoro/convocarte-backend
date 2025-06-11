Feature: Artist Casting Postulation Search
    As an artist, 
    I want to remove a postulation from my postulations list
    So that I can avoid confusion with my active postulations

  Scenario: Successful postulation removal
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
    When I try to delete the postulation
    Then the postulation will be deleted from the system

  Scenario: Unsuccessful non-existent postulation removal
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    When I try to delete a non-existent postulation
    Then I should be notified that the postulation doesnt exists so it cant be deleted