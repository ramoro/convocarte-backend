Feature: Casting Call Publication
  As a casting director
  I want to be able to publish a casting
  So that other artists can apply, allowing me to evaluate them

  Scenario: Successful Casting Call publication
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
    And I publish the casting call "Searching Neo For Matrix 4" with an expiration date greater than the current date
    Then the casting call should be successfully published