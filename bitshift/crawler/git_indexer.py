"""
:synopsis: Index all the files in a Git repository.

...more info soon...
"""

import fileinput, subprocess, os

from .database import Database

def index_repository(repo_url, framework_name):
    """
    Insert a Codelet for every file in a Git repository.

    `git clone` the Git repository located at **repo_url**, and create a Codelet
    for every one of non-binary (text) files in its if main branch (usually
    *master*).
    """

    repo_name = repo_url.split("/")[-1]
    subprocess.call("git clone %s" % repo_url, shell=True)
    os.chdir(repo_name)

    commits_meta = _get_commits_metadata()
    for filename in commits_meta.keys():
        with open(filename, "r") as source_file:
            source = source_file.read()

        authors = [(author,) for author in commits_meta["authors"]]
        codelet = Codelet("%s:%s" % (repo_name, filename), source, filename,
                          None, authors, _generate_file_url(filename, repo_url),
                          framework_name, commits_meta["time_created"],
                          commits_meta["time_last_modified"])
        Database.insert(codelet)

    os.chdir("..")
    subprocess.call("rm -rf %s" % repo_name, shell=True)

def _generate_file_url(filename, repo_url, framework_name):
    """
    Return a url for a filename from a Git wrapper framework.

    :param filename: The path of the file.
    :param repo_url: The url of the file's parent repository.
    :param framework_name: The name of the framework the repository is from.

    :type filename: str
    :type repo_url: str
    :type framework_name: str

    :return: The file's full url on the given framework.
    :rtype: str
    """

    if framework_name == "github":
        default branch = subprocess.check_output("git branch --no-color", \
                                                 shell=True)[2:-1]
        return "%s/blob/%s/%s" % (repo_url, default_branch, filename)

def _get_git_commits():
    """
    Return the current working directory's formatted commit data.

    Uses `git log` to generate metadata about every single file in the
    repository's commit history.

    :return: The author, timestamp, and names of all modified files of every
        commit.
        .. code-block:: python
           sample_returned_array = [
               {
                   "author" : (str) "author"
                   "timestamp" : (int) 1396919293,
                   "filenames" : (str array) ["file1", "file2"]
               }
           ]
    :rtype: dictionary
    """

    git_log_cmd = ("git --no-pager --no-color log --name-only "
        "--pretty=format:'%n%n%an%n%at' -z")
    git_log = subprocess.check_output(git_log_cmd, shell=True)

    commits = []
    for commit in git_log.split("\n\n"):
        fields = commit.split("\n")
        if len(fields) > 2:
            commits.append({
                "author" : fields[0],
                "timestamp" : int(fields[1]),
                "filenames" : fields[2].split("\0")[:-2]
            })

    return commits

def _get_tracked_files():
    """
    Return a list of the filenames of all files in the Git repository.

    Get a list of the filenames of the non-binary (Perl heuristics used for
    filetype identification) files currently inside the current working
    directory's Git repository.

    :return: The filenames of all non-binary files.
    :rtype: str array
    """

    tracked_files = subprocess.check_output("perl -le 'for (@ARGV){ print if \
        -f && -T }' $(find . -type d -name .git -prune -o -print)", shell=True)
    return [filename[2:] for filename in tracked_files.split("\n")[:-1]]

def _get_commits_metadata():
    """
    Return a dictionary containing every tracked file's metadata.

    :return: A dictionary with author names, time of creation, and time of last
        modification for every filename key.
        .. code-block:: python
               sample_returned_dict = {
                   "my_file" : {
                       "authors" : (str array) ["author1", "author2"],
                       "time_created" : (int) 1395939566,
                       "time_last_modified" : (int) 1396920409
                   }
               }
    :rtype: dictionary
    """

    commits = _get_git_commits()
    tracked_files  = _get_tracked_files()

    files_meta = {}
    for commit in commits:
        for filename in commit["filenames"]:
            if filename not in tracked_files:
                continue

            if filename not in files_meta.keys():
                files_meta[filename] = {
                    "authors" : [commit["author"]],
                    "time_last_modified" : commit["timestamp"]
                }
            else:
                if commit["author"] not in files_meta[filename]["authors"]:
                    files_meta[filename]["authors"].append(commit["author"])
                files_meta[filename]["time_created"] = commit["timestamp"]

    return files_meta
