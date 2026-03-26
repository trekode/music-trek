import sys
import os
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QDockWidget, QStatusBar, QTabWidget, \
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QFileDialog, QStyleFactory, QSizePolicy, QSlider, \
    QFrame
from PyQt6.QtGui import QPixmap, QAction, QKeySequence, QPainter, QColor, QPainterPath
from PyQt6.QtCore import Qt, QStandardPaths, QUrl, QSize
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from track_item_widget import TrackItemWidget
from mutagen.mp3 import MP3
from clickable_slider import ClickableSlider


class MainWindow(QMainWindow):

    def  __init__(self):
        super().__init__()

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.mediaStatusChanged.connect(self.media_status_changed)
        self.audio_output.setVolume(1.0)

        self.inicialize_ui()
        self.status_bar = QStatusBar()

        self.setStatusBar(self.status_bar)

        self.current_music_folder = ""
        self.original_track_list = []
        self.track_list = []
        self.current_track = None
        self.current_track_index = None

        self.is_playing = False
        self.is_shuffle_on = False
        self.repeat = "none"

        with open("styles.css", "r") as file:
            style = file.read()
        self.setStyleSheet(style)
        

    def inicialize_ui(self):
        self.setGeometry(200,100,700,550)
        self.setMinimumHeight(188)
        self.setWindowTitle("Music Player")
        self.generate_main_window()
        self.create_dock()
        self.create_action()
        self.create_menu()
        self.show()


    def generate_main_window(self):
        # WIDGETS

        self.main_widget = QWidget()

        self.player_image = QLabel()
        self.player_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.player_image.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.original_pixmap = QPixmap("./images/player_image.jpg")

        self.slider = ClickableSlider(Qt.Orientation.Horizontal, self)
        self.slider.setRange(0, 100)
        self.slider.setValue(0)
        self.slider.setEnabled(False)
        self.slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.slider.setFixedHeight(15)
        # self.slider.setMinimumWidth(100)
        self.player.durationChanged.connect(lambda dur: (self.slider.setRange(0, dur), self.slider.setEnabled(True)))
        self.player.positionChanged.connect(lambda pos: self.slider.setValue(pos))
        self.slider.sliderMoved.connect(lambda pos: self.player.setPosition(pos))

        self.play_pause_button = QPushButton()
        self.play_pause_button.setObjectName("play_pause_button")
        self.play_pause_button.clicked.connect(self.play_pause_track)
        self.play_pause_button.setEnabled(False)

        self.next_button = QPushButton()
        self.next_button.setObjectName("next_button")
        self.next_button.clicked.connect(lambda: self.next_track(auto=False))
        self.next_button.setEnabled(False)

        self.previous_button = QPushButton()
        self.previous_button.setObjectName("previous_button")
        self.previous_button.clicked.connect(self.previous_track)
        self.previous_button.setEnabled(False)

        self.ten_forward_button = QPushButton()
        self.ten_forward_button.setObjectName("ten_forward_button")
        self.ten_forward_button.clicked.connect(lambda: self.skip_seconds(10))
        self.ten_forward_button.setEnabled(False)

        self.ten_backward_button = QPushButton()
        self.ten_backward_button.setObjectName("ten_backward_button")
        self.ten_backward_button.clicked.connect(lambda: self.skip_seconds(-10))
        self.ten_backward_button.setEnabled(False)

        self.repeat_button = QPushButton()
        self.repeat_button.setObjectName("repeat_button")
        self.repeat_button.clicked.connect(self.handle_repeat_click)

        self.shuffle_button = QPushButton()
        self.shuffle_button.setObjectName("shuffle_button")
        self.shuffle_button.clicked.connect(self.handle_shuffle_click)

        self.play_pause_button.setFixedSize(50, 50)
        self.ten_forward_button.setFixedSize(42, 42)
        self.ten_backward_button.setFixedSize(42, 42)
        self.next_button.setFixedSize(38, 38)
        self.previous_button.setFixedSize(38, 38)
        self.shuffle_button.setFixedSize(30, 30)
        self.repeat_button.setFixedSize(30, 30)

        self.volume_button = QPushButton()
        self.volume_button.setObjectName("volume_button")
        self.volume_button.clicked.connect(self.handle_volume_button_click)
        self.volume_button.setFixedSize(30, 30)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(self.audio_output.volume() * 100))  # Valor inicial
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setToolTip("Volume")
        self.volume_slider.valueChanged.connect(self.change_volume)

        self.song_name = QLabel()
        self.song_name.setObjectName("song_name")
        self.song_name.setMinimumWidth(170)

        # LAYOUT

        self.setCentralWidget(self.main_widget)

        main_layout = QVBoxLayout()
        self.main_widget.setLayout(main_layout)

        slider_hbox = QHBoxLayout()
        slider_hbox.setContentsMargins(7, 0, 7, 0)
        slider_hbox.addWidget(self.slider)
        slider_container = QWidget()
        slider_container.setLayout(slider_hbox)

        buttons_hbox = QHBoxLayout()
        buttons_hbox.setContentsMargins(15, 8, 15, 8)
        buttons_hbox.setSpacing(5)

        buttons_hbox.addWidget(self.shuffle_button)
        buttons_hbox.addWidget(self.previous_button)
        buttons_hbox.addWidget(self.ten_backward_button)
        buttons_hbox.addWidget(self.play_pause_button)
        buttons_hbox.addWidget(self.ten_forward_button)
        buttons_hbox.addWidget(self.next_button)
        buttons_hbox.addWidget(self.repeat_button)

        buttons_container = QWidget()
        buttons_container.setObjectName("buttons_container")
        buttons_container.setLayout(buttons_hbox)

        volume_layout = QHBoxLayout()

        volume_layout.addWidget(self.volume_button, stretch=0)
        volume_layout.addWidget(self.volume_slider, stretch=1)
        volume_container = QWidget()
        volume_container.setLayout(volume_layout)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.song_name)
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(buttons_container)
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(volume_container)
        self.bottom_container = QWidget()
        self.bottom_container.setLayout(bottom_layout)

        image_container_layout = QHBoxLayout()
        image_container_layout.addWidget(self.player_image)
        image_container = QWidget()
        image_container.setContentsMargins(0,0,0,0)
        image_container.setLayout(image_container_layout)

        player_layout = QVBoxLayout()
        player_layout.setContentsMargins(0, 20, 0, 10)
        player_layout.setSpacing(0)
        player_layout.addWidget(image_container, stretch=1)
        player_layout.addWidget(slider_container, stretch=0)
        player_layout.addWidget(self.bottom_container, stretch=0)
        self.player_container = QWidget()
        self.player_container.setLayout(player_layout)

        main_layout.addWidget(self.player_container)


    def create_action(self):
        self.open_folder_action = QAction("Open Folder", self)
        self.open_folder_action.setShortcut(QKeySequence("Ctrl+O"))
        self.open_folder_action.setStatusTip("Open a folder with a playlist")
        self.open_folder_action.triggered.connect(self.open_folder)

        self.view_playlist_action = QAction("View Playlist", self, checkable=True)
        self.view_playlist_action.setShortcut(QKeySequence("Ctrl+L"))
        self.view_playlist_action.setStatusTip("Show/Hide Playlist")
        self.view_playlist_action.triggered.connect(self.view_playlist)
        self.view_playlist_action.setChecked(True)

        self.view_player_image_action = QAction("View Player Image", self, checkable=True)
        self.view_player_image_action.setShortcut(QKeySequence("Ctrl+I"))
        self.view_player_image_action.setStatusTip("Show/Hide Player Image")
        self.view_player_image_action.triggered.connect(self.view_player_image)
        self.view_player_image_action.setChecked(True)


    def create_menu(self):
        self.menuBar().setStyle(QStyleFactory.create("Fusion"))

        open_menu = self.menuBar().addMenu("Open")
        open_menu.addAction(self.open_folder_action)

        view_menu = self.menuBar().addMenu("View")
        view_menu.addAction(self.view_playlist_action)
        view_menu.addAction(self.view_player_image_action)


    def create_dock(self):
        self.playlist = QListWidget() 
        self.playlist.itemDoubleClicked.connect(self.handle_track_double_click)
        
        self.dock = QDockWidget()
        self.dock.setWindowTitle("Playlist")
        self.dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)

        self.dock.setWidget(self.playlist)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
        self.dock.visibilityChanged.connect(self.sync_view_playlist_action)

    
    def view_playlist(self):
        if self.view_playlist_action.isChecked():
            self.dock.show()
            self.update_pixmap()
        else:
            self.dock.hide()
            self.update_pixmap()


    def sync_view_playlist_action(self, visible):
        self.view_playlist_action.setChecked(visible)


    def view_player_image(self):
        if self.view_player_image_action.isChecked():
            self.player_image.show()
        else:
            self.player_image.hide()


    def open_folder(self):
        initial_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.MusicLocation)
        self.current_music_folder = QFileDialog.getExistingDirectory(None, "Select a folder", initial_dir)
        if not self.current_music_folder:
            return

        for file in os.listdir(self.current_music_folder):
            file_path = os.path.join(self.current_music_folder, file)

            if file_path.endswith(".mp3"):
                audio = MP3(file_path)
                duration_seconds = int(audio.info.length)
                duration_str = f"{duration_seconds // 60}:{duration_seconds % 60:02d}"
                item = QListWidgetItem()
                widget = TrackItemWidget(file, duration_str, file_path)
                item.setSizeHint(widget.sizeHint())
                self.playlist.addItem(item)
                self.playlist.setItemWidget(item, widget)

                self.original_track_list.append(file_path)
                self.track_list.append(file_path)

                if self.is_shuffle_on:
                    self.shuffle_tracks()

        self.current_track = self.track_list[0]
        self.song_name.setText(Path(self.current_track).stem)
        self.current_track_index = 0
        source = QUrl.fromLocalFile(self.current_track)
        self.player.setSource(source)
        self.update_buttons_style()
        self.player.play()
        self.is_playing = True
        self.change_play_pause_button_style("pause")
        self.highlight_current_track()


    # SLOT HANDLING

    def play_pause_track(self):
        if not self.player.source().isEmpty():
            if self.is_playing:
                self.player.pause()
                self.change_play_pause_button_style("play")
                self.is_playing = False
            else:
                self.player.play()
                self.change_play_pause_button_style("pause")
                self.is_playing = True


    def next_track(self, auto):
        if not self.track_list or self.current_track_index is None:
            return

        if self.repeat != "one":
            self.current_track_index += 1
            if self.current_track_index >= len(self.track_list):
                self.current_track_index = 0 # loop to the start
                if self.repeat == "none" and auto:
                    self.is_playing = False
                    self.change_play_pause_button_style("play")
                    return

        self.current_track = self.track_list[self.current_track_index]
        self.highlight_current_track()
        track_path = self.track_list[self.current_track_index]
        self.player.setSource(QUrl.fromLocalFile(track_path))
        if self.is_playing:
            self.player.play()


    def previous_track(self):
        if not self.track_list or self.current_track_index is None:
            return

        if self.repeat != "one":
            self.current_track_index -= 1
            if self.current_track_index < 0:
                self.current_track_index = len(self.track_list)-1 # loop to the end

        self.current_track = self.track_list[self.current_track_index]
        self.highlight_current_track()
        track_path = self.track_list[self.current_track_index]
        self.player.setSource(QUrl.fromLocalFile(track_path))
        if self.is_playing:
            self.player.play()


    def skip_seconds(self, seconds: int):
        current_pos = self.player.position()  # en ms
        new_pos = current_pos + (seconds * 1000)
        new_pos = max(0, min(new_pos, self.player.duration())) # Evitar que se salga de los límites
        self.player.setPosition(new_pos)


    def handle_shuffle_click(self):
        if self.current_track_index is not None:
            self.current_track = self.track_list[self.current_track_index]
        if self.is_shuffle_on:
            self.shuffle_button.setStyleSheet("image: url(./images/shuffle_off.png)")
            self.is_shuffle_on = False
            self.unshuffle_tracks()
        else:
            self.shuffle_button.setStyleSheet("image: url(./images/shuffle_on.png)")
            self.is_shuffle_on = True
            self.shuffle_tracks()

        if self.current_track:
            self.current_track_index = self.track_list.index(self.current_track)


    def shuffle_tracks(self):
        import random
        random.shuffle(self.track_list)


    def unshuffle_tracks(self):
        self.track_list = self.original_track_list.copy()


    def handle_repeat_click(self):
        repeat_modes = ["none", "all", "one"]
        current_index = repeat_modes.index(self.repeat)
        new_index = (current_index + 1) % len(repeat_modes)
        self.repeat = repeat_modes[new_index]
        self.repeat_button.setStyleSheet(f"image: url(./images/repeat_{self.repeat}.png);")


    def handle_volume_button_click(self):
        if self.audio_output.volume() > 0:
            self.audio_output.setVolume(0.0)
            self.volume_button.setStyleSheet("image: url(./images/volume_off.png)")

        else:
            self.audio_output.setVolume(self.volume_slider.value()/100)
            self.volume_button.setStyleSheet("image: url(./images/volume_on.png)")


    def change_volume(self, value):
        self.audio_output.setVolume(value / 100)
        self.volume_button.setStyleSheet("image: url(./images/volume_on.png)")


    def handle_track_double_click(self, item):
        widget = self.playlist.itemWidget(item)

        self.current_track = widget.track_path
        self.current_track_index = self.track_list.index(self.current_track)

        self.player.setSource(QUrl.fromLocalFile(self.current_track))
        self.player.play()
        self.is_playing = True
        self.change_play_pause_button_style("pause")
        self.highlight_current_track()


    def media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.next_track(auto=True)


    def highlight_current_track(self):
        for i in range(self.playlist.count()):
            item = self.playlist.item(i)
            widget = self.playlist.itemWidget(item)

            if widget.track_path == self.current_track:
                widget.title_label.setGlowEnabled(enabled=True)
                widget.duration_label.setGlowEnabled(enabled=True)
            else:
                widget.title_label.setGlowEnabled(enabled=False)
                widget.duration_label.setGlowEnabled(enabled=False)


    # STYLE SETTINGS

    def change_play_pause_button_style(self, style):
        if style == "play":
            if self.play_pause_button.isEnabled():
                self.play_pause_button.setStyleSheet(
                    "image: url(./images/play_enabled.png);"
                    "padding: 8px 8px 8px 12px"
                    )
            else:
                self.play_pause_button.setStyleSheet(
                    "image: url(./images/play_disabled.png);"
                    "padding: 8px 8px 8px 12px"
                    )

        elif style == "pause":
            self.play_pause_button.setStyleSheet(
                "image: url(./images/pause.png);"
                "padding: 10px 10px 10px 11px"
                )
        else:
            return


    def update_buttons_style(self):
        if not self.player.source().isEmpty():
            self.play_pause_button.setEnabled(True)
            self.next_button.setEnabled(True)
            self.next_button.setStyleSheet("image: url(./images/next_enabled.png)")
            self.previous_button.setEnabled(True)
            self.previous_button.setStyleSheet("image: url(./images/previous_enabled.png)")
            self.ten_forward_button.setEnabled(True)
            self.ten_forward_button.setStyleSheet("image: url(./images/ten_forward_enabled.png)")
            self.ten_backward_button.setEnabled(True)
            self.ten_backward_button.setStyleSheet("image: url(./images/ten_backward_enabled.png)")

        else:
            self.play_pause_button.setEnabled(False)
            self.next_button.setEnabled(False)
            self.previous_button.setEnabled(False)
            self.ten_forward_button.setEnabled(False)
            self.ten_backward_button.setEnabled(False)


    def update_pixmap(self):
        if self.original_pixmap.isNull():
            return

        container_size = self.player_container.size()

        # Escala la imagen manteniendo el aspect ratio, llenando el contenedor
        scaled = self.original_pixmap.scaled(container_size,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            # Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # Crear un pixmap del tamaño del contenedor
        final_pixmap = QPixmap(container_size)
        final_pixmap.fill(Qt.GlobalColor.transparent)  # fondo transparente

        # Coordenadas para centrar la imagen escalada
        x = (container_size.width() - scaled.width()) // 2
        y = (container_size.height() - scaled.height()) // 2

        # Pegar la imagen escalada centrada
        painter = QPainter(final_pixmap)
        painter.drawPixmap(x, y, scaled)
        painter.end()

        self.player_image.setPixmap(final_pixmap)

        # if scaled.width() > 300:
        #     self.slider.setFixedWidth(scaled.width())
        #     self.bottom_container.setFixedWidth(scaled.width())


    def showEvent(self, event):
        print("song_image size:", self.player_image.size())
        self.update_pixmap()
        super().showEvent(event)


    def resizeEvent(self, event):
        self.update_pixmap()
        super().resizeEvent(event)



if __name__ == '__main__':
    app  = QApplication(sys.argv)
    # app.setFont(QFont("Arial", 12))
    window = MainWindow()
    sys.exit(app.exec())