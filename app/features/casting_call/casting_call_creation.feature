Feature: Casting Call Creation
  As a casting director
  I want to be able to create a casting associated with my project
  So I can publish it when I decide to start my artists search for my project

  Scenario: Successful Casting Call creation
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And I have a form template with title "Form for Matrix" with one form field
    And I have a project with name "Matrix 4" and an associated role called "Neo"
    When I create a casting call for the project "Matrix 4" associating the role "Neo" to the form template "Form for Matrix"
      | field                     | value                      |
      | title                     | Searching Neo For Matrix 4 |
      | remuneration_type         | Remunerado |
    And I edit the form "Form for Matrix" generated for the exposed role "Neo" setting three form fields
    Then form "Form for Matrix" associated to the role "Neo" within the casting call "Searching Neo For Matrix 4" should have "3" form fields