Feature: Project Edition
  As a casting director
  I want to be able to edit a project and its roles so 
  So I can update it if I change my mind about what the project will be like and what roles will make it up

  Scenario: Successful edition of a project with no associated casting 
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And I have a project with name "Matrix 4" and an associated role called "Neo"
    When I try to edit project name, project description and role name
    | field                    | value                           |
    | new_name                 | Matrix renovado 4               |
    | new_description          | Proyecto sobre pelicula Matrix  |
    | region                   | Ciudad Autónoma de Buenos Aires |
    | category                 | Cine-largometraje               |
    | new_role_name            | Trinity                         |
    Then the project information should be successfully updated on the system

  Scenario: Unsuccessful edition of Project within an unended casting
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And I have a form template with title "Form for Matrix"
    And I have a project with name "Matrix 4" and an associated role called "Neo"
    And I create a casting call for the project "Matrix 4" associating the role "Neo" to the form template "Form for Matrix"
      | field                     | value                      |
      | title                     | Searching Neo For Matrix 4 |
      | remuneration_type         | Remunerado |
    When I try to edit project name, project description and role name
      | field                    | value                           |
      | new_name                 | Matrix renovado 4               |
      | new_description          | Proyecto sobre pelicula Matrix |
      | region                   | Ciudad Autónoma de Buenos Aires |
      | category                 | Cine-largometraje               |
      | new_role_name            | Trinity                         |
    Then the project information should not be successfully updated on the system
    And the user should be notified that the project is being used and must end the castings that are using it in order to update the project
    
  Scenario: Successful edition of a project within ended castings
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And I have a form template with title "Form for Matrix"
    And I have a project with name "Matrix 4" and an associated role called "Neo"
    And I create a casting call for the project "Matrix 4" associating the role "Neo" to the form template "Form for Matrix"
      | field                     | value                      |
      | title                     | Searching Neo For Matrix 4 |
      | remuneration_type         | Remunerado |
    And I publish the casting call with an expiration date greater than the current date
    And I finish the casting call
    When I try to edit project name, project description and role name
      | field                    | value                           |
      | new_name                 | Matrix renovado 4               |
      | new_description          | Proyecto sobre pelicula Matrix  |
      | region                   | Ciudad Autónoma de Buenos Aires |
      | category                 | Cine-largometraje               |
      | new_role_name            | Trinity                         |
    Then the project information should be successfully updated on the system

  Scenario: Unsuccessful edition of a project with existing name within users projects list
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And I have a project with name "Harry Potter 4" and an associated role called "Harry"
    And I have a project with name "Matrix 4" and an associated role called "Neo"
    When I try to edit project named "Matrix 4" with name "Harry Potter 4"
      | field                    | value                           |
      | new_name                 | Harry Potter 4                  |
      | new_description          | Proyecto sobre pelicula Matrix  |
      | region                   | Ciudad Autónoma de Buenos Aires |
      | category                 | Cine-largometraje               |
      | new_role_name            | Trinity                         |
    Then the project information should not be successfully updated on the system
    And the user should be notified that they already have a project with that name

  Scenario: Unsuccessful edition of Project with two roles with same name
    Given Im logged in on the platform with my account
    | field                | value                |
    | fullname             | Frodo Bolson         |
    | email                | frodohobbit@lord.com |
    | password             | Frodo123*            |
    And I create a project named "Matrix Movie" with two roles named "Neo" and "Trinity"
    When I try to edit project setting two roles named "Neo"
      | field                    | value                           |
      | new_name                 | Harry Potter 4                  |
      | new_description          | Proyecto sobre pelicula Matrix  |
      | region                   | Ciudad Autónoma de Buenos Aires |
      | category                 | Cine-largometraje               |
      | new_role_name            | Neo                             |
    Then the project roles should not be successfully updated on the system
    And the user should be notified that the project shouldnt have more than one role with the same name


