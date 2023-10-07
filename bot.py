"""Load in audio data and transcribe it with Whisper."""
import os
from pathlib import Path

import click
import whisper

from chain import get_chain

os.environ["TOKENIZERS_PARALLELISM"] = "false"


def transcribe_audio_data(audio_filename: str, transcription_folder: str):
    """
    Transcribe audio data.
    
    Parameters
    ----------
    audio_filename : str
        audio file to be transcribed
    transcription_folder : str
        folder into which transcribed text will be placed 
    """
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
        file.write(results["text"])


def answer_questions(question: str, cache_dir: str):
    """
    Answer questions.
    
    Parameters
    ----------
    question : str
        question to be answered
    cache_dir : str
        directory of a vector database
    """
    print("Answering questions...")
    chain = get_chain(cache_dir)
    print(chain({"question": question}, return_only_outputs=True))


@click.command()
@click.option("--audio_filename", default="", help="Audio file to be transcribed.")
@click.option("--question", default="", help="Answer questions.")
@click.option(
    "--transcription_folder",
    default="transcriptions",
    help="Folder to save transcribed audio recordings.",
)
@click.option(
    "--cache_folder", default="./cache", help="Folder to save cached embeddings."
)
def main(
    audio_filename: str, transcription_folder: str, question: str, cache_folder: str
):
    """
    Parameters
    ----------
    audio_filename : str
        audio file to be transcribed
    transcription_folder : str
        folder into which transcribed text will be placed 
    question : str
        question to be answered
    cache_dir : str
        directory of a vector database
    """
    if audio_filename:
        transcribe_audio_data(audio_filename, transcription_folder)

    if question:
        answer_questions(question, cache_folder)


if __name__ == "__main__":
    main()
