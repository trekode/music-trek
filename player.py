import random
from PyQt6.QtCore import QObject, pyqtSignal, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput


class Player(QObject):
    playback_state_changed = pyqtSignal(bool)  # True if it's playing
    track_changed = pyqtSignal(str)  # Emits current track path
    playlist_changed = pyqtSignal(list)  # Because shuffle/unshuffle
    shuffle_state_changed = pyqtSignal(bool)  # True if shuffle is on
    volume_state_changed = pyqtSignal(bool)  # True if volume is mute
    duration_changed = pyqtSignal(int)  # Duración del track en ms
    position_changed = pyqtSignal(int)  # Posición actual en ms


    def __init__(self):
        super().__init__()

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.70)

        self.original_track_list = []
        self.track_list = []
        self.current_track_index = None

        self.is_playing = False
        self.is_muted = False
        self.is_shuffle_on = False
        self.repeat = "none"  # none, all, one

        self.player.mediaStatusChanged.connect(self._media_status_changed)
        self.player.positionChanged.connect(self.position_changed.emit)
        self.player.durationChanged.connect(self.duration_changed.emit)


    # -------------------- TRACK LOADING --------------------

    def set_tracks(self, track_paths: list):
        self.original_track_list = track_paths.copy()
        self.track_list = track_paths.copy()
        if self.track_list:
            if self.is_shuffle_on:
                self.shuffle_tracks()

            self.current_track_index = 0
            self.load_current_track()
            self.play()


    def load_current_track(self):
        if self.current_track_index is not None:
            current_track_path = self.get_current_track_path()
            source = QUrl.fromLocalFile(current_track_path)
            self.player.setSource(source)
            self.track_changed.emit(current_track_path)


    # -------------------- REPRODUCTION CONTROL  --------------------

    def play(self):
        if self.player.source().isEmpty():
            return
        self.player.play()
        self.is_playing = True
        self.playback_state_changed.emit(self.is_playing)


    def pause(self):
        self.player.pause()
        self.is_playing = False
        self.playback_state_changed.emit(self.is_playing)


    def play_pause(self):
        if self.is_playing:
            self.pause()
        else:
            self.play()


    def next_track(self, auto=False):
        if not self.track_list or self.current_track_index is None:
            return

        if self.repeat != "one":
            self.current_track_index += 1
            if self.current_track_index >= len(self.track_list):
                self.current_track_index = 0
                if self.repeat == "none" and auto:
                    self.pause()
                    return

        self.load_current_track()
        if self.is_playing:
            self.player.play()


    def previous_track(self):
        if not self.track_list or self.current_track_index is None:
            return

        if self.repeat != "one":
            self.current_track_index -= 1
            if self.current_track_index < 0:
                self.current_track_index = len(self.track_list)-1

        self.load_current_track()
        if self.is_playing:
            self.player.play()


    def skip_seconds(self, seconds: int):
        if self.player.duration() <= 0:
            return
        new_pos = self.player.position() + (seconds * 1000)
        new_pos = max(0, min(new_pos, self.player.duration())) # Evitar que se salga de los límites
        self.player.setPosition(new_pos)


    def set_track_by_path(self, track_path: str):
        if track_path in self.track_list:
            self.current_track_index = self.track_list.index(track_path)
            self.player.setSource(QUrl.fromLocalFile(track_path))
            self.play()
            self.track_changed.emit(track_path)


    # -------------------- SHUFFLE / REPEAT --------------------

    def toggle_shuffle(self):
        self.is_shuffle_on = not self.is_shuffle_on
        self.shuffle_state_changed.emit(self.is_shuffle_on)

        if not self.track_list:
            return

        if self.is_shuffle_on:
            self.shuffle_tracks()

        else:
            self.unshuffle_tracks()

        self.playlist_changed.emit(self.track_list)


    def shuffle_tracks(self):
        current_track = None

        if self.current_track_index is not None:
            current_track = self.track_list[self.current_track_index]

        random.shuffle(self.track_list)

        if current_track:
            self.current_track_index = self.track_list.index(current_track)


    def unshuffle_tracks(self):
        if self.current_track_index is not None:
            current_track = self.track_list[self.current_track_index]
            self.track_list = self.original_track_list.copy()
            self.current_track_index = self.track_list.index(current_track)


    def toggle_repeat(self):
        repeat_modes = ["none", "all", "one"]
        current_index = repeat_modes.index(self.repeat)
        new_index = (current_index + 1) % len(repeat_modes)
        self.repeat = repeat_modes[new_index]


    # -------------------- VOLUME --------------------

    def toggle_mute(self, slider_value: float):
        if self.audio_output.volume() > 0:
            self.audio_output.setVolume(0.0)
            self.is_muted = True
        else:
            self.audio_output.setVolume(slider_value/100)
            self.is_muted = False

        self.volume_state_changed.emit(self.is_muted)


    def change_volume(self, value):
        self.is_muted = False
        self.audio_output.setVolume(value)
        self.volume_state_changed.emit(self.is_muted)


    # ----------------SIGNALS / INTERNAL CALLBACKS  --------------------

    def _media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.next_track(auto=True)


    # -------------------- UTILITIES --------------------

    def get_current_track_path(self):
        if self.current_track_index is not None:
            return self.track_list[self.current_track_index]
        return None


    # ---------------------------------------------------------

    def set_position(self, pos: int):
        self.player.setPosition(pos)