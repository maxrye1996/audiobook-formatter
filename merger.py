import os
import re
from mutagen.easyid3 import EasyID3
from json import load

# get config
with open("./config.json") as f:
    config = load(f)

# start in target directory
os.chdir(config["merger_parent_directory"])

# find sub directories
target_directories = os.listdir()

# start looping sub directories to find files
commands_to_run = ""
errors = []
for dir in target_directories:
    if os.path.isdir(dir):
        current_dir = str(config["merger_parent_directory"]) + "\\" + dir
        target_files = os.listdir(current_dir)

        # check for sub directory
        for file in target_files:
            if os.path.isdir(current_dir + "\\" + file):
                # then we got a sub directory
                current_dir += "\\" + file
                target_files = os.listdir(current_dir)

        for file in target_files:
            # remove any non mp3s
            if os.path.splitext(file)[1][1:] != "mp3":
                if os.path.splitext(file)[1][1:] == "m4b":
                    # add to the m4b list to be moved
                    current_file = current_dir + "\\" + file
                    output_dir = str(config["merger_output_directory"])
                    command = "copy /b \"" + current_file + "\" \"" + str(output_dir) + "\\" + str(file) + "\""
                    commands_to_run += command + "\n"
                    target_files.remove(file)
                else:
                    print("WE DONT DO THAT HERE, removing " + file)
                    target_files.remove(file)

        # now reorder files in list numerically (using regex because windows sucks)
        target_files.sort(key=lambda var:[int(x) if x.isdigit() else x for x in re.findall(r'[^0-9]|[0-9]+', var)])

        # produce command in format:
        # copy /b "dir\file1.mp3" + "dir\file2.mp3" "output_dir\output.mp3"
        # check if output directory exists
        try:
            if len(target_files) > 0:
                command = "copy /b"
                output_dir = str(config["merger_output_directory"])
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                for file in target_files:
                    current_file = current_dir + "\\" + file
                    command += " \"" + current_file + "\" +"

                audio = EasyID3(current_file)
                if "album" in audio:
                    title = audio['album'][0]
                elif "title" in audio:
                    title = audio['title'][0]
                else:
                    title = dir

                command = command[:-1]
                command += "\"" + str(output_dir) + "\\" + str(title) + ".mp3"

                commands_to_run += command + "\n"
            else:
                print("I'VE GOT NOTHING LEFT - in this dir: " + dir)
        except:
            errors.append("found and issue with: "+file)
    else:
        if os.path.splitext(dir)[1][1:] == "mp3":
            try:
                # we have a lone mp3
                output_dir = str(config["merger_output_directory"])
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                audio = EasyID3(dir)
                if "album" in audio:
                    title = audio['album'][0]
                elif "title" in audio:
                    title = audio['title'][0]
                else:
                    title = dir
                current_file = str(config["merger_parent_directory"]) + "\\" + dir
                command = "copy /b \"" + current_file + "\" \"" + str(output_dir) + "\\" + str(title) + "\""

                commands_to_run += command + "\n"
            except:
                errors.append("found and issue with: " + dir)
        else:
            if os.path.splitext(dir)[1][1:] == "m4b":
                # add to the m4b list to be moved
                current_file = str(config["merger_parent_directory"]) + "\\" + dir
                output_dir = str(config["merger_output_directory"])
                command = "copy /b \"" + current_file + "\" \"" + str(output_dir) + "\\" + str(dir) + "\""
                commands_to_run += command + "\n"
            else:
                print("THATS NOT AN MP3, " + dir)

# print commands into bat file
file = open("./commands_to_run.bat", "w")
file.write(commands_to_run)
file.close()

print("These errors were found:")
print(errors)

print("starting execution")
os.startfile(config["merger_parent_directory"] + "\\" + "commands_to_run.bat")