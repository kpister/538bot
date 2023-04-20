import os
import warnings # suppress warning for awhile
from piazza_api import Piazza
from html2text import HTML2Text

from chain import get_chain

def gpt_reply(course, chain, HTML_2_TEXT, verbose):
    answer = None
    fetched_posts = course.iter_all_posts(limit=12) # fetched_posts is a generator
    list_posts = []
    for post in fetched_posts:
        list_posts.append(post)
        
    target_post = list_posts[10]
    if target_post['history'][0]['content'].lower() == 'gpt':
        html_question = target_post['history'][0]['subject']
        text_question = HTML_2_TEXT.handle(html_question).strip()
        if verbose:
            print("Question:", text_question)
        answer = chain({"question": text_question}, return_only_outputs=True)
        if verbose:
            print("Answer:", answer)
        course._rpc.content_student_answer(target_post['id'], answer['answer'], 10000, False)
    return answer

def main():
    print("Initialize the program...")
    EMAIL = "rattanakornp@wisc.edu" # Piazza username
    PASSWORD = "87lemons" # Piazza password
    network_id = "lcguqjpvo0q39j" # Course CS 538
    OPENAI_API_KEY = 
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

    piazza = Piazza()
    piazza.user_login(email=EMAIL, password=PASSWORD)
    course = piazza.network(network_id)

    HTML_2_TEXT = HTML2Text()
    HTML_2_TEXT.ignore_links = True
    with warnings.catch_warnings(): # suppress warning for awhile
        warnings.simplefilter("ignore")
        chain = get_chain("cache")
    print("Done initialization!")
    
    while True:
        user_input = input()
        if len(user_input) == 0:
            print("Start answering...")
            gpt_reply(course, chain, HTML_2_TEXT, False)
            print("Answered!")
        elif user_input.lower() == "exit":
            print("Bye!")
            break
        else:
            gpt_reply(course, chain, HTML_2_TEXT, True)
            print("Answered!")

if __name__ == "__main__":
    main()
