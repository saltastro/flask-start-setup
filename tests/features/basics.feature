Feature: Illustrating the use of Behave

  Scenario: Setting a number

    Given a is 42
    When I set b to be equal to a
    Then b is 42
