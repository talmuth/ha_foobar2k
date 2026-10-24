"""Test the foobar2000 media player platform."""

from homeassistant.components.media_player import DOMAIN as MP_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, STATE_PLAYING
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_component import async_update_entity
from homeassistant.setup import async_setup_component

ENTITY_ID = "media_player.foobar2000"


async def _setup(hass: HomeAssistant, **extra) -> None:
    config = {MP_DOMAIN: [{"platform": "foobar2000", "host": "foobar"} | extra]}
    assert await async_setup_component(hass, MP_DOMAIN, config)
    await hass.async_block_till_done()


async def test_setup_and_update(hass: HomeAssistant, mock_remote) -> None:
    """Entity is created from YAML and reflects the player state after a poll."""
    await _setup(hass)
    await async_update_entity(hass, ENTITY_ID)

    state = hass.states.get(ENTITY_ID)
    assert state.state == STATE_PLAYING
    assert state.attributes["media_title"] == "Song"
    assert state.attributes["media_artist"] == "Artist"
    assert state.attributes["volume_level"] == 0.5
    assert state.attributes["source_list"] == ["Default", "Rock"]


async def test_player_offline(hass: HomeAssistant, mock_remote) -> None:
    """No response from the player means off."""
    mock_remote.state.return_value = None
    await _setup(hass)
    await async_update_entity(hass, ENTITY_ID)

    assert hass.states.get(ENTITY_ID).state == "off"


async def test_services(hass: HomeAssistant, mock_remote) -> None:
    """Media player services map to foo_httpcontrol commands."""
    await _setup(hass)
    await async_update_entity(hass, ENTITY_ID)

    calls = [
        ("media_pause", {}, [("PlayOrPause",)]),
        ("media_stop", {}, [("Stop",)]),
        ("media_next_track", {}, [("StartNext",)]),
        ("volume_set", {"volume_level": 0.3}, [("Volume", 30)]),
        ("shuffle_set", {"shuffle": True}, [("PlaybackOrder", 4)]),
        ("media_seek", {"seek_position": 5}, [("SeekSecond", 5)]),
        ("select_source", {"source": "Rock"}, [("SwitchPlaylist", 1), ("Start", 0)]),
    ]
    for service, data, expected in calls:
        mock_remote.cmd.reset_mock()
        await hass.services.async_call(MP_DOMAIN, service, {ATTR_ENTITY_ID: ENTITY_ID} | data, blocking=True)
        assert [c.args for c in mock_remote.cmd.call_args_list] == expected, service
