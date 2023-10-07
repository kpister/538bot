from piazza_api import Piazza
from html2text import HTML2Text

def fetch_piazza_posts(email: str, password: str, network_id: str = "lcguqjpvo0q39j", limit: int = 60):
    """
    Parameters
    ----------
    email : str
        email used to login Piazza
    password : str
        password used to login Piazza
    network_id : str
        Piazza course id (can be found in the URL: https://piazza.com/class/{network_id})
        (default is "lcguqjpvo0q39j" which is a course id of CS 538, Spring 2023)
    limit : int
        the number of Piazza posts that will be fetched (if the number is too high,
        Piazza might get unresponsive. -> might be able to fix this by fetching certain
        number of posts, then wait, then fetch another batch.)
    """
    piazza = Piazza()
    piazza.user_login(email=email, password=password)
    course = piazza.network(network_id)
    fetched_posts = course.iter_all_posts(limit=limit) # fetched_posts is a generator
    
    # convert a generator to a list
    list_posts = []
    for post in fetched_posts:
        list_posts.append(post)
        
    return list_posts 
    
def write_fetched_children_posts_to_file(post_replies, file, indent, HTML_2_TEXT):
    """
    Recursively write Piazza post replies to a file.
    
    Parameters
    ----------
    post_replies
        a list of dictionaries that contain Piazza replies of a given Piazza post/reply 
        (we can have a reply replying another reply.)
    file
        a file object that we will write our text to
    indent
        the number of indents used to indent a Piazza reply. 
        a reply to the original post = 1 indent
        a reply to the reply to the original post = 2 indents
        and so on
        Right now, this feature doesn't work yet.
    HTML_2_TEXT
        an object used to convert a HTML text to a normal text
    """
    indent = indent + 1
    for post_reply in post_replies: # The recursion ends when there is no more children post (post_replies is an empty list.).
        if "subject" in post_reply.keys():
            html_text = post_reply["subject"]
            # file.write(HTML_2_TEXT.handle(post_reply['subject']))
        else:
            # file.write(HTML_2_TEXT.handle(post_reply['history'][0]['content']))
            html_text = post_reply["history"][0]["content"]
        file.write("Nested Replies: " + str(indent))
        file.write(HTML_2_TEXT.handle(html_text))
        write_fetched_children_posts_to_file(post_reply["children"], file, indent, HTML_2_TEXT)

def write_fetched_posts_to_file(list_posts, post_file_name: str):
    """
    Write Piazza posts and their replies to a file.
    
    Parameters
    ----------
    list_posts
        a list of dictionaries that contain Piazza posts and their replies
    post_file_name : str
        name of the text file that will store the text of all Piazza posts and their replies
    """
    HTML_2_TEXT = HTML2Text()
    HTML_2_TEXT.ignore_links = True
    
    if not post_file_name.endswith(".txt"):
        print("Automatically add '.txt' extension to the file name...")
        post_file_name = post_file_name + ".txt"
        
    with open(post_file_name, "w") as file:
        for post in list_posts:
            file.write("-"*50 + "\n") # boundary between posts
            file.write("Subject\n")
            file.write(HTML_2_TEXT.handle(post["history"][0]["subject"])) # subject title of the question
            file.write("Content")
            file.write(HTML_2_TEXT.handle(post["history"][0]["content"])) # content of the question
            indent = 0 # indent the post replies
            write_fetched_children_posts_to_file(post["children"], file, indent, HTML_2_TEXT) 

if __name__ == "__main__":
    EMAIL = input("Please input your email used to login Piazza: ")
    PASSWORD = input("Please input your password used to login Piazza: ")
    post_file_name = input("Please input the name of the file that will be used to store Piazza posts and their replies (end with \'.txt\'): ")
    list_posts = fetch_piazza_posts(EMAIL, PASSWORD)
    write_fetched_posts_to_file(list_posts, post_file_name)      