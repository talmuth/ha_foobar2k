"""Global fixtures for foobar2000 integration."""

from unittest.mock import MagicMock, patch

import pytest

# Import before the hass fixture mounts pytest-homeassistant-custom-component's own
# testing_config/custom_components onto sys.path, which would otherwise shadow ours.
import custom_components.foobar2000  # noqa: F401

pytest_plugins = "pytest_homeassistant_custom_component"

STATE_PLAYING = {
    "isPlaying": "1",
    "isPaused": "0",
    "title": "Song",
    "artist": "Artist",
    "album": "Album",
    "volume": "50",
    "playbackorder": "0",
    "itemPlayingLen": "300",
    "albumArt": "albumart/1.jpg",
    "itemPlayingPos": "10",
}

PLAYLISTS = {
    "playlistActive": "0",
    "playlists": [{"name": "Default"}, {"name": "Rock"}],
}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations in Home Assistant."""
    yield


@pytest.fixture
def mock_remote():
    """Patch pyfoobar2k.FoobarRemote with a mock reporting a playing track."""
    remote = MagicMock()
    remote.url = "http://foobar:8888/pyfoobar2k"
    remote.state.return_value = STATE_PLAYING
    remote.playlist.return_value = PLAYLISTS
    with patch("pyfoobar2k.FoobarRemote", return_value=remote):
        yield remote
