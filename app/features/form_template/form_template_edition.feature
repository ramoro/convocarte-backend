Feature: Form Template Creation
  As a casting director
  I want to be able to update a form template
  So that when applying, people can enter the new information that I need them to send me

  Scenario: Successful Form Template edition
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And I have a form template with title "Form for Matrix" with one form field
    When I edit the form template adding a form field
    Then the form template "Form for Matrix" should be updated with two form fields

  Scenario: Unsuccessful edition of Form Template with an existing title
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And I have a form template with title "Form for Matrix" with one form field
    And I have a form template with title "Form for Harry Potter" with one form field
    When I edit the form template "Form for Matrix" with the existing title "Form for Harry Potter"
    Then the form template "Form for Matrix" should not be updated
    And the user should be notified that they already have a form with that title

