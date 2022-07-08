import json
import os
import re
from json import load

# get config
with open("./config.json") as f:
    config: dict = load(f)

# start in Audiobook folder
os.chdir(config["merger_parent_directory"])

# find sub directories - AUTHORS
authors: list = os.listdir()
total_books: int = 0
dir_books: int = 0
dir_books_path: list[str] = []
file_books: int = 0
print(f"Authors: {len(authors)}")
for author in authors:
    current_dir = str(config["merger_parent_directory"]) + "\\" + author
    books: list = os.listdir(current_dir)
    total_books += len(books)
    for book in books:
        if os.path.isdir(current_dir+"\\"+book):
            dir_books_path.append(current_dir+"\\"+book)
            dir_books += 1
        else:
            file_books += 1

print(f"Total books: {total_books}")
print(f"Directory books: {dir_books}")
print(f"file books: {file_books}")

print(f"Off to make commands for {len(dir_books_path)} directories ")

total_book_files: list = []
commands_to_run: list = []
file_extensions_found: dict = {}
for book in dir_books_path:
    book_files = os.listdir(book)
    total_book_files.append(book_files)
    print(f"{len(book_files)} in here")
    if len(book_files) == 1:
        command: str = ""
        # then we have a singular book, just copy and delete dir
        book_file_name: str = book_files[0]
        book_title: str = book.split("\\")[-1]
        book_path: str = book.replace("\\"+book_title, "")

        # check extension, if not audiobook just make the delete
        file_extension = book_file_name.split(".")[-1].lower()
        if file_extension in file_extensions_found:
            file_extensions_found[file_extension] += 1
        else:
            file_extensions_found[file_extension] = 1

        if file_extension == "mp3" or file_extension == "m4b" or file_extension == "m4a":
            command = f"copy /b \"{book}\\{book_file_name}\" \"{book_path}\\{book_title}.{file_extension}\""
            commands_to_run.append(command)

        # now make the rmdir commands
        command = f"rmdir /s /q \"{book}\""
        commands_to_run.append(command)

print(f"Found a total of {len(total_book_files)} in directories")
print(f"Found a total of these file types: \n{file_extensions_found}")
print(f"Created a total of {len(commands_to_run)} commands to run")

output_file = open("Y:/commands_to_run.bat", "w")
for command in commands_to_run:
    try:
        output_file.write(command)
        output_file.write("\n")
    except Exception as e:
        print(f"tried writin {command}")
        print(e)
output_file.close()
