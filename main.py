import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QDockWidget, QStatusBar, QWidget, \
    QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QStyleFactory, QSizePolicy, QSlider, QFileDialog, \
    QSpacerItem
from PyQt6.QtGui import QPixmap, QAction, QKeySequence, QPainter, QFont
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import QStandardPaths
from mutagen import File
from track_item_widget import TrackItemWidget
from clickable_slider import ClickableSlider
from player import Player


SONG_NAME_FONT = QFont("Dubai", 14)
AUDIO_EXTENSIONS = (".mp3", ".wav", ".flac", ".ogg", ".m4a")


class MainWindow(QMainWindow):

    def  __init__(self):
        super().__init__()

        self.player = Player()
        self.player.playback_state_changed.connect(self.update_play_pause_button)
        self.player.shuffle_state_changed.connect(self.update_shuffle_button)
        self.player.volume_state_changed.connect(self.update_volume_button)
        self.player.track_changed.connect(self.update_current_track)

        self.inicialize_ui()
        self.status_bar = QStatusBar()

        self.setStatusBar(self.status_bar)

        self.current_music_folder = ""
        self.track_paths_list = []


        with open("styles.css", "r") as file:
            style = file.read()
        self.setStyleSheet(style)
        

    def inicialize_ui(self):
        self.setGeometry(200,100,950,550)
        self.setMinimumHeight(188)
        self.setWindowTitle("Trek Music")
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
        self.player.duration_changed.connect(lambda dur: (self.slider.setRange(0, dur), self.slider.setEnabled(True)))
        self.player.position_changed.connect(lambda pos: self.slider.setValue(pos))
        self.slider.sliderMoved.connect(lambda pos: self.player.set_position(pos))

        self.track_name = QLabel()
        self.track_name.setFont(SONG_NAME_FONT)
        self.track_name.setObjectName("song_name")
        self.track_name.setMinimumWidth(136)
        self.track_name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        reproduction_buttons_container = self.generate_reproduction_buttons()

        self.volume_button = QPushButton()
        self.volume_button.setObjectName("volume_button")
        self.volume_button.clicked.connect(self.handle_volume_button_click)
        self.volume_button.setFixedSize(30, 30)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(self.player.audio_output.volume() * 100))  # Valor inicial
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setToolTip("Volume")
        self.volume_slider.valueChanged.connect(self.change_volume)

        # LAYOUT

        self.setCentralWidget(self.main_widget)

        main_layout = QVBoxLayout()
        self.main_widget.setLayout(main_layout)

        slider_hbox = QHBoxLayout()
        slider_hbox.setContentsMargins(7, 0, 7, 0)
        slider_hbox.addWidget(self.slider)
        slider_container = QWidget()
        slider_container.setLayout(slider_hbox)

        volume_layout = QHBoxLayout()
        volume_layout.setContentsMargins(0,0,0,0)
        volume_layout.addWidget(self.volume_button)
        volume_layout.addWidget(self.volume_slider)
        volume_container = QWidget()
        volume_container.setLayout(volume_layout)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0,0,0,0)

        bottom_layout.addWidget(self.track_name, 2)
        bottom_layout.addStretch()
        bottom_layout.addWidget(reproduction_buttons_container, 6)
        bottom_layout.addStretch()
        bottom_layout.addWidget(volume_container, 2)
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


    def generate_reproduction_buttons(self):

        # WIDGETS

        self.play_pause_button = QPushButton()
        self.play_pause_button.setObjectName("play_pause_button")
        self.play_pause_button.clicked.connect(self.handle_play_pause_click)
        self.play_pause_button.setEnabled(False)

        self.next_button = QPushButton()
        self.next_button.setObjectName("next_button")
        self.next_button.clicked.connect(lambda: self.player.next_track(auto=False))
        self.next_button.setEnabled(False)

        self.previous_button = QPushButton()
        self.previous_button.setObjectName("previous_button")
        self.previous_button.clicked.connect(self.player.previous_track)
        self.previous_button.setEnabled(False)

        self.ten_forward_button = QPushButton()
        self.ten_forward_button.setObjectName("ten_forward_button")
        self.ten_forward_button.clicked.connect(lambda: self.player.skip_seconds(10))
        self.ten_forward_button.setEnabled(False)

        self.ten_backward_button = QPushButton()
        self.ten_backward_button.setObjectName("ten_backward_button")
        self.ten_backward_button.clicked.connect(lambda: self.player.skip_seconds(-10))
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

        # LAYOUT

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

        return buttons_container


    def create_action(self):
        self.open_files_action = QAction("Open Files", self)
        self.open_files_action.setShortcut(QKeySequence("Ctrl+F"))
        self.open_files_action.setStatusTip("Open music files to add to the playlist")
        self.open_files_action.triggered.connect(self.open_files)

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
        open_menu.addAction(self.open_files_action)
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


    def open_files(self):
        initial_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.MusicLocation
        )

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select music files",
            initial_dir,
            "Audio Files (*.mp3 *.wav *.flac *.ogg *.m4a)"
        )

        if not files:
            return

        self._add_tracks(files)


    def open_folder(self):
        """Open a folder and add all music files, including those in subfolders."""
        initial_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.MusicLocation)
        folder = QFileDialog.getExistingDirectory(None, "Select a folder", initial_dir)
        if not folder:
            return

        track_paths_list = []

        # Walk through folder and subfolders
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(AUDIO_EXTENSIONS):
                    track_paths_list.append(os.path.join(root, file))

        self._add_tracks(track_paths_list)


    def _add_tracks(self, paths):
        paths = list(dict.fromkeys(paths))  # remove duplicates

        self.playlist.clear()
        self.track_paths_list.clear()

        for track_path in paths:
            audio = File(track_path)
            if audio is None or audio.info is None:
                continue

            duration_seconds = int(audio.info.length)
            duration_str = f"{duration_seconds // 60}:{duration_seconds % 60:02d}"

            item = QListWidgetItem()
            widget = TrackItemWidget(os.path.basename(track_path), duration_str, track_path)
            item.setSizeHint(widget.sizeHint())

            self.playlist.addItem(item)
            self.playlist.setItemWidget(item, widget)

            self.track_paths_list.append(track_path)

        if self.track_paths_list:
            self.player.set_tracks(self.track_paths_list)
            self.update_buttons_style()


    def handle_play_pause_click(self):
        self.player.play_pause()


    def update_play_pause_button(self, is_playing):
        if is_playing:
            self.play_pause_button.setStyleSheet(
                "image: url(./images/pause.png);"
                "padding: 10px 10px 10px 11px"
            )
        else:
            self.play_pause_button.setStyleSheet(
                "image: url(./images/play_enabled.png);"
                "padding: 8px 8px 8px 12px"
            )


    def handle_shuffle_click(self):
        self.player.toggle_shuffle()


    def update_shuffle_button(self, is_shuffle_on):
        if is_shuffle_on:
            self.shuffle_button.setStyleSheet("image: url(./images/shuffle_on.png)")
        else:
            self.shuffle_button.setStyleSheet("image: url(./images/shuffle_off.png)")


    def handle_repeat_click(self):
        self.player.toggle_repeat()
        self.repeat_button.setStyleSheet(f"image: url(./images/repeat_{self.player.repeat}.png);")


    def handle_volume_button_click(self):
        self.player.toggle_mute(self.volume_slider.value())


    def update_volume_button(self, is_muted):
        if is_muted:
            self.volume_button.setStyleSheet("image: url(./images/volume_off.png)")
        else:
            self.volume_button.setStyleSheet("image: url(./images/volume_on.png)")


    def change_volume(self, value):
        self.player.change_volume(value/100)


    def update_current_track(self, current_track):
        self.track_name.setText(Path(current_track).stem)
        self.highlight_current_track(current_track)


    def highlight_current_track(self, current_track):
        for i in range(self.playlist.count()):
            item = self.playlist.item(i)
            widget = self.playlist.itemWidget(item)

            if widget.track_path == current_track:
                widget.title_label.setGlowEnabled(enabled=True)
                widget.duration_label.setGlowEnabled(enabled=True)
            else:
                widget.title_label.setGlowEnabled(enabled=False)
                widget.duration_label.setGlowEnabled(enabled=False)


    def handle_track_double_click(self, item):
        widget = self.playlist.itemWidget(item)
        self.player.set_track_by_path(widget.track_path)


    def update_buttons_style(self):
        if self.track_paths_list is not None:
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