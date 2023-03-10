"""Load in audio data and transcribe it with Whisper."""
import os

import click
import whisper

from chain import get_chain


def transcribe_audio_data(filename: str):
    """Transcribe audio data."""
    print("Transcribing audio data...")

    whisper_model_version = "base"  # one of "base", "small", "medium", "large"

    if not os.path.exists(filename):
        raise FileNotFoundError(f"{filename} does not exist.")

    whisper_model = whisper.load_model(whisper_model_version)

    # TODO use a synopsis of the lecture itself?
    results = whisper_model.transcribe(
        filename,
        initial_prompt="This is a class on functional programming.",
        word_timestamps=True,
    )

    # results is dictionary containing the resulting text ("text") and segment-level details ("segments"), and
    # the spoken language ("language"), which is detected when `decode_options["language"]` is None.

    # TODO parse the dictionary


def answer_questions(question: str):
    """Answer questions."""
    print("Answering questions...")
    print(get_chain()({"question": question}, return_only_outputs=True))


@click.command()
@click.option("--transcribe", default="", help="Transcribe audio data.")
@click.option("--question", default="", help="Answer questions.")
def main(transcribe: str, question: str):
    if transcribe:
        transcribe_audio_data(transcribe)

    if question:
        answer_questions(question)


if __name__ == "__main__":
    main()
