Feature: Casting Call Publication
  As a casting director
  I want to be able to publish a casting
  So that other artists can apply, allowing me to evaluate them

  Scenario: Successful Casting Call publication
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodo123@example.com |
    | password             | Frodo123*            |
    And I have a form template with title "Form for Matrix"
    And I have a project with name "Matrix 4" and an associated role called "Neo"
    And I have a casting call with title "Searching Neo For Matrix 4" associated to the project "Matrix 4"
    When I publish the casting call with an expiration date greater than the current date
    Then the casting call with the title "Searching Neo For Matrix 4" should be successfully published

 Scenario: Successful publication of a paused casting
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodo123@example.com |
    | password             | Frodo123*            |
    And I have a form template with title "Form for Matrix"
    And I have a project with name "Matrix 4" and an associated role called "Neo"
    And I have a casting call published with title "Searching Neo For Matrix 4" associated to the project "Matrix 4"
    And I pause the casting call publication
    When I publish the casting call with an expiration date greater than the current date
    Then the casting call with the title "Searching Neo For Matrix 4" should be successfully published

  Scenario: Unsuccessful publication of a casting with expiration date less than the current date
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodo123@example.com |
    | password             | Frodo123*            |
    And I have a form template with title "Form for Matrix"
    And I have a project with name "Matrix 4" and an associated role called "Neo"
    And I have a casting call with title "Searching Neo For Matrix 4" associated to the project "Matrix 4"
    When I publish the casting call with an expiration date less than the current date
    Then the casting call with the title "Searching Neo For Matrix 4" should not be published
    And the user should be notified that the expiration date must be greater than the current date

  Scenario: Unsuccessful publication of a paused casting with expiration date less than the current date
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodo123@example.com |
    | password             | Frodo123*            |
    And I have a form template with title "Form for Matrix"
    And I have a project with name "Matrix 4" and an associated role called "Neo"
    And I have a casting call published with title "Searching Neo For Matrix 4" associated to the project "Matrix 4"
    And I pause the casting call publication
    When I publish the casting call with an expiration date less than the current date
    Then the casting call with the title "Searching Neo For Matrix 4" should not be published
    And the user should be notified that the expiration date must be greater than the current date

  Scenario: Unsuccessful publication of a an ended casting
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodo123@example.com |
    | password             | Frodo123*            |
    And I have a form template with title "Form for Matrix"
    And I have a project with name "Matrix 4" and an associated role called "Neo"
    And I have a casting call published with title "Searching Neo For Matrix 4" associated to the project "Matrix 4"
    And I pause the casting call publication
    When I publish the casting call with an expiration date less than the current date
    Then the casting call with the title "Searching Neo For Matrix 4" should not be published
    And the user should be notified that the expiration date must be greater than the current date