"""Support for foobar2000 Music Player as media player.

via pyfoobar2k https://gitlab.com/ed0zer-projects/pyfoobar2k
And foobar2000 component foo_httpcontrol by oblikoamorale https://bitbucket.org/oblikoamorale/foo_httpcontrol
"""

from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, script
import homeassistant.util.dt as dt_util

try:
    from homeassistant.components.media_player import (
        PLATFORM_SCHEMA as MEDIA_PLAYER_PLATFORM_SCHEMA,
        MediaPlayerEntity,
    )
except ImportError:
    from homeassistant.components.media_player import (
        PLATFORM_SCHEMA as MEDIA_PLAYER_PLATFORM_SCHEMA,
        MediaPlayerDevice as MediaPlayerEntity,
    )

from pyfoobar2k import FoobarRemote

from homeassistant.components.media_player.const import (
    MediaPlayerEntityFeature,
    MediaType,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_TIMEOUT,
    CONF_USERNAME,
    STATE_IDLE,
    STATE_OFF,
    STATE_PAUSED,
    STATE_PLAYING,
    STATE_UNKNOWN,
)

REQUIREMENTS = ["pyfoobar2k==0.2.8"]

SCAN_INTERVAL = timedelta(seconds=5)
_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Foobar2000"
DEFAULT_PORT = "8888"
DEFAULT_TIMEOUT = 3
DEFAULT_VOLUME_STEP = 5
CONF_VOLUME_STEP = "volume_step"
CONF_TURN_ON_ACTION = "turn_on_action"
CONF_TURN_OFF_ACTION = "turn_off_action"

SUPPORT_FOOBAR_PLAYER = (
    MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.PREVIOUS_TRACK
    | MediaPlayerEntityFeature.STOP
    | MediaPlayerEntityFeature.SEEK
    | MediaPlayerEntityFeature.SHUFFLE_SET
    | MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.SELECT_SOURCE
)

MEDIA_PLAYER_PLATFORM_SCHEMA = MEDIA_PLAYER_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_USERNAME): cv.string,
        vol.Optional(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
        vol.Optional(CONF_VOLUME_STEP, default=DEFAULT_VOLUME_STEP): cv.positive_int,
        vol.Optional(CONF_TURN_ON_ACTION, default=None): cv.SCRIPT_SCHEMA,
        vol.Optional(CONF_TURN_OFF_ACTION, default=None): cv.SCRIPT_SCHEMA,
    }
)


def setup_platform(hass: HomeAssistant, config, add_devices, discovery_info=None):
    """Set up the Foobar Player platform."""

    name = config.get(CONF_NAME)
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    timeout = config.get(CONF_TIMEOUT)
    volume_step = config.get(CONF_VOLUME_STEP)
    turn_on_action = config.get(CONF_TURN_ON_ACTION)
    turn_off_action = config.get(CONF_TURN_OFF_ACTION)

    remote = FoobarRemote(host, port, username, password, timeout)

    add_devices(
        [FoobarDevice(hass, remote, name, volume_step, turn_on_action, turn_off_action)]
    )


class FoobarDevice(MediaPlayerEntity):
    """Representation of a Foobar2000 media player device.

    Attributes:
        _name (str): The name of the media player.
        _remote (object): The remote control interface for the media player.
        hass (object): Home Assistant instance.
        _volume (float): The current volume level of the media player.
        _track_name (str): The name of the currently playing track.
        _track_artist (str): The artist of the currently playing track.
        _track_album_name (str): The album name of the currently playing track.
        _track_duration (int): The duration of the currently playing track in seconds.
        _track_position (int): The current position of the track in seconds.
        _track_position_updated_at (datetime): The last time the track position was updated.
        _albumart (str): The URL of the album art for the currently playing track.
        _current_playlist (str): The name of the current playlist.
        _playlists (list): A list of available playlists.
        _shuffle (int): The shuffle mode status.
        _volume_step (int): The step size for volume adjustments.
        _selected_source (str): The currently selected source.
        _state (str): The current state of the media player.
        _base_url (str): The base URL for the remote control interface.
        _albumart_path (str): The path to the album art image.
        _turn_on_action (object): The script to execute when turning on the media player.
        _turn_off_action (object): The script to execute when turning off the media player.

    Methods:
        update(): Update the state and attributes of the media player.
        name(): Return the name of the device.
        state(): Return the state of the device.
        should_poll(): Return True if entity has to be polled for state.
        volume_level(): Return the volume level of the media player (0 to 1).
        is_volume_muted(): Return True if volume is muted.
        media_content_type(): Return the content type of current playing media.
        media_title(): Return the title of current playing track.
        media_artist(): Return the artist of current playing track.
        media_album_name(): Return the album name of current playing track.
        supported_features(): Return the supported features of the media player.
        turn_on(): Execute turn_on_action to turn on media player.
        turn_off(): Execute turn_off_action to turn off media player.
        media_play_pause(): Send the media player the command for play/pause.
        media_pause(): Send the media player the command for play/pause if playing.
        media_stop(): Send the media player the stop command.
        media_play(): Send the media player the command to play at the current playlist.
        media_previous_track(): Send the media player the command for previous track.
        media_next_track(): Send the media player the command for next track.
        set_volume_level(volume): Send the media player the command for setting the volume.
        volume_up(): Send the media player the command for volume up.
        volume_down(): Send the media player the command for volume down.
        mute_volume(mute): Mute the volume.
        media_position_updated_at(): Return the time when the position of the current playing media was valid.
        media_duration(): Return the duration of current playing media in seconds.
        media_position(): Return the position of current playing media in seconds.
        media_seek(position): Send the media player the command to seek in current playing media.
        media_image_url(): Return the image URL of current playing media.
        source(): Return the current source name.
        source_list(): Return the list of available input sources.
        select_source(source): Select input source.
        media_playlist(): Return the title of the playlist currently playing.
        set_shuffle(shuffle): Send the media player the command to enable/disable shuffle mode.
        shuffle(): Return True if shuffle is enabled.

    """

    def __init__(
        self,
        hass: HomeAssistant | None,
        remote,
        name,
        volume_step,
        turn_on_action=None,
        turn_off_action=None,
    ) -> None:
        """Initialize the FoobarDevice.

        :param hass: Home Assistant instance.
        :param remote: The remote control interface for the media player.
        :param name: The name of the media player.
        :param volume_step: The step size for volume adjustments.
        :param turn_on_action: The script to execute when turning on the media player.
        :param turn_off_action: The script to execute when turning off the media player.
        """

        self._name = name
        self._remote = remote
        self.hass = hass
        self._volume = 0.0
        self._track_name = ""
        self._track_artist = ""
        self._track_album_name = ""
        self._track_duration = 0
        self._track_position = 0
        self._track_position_updated_at = None
        self._albumart = ""
        self._current_playlist = ""
        self._playlists = []
        self._shuffle = 0
        self._volume_step = volume_step
        self._selected_source = None
        self._state = STATE_UNKNOWN
        self._base_url = self._remote.url
        self._albumart_path = ""
        # Script creation for the turn on/off config options
        if turn_on_action is not None:
            turn_on_action = script.Script(
                self.hass,
                turn_on_action,
                f"{self.name} turn ON script",
                self.async_update_ha_state(True),
            )
        if turn_off_action is not None:
            turn_off_action = script.Script(
                self.hass,
                turn_off_action,
                f"{self.name} turn OFF script",
                self.async_update_ha_state(True),
            )

        self._turn_on_action = turn_on_action
        self._turn_off_action = turn_off_action

    def update(self):
        """Update the state and attributes of the media player.

        This method retrieves the current state and attributes from the remote
        media player and updates the internal state and attributes accordingly.
        It handles different states such as playing, paused, idle, and off.
        Additionally, it updates the playlist information if available.

        Raises:
            Exception: If updating the state or sources fails, an error is logged
                       and the state is set to STATE_UNKNOWN.

        """
        try:
            info = self._remote.state()
            if info:
                if info["isPlaying"] == "1":
                    self._state = STATE_PLAYING
                elif info["isPaused"] == "1":
                    self._state = STATE_PAUSED
                else:
                    self._state = STATE_IDLE
            else:
                self._state = STATE_OFF
            self.schedule_update_ha_state()

            if self._state in [STATE_PLAYING, STATE_PAUSED]:
                self._track_name = info["title"]
                self._track_artist = info["artist"]
                self._track_album_name = info["album"]
                self._volume = int(info["volume"]) / 100
                self._shuffle = info["playbackorder"]
                self._track_duration = int(info["itemPlayingLen"])
                self._albumart_path = info["albumArt"]
                self._track_position = int(info["itemPlayingPos"])
                self._track_position_updated_at = dt_util.utcnow()

            if self._state in [STATE_PLAYING, STATE_PAUSED, STATE_IDLE]:
                sources_info = self._remote.playlist()
                if sources_info:
                    current_playlist_position = int(sources_info["playlistActive"])
                    playlists_raw = sources_info["playlists"]
                    self._current_playlist = playlists_raw[current_playlist_position][
                        "name"
                    ]
                    self._playlists = [item["name"] for item in playlists_raw]
                else:
                    _LOGGER.warning("Updating %s sources failed:", self._name)
        except (ConnectionError, TimeoutError, KeyError) as e:
            _LOGGER.error("Updating %s state failed: %s", self._name, e)
            self._state = STATE_UNKNOWN

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def should_poll(self):
        """Return True if entity has to be polled for state."""
        return True

    @property
    def volume_level(self):
        """Volume level of the media player (0 to 1)."""
        return float(self._volume)

    @property
    def is_volume_muted(self):
        """Return True if volume is muted."""
        return float(self._volume) == 0

    @property
    def media_content_type(self):
        """Content type of current playing media."""
        return MediaType.MUSIC

    @property
    def media_title(self):
        """Title of current playing track."""
        return self._track_name

    @property
    def media_artist(self):
        """Artist of current playing track."""
        return self._track_artist

    @property
    def media_album_name(self):
        """Album name of current playing track."""
        return self._track_album_name

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        supported_features = SUPPORT_FOOBAR_PLAYER
        if self._turn_on_action is not None:
            supported_features |= MediaPlayerEntityFeature.TURN_ON
        if self._turn_off_action is not None:
            supported_features |= MediaPlayerEntityFeature.TURN_OFF
        return supported_features

    def turn_on(self):
        """Execute turn_on_action to turn on media player."""
        if self._turn_on_action is not None:
            self._turn_on_action.run(variables={"entity_id": self.entity_id})
        else:
            _LOGGER.warning("Action turn_on requested but turn_on_action is none")

    def turn_off(self):
        """Execute turn_off_action to turn on media player."""
        if self._turn_off_action is not None:
            self._turn_off_action.run(variables={"entity_id": self.entity_id})
        else:
            _LOGGER.warning("Action turn_off requested but turn_off_action is none")

    def media_play_pause(self):
        """Send the media player the command for play/pause."""
        self._remote.cmd("PlayOrPause")

    def media_pause(self):
        """Send the media player the command for play/pause if playing."""
        if self._state == STATE_PLAYING:
            self._remote.cmd("PlayOrPause")

    def media_stop(self):
        """Send the media player the stop command."""
        self._remote.cmd("Stop")

    def media_play(self):
        """Send the media player the command to play at the current playlist."""
        self._remote.cmd("Start")

    def media_previous_track(self):
        """Send the media player the command for prev track."""
        self._remote.cmd("StartPrevious")

    def media_next_track(self):
        """Send the media player the command for next track."""
        self._remote.cmd("StartNext")

    def set_volume_level(self, volume):
        """Send the media player the command for setting the volume."""
        self._remote.cmd("Volume", int(volume * 100))

    def volume_up(self):
        """Send the media player the command for volume down."""
        self._remote.cmd("VolumeDelta", self._volume_step)

    def volume_down(self):
        """Send the media player the command for volume down."""
        self._remote.cmd("VolumeDelta", -self._volume_step)

    def mute_volume(self, mute):
        """Mute the volume."""
        self._remote.cmd("VolumeMuteToggle")

    @property
    def media_position_updated_at(self):
        """When was the position of the current playing media valid.

        Returns value from homeassistant.util.dt.utcnow().
        """
        return self._track_position_updated_at

    @property
    def media_duration(self):
        """Duration of current playing media in seconds."""
        return self._track_duration

    @property
    def media_position(self):
        """Position of current playing media in seconds."""
        if self._state in [STATE_PLAYING, STATE_PAUSED]:
            return self._track_position
        return None

    def media_seek(self, position):
        """Send the media player the command to seek in current playing media."""
        self._remote.cmd("SeekSecond", position)

    @property
    def media_image_url(self):
        """Image url of current playing media."""
        if "cover_not_available" not in self._albumart_path:
            self._albumart = f"{self._base_url}/{self._albumart_path}"
        return self._albumart

    @property
    def source(self):
        """Return  current source name."""
        return self._current_playlist

    @property
    def source_list(self):
        """List of available input sources."""
        return self._playlists

    def select_source(self, source):
        """Select input source."""
        playlists = self._remote.playlist()["playlists"]
        source_position = [
            index for index, item in enumerate(playlists) if item["name"] == source
        ][0]
        # ignoring first playlist in playlists index
        if source_position == 0:
            return
        if source_position is not None:
            self._remote.cmd("SwitchPlaylist", source_position)
            self._remote.cmd("Start", 0)
            self._current_playlist = source

    @property
    def media_playlist(self):
        """Title of Playlist currently playing."""
        return self._current_playlist

    def set_shuffle(self, shuffle):
        """Send the media player the command to enable/disable shuffle mode."""
        playback_order = 4 if shuffle else 0
        self._remote.cmd("PlaybackOrder", playback_order)

    @property
    def shuffle(self):
        """Boolean if shuffle is enabled."""
        return int(self._shuffle) == 4
