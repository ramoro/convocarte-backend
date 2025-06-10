Feature: Casting Call Search
  As an artist, 
  I want to be able to search for castings 
  to decide which ones to apply to.

  Scenario: Successful search for a published theater casting
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
    When I try to search for theater castings
    Then the system displays the casting as a result

  Scenario: Unsuccessful search for unpublished advertising castings
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
    When I try to search for advertising castings
    Then the system does not show any castings as results