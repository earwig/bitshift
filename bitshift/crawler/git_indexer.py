"""
:synopsis: Index all the files in a Git repository.

.. todo::
    Add documentation, threaded Indexer class.
"""

import shutil, subprocess, os

from ..database import Database
from ..codelet import Codelet

GIT_CLONE_DIR = "/tmp"

class ChangeDir(object):
    """
    A wrapper class for os.chdir(), to map onto `with` and handle exceptions.

    :ivar new_path: (str) The path to change the current directory to.
    :ivar old_path: (str) The path of the directory to return to.
    """

    def __init__(self, new_path):
        """
        Create a ChangeDir instance.

        :param new_path: The directory to enter.

        :type new_path: str
        """

        self.new_path = new_path

    def __enter__(self):
        """
        Change the current working-directory to **new_path**.
        """

        self.old_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, *exception):
        """
        Change the current working-directory to **old_path**.

        :param exception: Various exception arguments passed by `with`.

        :type exception: varargs
        """

        os.chdir(self.old_path)

def index_repository(repo_url, framework_name):
    """
    Clone and index (create and insert Codeletes for) a Git repository.

    `git clone` the Git repository located at **repo_url**, call
    _insert_repository_codelets, then remove said repository.

    :param repo_url: The url the Git repository was cloned from.
    :param framework_name: The name of the framework the repository is from.

    :type repo_url: str
    :type framework_name: str

    :return: Temporary: the new codelets, for testing purposes.
    :rtype: Codelet array
    """

    repo_name = repo_url.split("/")[-1]
    codelets = []

    with ChangeDir(GIT_CLONE_DIR) as git_clone_dir:
        subprocess.call("git clone %s" % repo_url, shell=True)
        with ChangeDir(repo_name) as repository_dir:
            codelets = _insert_repository_codelets(repo_url, repo_name,
                                                   framework_name)
        shutil.rmtree("%s/%s" % (GIT_CLONE_DIR, repo_name))

    return codelets

def _insert_repository_codelets(repo_url, repo_name, framework_name):
    """
    Create a Codelet for the files inside a Git repository.

    Create a new Codelet, and insert it into the Database singlet, for every
    file inside the current working directory's default branch (usually
    *master*).

    :param repo_url: The url the Git repository was cloned from.
    :param repo_name: The name of the repository.
    :param framework_name: The name of the framework the repository is from.

    :type repo_url: str
    :type repo_name: str
    :type framework_name: str
    """

    codelets = []
    commits_meta = _get_commits_metadata()
    for filename in commits_meta.keys():
        with open(filename, "r") as source_file:
            source = source_file.read()

        authors = [(author,) for author in commits_meta[filename]["authors"]]
        codelets.append(
                Codelet("%s:%s" % (repo_name, filename), source, filename,
                        None, authors, _generate_file_url(filename, repo_url,
                                                          framework_name),
                        commits_meta[filename]["time_created"],
                        commits_meta[filename]["time_last_modified"]))

    return codelets

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
        default_branch = subprocess.check_output("git branch --no-color",
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

    git_log = subprocess.check_output(
            ("git --no-pager log --name-only"
            " --pretty=format:'%n%n%an%n%at' -z"), shell=True)

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

    tracked_files = subprocess.check_output(
            ("perl -le 'for (@ARGV){ print if -f && -T }'"
            " $(find . -type d -name .git -prune -o -print)"), shell=True)
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
                    "time_last_modified" : commit["timestamp"],
                    "time_created" : commit["timestamp"]
                }
            else:
                if commit["author"] not in files_meta[filename]["authors"]:
                    files_meta[filename]["authors"].append(commit["author"])
                files_meta[filename]["time_created"] = commit["timestamp"]

    return files_meta
