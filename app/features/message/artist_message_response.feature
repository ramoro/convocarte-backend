Feature: Artist message response to casting director
    As an artist,
    I want to be able to respond to messages sent by the casting director regarding my postulations
    so I can ask questions if any arise

    Scenario: Successful message response to casting director
        Given Im logged in on the platform with my account
        | field                | value                |
        | fullname             | Frodo Bolson         |
        | email                | frodohobbit@lord.com |
        | password             | Frodo123*            |
        And a user that has a published theater casting with title "Searching Neo For Matrix 4" and open role "Neo"
        | field                | value               |
        | fullname             | Albus Dumbledore    |
        | email                | albus@bigwizard.com |
        | password             | Albus123*           |
        And I postulate for the open role "Neo" within the published casting
        And the casting director owner of the casting sends me a message
        When I try to response to the message telling "I will be there"
        Then a message with the content "I will be there" is created
        And the casting director receives the message
    
    Scenario: Unsuccessful message response to an non-existent message
        Given Im logged in on the platform with my account
        | field                | value                |
        | fullname             | Frodo Bolson         |
        | email                | frodohobbit@lord.com |
        | password             | Frodo123*            |
        And a user that has a published theater casting with title "Searching Neo For Matrix 4" and open role "Neo"
        | field                | value               |
        | fullname             | Albus Dumbledore    |
        | email                | albus@bigwizard.com |
        | password             | Albus123*           |
        And I postulate for the open role "Neo" within the published casting
        When I try to response to a non-existent message with "I will be there"
        Then a message with the content "I will be there" is not created
        And I will be notify that "Cannot respond to a non-existent message"