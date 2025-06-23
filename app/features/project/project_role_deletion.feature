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
        When I attempt to update the project deleting the role called "Neo"
        | field                    | value                           |
        | name                     | Matrix Movie                    |
        | region                   | Ciudad Autónoma de Buenos Aires |
        | category                 | Cine-largometraje               |
        | role_one                 | Trinity                         |
        Then the role "Neo" is removed from the project

    Scenario: Unsuccessful Role Deletion Within a Project
        Given Im logged in on the platform with my account
        | field                | value                |
        | fullname             | Frodo Bolson         |
        | email                | frodohobbit@lord.com |
        | password             | Frodo123*            |
        And I create a Project called "Matrix 4" with a role called "Neo"
        When I attempt to update the project deleting the role called "Neo"
        | field                    | value                           |
        | name                     | Matrix Movie                    |
        | region                   | Ciudad Autónoma de Buenos Aires |
        | category                 | Cine-largometraje               |
        Then the role "Neo" is not deleted
        And Im notified that the project cannot remain without roles