Feature: Artist Account Deletion
    As a user
    I want to permanently delete all my registered information
    So that my history, photos, and data are completely removed from a site I no longer use

  Scenario: Successful Artist Account Deletion Without Projects
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    When I try to delete my account
    Then the account is deleted from the system

  Scenario: Successful Artist Account Deletion With Postulation
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
    
  Scenario: Unsuccessful Deletion of a non-existent artist account
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    When I try to delete an non-existent account
    Then the account is not deleted from the system
    And i am notified that the account couldnt be deleted because it doesnt exists
