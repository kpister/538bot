import os
import warnings # suppress warning for awhile
import click
from piazza_api import Piazza
from html2text import HTML2Text

from chain import get_chain

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
    
    # Fetch several of the latest Piazza posts
    answer = None
    fetched_posts = course.iter_all_posts(limit=12) # fetched_posts is a generator
    list_posts = []
    for post in fetched_posts:
        list_posts.append(post)
        
    target_post = list_posts[10] # Pick the post that we want to answer
    if target_post['history'][0]['content'].lower() == 'gpt': # If the content of the question says "gpt," 
                                                              # this indicates that the user wants to use 
                                                              # this program to answer that quesition.
        html_question = target_post['history'][0]['subject'] # The subject of the post will be a question.
        text_question = HTML_2_TEXT.handle(html_question).strip()
        if verbose:
            print("Question:", text_question)
        answer = chain({"question": text_question}, return_only_outputs=True)
        if verbose:
            print("Answer:", answer)
        course._rpc.content_student_answer(target_post['id'], answer['answer'], 10000, False) # Post the answer to that question
    return answer

@click.command()
@click.option("--email", default="", help="Piazza username.")
@click.option("--password", default="", help="Piazza password.")
@click.option(
    "--network_id",
    default="lcguqjpvo0q39j",
    help="""Piazza course id (can be found in the URL: https://piazza.com/class/{network_id})
            (default is "lcguqjpvo0q39j" which is a course id of CS 538, Spring 2023)""",
)
@click.option(
    "--openai_api_key", default="", help="A key for OpenAI APIs."
)
def main(
    email: str, password: str, network_id: str, openai_api_key: str
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
    print("Initialize the program...")
    os.environ["OPENAI_API_KEY"] = openai_api_key

    piazza = Piazza()
    piazza.user_login(email=email, password=password)
    course = piazza.network(network_id)

    HTML_2_TEXT = HTML2Text()
    HTML_2_TEXT.ignore_links = True
    with warnings.catch_warnings(): # suppress warning for awhile
        warnings.simplefilter("ignore")
        chain = get_chain("cache")
    print("Done initialization!")
    
    print("""Type 'exit' to exit this program, 
          type anything to print questions/answers posted on Piazza, 
          type nothing (hitting enter) to just answer the questions""")
    while True:
        user_input = input()
        if user_input.lower() == "exit":
            print("Bye!")
            break
        else:
            print("Start answering...")
            verbose = (len(user_input) != 0)
            gpt_reply(course, chain, HTML_2_TEXT, verbose)
            print("Answered!")

if __name__ == "__main__":
    main()
