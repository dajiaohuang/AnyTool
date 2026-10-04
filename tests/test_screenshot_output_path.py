import pytest
from PIL import Image

from anytool.local_server.utils import screenshot


@pytest.mark.parametrize("region", [False, True])
def test_screenshot_accepts_output_filename_without_parent_directory(monkeypatch, tmp_path, region):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(screenshot.pyautogui, "screenshot", lambda **kwargs: Image.new("RGB", (2, 2)))
    helper = screenshot.ScreenshotHelper.__new__(screenshot.ScreenshotHelper)
    helper.adapter = None
    if region:
        success = helper.capture_region("shot.png", 0, 0, 2, 2)
    else:
        success = helper.capture("shot.png", with_cursor=False)
    assert success
    with Image.open("shot.png") as image:
        assert image.size == (2, 2)
