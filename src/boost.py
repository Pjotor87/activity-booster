from logzero import logger
import os
from os import listdir
from os.path import isfile, join
import pathlib
import random
from git import Repo
from datetime import datetime, timedelta
from shutil import copyfile


def get_random(list):
    choice = random.choice(list)
    return choice if choice else get_random(list)


def git_push(repo, commit_message, files_list, is_add_not_remove=True):
    successful_push = False
    try:
        logger.info("Adding...")

        if is_add_not_remove is True:
            repo.index.add(files_list)
        else:
            repo.index.remove(files_list)

        logger.info("Commiting with message: {0}".format(commit_message))
        repo.index.commit(commit_message)
        logger.info("Pushing...")
        repo.git.push()
        successful_push = True
    except Exception as ex:
        logger.error('Some error occured while pushing the code')
        logger.error(ex)
    return successful_push


def boost(git_repo_url="https://github.com/Pjotor87/activity-booster.git"):
    datetime_format = "%Y_%m_%d___%H%M%S"
    ws_path = join(pathlib.Path().absolute(), "../", "activity-booster-ws")
    this_run = datetime.now().strftime(datetime_format)
    this_second_run = datetime.now().strftime(datetime_format) + "_s"
    ws_this_run_path = join(ws_path, this_run)
    ws_this_second_run_path = join(ws_path, this_second_run)

    db_path = join(pathlib.Path().absolute(), "db")
    file_names = [f for f in listdir(db_path) if isfile(join(db_path, f))]
    file_paths = [join(db_path, f) for f in listdir(db_path) if isfile(join(db_path, f))]
    file_contents = []
    for file_path in file_paths:
        with open(file_path) as f:
            content = f.readlines()
            content = [x.strip() for x in content]
            file_contents.append(content)

    dummy_files_path = join(db_path, "dummyfiles")
    dummy_file_names = [f for f in listdir(dummy_files_path) if isfile(join(dummy_files_path, f))]
    dummy_file_paths = [join(dummy_files_path, f) for f in listdir(dummy_files_path) if isfile(join(dummy_files_path, f))]
    dummy_file_contents = []
    for file_path in dummy_file_paths:
        with open(file_path) as f:
            content = f.readlines()
            content = [x.strip() for x in content]
            dummy_file_contents.append(content)

    should_add_not_remove = len(file_contents[0]) == 0

    if(should_add_not_remove):
        # Clone
        logger.info("Cloning from {0}".format(git_repo_url))
        repo = Repo.clone_from(git_repo_url, ws_this_run_path)
        # Copy file
        copyfile(dummy_file_paths[0], join(ws_this_run_path, dummy_file_names[0]))
        # Add, commit and push
        successfully_pushed = git_push(repo, get_random(file_contents[2]), [dummy_file_names[0]])
        # Track boost push
        if successfully_pushed is True:
            file_contents[0].append("{0},{1},{2},{3}".format(git_repo_url, this_run, "ADD", dummy_file_names[0]))
            with open(file_paths[0], 'w') as filehandle:
                filehandle.writelines("%s\n" % line for line in file_contents[0])
    else:
        for line in file_contents[0]:
            git_url = line.split(',')[0]
            if git_url == git_repo_url:
                directive = line.split(',')[2]
                if directive == "ADD":
                    datetime_of_add = datetime.strptime(line.split(',')[1], datetime_format)
                    days_in_hours = (24 * 3)
                    days_in_hours = 0
                    removal_datetime = datetime_of_add + timedelta(hours=days_in_hours)
                    if datetime.now() > removal_datetime:
                        # Clone
                        logger.info("Cloning from {0}".format(git_repo_url))
                        repo = Repo.clone_from(git_repo_url, ws_this_second_run_path)
                        # Remove file
                        os.remove(join(ws_this_second_run_path, dummy_file_names[0]))
                        successfully_pushed = git_push(repo, get_random(file_contents[1]), [dummy_file_names[0]], is_add_not_remove=False)
                        # Track boost push
                        if successfully_pushed is True:
                            file_contents[0].remove(line)
                            with open(file_paths[0], 'w') as filehandle:
                                filehandle.writelines("%s\n" % line for line in file_contents[0])
                            break
                    else:
                        logger.info("Not time yet for this one...")
