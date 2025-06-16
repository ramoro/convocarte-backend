Feature: Casting Director Casting Postulation Choice
    As an Casting Director, 
    I want to be able to select a specific postulation from my list of postulations as the chosen one to fill the casted role in the casting I published,
    so I can easily see which artist I selected for the role.

  Scenario: Successful postulation Choice
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
    When I try to choose the postulation
    Then the postulation is chosen

  Scenario: Unsuccessful choice of postulation belonging to another casting director's casting
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
    When I try to choose the postulation
    Then the postulation is not chosen
    And I will be notify that "Cannot choice postulation to fill the role in a casting you did not create"

    Scenario: Unsuccessful choice of a rejected postulation
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
    And I reject the postulation
    When I try to choose the postulation
    Then the postulation is not chosen
    And I will be notify that "Cannot choice a rejected postulation to fill the role"
