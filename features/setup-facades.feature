Feature: setup facades
  As a system architect I want the installation
  enginers and developers have an ability
  to manipulate facades in easy, intuitive,
  and error-prone way.

  Scenario: create facade
    Given I have and prepared SVG image
    And name and description text for facade.
    And I have "Facades" application open
    And I am on a list page

    When I press the "Add" button
    Then form page appears
    And the "Save" button is disabled
    And I can see "Create Facade" title
    And I can see empty fields "Name", "Description", "Image"
    And "Image" field shows placeholder text "Please upload an SVG image"
    And "Image" field has "Select File..." button

    When I fill "Name" and "Description" field with given data
    Then approptiate text appears

    When I press "Select File..." button
    Then system file selection dialog appears
    And I am able to select only files with ".svg" extension

    When I select a file and confirm an action in system-dependent way
    Then file selection dialog must disappear
    And I can see an preview of uploaded image near the "Select File..." button.

    When I need to change the image I press "Select File..."
    Then I can select other file
    And I can see an preview of uploaded image near the "Select File..." button.

    When all fields are filled
    Then "Save" button is enabled

    When I press "Save" button
    Then data saved
    And application is switched to a facades list

  Scenario: edit facade
    Given I have new SVG image
    And I have "Facades" application open
    And I am on a list page

    When I'm double-clicking on desired facade
    Then form page appears
    And I can see "Edit Facades" title
    And "Name" and "Description" fields filled with proper values
    And "Image" field shows preview near "Select File..." button

    When I press "Select File..." button
    Then system file selection dialog appears
    And I am able to select only files with ".svg" extension

    When I select a file and confirm an action in system-dependent way
    Then file selection dialog must disappear
    And I can see an preview of uploaded image near the "Select File..." button.

    When I press "Save" button
    Then data saved
    And application is switched to a facades list
