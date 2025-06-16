Feature: Form Update
  As a casting director
  I want to be able to edit a form of an open role within a casting
  So that other artists can see the new information that i need to evaluate them

  Scenario: Successful Form Edition of an open role within an unpublished casting
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
    And I edit the form "Form for Matrix" generated for the open role "Neo" setting three form fields
    Then form "Form for Matrix" associated to the role "Neo" within the casting call "Searching Neo For Matrix 4" should have "3" form fields

 Scenario: Successful Form Edition of an open role within a paused casting
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
    And I pause the casting call publication
    When I edit the form "Form for Matrix" generated for the open role "Neo" setting three form fields
    Then form "Form for Matrix" associated to the role "Neo" within the casting call "Searching Neo For Matrix 4" should have "3" form fields

  Scenario: Unsuccessful Form Edition of an open role within a published casting
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
    When I edit the form "Form for Matrix" generated for the open role "Neo" setting three form fields
    Then the form "Form for Matrix" associated to the role "Neo" within the casting call "Searching Neo For Matrix 4" should not have "3" more fields
    And the user should be notified that the form cant be updated cause it belongs to a published casting call
  
  Scenario: Unsuccessful Form Edition of an open role within a finished casting
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
    When I edit the form "Form for Matrix" generated for the open role "Neo" setting three form fields
    Then the form "Form for Matrix" associated to the role "Neo" within the casting call "Searching Neo For Matrix 4" should not have "3" more fields
    And the user should be notified that the form cant be updated cause it belongs to a finished casting call