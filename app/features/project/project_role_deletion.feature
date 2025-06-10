Feature: Project Role deletion
    As a casting director, 
    I want to be able to delete a role within a project 
    So i can avoid confusion between roles I actually need to fill and those I don't.

    Scenario: Successful Role Deletion Within a Project
        Given Im logged in on the platform with my account
        | field                | value                |
        | fullname             | Frodo Bolson         |
        | email                | frodohobbit@lord.com |
        | password             | Frodo123*            |
        And I create a project called "Matrix Movie" with two roles named "Neo" and "Trinity"
        When I attempt to delete the role called "Neo"
        Then the role is removed from the project

    Scenario: Unsuccessful Role Deletion Within a Project
        Given Im logged in on the platform with my account
        | field                | value                |
        | fullname             | Frodo Bolson         |
        | email                | frodohobbit@lord.com |
        | password             | Frodo123*            |
        And I create a Project called "Matrix 4" with a role called "Neo"
        When I attempt to delete the role called "Neo"
        Then the role is not deleted
        And Im notified that the project cannot remain without roles