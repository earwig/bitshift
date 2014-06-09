"""
:synopsis: Contains a singleton GitIndexer class, which clones and indexes git
    repositories.
"""

from datetime import datetime
import logging
import os
import Queue
import shutil
import string
import time
import threading

from bs4 import UnicodeDammit
import git

from ..database import Database
from ..parser import parse, UnsupportedFileError
from ..codelet import Codelet

GIT_CLONE_DIR = "/tmp/bitshift"
THREAD_QUEUE_SLEEP = 0.5
MAX_INDEX_QUEUE_SIZE = 10

class GitRepository(object):
    """
    A representation of a Git repository's metadata.

    :ivar url: (str) The repository's url.
    :ivar name: (str) The name of the repository.
    :ivar framework_name: (str) The name of the online Git framework that the
        repository belongs to (eg, GitHub, BitBucket).
    :ivar rank: (float) The rank of the repository, as assigned by
        :class:`crawler.GitHubCrawler`.
    :ivar path: (str) The repository's on-disk directory path.
    :ivar repo: (git.Repo) A git.Repo representation of the repository.
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
        dirname = name.replace("/", "-") + "-" + str(int(time.time()))
        self.path = os.path.join(GIT_CLONE_DIR, dirname)
        self.repo = None

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

        while True:
            while self.index_queue.empty() and self.run_event.is_set():
                time.sleep(THREAD_QUEUE_SLEEP)
            if not self.run_event.is_set():
                break

            repo = self.index_queue.get()
            self.index_queue.task_done()
            self._index_repository(repo)

    def _index_repository(self, repo):
        """
        Clone and index (create and insert Codeletes for) a Git repository.

        `git clone` the Git repository located at **repo.url**, call
        `_insert_repository_codelets()`, then remove said repository.

        :param repo: The metadata of the repository to be indexed.
        :type repo: :class:`GitRepository`
        """

        self._logger.info(u"Indexing repo: %s", repo.name)
        try:
            self._insert_repository_codelets(repo)
        except Exception:
            self._logger.exception("Exception raised while indexing:")
        finally:
            if os.path.isdir(repo.path):
                shutil.rmtree(repo.path)

    def _insert_repository_codelets(self, repo):
        """
        Create and insert a Codelet for the files inside a Git repository.

        Create a new Codelet, and insert it into the Database singleton, for
        every file inside the current working directory's default branch
        (usually *master*).

        :param repo_url: The metadata of the repository to be indexed.

        :type repo_url: :class:`GitRepository`
        """

        commits_meta = self._get_commits_metadata(repo)
        if commits_meta is None:
            return

        for filename, data in commits_meta.iteritems():
            authors = [(author, None) for author in data["authors"]]
            encoded_source = data["blob"].data_stream.read()
            source = UnicodeDammit(encoded_source).unicode_markup
            url = self._generate_file_url(filename, repo)
            codelet = Codelet("%s: %s" % (repo.name, filename), source,
                            filename, None, authors, url, data["time_created"],
                            data["time_last_modified"], repo.rank)
            self._logger.debug("Indexing file: %s", codelet.name)
            try:
                parse(codelet)
            except UnsupportedFileError:
                continue
            self.database.insert(codelet)

    def _generate_file_url(self, filename, repo):
        """
        Return a url for a filename from a Git wrapper framework.

        :param filename: The path of the file.
        :param repo: The git repo.

        :type filename: str
        :type repo: :class:`GitRepository`

        :return: The file's full url on the given framework, if successfully
            derived.
        :rtype: str, or None
        """

        if repo.framework_name == "GitHub":
            default_branch = repo.repo.active_branch
            parts = [repo.url, "blob", default_branch, filename]
        elif repo.framework_name == "Bitbucket":
            try:
                commit_hash = repo.repo.head.commit.hexsha
            except ValueError:  # No commits
                return None
            parts = [repo.url, "src", commit_hash, filename]
        return "/".join(s.strip("/") for s in parts)

    def _walk_history(self, files, head):
        """Walk a repository's history for metadata."""
        def update_entry(commit, entry, new_file):
            entry["authors"].add(commit.author.name)
            commit_ts = datetime.utcfromtimestamp(commit.committed_date)
            if commit_ts > entry["time_last_modified"]:
                entry["time_last_modified"] = commit_ts
            if new_file:
                entry["time_created"] = commit_ts

        def handle_commit(commit, paths):
            if not commit.parents:
                for item in commit.tree.traverse():
                    if item.type == "blob" and item.path in paths:
                        update_entry(commit, files[paths[item.path]], True)
                return

            for parent in commit.parents:
                for diff in parent.diff(commit, create_patch=True):
                    pth = diff.rename_to if diff.renamed else diff.b_blob.path
                    if pth not in paths:
                        continue
                    update_entry(commit, files[paths[pth]], diff.new_file)
                    if diff.renamed:
                        paths[diff.rename_from] = paths[pth]
                        del paths[pth]

        pending = [(head, {path: path for path in files})]
        while pending:
            commit, paths = pending.pop()
            handle_commit(commit, paths)
            for parent in commit.parents:
                new_paths = paths.copy() if len(commit.parents) > 1 else paths
                pending.append((parent, new_paths))

    def _get_commits_metadata(self, repo):
        """
        Return a dictionary containing every valuable tracked file's metadata.

        :return: A dictionary with author names, time of creation, and time of
            last modification for every filename key.
            .. code-block:: python
                sample_returned_dict = {
                    "my_file" : {
                        "blob": (GitPython Blob) <object>,
                        "authors" : (str set) {"author1", "author2"},
                        "time_created" : (`datetime.datetime`) <object>,
                        "time_last_modified" : (`datetime.datetime`) <object>
                    }
                }
        :rtype: dictionary of dictionaries
        """
        try:
            tree = repo.repo.head.commit.tree
        except ValueError:  # No commits
            return {}

        files = {}
        for item in tree.traverse():
            if item.type == "blob" and self._is_ascii(item.data_stream):
                files[item.path] = {
                    "blob": item,
                    "authors" : set(),
                    "time_last_modified": datetime.utcfromtimestamp(0),
                    "time_created": datetime.utcfromtimestamp(0)
                }

        self._walk_history(files, repo.repo.head.commit)
        return files

    def _is_ascii(self, source):
        """
        Heuristically determine whether a file is ASCII text or binary.

        If a portion of the file contains null bytes, or the percentage of bytes
        that aren't ASCII is greater than 30%, then the file is concluded to be
        binary. This heuristic is used by the `file` utility, Perl's inbuilt `-T`
        operator, and is the de-facto method for in : passdetermining whether a
        file is ASCII.

        :param source: The file object to test.

        :type source: `file`

        :return: Whether the file is probably ASCII.
        :rtype: Boolean
        """

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

        while True:
            while self.clone_queue.empty() and self.run_event.is_set():
                time.sleep(THREAD_QUEUE_SLEEP)
            if not self.run_event.is_set():
                break
            repo = self.clone_queue.get()
            self.clone_queue.task_done()

            try:
                self._clone_repository(repo)
            except Exception:
                self._logger.exception("Exception raised while cloning:")

    def _clone_repository(self, repo):
        """
        Attempt cloning a Git repository.

        :param repo: Metadata about the repository to clone.

        :type repo: :class:`GitRepository`
        """

        self._logger.info("Cloning repo: %s", repo.url)
        repo.repo = git.Repo.clone_from(repo.url, to_path=repo.path, bare=True,
                                        single_branch=True)
        while self.index_queue.full() and self.run_event.is_set():
            time.sleep(THREAD_QUEUE_SLEEP)
        if self.run_event.is_set():
            self.index_queue.put(repo)
