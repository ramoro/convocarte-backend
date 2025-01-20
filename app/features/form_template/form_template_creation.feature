Feature: Form Template Creation
  As a casting director
  I want to be able to create a form template
  So other users can fill it out when publishing a casting

  Scenario: Successful Form Template creation
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    When I create a form template with title "Form for Matrix" and some form fields
    Then a form template with the title "Form for Matrix" should be created successfully for the user

  Scenario: Unsuccessful creation of Form Template with an existing title
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And I have a form template with title "Form for Matrix" and some form fields
    When I create a form template with title "Form for Matrix" and some form fields 
    Then the form template should not be created for the user
    And the user should be notified that they already have a form with that title


