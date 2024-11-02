from spleeter.separator import Separator
import os
import sys
import librosa
import noisereduce as nr
import soundfile as sf  # This library is typically used for writing files in librosa
import argparse

def separate_audio(input_audio_path, output_directory):
    print(f"Input audio path: {input_audio_path}")
    print(f"Output directory: {output_directory}")
    print(f"File exists: {os.path.exists(input_audio_path)}")

    # Initialize the Separator with the 4stems model for more detailed separation
    separator = Separator('spleeter:4stems')
    
    # Perform separation
    try:
        separator.separate_to_file(input_audio_path, output_directory)
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

    base_name = os.path.basename(input_audio_path)
    file_name_without_extension = os.path.splitext(base_name)[0]
    
    # Paths for the separated files
    separated_folder = os.path.join(output_directory, file_name_without_extension)
    vocals_path = os.path.join(separated_folder, 'vocals.wav')

    # Apply noise reduction to the vocals track if needed
    vocals_audio, rate = librosa.load(vocals_path, sr=None)
    reduced_noise_vocals = nr.reduce_noise(y=vocals_audio, sr=rate)

    # Resample the audio to 16kHz
    vocals_audio_resampled = librosa.resample(reduced_noise_vocals, orig_sr=rate, target_sr=16000)

    # Write the processed and resampled vocals back to file (overwriting the original)
    sf.write(vocals_path, vocals_audio_resampled, 16000)

    # Return the path to the processed vocals file
    return vocals_path

if __name__ == '__main__':
    # Example code to get the input arguments
    input_audio_path = sys.argv[1] if len(sys.argv) > 1 else None
    output_directory = sys.argv[2] if len(sys.argv) > 2 else None

    # Validate the input audio path
    if input_audio_path is None or not os.path.isfile(input_audio_path):
        print(f"Error: The file {input_audio_path} does not exist.")
        sys.exit(1)

    # Call your function with validated paths
    vocals_path, instrumental_path = separate_audio(input_audio_path, output_directory)

'''
if __name__ == '__main__':
    # Hard-coded paths for testing
    input_audio_path = 'C:\\Users\\jcthi\Visual Studio Code\\YT - MP3\\audio_input\\songs-mp3\\SICKO MODE.mp3'  # Update this path
    output_directory = 'C:\\Users\\jcthi\Visual Studio Code\\YT - MP3\\audio_input\\vocals_instrumentals'  # Update this path

    # Ensure the hard-coded paths are directories that exist
    if not os.path.isfile(input_audio_path):
        print(f"Error: The file {input_audio_path} does not exist.")
        sys.exit(1)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Call the function with the hard-coded paths
    vocals_path, instrumental_path = separate_audio_and_label(input_audio_path, output_directory)
'''