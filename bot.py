"""Load in audio data and transcribe it with Whisper."""
import os
from pathlib import Path

import click
import whisper

from chain import get_chain


def transcribe_audio_data(audio_filename: str, transcription_folder: str):
    """Transcribe audio data."""
    print("Transcribing audio data...")

    whisper_model_version = "base"  # one of "base", "small", "medium", "large"

    if not os.path.exists(audio_filename):
        raise FileNotFoundError(f"{audio_filename} does not exist.")

    whisper_model = whisper.load_model(whisper_model_version)

    # TODO use a synopsis of the lecture itself?
    results = whisper_model.transcribe(
        audio_filename,
        initial_prompt="This is a class on functional programming.",
        word_timestamps=True,
    )

    # results is dictionary containing the resulting text ("text") and segment-level details ("segments"), and
    # the spoken language ("language"), which is detected when `decode_options["language"]` is None.

    # TODO parse the dictionary
    transcription_filename = os.path.splitext(audio_filename)[0] + ".txt"
    Path(transcription_folder).mkdir(exist_ok=True)

    with open(os.path.join(transcription_folder, transcription_filename), "w") as file:
        file.write(results['text'])


def answer_questions(question: str, transcription_folder: str):
    """Answer questions."""
    print("Answering questions...")
    print(get_chain(transcription_folder)({"question": question}, return_only_outputs=True))


@click.command()
@click.option("--audio_filename", default="", help="Audio file to be transcribed.")
@click.option("--question", default="", help="Answer questions.")
@click.option("--transcription_folder", default="transcriptions", help="Folder to save transcribed audio recordings.")
def main(audio_filename: str, transcription_folder: str, question: str):
    if audio_filename:
        transcribe_audio_data(audio_filename, transcription_folder)

    if question:
        answer_questions(question, transcription_folder)


if __name__ == "__main__":
    main()
