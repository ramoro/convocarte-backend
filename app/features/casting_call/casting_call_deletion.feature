Feature: Casting Call Deletion
  As a casting director
  I want to be able to delete a casting call
  so i prevent mixing them with active casting calls
 
  Scenario: Successful Casting Call deletion
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
    And I try to delete the casting call
    Then the casting call is deleted from the system
    And the casting call forms should desappear from the system

  Scenario: Successful Finished Casting Call deletion
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
    And I create a casting call for the project "Matrix 4" associating the role "Neo" to the form template "Form for Matrix"
      | field                     | value                      |
      | title                     | Searching Neo For Matrix 4 |
      | remuneration_type         | Remunerado |
    And I publish the casting call with an expiration date greater than the current date
    And I finish the casting call
    When I try to delete the casting call
    Then the casting call is deleted from the system
    And the casting call forms should desappear from the system

  Scenario: Unsuccessful Published Casting Call deletion
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
    And I create a casting call for the project "Matrix 4" associating the role "Neo" to the form template "Form for Matrix"
      | field                     | value                      |
      | title                     | Searching Neo For Matrix 4 |
      | remuneration_type         | Remunerado |
    And I publish the casting call with an expiration date greater than the current date
    When I try to delete the casting call
    Then the casting call should not be eliminated from the system    
    And the user should be notified that the casting call cant be deleted cause its published

  Scenario: Unsuccessful Paused Casting Call deletion
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
    And I create a casting call for the project "Matrix 4" associating the role "Neo" to the form template "Form for Matrix"
      | field                     | value                      |
      | title                     | Searching Neo For Matrix 4 |
      | remuneration_type         | Remunerado |
    And I publish the casting call with an expiration date greater than the current date
    When I pause the casting call
    And I try to delete the casting call
    Then the casting call should not be eliminated from the system
    And the user should be notified that the casting call cant be deleted cause its paused