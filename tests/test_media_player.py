"""Test the foobar2000 media player platform."""

import logging

from homeassistant.components.media_player import DOMAIN as MP_DOMAIN
from homeassistant.components.media_player import MediaPlayerEntityFeature
from homeassistant.const import ATTR_ENTITY_ID, STATE_PLAYING
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_component import async_update_entity
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import async_mock_service
import requests

from .conftest import STATE_PLAYING as PLAYING_INFO

ENTITY_ID = "media_player.foobar2000"


async def _setup(hass: HomeAssistant, **extra) -> None:
    config = {MP_DOMAIN: [{"platform": "foobar2000", "host": "foobar"} | extra]}
    assert await async_setup_component(hass, MP_DOMAIN, config)
    await hass.async_block_till_done()


async def test_setup_and_update(hass: HomeAssistant, mock_remote) -> None:
    """Entity is created from YAML and reflects the player state right away."""
    await _setup(hass)

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


async def test_no_turn_on_off_without_actions(hass: HomeAssistant, mock_remote) -> None:
    """Turn on/off are only supported when the corresponding action is configured."""
    await _setup(hass)

    features = hass.states.get(ENTITY_ID).attributes["supported_features"]
    assert not features & MediaPlayerEntityFeature.TURN_ON
    assert not features & MediaPlayerEntityFeature.TURN_OFF


async def test_turn_on_off_actions(hass: HomeAssistant, mock_remote) -> None:
    """Turn on/off run the configured scripts with the entity_id variable."""
    calls = async_mock_service(hass, "test", "power")
    await _setup(
        hass,
        turn_on_action={"action": "test.power", "data": {"on": True, "entity": "{{ entity_id }}"}},
        turn_off_action={"action": "test.power", "data": {"on": False, "entity": "{{ entity_id }}"}},
    )

    features = hass.states.get(ENTITY_ID).attributes["supported_features"]
    assert features & MediaPlayerEntityFeature.TURN_ON
    assert features & MediaPlayerEntityFeature.TURN_OFF

    for service in ("turn_on", "turn_off"):
        await hass.services.async_call(MP_DOMAIN, service, {ATTR_ENTITY_ID: ENTITY_ID}, blocking=True)
    await hass.async_block_till_done()

    assert [c.data for c in calls] == [{"on": True, "entity": ENTITY_ID}, {"on": False, "entity": ENTITY_ID}]


async def test_unique_id(hass: HomeAssistant, entity_registry: er.EntityRegistry, mock_remote) -> None:
    """A configured unique_id registers the entity so it can be managed from the UI."""
    await _setup(hass, unique_id="living_room")

    entry = entity_registry.async_get(ENTITY_ID)
    assert entry is not None
    assert entry.unique_id == "living_room"


async def test_no_unique_id(hass: HomeAssistant, entity_registry: er.EntityRegistry, mock_remote) -> None:
    """Without unique_id the entity isn't registered, as before."""
    await _setup(hass)

    assert hass.states.get(ENTITY_ID) is not None
    assert entity_registry.async_get(ENTITY_ID) is None


def _our_logs(caplog, text):
    return [r for r in caplog.records if r.name == "custom_components.foobar2000.media_player" and text in r.message]


async def test_offline_logged_once(hass: HomeAssistant, mock_remote, caplog) -> None:
    """Going offline and coming back are each logged once, not on every poll."""
    await _setup(hass)

    mock_remote.state.return_value = None
    for _ in range(3):
        await async_update_entity(hass, ENTITY_ID)
    assert hass.states.get(ENTITY_ID).state == "off"
    assert len(_our_logs(caplog, "is not responding")) == 1

    mock_remote.state.return_value = PLAYING_INFO
    for _ in range(2):
        await async_update_entity(hass, ENTITY_ID)
    assert hass.states.get(ENTITY_ID).state == STATE_PLAYING
    assert len(_our_logs(caplog, "is responding again")) == 1


async def test_bad_response_logged_once(hass: HomeAssistant, mock_remote, caplog) -> None:
    """A non-JSON response (template not installed) logs one hint and leaves the state unknown."""
    mock_remote.state.side_effect = requests.exceptions.JSONDecodeError("Expecting value", "<html>", 0)
    await _setup(hass)
    await async_update_entity(hass, ENTITY_ID)

    assert hass.states.get(ENTITY_ID).state == "unknown"
    logs = _our_logs(caplog, "pyfoobar2k template")
    assert len(logs) == 1
    assert logs[0].levelno == logging.ERROR


async def test_pyfoobar2k_poll_errors_demoted(hass: HomeAssistant, caplog) -> None:
    """pyfoobar2k's per-poll connection errors are demoted; command errors are kept."""
    lib_logger = logging.getLogger("pyfoobar2k.foobarhttp")
    with caplog.at_level(logging.INFO):
        lib_logger.error("Fetching player state failed: %s", "refused")
        lib_logger.error("Sending command to player failed: %s", "refused")

    errors = [r.getMessage() for r in caplog.records if r.name == lib_logger.name and r.levelno >= logging.ERROR]
    assert errors == ["Sending command to player failed: refused"]
