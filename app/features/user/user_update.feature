Feature: User Update
    As an artist,
    I want to be able to update my profile 
    so that casting directors can know how to contact me, 
    as well as my physical characteristics, skills, education, work experience in the industry, and my current appearance.

 Scenario: Successful Artist Profile Update
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    When I try to update my weight with 68 and my height with 1.75 in my profile
    Then my weight is updated with 68 and my height with 1.75 in the system

  Scenario: Unsuccessful Artist Profile Update
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And there is another user with a different account
    | field                | value               |
    | fullname             | Albus Dumbledore    |
    | email                | albus@bigwizard.com |
    | password             | Albus123*           |
    When I try to update that users weight and height with 68 and 1.75 respectively 
    Then the weight and height of the other user it not updated with 68 and 17.5 respectively
    And I am notified that I cannot update the information of a user I am not logged in as