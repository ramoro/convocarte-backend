Feature: Casting Call Creation
  As a casting director
  I want to be able to create a casting associated with my project
  So I can show what i need for my project

  Scenario: Successful Casting Call creation
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And I create a form template with title "Form for Matrix" and some form fields
      | field                     | value             |
      | title                     | Nombre y Apellido |
      | type                      | text              |
      | order                     | 0                 |
      | is_required               | True              |
    And I create a Project called "Matrix 4" with a role called "Neo"
    When I create a casting call for the project "Matrix 4" associating the role "Neo" to the form template "Form for Matrix"
      | field                     | value                      |
      | title                     | Searching Neo For Matrix 4 |
      | remuneration_type         | Remunerado |
    Then a casting call with the title "Searching Neo For Matrix 4" should be created successfully as draft
    And a form should be created successfully for the casting role with the same title and same fields that the form template "Form for Matrix"

  Scenario: Unsuccessful casting call creation without roles associated
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And I create a Project called "Matrix 4" with a role called "Neo"
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
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And I create a Project called "Matrix 4" with a role called "Neo"
    When I create a casting call associating the role "Neo" without assigning a form template to it
    | field                     | value                      |
    | title                     | Searching Neo For Matrix 4 |
    | remuneration_type         | Remunerado |
    Then no casting call should be created in the system
    And the user should be notified that each role must have a form template assigned