Feature: Casting Director Casting Postulation Rejection
    As an Casting Director, 
    I want to remove a postulation from my postulations list
    So that I can avoid confusion with my active postulations

  Scenario: Successful postulation rejection
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
    And an artist applied for the role with his account
    | field                | value               |
    | fullname             | Albus Dumbledore    |
    | email                | albus@bigwizard.com |
    | password             | Albus123*           |
    When I try to reject the postulation
    Then the postulation is rejected
    And the postulation will be deleted from the casting

  Scenario: Unsuccessful rejection of postulation for another director's casting
    Given a user that has a published theater casting with title "Searching Neo For Matrix 4" and open role "Neo"
    | field                | value               |
    | fullname             | Albus Dumbledore    |
    | email                | albus@bigwizard.com |
    | password             | Albus123*           |
    And an artist applied for the role with his account
    | field                | value                  |
    | fullname             | Cedric Digory          |
    | email                | cedridig@bigwizard.com |
    | password             | Cedric123*             |
    And Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    When I try to reject the postulation
    Then the postulation is not rejected
    And I will be notify that "Cannot reject postulations from a casting that is not yours"
