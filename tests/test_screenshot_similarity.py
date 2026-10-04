import pytest
from PIL import Image

from anytool.local_server.utils.screenshot import ScreenshotHelper


@pytest.mark.parametrize("mode", ["RGB", "RGBA", "L"])
def test_identical_screenshots_have_similarity_one(tmp_path, mode):
    path = tmp_path / "image.png"
    Image.new(mode, (3, 2), 0).save(path)
    helper = ScreenshotHelper.__new__(ScreenshotHelper)
    assert helper.compare_screenshots(str(path), str(path)) == 1


def test_similarity_is_normalized_by_channel_intensity(tmp_path):
    helper = ScreenshotHelper.__new__(ScreenshotHelper)
    paths = [tmp_path / f"{shade}.png" for shade in (0, 128, 255)]
    for path, shade in zip(paths, (0, 128, 255)):
        Image.new("RGB", (3, 2), (shade,) * 3).save(path)
    assert helper.compare_screenshots(str(paths[0]), str(paths[2])) == 0
    assert helper.compare_screenshots(str(paths[0]), str(paths[1])) == pytest.approx(1 - 128 / 255)
