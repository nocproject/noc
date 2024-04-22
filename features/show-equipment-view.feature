Feature: show equipment view
  As a boss of a tech support team I need
  all my staff, including on-site engineers
  and third line support, to see the same actual
  visual representation of the equipment,
  including transceivers and modules. This will
  help to exclude the misunderstandings and
  will reduce amount of the human errors.
  
  Scenario: show facade
    Given I have an inventory object selected
    And object has facade
    Then In the object's details area I must see "Facade" tab
    And "Facade" tab must show the graphical representation of the object
