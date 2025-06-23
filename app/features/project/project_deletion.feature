Feature: Project Deletion
  As a casting director
  I want to be able to delete a project that im not going to do
  So I can have a better visualization of the rest of my projects

  Scenario: Successful deletion of a project with no associated casting 
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And I create a project named "Matrix Movie"
    When I try to delete the project
    Then the project should successfully desappear from the system

  Scenario: Unsuccessful deletion of Project within an unended casting
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
    When I try to delete the project
    Then the project should not be eliminated from the system
    And the user should be notified that the project is being used and must end the castings that are using it in order to delete the project
    
  Scenario: Successful deletion of a project within ended castings
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
    When I try to delete the project
    Then the project should successfully desappear from the system
    And the castings associated should desappear from the system


