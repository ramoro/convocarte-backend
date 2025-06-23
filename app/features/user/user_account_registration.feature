Feature: Account Registration
  As an artist
  I want to register my academic and work experiences
  So I can find possible job opportunities

  Scenario: Successful User Registration with a valid email, full name, and password
    Given there is no account registered with the email "frodo123@example.com"
    When I register an account with valid data
      | field                | value               |
      | fullname             | Frodo Bolson        |
      | email                | frodo123@example.com |
      | password             | Password123*        |
      | password_confirmation | Password123*      |
    Then an account with the email "frodo123@example.com" is created in the system

  Scenario: Unsuccessful User Registration with an already registered email
    Given there is an account registered with the email "frodo123@example.com"
    When I try to register an account with the same email and a valid data
      | field                | value               |
      | fullname             | Frodo Bolson        |
      | email                | frodo123@example.com |
      | password             | Password123*        |
      | password_confirmation | Password123*      |
    Then the account is not created in the system
    And the user is notified that an account with that email already exists

  Scenario: Unsuccessful User Registration due to missing full name
    Given there is no account registered with the email "frodo123@example.com"
    When I register an account with that email and no full name
      | field                | value               |
      | email                | frodo123@example.com |
      | password             | Password123*        |
      | password_confirmation | Password123*      |
    Then the account is not created in the system 
    And the user is notified that the field is required

  Scenario: Unsuccessful User Registration due to missing email
    Given there is no account registered with the email "frodo123@example.com"
    When I register an account with no email
      | field                | value               |
      | fullname             | Frodo Bolson        |
      | password             | Password123*        |
      | password_confirmation | Password123*      |
    Then the account is not created in the system
    And the user is notified that the field is required

  Scenario: Unsuccessful User Registration due to missing password
    Given there is no account registered with the email "frodo123@example.com"
    When I register an account with no password
      | field                | value               |
      | fullname             | Frodo Bolson        |
      | email                | frodo123@example.com |
      | password_confirmation | Password123*      |
    Then the account is not created in the system
    And the user is notified that the field is required

  Scenario: Unsuccessful User Registration due to password and confirmation password mismatch
    Given there is no account registered with the email "frodo123@example.com"
    When I register with a password that does not match the confirmation password
      | field                | value               |
      | fullname             | Frodo Bolson        |
      | email                | frodo123@example.com |
      | password             | Password           |
      | password_confirmation | Password123*      |
    Then the account is not created in the system
    And the user is notified that the passwords must match