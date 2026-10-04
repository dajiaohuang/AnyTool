from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from anytool.grounding.backends.gui.transport.actions import build_pyautogui_command


@pytest.mark.parametrize("dx,dy", [(4, 0), (-4, 0), (4, -2), (0, 2)])
def test_scroll_action_executes_both_requested_axes(dx, dy):
    gui = SimpleNamespace(scroll=Mock(), hscroll=Mock())
    command = build_pyautogui_command("SCROLL", {"dx": dx, "dy": dy})
    exec(command, {"pyautogui": gui})
    if dx:
        gui.hscroll.assert_called_once_with(dx)
    else:
        gui.hscroll.assert_not_called()
    gui.scroll.assert_called_once_with(dy)
