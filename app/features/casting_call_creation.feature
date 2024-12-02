Feature: Casting Call Creation
  As a casting director
  I want to be able to create a casting associated with my project
  So I can publish it when I decide to start my artists search for my project

  Scenario: Successful Casting Call creation
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodo123@example.com |
    | password             | Frodo123*            |
    And I have a form template with title "Form for Matrix"
    And I have a project with name "Matrix 4" and an associated role called "Neo"
    When I create a casting call for the project "Matrix 4" associating the role "Neo" to the form template "Form for Matrix"
      | field                     | value                      |
      | title                     | Searching Neo For Matrix 4 |
      | remuneration_type         | Remunerado |
    Then a casting call with the title "Searching Neo For Matrix 4" should be created successfully as draft

  Scenario: Unsuccessful casting call creation without roles associated
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodo123@example.com |
    | password             | Frodo123*            |
    And I have a project with name "Matrix 4" and an associated role called "Neo"
    When I create a casting call for the project "Matrix 4" without associating any roles to it
    | field                     | value                      |
    | title                     | Searching Neo For Matrix 4 |
    | remuneration_type         | Remunerado |
    Then no casting call should be created in the system
    And the user should be notified that the casting call must have at least one role associated

  Scenario: Unsuccessful casting call creation with one role without a form template assigned
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodo1234@example.com |
    | password             | Frodo123*            |
    And I have a project with name "Matrix 4" and an associated role called "Neo"
    When I create a casting call associating the role "Neo" without assigning a form template to it
    | field                     | value                      |
    | title                     | Searching Neo For Matrix 4 |
    | remuneration_type         | Remunerado |
    Then no casting call should be created in the system
    And the user should be notified that each role must have a form template assigned