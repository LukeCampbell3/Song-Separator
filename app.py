import sys
import os
import shutil
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from main import separate_audio  # Importing the separate_audio function

class AudioSeparatorApp(QWidget):
    def __init__(self, parent=None):
        super(AudioSeparatorApp, self).__init__(parent)
        self.resize(600, 400)
        
        # Main layout setup
        layout = QVBoxLayout()
        
        # Select file button
        self.select_file_btn = QPushButton("Select Audio File")
        self.select_file_btn.setFixedSize(150, 50)
        self.select_file_btn.clicked.connect(self.select_file)
        
        # File path display
        self.file_path_display = QLineEdit()
        self.file_path_display.setReadOnly(True)
        
        # Select output folder button
        self.select_output_btn = QPushButton("Select Output Folder")
        self.select_output_btn.setFixedSize(150, 50)
        self.select_output_btn.clicked.connect(self.select_output_folder)
        
        # Output path display
        self.output_path_display = QLineEdit()
        self.output_path_display.setReadOnly(True)
        
        # Process button
        self.process_btn = QPushButton("Separate Audio")
        self.process_btn.setFixedSize(150, 50)
        self.process_btn.clicked.connect(self.process_audio)
        
        # Loading indicator
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()  # Hide initially, show only during processing
        
        # Status display
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        
        # Adding widgets to layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.select_file_btn)
        button_layout.addWidget(self.select_output_btn)
        button_layout.addWidget(self.process_btn)
        
        layout.addLayout(button_layout)
        layout.addWidget(self.file_path_display)
        layout.addWidget(self.output_path_display)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_display)
        
        self.setLayout(layout)
        self.setWindowTitle("Audio Separator App")
        
        # Initialize output path
        self.output_directory = None

    def select_file(self):
        # Open file dialog to select .mp3 or .wav files
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '', "Audio files (*.mp3 *.wav)")
        if fname:
            self.file_path_display.setText(fname)
            self.status_display.append(f"Selected file: {fname}")

    def select_output_folder(self):
        # Open file dialog to select an output directory
        output_dir = QFileDialog.getExistingDirectory(self, 'Select Output Folder')
        if output_dir:
            self.output_directory = output_dir
            self.output_path_display.setText(output_dir)
            self.status_display.append(f"Selected output folder: {output_dir}")

    def process_audio(self):
        input_audio_path = self.file_path_display.text()
        if not input_audio_path:
            self.status_display.append("Please select a file first.")
            return
        if not self.output_directory:
            self.status_display.append("Please select an output folder.")
            return
        
        # Show and start the progress bar
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)  # Indeterminate state (loader)
        
        # Run the separation process in a separate thread to avoid blocking the UI
        self.thread = QThread()
        self.worker = AudioProcessor(input_audio_path, self.output_directory)
        self.worker.moveToThread(self.thread)
        
        # Connect signals and slots
        self.thread.started.connect(self.worker.process)
        self.worker.finished.connect(self.on_process_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.start()
    
    def on_process_finished(self, result_message):
        self.progress_bar.hide()  # Hide the progress bar once done
        self.progress_bar.setRange(0, 100)  # Reset for next run
        self.status_display.append(result_message)
    
        # If an output folder path is provided in result_message, display it for the user
        if "Output saved to folder:" in result_message:
            output_path = result_message.split("Output saved to folder:")[-1].strip()
            self.status_display.append(f"Separated files are located at: {output_path}")

    
class AudioProcessor(QObject):
    finished = pyqtSignal(str)
    
    def __init__(self, input_audio_path, output_directory):
        super().__init__()
        self.input_audio_path = input_audio_path
        self.output_directory = output_directory
    
    def process(self):
        try:
            # Run the separation process
            file_path = separate_audio(self.input_audio_path, self.output_directory)
            
            # # Determine the song name to locate the output files
            # song_name = os.path.splitext(os.path.basename(self.input_audio_path))[0]
            # song_output_folder = os.path.join(self.output_directory, song_name)
            
            # Verify the separated files exist in the output folder
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Separated files not found at {file_path}")

            # Send path of the separated folder to the main application
            self.finished.emit(f"Audio separation complete. Output saved to folder: {file_path}")
        
        except FileNotFoundError as e:
            # Handle missing file error gracefully
            self.finished.emit(f"An error occurred: {str(e)}")
        
        except Exception as e:
            # Catch any other exceptions
            self.finished.emit(f"An error occurred: {str(e)}")


def main():
    app = QApplication(sys.argv)
    ex = AudioSeparatorApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
