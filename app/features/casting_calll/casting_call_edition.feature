Feature: Casting Call Edition
  As a casting director
  I want to be able to edit a casting and its roles
  So that applicants users know the new requirements for the roles when they apply

  Scenario: Successful Casting Call Edition
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And I have a form template with title "Form for Matrix"
    And I have a project with name "Matrix 4" and an associated role called "Neo"
    When I create a casting call for the project "Matrix 4" associating the role "Neo" to the form template "Form for Matrix"
      | field                     | value                      |
      | title                     | Searching Neo For Matrix 4 |
      | remuneration_type         | Remunerado |
    And I edit the casting call "Searching Neo For Matrix 4" with the title "Searching Neo For Matrix 5" and its role "Neo" with minimum age requirement "25"
    Then the casting call should be successfully updated with the title "Searching Neo For Matrix 5" and its role "Neo" should have a minimum age requirement of "25"

  Scenario: Successful Edition of a Paused Casting Call
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And I have a form template with title "Form for Matrix"
    And I have a project with name "Matrix 4" and an associated role called "Neo"
    And I create a casting call for the project "Matrix 4" associating the role "Neo" to the form template "Form for Matrix"
      | field                     | value                      |
      | title                     | Searching Neo For Matrix 4 |
      | remuneration_type         | Remunerado |
    And I publish the casting call with an expiration date greater than the current date
    When I pause the casting call
    And I edit the casting call "Searching Neo For Matrix 4" with the title "Searching Neo For Matrix 5" and its role "Neo" with minimum age requirement "25"
    Then the casting call should be successfully updated with the title "Searching Neo For Matrix 5" and its role "Neo" should have a minimum age requirement of "25"

  Scenario: Unsuccessful Edition of a Published Casting Call
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And I have a form template with title "Form for Matrix"
    And I have a project with name "Matrix 4" and an associated role called "Neo"
    And I create a casting call for the project "Matrix 4" associating the role "Neo" to the form template "Form for Matrix"
      | field                     | value                      |
      | title                     | Searching Neo For Matrix 4 |
      | remuneration_type         | Remunerado |
    And I publish the casting call with an expiration date greater than the current date
    When I edit the casting call "Searching Neo For Matrix 4" with the title "Searching Neo For Matrix 5" and its role "Neo" with minimum age requirement "25"
    Then the casting call should not be successfully updated with the title "Searching Neo For Matrix 5" and its role "Neo" with minimum age requirement "25"
    And the user should be notified that the casting must be paused to be updated

  Scenario: Unsuccessful Edition of an ended Casting Call
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And I have a form template with title "Form for Matrix"
    And I have a project with name "Matrix 4" and an associated role called "Neo"
    And I create a casting call for the project "Matrix 4" associating the role "Neo" to the form template "Form for Matrix"
      | field                     | value                      |
      | title                     | Searching Neo For Matrix 4 |
      | remuneration_type         | Remunerado |
    And I publish the casting call with an expiration date greater than the current date
    And I finish the casting call
    When I edit the casting call "Searching Neo For Matrix 4" with the title "Searching Neo For Matrix 5" and its role "Neo" with minimum age requirement "25"
    Then the casting call should not be successfully updated with the title "Searching Neo For Matrix 5" and its role "Neo" with minimum age requirement "25"
    And the user should be notified that the casting has finished and cant be edited