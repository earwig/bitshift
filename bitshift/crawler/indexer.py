"""
:synopsis: Contains a singleton GitIndexer class, which clones and indexes git
    repositories.
"""

import bs4, os, re, shutil, subprocess, threading

from ..database import Database
from ..codelet import Codelet

GIT_CLONE_DIR = "/tmp/bitshift"

class GitIndexer(threading.Thread):
    """
    A singleton Git repository indexer.

    `GitIndexer` clones and indexes the repositories at urls found by the
    :mod:`bitshift.crawler.crawler` Git crawlers.

    :ivar repository_queue: (:class:`Queue.Queue`) A queue containing urls found
        by the :mod:`bitshift.crawler.crawler` Git crawlers.
    """

    def __init__(self, repository_queue):
        """
        Create an instance of the singleton `GitIndexer`.

        :param repository_queue: see :attr:`GitIndexer.repository_queue`

        :type repository_queue: see :attr:`GitIndexer.repository_queue`
        """

        self.repository_queue = repository_queue
        super(GitIndexer, self).__init__()

    def run(self):
        """
        Retrieve new repository urls, clone, and index them.

        Blocks until new urls appear in :attr:`GitIndexer.repository_queue`,
        then retrieves one, and attempts cloning/indexing it. Should any errors
        occur, the new repository will be discarded and the crawler will
        index the next in the queue.
        """

        while True:
            while self.repository_queue.empty():
                pass

            repo = self.repository_queue.get()
            self.repository_queue.task_done()

            try:
                _index_repository(repo["url"], repo["name"],
                        repo["framework_name"])
            except: # desperate times -- will be modified later
                pass

class _ChangeDir(object):
    """
    A wrapper class for os.chdir(), to map onto `with` and handle exceptions.

    :ivar new_path: (str) The path to change the current directory to.
    :ivar old_path: (str) The path of the directory to return to.
    """

    def __init__(self, new_path):
        """
        Create a _ChangeDir instance.

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

def _index_repository(repo_url, repo_name, framework_name):
    """
    Clone and index (create and insert Codeletes for) a Git repository.

    `git clone` the Git repository located at **repo_url**, call
    _insert_repository_codelets, then remove said repository.

    :param repo_url: The url the Git repository was cloned from.
    :param repo_name: The name of the repository.
    :param framework_name: The name of the framework the repository is from.

    :type repo_url: str
    :type repo_name: str
    :type framework_name: str
    """

    GIT_CLONE_TIMEOUT = 60

    with _ChangeDir(GIT_CLONE_DIR) as git_clone_dir:
        if subprocess.call("perl -e 'alarm shift @ARGV; exec @ARGV' %d git \
                clone %s" % (GIT_CLONE_TIMEOUT, repo_url), shell=True) != 0:
            return

        with _ChangeDir(repo_name) as repository_dir:
            _insert_repository_codelets(repo_url, repo_name, framework_name)
        shutil.rmtree("%s/%s" % (GIT_CLONE_DIR, repo_name))

def _insert_repository_codelets(repo_url, repo_name, framework_name):
    """
    Create and insert a Codelet for the files inside a Git repository.

    Create a new Codelet, and insert it into the Database singleton, for every
    file inside the current working directory's default branch (usually
    *master*).

    :param repo_url: The url the Git repository was cloned from.
    :param repo_name: The name of the repository.
    :param framework_name: The name of the framework the repository is from.

    :type repo_url: str
    :type repo_name: str
    :type framework_name: str
    """

    commits_meta = _get_commits_metadata()
    for filename in commits_meta.keys():
        with open(filename, "r") as source_file:
            source = _decode(source_file.read())
            if source is None:
                return

        authors = [(_decode(author),) for author in \
                commits_meta[filename]["authors"]]
        codelet = Codelet("%s:%s" % (repo_name, filename), source, filename,
                        None, authors, _generate_file_url(filename, repo_url,
                                framework_name),
                        commits_meta[filename]["time_created"],
                        commits_meta[filename]["time_last_modified"])

        db.codelets.insert({
            "name" : codelet.name,
            "authors" : codelet.authors
        })

        # Database.insert(codelet)

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

    if framework_name == "GitHub":
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

    git_log = subprocess.check_output(("git --no-pager log --name-only"
            " --pretty=format:'%n%n%an%n%at' -z"), shell=True)

    commits = []
    for commit in git_log.split("\n\n"):
        fields = commit.split("\n")
        if len(fields) > 2:
            commits.append({
                "author" : fields[0],
                "timestamp" : int(fields[1]),
                "filenames" : fields[2].split("\x00")[:-2]
            })

    return commits

def _get_tracked_files():
    """
    Return a list of the filenames of all valuable files in the Git repository.

    Get a list of the filenames of the non-binary (Perl heuristics used for
    filetype identification) files currently inside the current working
    directory's Git repository. Then, weed out any boilerplate/non-code files
    that match the regex rules in GIT_IGNORE_FILES.

    :return: The filenames of all index-worthy non-binary files.
    :rtype: str array
    """

    GIT_IGNORE_FILES = [".*licen[cs]e.*", ".*readme.*"]

    tracked_files = subprocess.check_output(("perl -le 'for (@ARGV){ print if \
            -f && -T }' $(find . -type d -name .git -prune -o -print)"),
            shell=True).split("\n")[:-1]

    valuable_files = []
    for filename in tracked_files:
        filename_match = any([re.match(pattern, filename, flags=re.IGNORECASE)
                for pattern in GIT_IGNORE_FILES])
        if not filename_match:
            valuable_files.append(filename[2:])
    return valuable_files

def _get_commits_metadata():
    """
    Return a dictionary containing every valuable tracked file's metadata.

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

def _decode(raw):
    """
    Return a decoded a raw string.

    :param raw: The string to string.

    :type raw: (str)

    :return: If the original encoding is successfully inferenced, return the
        decoded string.
    :rtype: str, or None

    .. warning::
        The raw string's original encoding is identified by heuristics which
        can, and occasionally will, fail. Decoding will then fail, and None
        will be returned.
    """

    try:
        return raw.decode(bs4.BeautifulSoup(raw).original_encoding)

    except (UnicodeDecodeError, UserWarning):
        return None
