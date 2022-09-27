import os
from difflib import SequenceMatcher


def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def tidy_author_names(authors: list) -> list:
    for i in range(0, len(authors), 1):
        authors[i] = authors[i].replace(" ", "")
        authors[i] = authors[i].replace(".", "")
    return authors


def find_similarities(authors: list) -> None:
    similar_count: int = 0
    for author in authors:
        similar_count = 0
        for a in authors:
            if similar(author, a) > 0.9:
                similar_count += 1
        if similar_count > 1:
            print(f"found similarities for {author}")


target_directory: str = "YOUR_AUDIOBOOK_DIR"
os.chdir(target_directory)
authors: list = os.listdir()
authors = tidy_author_names(authors)
find_similarities(authors)

