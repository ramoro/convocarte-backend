Feature: Casting director's email sent to artist postulation
    As a casting director
    I want to message artists who applied to my casting
    So I can communicate selection updates and requirements

 Scenario: Successful message sent to applied artist
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
    When I try to send a message to the artist that says "The casting will be the next saturday at 8 am"
    Then a message with the content "The casting will be the next saturday at 8 am" is created
    And the artist postulation receives the message

  Scenario: Unsuccessful message sent to an artist who has not applied
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
    | remuneration_type         | Remunerado                 |
    And I publish the casting call with an expiration date greater than the current date
    And an artist that did not postulate for the role
    | field                | value               |
    | fullname             | Albus Dumbledore    |
    | email                | albus@bigwizard.com |
    | password             | Albus123*           |
    When I try to send a message to the artist that says "The casting will be the next saturday at 8 am"
    Then a message with the content "The casting will be the next saturday at 8 am" is not created 
    And I will be notify that "Cannot send a message to a non-existent postulation"