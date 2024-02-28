import os
import time
import warnings  # suppress warning for awhile
import click
from piazza_api import Piazza
from piazza_api.network import FolderFilter
from html2text import HTML2Text

from chain import get_chain


def cache_check_set(id: str) -> bool:
    if os.path.exists("post_cache.txt"):
        with open("post_cache.txt") as w:
            ids = w.readlines()
    else:
        ids = []

    ids = list(map(lambda x: x.strip(), ids))
    if id in ids:
        return True

    ids.append(id)
    with open("post_cache.txt", "w") as w:
        w.write("\n".join(ids))
    return False


def gpt_reply(course, chain, HTML_2_TEXT, verbose: bool):
    """
    Fetch a question from Piazza, answer it, and post the answer back to Piazza.

    Parameters
    ----------
    course
        a Network object representing a Piazza course
        (https://github.com/hfaran/piazza-api/blob/develop/piazza_api/network.py#L46)
    chain
        a chain used to answer questions
    HTML_2_TEXT
        an object used to convert HTML into clean text
    verbose : bool
        if true, print a question posted on Piazza, and the answer of that question
        to a console
        (if false, any questions/answers will only show up on Piazza but not on the console)
    """
    # This is still a hacky way to fetch a question from Piazza and post the answer to it.
    posts = course.get_filtered_feed(FolderFilter(folder_name="gpt"))
    for post in posts["feed"]:
        # skip anything we have seen before
        if cache_check_set(post["id"]):
            continue

        subject = HTML_2_TEXT.handle(post["subject"]).strip()
        content = HTML_2_TEXT.handle(
            post["content_snipet"]
        ).strip()  # typo is intentional from library

        text_question = f"{subject}\nQuestion content: {content}"
        # The subject of the post will be a question.
        if verbose:
            print("Question:", text_question)
        answer = chain({"question": text_question}, return_only_outputs=True)
        if verbose:
            print("Answer:", answer)
        # Post the answer to that question
        course.create_followup(post, answer["answer"] + "\n-gpt on behalf of Kaiser")


@click.command()
@click.option("--email", default="", help="Piazza username")
@click.option("--password", default="", help="Piazza password")
@click.option(
    "--network_id",
    default="lrnlq1hx7ux6vw",
    help="Piazza course id (can be found in the URL: https://piazza.com/class/{network_id})",
)
@click.option("--openai_api_key", default="", help="A key for OpenAI APIs")
@click.option("--cache_dir", default="./cache", help="Folder that saved embeddings")
def main(
    email: str, password: str, network_id: str, openai_api_key: str, cache_dir: str
):
    """
    Automatically answer Piazza questions.

    Parameters
    ----------
    email : str
        an email address used to login Piazza account
    password : str
        a password used to login Piazza account
    network_id : str
        Piazza course id (can be found in the URL: https://piazza.com/class/{network_id})
        (default is "lcguqjpvo0q39j" which is a course id of CS 538, Spring 2023)
    openai_api_key : str
        a key for OpenAI APIs
    """
    print("Initializing the program...")
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
    email = email or os.environ["PIAZZA_USERNAME"]
    password = password or os.environ["PIAZZA_PASSWORD"]

    piazza = Piazza()
    piazza.user_login(email=email, password=password)
    course = piazza.network(network_id)

    HTML_2_TEXT = HTML2Text()
    HTML_2_TEXT.ignore_links = True
    with warnings.catch_warnings():  # suppress warning for awhile
        warnings.simplefilter("ignore")
    chain = get_chain(cache_dir)
    print("Done initialization!")

    while True:
        print("Checking for new posts to gpt folder...")
        gpt_reply(course, chain, HTML_2_TEXT, True)
        time.sleep(600)


if __name__ == "__main__":
    main()
