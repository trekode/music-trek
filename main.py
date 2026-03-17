import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QDockWidget, QStatusBar, QTabWidget, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QFileDialog, QStyleFactory, QSizePolicy, QSlider
from PyQt6.QtGui import QPixmap, QAction, QKeySequence, QPainter, QColor
from PyQt6.QtCore import Qt, QStandardPaths, QUrl
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
        tab_bar = QTabWidget(self)
        self.player_container = QWidget()
        self.settings_container = QWidget()
        tab_bar.addTab(self.player_container, "Player")
        tab_bar.addTab(self.settings_container, "Settings")

        self.generate_player_tab()
        self.generate_settings_tab()

        tab_h_box = QHBoxLayout()
        tab_h_box.addWidget(tab_bar)

        main_container = QWidget()
        main_container.setLayout(tab_h_box)
        self.setCentralWidget(main_container)
        

    def generate_player_tab(self):
        player_vbox = QVBoxLayout()
        buttons_hbox = QHBoxLayout()

        self.song_image = QLabel()
        self.song_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.song_image.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.original_pixmap = QPixmap("./images/player_image.jpg")

        self.shuffle_button = QPushButton()
        self.shuffle_button.setObjectName("shuffle_button")
        self.shuffle_button.clicked.connect(self.handle_shuffle_click)

        previous_button = QPushButton()
        previous_button.setObjectName("previous_button")
        previous_button.clicked.connect(self.previous_track)

        self.play_pause_button = QPushButton()
        self.play_pause_button.setObjectName("play_pause_button")
        self.play_pause_button.clicked.connect(self.play_pause_track)

        next_button = QPushButton()
        next_button.setObjectName("next_button")
        next_button.clicked.connect(lambda: self.next_track(auto=False))

        self.repeat_button = QPushButton()
        self.repeat_button.setObjectName("repeat_button")
        self.repeat_button.clicked.connect(self.handle_repeat_click)

        self.shuffle_button.setFixedSize(40,40)
        previous_button.setFixedSize(40,40)
        self.play_pause_button.setFixedSize(50,50)
        next_button.setFixedSize(40,40)
        self.repeat_button.setFixedSize(40,40)

        buttons_hbox.addWidget(self.shuffle_button)
        buttons_hbox.addWidget(previous_button)
        buttons_hbox.addWidget(self.play_pause_button)
        buttons_hbox.addWidget(next_button)
        buttons_hbox.addWidget(self.repeat_button)

        buttons_container = QWidget()
        buttons_container.setLayout(buttons_hbox)

        self.slider = ClickableSlider(Qt.Orientation.Horizontal, self)
        self.slider.setRange(0, 100)
        self.slider.setValue(0)
        self.slider.setEnabled(False)
        self.slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.slider.setFixedHeight(15)
        self.player.durationChanged.connect(lambda dur: (self.slider.setRange(0, dur), self.slider.setEnabled(True)))
        self.player.positionChanged.connect(lambda pos: self.slider.setValue(pos))
        self.slider.sliderMoved.connect(lambda pos: self.player.setPosition(pos))

        player_vbox.addWidget(self.song_image, stretch=1)
        player_vbox.addWidget(self.slider)
        player_vbox.addWidget(buttons_container, stretch=0)

        self.player_container.setLayout(player_vbox)


    def generate_settings_tab(self):
        settings_layout = QVBoxLayout()
        volume_layout = QHBoxLayout()

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)       # 0% a 100%
        self.volume_slider.setValue(int(self.audio_output.volume() * 100))  # Valor inicial
        self.volume_slider.setFixedWidth(120)      # opcional, para que no quede gigante
        self.volume_slider.setToolTip("Volume")
        self.volume_slider.valueChanged.connect(self.change_volume)

        volume_label = QLabel("Volume")
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        volume_container = QWidget()
        volume_container.setLayout(volume_layout)

        settings_layout.addWidget(volume_container)
        settings_layout.addStretch()

        self.settings_container.setLayout(settings_layout)


    def create_action(self):
        self.view_playlist_action = QAction("View Playlist", self, checkable=True)
        self.view_playlist_action.setShortcut(QKeySequence("Ctrl+L"))
        self.view_playlist_action.setStatusTip("Show/Hide Playlist")
        self.view_playlist_action.triggered.connect(self.view_playlist)
        self.view_playlist_action.setChecked(True)

        self.open_folder_action = QAction("Open Folder", self)
        self.open_folder_action.setShortcut(QKeySequence("Ctrl+O"))
        self.open_folder_action.setStatusTip("Open a folder with a playlist")
        self.open_folder_action.triggered.connect(self.open_folder)


    def create_menu(self):
        self.menuBar().setStyle(QStyleFactory.create("Fusion"))

        open_menu = self.menuBar().addMenu("Open")
        open_menu.addAction(self.open_folder_action)

        view_menu = self.menuBar().addMenu("View")
        view_menu.addAction(self.view_playlist_action)


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
        else:
            self.dock.hide()


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
        self.current_track_index = 0
        source = QUrl.fromLocalFile(self.current_track)
        self.player.setSource(source)
        self.player.play()
        self.is_playing = True
        self.change_play_pause_button_style("pause")
        self.highlight_current_track()

    
    def sync_view_playlist_action(self, visible):
        self.view_playlist_action.setChecked(visible)


    def update_pixmap(self):
        if self.original_pixmap.isNull():
            return

        container_size = self.player_container.size()
        
        # Escala la imagen manteniendo el aspect ratio, llenando el contenedor
        scaled = self.original_pixmap.scaled(
            container_size,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
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
        
        self.song_image.setPixmap(final_pixmap)


    def showEvent(self, event):
        self.update_pixmap()
        super().showEvent(event)

    
    def resizeEvent(self, event):
        self.update_pixmap()
        super().resizeEvent(event)


    # SLOT HANDLING

    def change_play_pause_button_style(self, style):
        if style == "play":
            self.play_pause_button.setStyleSheet(
                "image: url(./images/play.png);"
                "padding: 8px 8px 8px 12px"
                )
        elif style == "pause":
            self.play_pause_button.setStyleSheet(
                "image: url(./images/pause.png);"
                "padding: 10px 10px 10px 11px"
                )
        else:
            return


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


    def handle_shuffle_click(self):
        if self.current_track_index is not None:
            self.current_track = self.track_list[self.current_track_index]
        if self.is_shuffle_on:
            self.shuffle_button.setStyleSheet("image: url(./images/shuffle_off.png);")
            self.is_shuffle_on = False
            self.unshuffle_tracks()
        else:
            self.shuffle_button.setStyleSheet("image: url(./images/shuffle_on.png);")
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


    def change_volume(self, value):
        self.audio_output.setVolume(value / 100)  # QAudioOutput espera un float entre 0 y 1



if __name__ == '__main__':
    app  = QApplication(sys.argv)
    # app.setFont(QFont("Arial", 12))
    window = MainWindow()
    sys.exit(app.exec())