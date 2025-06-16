Feature: User Account Deletion
    As a user, 
    I want to delete all the information I registered, 
    so that no personal or work data remains on a platform I no longer use.

  Scenario: Successful Account Deletion Without Projects
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    When I try to delete my account
    Then the account is deleted from the system

  Scenario: Successful Account Deletion With a Project
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And I create a Project called "Matrix 4" with a role called "Neo"
    When I try to delete my account
    Then the account is deleted from the system
    And the project is deleted from the system along with the role
    
  Scenario: Successful Account Deletion With a Project with an associated casting
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And I create a project called "Matrix 4" with a role called "Neo"
    And I create a form template with title "Movies Form" and some form fields
    | field                     | value             |
    | title                     | Nombre y Apellido |
    | type                      | text              |
    | order                     | 0                 |
    | is_required               | True              |
    And I create a casting call for the project "Matrix 4" associating the role "Neo" to the form template "Movies Form"
    | field                     | value                      |
    | title                     | Searching Neo For Matrix 4 |
    | remuneration_type         | Remunerado |
    When I try to delete my account
    Then the account is deleted from the system
    And the project is deleted from the system along with the role
    And the form template is deleted from the system
    And the casting call is deleted from the system

  Scenario: Successful Account Deletion With Postulation
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
    And I postulate for the open role "Neo" within the published casting  
    When I try to delete my account
    Then the account is deleted from the system
    And the postulation is deleted from the system

  Scenario: Unsuccessful Deletion of a non-existent account
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    When I try to delete an non-existent account
    Then the account is not deleted from the system
    And i am notified that the account couldnt be deleted because it doesnt exists