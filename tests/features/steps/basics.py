from behave import *

use_step_matcher("re")


@given("a is 42")
def step_impl(context):
    context.a = 42


@when("I set b to be equal to a")
def step_impl(context):
    context.b = context.a


@then("b is 42")
def step_impl(context):
    assert context.b == 42
