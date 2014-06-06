"""
:synopsis: Contains a singleton GitIndexer class, which clones and indexes git
    repositories.
"""

import datetime
import logging
import os
import Queue
import shutil
import string
import subprocess
import time
import threading

import bs4

from ..database import Database
from ..parser import parse, UnsupportedFileError
from ..languages import LANGS
from ..codelet import Codelet

GIT_CLONE_DIR = "/tmp/bitshift"
THREAD_QUEUE_SLEEP = 0.5

class GitRepository(object):
    """
    A representation of a Git repository's metadata.

    :ivar url: (str) The repository's url.
    :ivar name: (str) The name of the repository.
    :ivar framework_name: (str) The name of the online Git framework that the
        repository belongs to (eg, GitHub, BitBucket).
    :ivar rank: (float) The rank of the repository, as assigned by
        :class:`crawler.GitHubCrawler`.
    """

    def __init__(self, url, name, framework_name, rank):
        """
        Create a GitRepository instance.

        :param url: see :attr:`GitRepository.url`
        :param name: see :attr:`GitRepository.name`
        :param framework_name: see :attr:`GitRepository.framework_name`
        :param rank: see :attr:`GitRepository.rank`

        :type url: str
        :type name: str
        :type framework_name: str
        :type rank: float
        """

        self.url = url
        self.name = name
        self.framework_name = framework_name
        self.rank = rank

class GitIndexer(threading.Thread):
    """
    A singleton Git repository indexer.

    :class:`GitIndexer` indexes the repositories cloned by the
    :class:`_GitCloner` singleton.

    :ivar index_queue: (:class:`Queue.Queue`) A queue containing
        :class:`GitRepository` objects for every new repository succesfully
        cloned by :class:`_GitCloner`, which are to be indexed.
    :ivar git_cloner: (:class:`_GitCloner`) The corresponding repository cloner,
        which feeds :class:`GitIndexer`.
    :ivar _logger: (:class:`logging.Logger`) A class-specific logger object.
    """

    def __init__(self, clone_queue, run_event):
        """
        Create an instance of the singleton `GitIndexer`.

        :param clone_queue: see :attr:`self.index_queue`

        :type index_queue: see :attr:`self.index_queue`
        """

        MAX_INDEX_QUEUE_SIZE = 10

        self.index_queue = Queue.Queue(maxsize=MAX_INDEX_QUEUE_SIZE)
        self.run_event = run_event
        self.git_cloner = _GitCloner(clone_queue, self.index_queue, run_event)
        self.git_cloner.start()
        self.database = Database()
        self._logger = logging.getLogger("%s.%s" %
                (__name__, self.__class__.__name__))
        self._logger.info("Starting.")

        if not os.path.exists(GIT_CLONE_DIR):
            os.makedirs(GIT_CLONE_DIR)

        super(GitIndexer, self).__init__(name=self.__class__.__name__)

    def run(self):
        """
        Retrieve metadata about newly cloned repositories and index them.

        Blocks until new repositories appear in :attr:`self.index_queue`, then
        retrieves one, and attempts indexing it. Should any errors occur, the
        new repository will be discarded and the indexer will index the next in
        the queue.
        """

        while self.run_event.is_set():
            while self.index_queue.empty():
                time.sleep(THREAD_QUEUE_SLEEP)

            repo = self.index_queue.get()
            self.index_queue.task_done()
            self._index_repository(repo)

    def _index_repository(self, repo):
        """
        Clone and index (create and insert Codeletes for) a Git repository.

        `git clone` the Git repository located at **repo.url**, call
        `_insert_repository_codelets()`, then remove said repository.

        :param repo_url: The metadata of the repository to be indexed.

        :type repo_url: :class:`GitRepository`
        """

        with _ChangeDir("%s/%s" % (GIT_CLONE_DIR, repo.name)):
            try:
                self._insert_repository_codelets(repo)
            except Exception:
                self._logger.exception("Exception raised while indexing:")
            finally:
                if os.path.isdir("%s/%s" % (GIT_CLONE_DIR, repo.name)):
                    if len([obj for obj in os.listdir('.') if
                            os.path.isdir(obj)]) <= 1:
                        shutil.rmtree("%s/%s" % (
                                GIT_CLONE_DIR, repo.name.split("/")[0]))
                    else:
                        shutil.rmtree("%s/%s" % (GIT_CLONE_DIR, repo.name))

    def _insert_repository_codelets(self, repo):
        """
        Create and insert a Codelet for the files inside a Git repository.

        Create a new Codelet, and insert it into the Database singleton, for
        every file inside the current working directory's default branch
        (usually *master*).

        :param repo_url: The metadata of the repository to be indexed.

        :type repo_url: :class:`GitRepository`
        """

        commits_meta = self._get_commits_metadata()
        if commits_meta is None:
            return

        for filename in commits_meta.keys():
            try:
                with open(filename) as source_file:
                    source = self._decode(source_file.read())
                    if source is None:
                        continue
            except IOError:
                continue

            authors = [(self._decode(author), None) for author in
                       commits_meta[filename]["authors"]]
            codelet = Codelet("%s:%s" % (repo.name, filename), source, filename,
                            None, authors, self._generate_file_url(filename,
                                    repo.url, repo.framework_name),
                            commits_meta[filename]["time_created"],
                            commits_meta[filename]["time_last_modified"],
                            repo.rank)
            try:
                parse(codelet)
            except UnsupportedFileError:
                continue
            self.database.insert(codelet)

    def _generate_file_url(self, filename, repo_url, framework_name):
        """
        Return a url for a filename from a Git wrapper framework.

        :param filename: The path of the file.
        :param repo_url: The url of the file's parent repository.
        :param framework_name: The name of the framework the repository is from.

        :type filename: str
        :type repo_url: str
        :type framework_name: str

        :return: The file's full url on the given framework, if successfully
            derived.
        :rtype: str, or None

        .. warning::
            Various Git subprocesses will occasionally fail, and, seeing as the
            information they provide is a crucial component of some repository
            file urls, None may be returned.
        """

        try:
            if framework_name == "GitHub":
                default_branch = subprocess.check_output("git branch"
                    " --no-color", shell=True)[2:-1]
                parts = [repo_url, "blob", default_branch, filename]
            elif framework_name == "Bitbucket":
                commit_hash = subprocess.check_output("git rev-parse HEAD",
                    shell=True).replace("\n", "")
                parts = [repo_url, "src", commit_hash, filename]
            return "/".join(s.strip("/") for s in parts)
        except subprocess.CalledProcessError:
            return None

    def _get_git_commits(self):
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
                       "timestamp" : (`datetime.datetime`) <object>,
                       "filenames" : (str array) ["file1", "file2"]
                   }
               ]
        :rtype: array of dictionaries
        """

        git_log = subprocess.check_output(("git --no-pager log --name-only"
                " --pretty=format:'%n%n%an%n%at' -z"), shell=True)

        commits = []
        for commit in git_log.split("\n\n"):
            fields = commit.split("\n")
            if len(fields) > 2:
                commits.append({
                    "author" : fields[0],
                    "timestamp" : datetime.datetime.fromtimestamp(int(fields[1])),
                    "filenames" : fields[2].split("\x00")[:-2]
                })

        return commits

    def _get_tracked_files(self):
        """
        Return a list of the filenames of all valuable files in the Git repository.

        Get a list of the filenames of the non-binary (Perl heuristics used for
        filetype identification) files currently inside the current working
        directory's Git repository. Then, weed out any boilerplate/non-code files
        that match the regex rules in GIT_IGNORE_FILES.

        :return: The filenames of all index-worthy non-binary files.
        :rtype: str array
        """

        files = []
        for dirname, subdir_names, filenames in os.walk("."):
            for filename in filenames:
                path = os.path.join(dirname, filename)
                if self._is_ascii(path):
                    files.append(path[2:])

        return files

    def _get_commits_metadata(self):
        """
        Return a dictionary containing every valuable tracked file's metadata.

        :return: A dictionary with author names, time of creation, and time of last
            modification for every filename key.
            .. code-block:: python
                   sample_returned_dict = {
                       "my_file" : {
                           "authors" : (str array) ["author1", "author2"],
                           "time_created" : (`datetime.datetime`) <object>,
                           "time_last_modified" : (`datetime.datetime`) <object>
                       }
                   }
        :rtype: dictionary of dictionaries
        """

        commits = self._get_git_commits()
        tracked_files = self._get_tracked_files()

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

    def _decode(self, raw):
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
            encoding = bs4.BeautifulSoup(raw).original_encoding
            return raw.decode(encoding) if encoding is not None else None

        except (LookupError, UnicodeDecodeError, UserWarning) as exception:
            return None

    def _is_ascii(self, filename):
        """
        Heuristically determine whether a file is ASCII text or binary.

        If a portion of the file contains null bytes, or the percentage of bytes
        that aren't ASCII is greater than 30%, then the file is concluded to be
        binary. This heuristic is used by the `file` utility, Perl's inbuilt `-T`
        operator, and is the de-facto method for in : passdetermining whether a
        file is ASCII.

        :param filename: The path of the file to test.

        :type filename: str

        :return: Whether the file is probably ASCII.
        :rtype: Boolean
        """

        try:
            with open(filename) as source:
                file_snippet = source.read(512)

                if not file_snippet:
                    return True

                ascii_characters = "".join(map(chr, range(32, 127)) +
                        list("\n\r\t\b"))
                null_trans = string.maketrans("", "")

                if "\0" in file_snippet:
                    return False

                non_ascii = file_snippet.translate(null_trans, ascii_characters)
                return not float(len(non_ascii)) / len(file_snippet) > 0.30

        except IOError:
            return False

class _GitCloner(threading.Thread):
    """
    A singleton Git repository cloner.

    Clones the repositories crawled by :class:`crawler.GitHubCrawler` for
    :class:`GitIndexer` to index.

    :ivar clone_queue: (:class:`Queue.Queue`) see
        :attr:`crawler.GitHubCrawler.clone_queue`.
    :ivar index_queue: (:class:`Queue.Queue`) see
        :attr:`GitIndexer.index_queue`.
    :ivar _logger: (:class:`logging.Logger`) A class-specific logger object.
    """

    def __init__(self, clone_queue, index_queue, run_event):
        """
        Create an instance of the singleton :class:`_GitCloner`.

        :param clone_queue: see :attr:`self.clone_queue`
        :param index_queue: see :attr:`self.index_queue`

        :type clone_queue: see :attr:`self.clone_queue`
        :type index_queue: see :attr:`self.index_queue`
        """

        self.clone_queue = clone_queue
        self.index_queue = index_queue
        self.run_event = run_event
        self._logger = logging.getLogger("%s.%s" %
                (__name__, self.__class__.__name__))
        self._logger.info("Starting.")
        super(_GitCloner, self).__init__(name=self.__class__.__name__)

    def run(self):
        """
        Retrieve metadata about newly crawled repositories and clone them.

        Blocks until new :class:`GitRepository` appear in
        :attr:`self.clone_queue`, then attempts cloning them. If
        succcessful, the cloned repository is added to :attr:`self.index_queue`
        for the `GitIndexer` to clone; otherwise, it is discarded.
        """

        while self.run_event.is_set():
            while self.clone_queue.empty():
                time.sleep(THREAD_QUEUE_SLEEP)
            repo = self.clone_queue.get()
            self.clone_queue.task_done()

            try:
                self._clone_repository(repo)
            except Exception:
                pass

    def _clone_repository(self, repo):
        """
        Attempt cloning a Git repository.

        :param repo: Metadata about the repository to clone.

        :type repo: :class:`GitRepository`
        """

        GIT_CLONE_TIMEOUT = 500

        queue_percent_full = (float(self.index_queue.qsize()) /
                self.index_queue.maxsize) * 100

        exit_code = None
        command = ("perl -e 'alarm shift @ARGV; exec @ARGV' %d git clone"
        " --single-branch %s %s/%s || pkill -f git")

        command_attempt = 0
        while exit_code is None:
            try:
                exit_code = subprocess.call(command % (GIT_CLONE_TIMEOUT,
                        repo.url, GIT_CLONE_DIR, repo.name), shell=True)
            except Exception:
                time.sleep(1)
                command_attempt += 1
                if command_attempt == 20:
                    break
                else:
                    continue
            else:
                break

        if exit_code != 0:
            if os.path.isdir("%s/%s" % (GIT_CLONE_DIR, repo.name)):
                shutil.rmtree("%s/%s" % (GIT_CLONE_DIR, repo.name))
            return

        while self.index_queue.full():
            time.sleep(THREAD_QUEUE_SLEEP)

        self.index_queue.put(repo)

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
