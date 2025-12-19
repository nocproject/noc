# ----------------------------------------------------------------------
# EventClassificationRule test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.sa.models.action import Action
from noc.sa.models.actioncommands import ActionCommands
from .utils import CollectionTestHelper

helper = CollectionTestHelper(ActionCommands)


def teardown_module(module=None):
    """
    Reset all helper caches when leaving module
    :param module:
    :return:
    """
    helper.teardown()


@pytest.fixture(scope="module", params=helper.get_fixture_params(), ids=helper.fixture_id)
def action_commands(database, request):
    yield helper.get_object(request.param)


def test_action_commands_collection_cases(database, action_commands):
    for expected, ctx in action_commands.iter_cases():
        commands = action_commands.action.render_action_commands(
            action_commands.profile,
            {},
            **ctx,
        )
        commands = "\n".join(commands)
        assert commands == expected, "Cannot match expected values"
