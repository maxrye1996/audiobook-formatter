import os
import re
import requests
import urllib
from json import load
from mutagen.easyid3 import EasyID3


def get_author(title, config):
    details = requests.get(
        f"https://www.googleapis.com/books/v1/volumes?q={urllib.parse.quote_plus(title)}&key={config['google_api_key']}")
    if "items" in details.json():
        book_details = details.json()['items'][0]['volumeInfo']
        artist = book_details['authors'][0]
    else:
        artist = None
    return artist


def format_book_title(book, config):
    book = book.replace("_", " ")
    book = re.sub("([\(\[]).*?([\)\]])", "\g<1>\g<2>", book)
    book = book.replace(" () ", "")
    book = book.replace(" ()", "")
    book = book.replace("()", "")
    book = book.replace(" [] ", "")
    book = book.replace(" []", "")
    book = book.replace("[]", "")
    if " by " in book:
        name_list = book.split(" by ")
        extension = name_list[1].split(".")
        book = name_list[0] + "." + extension[-1]
    if " - " in book:
        name_list = book.split(" - ")
        extension = name_list[1].split(".")
        book = name_list[0] + "." + extension[-1]
    book = book.lstrip()
    return book

# get config
with open("./config.json") as f:
    config = load(f)

# loop folder for each book
os.chdir(config['formatter_parent_directory'])
target_files = os.listdir()
for book in target_files:
    try:
        title = None
        artist = None
        query_string = ""
        details = None
        book_details = None

        orig_book_name = book
        book = format_book_title(book, config)
        os.rename(orig_book_name, book)

        # read properties
        audio = EasyID3(book)
        # print(audio)
        name_list = book.split(".")
        title = name_list[0]
        if "artist" in audio:
            artist = audio['artist'][0]

        if artist is None:
            artist = get_author(title, config)
            if artist is None:
                if "title" in audio:
                    title = audio['title'][0]
                    artist = get_author(title, config)
                if artist is None:
                    if "album" in audio:
                        title = audio['album'][0]
                        artist = get_author(title, config)

        # use google api to fill in gaps
        if artist is None:
            artist = "ERROR"

        audio["title"] = title
        audio["album"] = title
        audio["artist"] = artist

        print("Completed book: " + title + ", " + artist)
        audio.save()

        # check if artist name is in plex library
        output_dir = config["plex_directory"] + "\\" + artist
        if os.path.isdir(output_dir):
            if os.path.isfile(output_dir + "\\" + book):
                print("we already have the book " + output_dir + "\\" + book)
            else:
                os.rename(book, output_dir + "\\" + book)
                print("moved book: " + book + " to existing dir : " + output_dir)

        else:
            os.mkdir(output_dir)
            os.rename(book, output_dir + "\\" + book)
            print("created directory: " + output_dir + " and moved book " + book + " into it")

    except Exception as e:
        print("WE GOT AN ERROR: " + str(e))

