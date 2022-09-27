import os
import re

target_directory: str = "YOUR_AUDIOBOOK_DIR"

# get all Authors
os.chdir(target_directory)
authors: list = os.listdir()
chapters_to_remove: list = []


# loops authors and get their books
errors: list = []
empty_dirs: list = []
for author in authors:
    books: list = os.listdir(author)
    if len(books) == 0:
        empty_dirs.append("\"" + target_directory + "/" + author + "\"")
    # if book is a file, move to a sub directory
    for book in books:
        if os.path.isdir(author + "/" + book):
            # then check for chapters
            chapters: list = os.listdir(author + "/" + book)

            if len(chapters) == 0:
                empty_dirs.append("\"" + target_directory + "/" + author + "/" + book + "\"")

            # remove anything that isnt audio
            for chapter in chapters:
                file_extension = os.path.splitext(chapter)[1][1:].lower()
                if file_extension != "mp3" and file_extension != "m4b" and file_extension != "m4a":
                    # print("found something weird: " + chapter)
                    chapters_to_remove.append("\"" + target_directory + "/" + author + "/" + book + "/" + chapter + "\"")
                    chapters.remove(chapter)

            if len(chapters) > 1:
                # order the list properly
                try: 
                    chapters.sort(key=lambda var: [int(x) if x.isdigit() else x for x in re.findall(r'[^0-9]|[0-9]+', var)])
                except Exception as e:
                    print("error sorting chapters:")
                    print(e)
                    break

                # now make the contantenate command
                command: str = "cat "
                delete_commands: list = []
                for chapter in chapters:
                    path = "\"" + target_directory + "\"/\"" + author + "\"/\"" + book + "\"/\"" + chapter + "\""
                    command += path + " "
                    delete_commands.append("rm -f " + path)

                file_extension: str = os.path.splitext(chapters[0])[1][1:].lower()
                command += "> \"" + target_directory + "\"/\"" + author + "\"/\"" + book + "\"/\"" + book + "." + file_extension + "\""
                print(command)
                print(delete_commands)
                os.system(command)
                for del_command in delete_commands:
                    os.system(del_command)

        else:
            # then we have a file so move to sub dri
            sub_directory = author + "/" + os.path.splitext(book)[0]

            try:
                print("making subdirectory: " + sub_directory)
                os.mkdir(sub_directory)
                print("moving book to " + author + "/" + book + "   " + sub_directory + "/" + book)
                os.rename(author + "/" + book, sub_directory + "/" + book)
            except Exception as e:
                errors.append(e)

print(errors)

print(chapters_to_remove)
extensions_found: dict = {}
delete_commands: list = []
for chapter in chapters_to_remove:
    file_extension = os.path.splitext(chapter)[1][1:].lower()
    if file_extension in extensions_found:
        extensions_found[file_extension] = extensions_found[file_extension] +1
    else:
        extensions_found[file_extension] = 1
    
    delete_commands.append("rm -f " + chapter)
print("extensions found to be deleted:")
print(extensions_found)
for del_command in delete_commands:
    os.system(del_command)

print("empty directorys: " + str(len(empty_dirs)))
delete_commands = []
for directory in empty_dirs:
    delete_commands.append("rm -r " + directory)

for del_command in delete_commands:
    os.system(del_command)
