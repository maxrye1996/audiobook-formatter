import json
import os
import re
from mutagen.easyid3 import EasyID3
from json import load

# get config
with open("./config.json") as f:
    config: dict = load(f)

# start in Audiobook folder
os.chdir(config["merger_parent_directory"])

# find sub directories - AUTHORS
authors: list = os.listdir()
# print(authors)
# start looping AUTHORS to find files
commands_to_run: list = []
move_commands: list = []
errors: list = []
book_formats: dict = {}
book_formats["directory"] = 0
book_formats["file"] = 0
book_dir_lengths: dict = {}
book_dir_lengths["none"] = 0
book_dir_lengths["one"] = 0
book_dir_lengths["more"] = 0

book_dir_lengths_after: dict = {}
book_dir_lengths_after["none"] = 0
book_dir_lengths_after["one"] = 0
book_dir_lengths_after["more"] = 0

delete_commands: list = []

file_extensions_found: dict = {}
print(f"starting to loop {len(authors)} authors")
authors.reverse()
for author in authors:
    current_dir = str(config["merger_parent_directory"]) + "\\" + author
    # now look each book in the author
    books: list = os.listdir(current_dir)
    # print(books)
    for book in books:
        if os.path.isdir(current_dir + "\\" + book):
            book_formats["directory"] += 1
            # we are in a directory, so these books need merging!
            current_dir = str(config["merger_parent_directory"]) + "\\" + author + "\\" + book
            target_files = os.listdir(current_dir)
            if len(target_files) == 0:
                book_dir_lengths["none"] += 1
            elif len(target_files) == 1:
                book_dir_lengths["one"] += 1
            else:
                book_dir_lengths["more"] += 1

            for file in target_files:
                # remove any non mp3s
                file_extension = os.path.splitext(file)[1][1:].lower()
                if file_extension in file_extensions_found:
                    file_extensions_found[file_extension] += 1
                else:
                    file_extensions_found[file_extension] = 1

                if file_extension != "mp3" and file_extension != "m4b" and file_extension != "m4a":
                    print("WE DONT DO THAT HERE, removing " + file)
                    # move_commands.append(f"md \"{str(config['merger_output_directory'])}\\{author}\\{book}\" 2> nul")
                    move_commands.append(f"del \"{current_dir}\\{file}\"")
                    target_files.remove(file)


            # now reorder files in list numerically (using regex because windows sucks)
            # print("Sorting current_dir: " + current_dir)
            # print(target_files)
            target_files.sort(key=lambda var: [int(x) if x.isdigit() else x for x in re.findall(r'[^0-9]|[0-9]+', var)])
            if len(target_files) == 0:
                book_dir_lengths_after["none"] += 1
            elif len(target_files) == 1:
                book_dir_lengths_after["one"] += 1
            else:
                book_dir_lengths_after["more"] += 1

            # produce command in format:
            # copy /b "dir\file1.mp3" + "dir\file2.mp3" "output_dir\output.mp3"
            # check if output directory exists
            try:
                if len(target_files) > 0:
                    command = ""
                    command = "copy /b"
                    output_dir = str(config["merger_parent_directory"]) + "\\" + author
                    for file in target_files:
                        file_extension = os.path.splitext(file)[1][1:]
                        current_file = current_dir + "\\" + file
                        command += " \"" + current_file + "\" +"
                        # move_commands.append(f"md \"{str(config['merger_output_directory'])}\\{author}\\{book}\" 2> nul")
                        move_commands.append(f"del \"{current_dir}\\{file}\"")

                    title = book

                    command = command[:-1]
                    command += "\"" + str(output_dir) + "\\" + str(title) + "." + file_extension

                    commands_to_run.append(command)

                else:
                    delete_commands.append(f"rmdir \\f \"{current_dir}\"")
            except Exception as e:
                errors.append("found and issue with: "+file)
                errors.append(e)
        else:
            book_formats["file"] += 1

# print commands into bat file
output_file = open("Y:/commands_to_run.bat", "w")
for command in commands_to_run:
    try:
        output_file.write(command)
        output_file.write("\n")
    except Exception as e:
        print(f"tried writin {command}")
        print(e)
output_file.close()

output_file = open("Y:/move_commands.bat", "w")
for command in move_commands:
    try:
        output_file.write(command)
        output_file.write("\n")
    except Exception as e:
        print(f"tried writin {command}")
        print(e)
output_file.close()

output_file = open("Y:/delete_commands.bat", "w")
for command in delete_commands:
    try:
        output_file.write(command)
        output_file.write("\n")
    except Exception as e:
        print(f"tried writin {command}")
        print(e)
output_file.close()



print("These errors were found:")
print(errors)

print("found these extesnions")
print(file_extensions_found)

print("found these book types")
print(book_formats)

print("numebr of fiiles indir")
print(book_dir_lengths)

print("numebr of fiiles indir aftere")
print(book_dir_lengths_after)

#
# print("starting the combinations")
# os.startfile("Y:/commands_to_run.bat")
# print("starting the moves")
# os.startfile("Y:/move_commands.bat")