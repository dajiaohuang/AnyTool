from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from anytool.local_server.platform_adapters import windows_adapter


@pytest.mark.parametrize("draw_fails", [False, True])
def test_cursor_capture_releases_owned_resources_without_destroying_shared_cursor(monkeypatch, draw_fails):
    gui = SimpleNamespace(
        GetCursorInfo=Mock(return_value=(1, 99, (0, 0))), GetDC=Mock(return_value=10),
        GetIconInfo=Mock(return_value=(False, 2, 3, 20, 21)),
        DestroyIcon=Mock(), DeleteObject=Mock(), ReleaseDC=Mock(),
    )
    bitmap = SimpleNamespace(CreateCompatibleBitmap=Mock(), GetHandle=Mock(return_value=17),
                             GetInfo=Mock(return_value={"bmWidth": 1, "bmHeight": 1}), GetBitmapBits=Mock(return_value=b"\x00\x00\x00\x00"))
    compatible = SimpleNamespace(SelectObject=Mock(return_value="old"), DeleteDC=Mock(),
                                 DrawIcon=Mock(side_effect=ValueError("draw failed") if draw_fails else None))
    dc = SimpleNamespace(CreateCompatibleDC=Mock(return_value=compatible))
    ui = SimpleNamespace(CreateDCFromHandle=Mock(return_value=dc), CreateBitmap=Mock(return_value=bitmap))
    monkeypatch.setattr(windows_adapter, "win32gui", gui, raising=False)
    monkeypatch.setattr(windows_adapter, "win32ui", ui, raising=False)
    image, hotspot = windows_adapter.WindowsAdapter.__new__(windows_adapter.WindowsAdapter)._get_cursor()
    gui.DestroyIcon.assert_not_called()
    gui.ReleaseDC.assert_called_once_with(0, 10)
    assert {call.args[0] for call in gui.DeleteObject.call_args_list} == {17, 20, 21}
    assert compatible.SelectObject.call_args.args == ("old",)
    compatible.DeleteDC.assert_called_once()
    if draw_fails:
        assert image is None
    else:
        assert image is not None
        assert hotspot == (2, 3)
