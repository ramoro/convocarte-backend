Feature: Casting Director Casting Postulation Search
  As a casting director, 
  I want to be able to reject a submission from the list of postulations received for a casting I created,
  so that I can more easily focus on the profiles that interest me.

  Scenario: Successful postulation removal
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
    When I try to view the postulation list for roles within the casting
    Then the system will show me the artists postulation

  Scenario: Unsuccessful attempt to view postulations for another director's casting
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
    When I try to view the postulation list for roles within the casting
    Then the system wont show any postulation
    And I will be notify that "You cannot get other casting calls with postulations"

