Feature: Project Creation
  As a casting director
  I want to be able to create a project
  So i can bring together the people with whom I am going to work

  Scenario: Successful Project creation
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    When I create a project with name "Matrix Movie"
    Then a project with the name "Matrix Movie" should be created successfully

  Scenario: Unsuccessful creation of Project with existing name within user projects
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And I have a project with name "Matrix Movie"
    When I create a project with name "Matrix Movie"
    Then the project should not be created for the user
    And the user should be notified that they already have a project with that name

  Scenario: Unsuccessful creation of Project with two roles with same name
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    When I create a project named "Matrix Movie" with two roles named "Neo"
    Then the project should not be created for the user
    And the user should be notified that the project shouldnt have more than one role with the same name

  Scenario: Unsuccessful creation of Project with no roles
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    When I create a project named "Matrix Movie" with no roles
    Then the project should not be created for the user
    And the user should be notified that the project should have at least one role

