Feature: Casting Call Publication
  As a casting director
  I want to be able to publish a casting
  So that other artists can see the differents roles i need to occupy in my project

  Scenario: Successful Casting Call publication
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
    And I publish the casting call "Searching Neo For Matrix 4" with an expiration date greater than the current date
    Then the casting call should be successfully published

 Scenario: Successful publication of a paused casting
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
    When I publish the casting call "Searching Neo For Matrix 4" with an expiration date greater than the current date
    Then the casting call should be successfully published

  Scenario: Unsuccessful publication of a casting with expiration date less than the current date
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
    When I publish the casting call "Searching Neo For Matrix 4" with an expiration date less than the current date
    Then the casting call should not be published
    And the user should be notified that the expiration date must be greater than the current date

  Scenario: Unsuccessful publication of a an ended casting
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
    When I publish the casting call "Searching Neo For Matrix 4" with an expiration date greater than the current date
    Then the casting call should not be published
    And the user should be notified that the casting cannot be published because it has already ended

  Scenario: Unsuccessful publication of a casting with a title already used by other published casting
    Given a user that has a published theater casting with title "Searching Neo For Matrix 4" and open role "Neo"
      | field                | value               |
      | fullname             | Albus Dumbledore    |
      | email                | albus@bigwizard.com |
      | password             | Albus123*           |
    And Im logged in on the platform with my account
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
    When I publish the casting call "Searching Neo For Matrix 4" with an expiration date greater than the current date
    Then the casting call should not be published
    And the user should be notified that there is already a published casting with the title "Searching Neo For Matrix 4"