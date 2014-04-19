"""
:synopsis: Main crawler module, to oversee all site-specific crawlers.

Contains all website/framework-specific Class crawlers.
"""

import logging, requests, time, threading

from bitshift.crawler import indexer

from ..codelet import Codelet
from ..database import Database

class GitHubCrawler(threading.Thread):
    """
    Crawler that retrieves links to all of GitHub's public repositories.

    GitHubCrawler is a threaded singleton that queries GitHub's API for urls
    to its public repositories, which it inserts into a :class:`Queue.Queue`
    shared with :class:`indexer.GitIndexer`.

    :ivar clone_queue: (:class:`Queue.Queue`) Contains :class:`GitRepository`
    with repository metadata retrieved by :class:`GitHubCrawler`, and other Git
    crawlers, to be processed by :class:`indexer.GitIndexer`.
    """

    def __init__(self, clone_queue):
        """
        Create an instance of the singleton `GitHubCrawler`.

        :param clone_queue: see :attr:`self.clone_queue`

        :type clone_queue: see :attr:`self.clone_queue`
        """

        self.clone_queue = clone_queue
        # logging.info("Starting %s." % self.__class__.__name__)
        super(GitHubCrawler, self).__init__(name=self.__class__.__name__)

    def run(self):
        """
        Query the GitHub API for data about every public repository.

        Pull all of GitHub's repositories by making calls to its API in a loop,
        accessing a subsequent page of results via the "next" URL returned in an
        API response header. Uses Severyn Kozak's (sevko) authentication
        credentials. For every new repository, a :class:`GitRepository` is
        inserted into :attr:`self.clone_queue`.
        """

        next_api_url = "https://api.github.com/repositories"
        authentication_params = {
            "client_id" : "436cb884ae09be7f2a4e",
            "client_secret" : "8deeefbc2439409c5b7a092fd086772fe8b1f24e"
        }
        api_request_interval = 5e3 / 60 ** 2

        while len(next_api_url) > 0:
            start_time = time.time()
            response = requests.get(next_api_url, params=authentication_params)

            queue_percent_full = (float(self.clone_queue.qsize()) /
                    self.clone_queue.maxsize) * 100
            # logging.info("API call made. Limit remaining: %s. Queue-size: (%d"
                    # "%%) %d/%d" % (response.headers["x-ratelimit-remaining"],
                    # queue_percent_full, self.clone_queue.qsize(),
                    # self.clone_queue.maxsize))

            for repo in response.json():
                while self.clone_queue.full():
                    time.sleep(1)

                self.clone_queue.put(indexer.GitRepository(
                        repo["html_url"], repo["full_name"].replace("/", ""),
                        "GitHub"))

            if int(response.headers["x-ratelimit-remaining"]) == 0:
                time.sleep(int(response.headers["x-ratelimit-reset"]) -
                           time.time())

            next_api_url = response.headers["link"].split(">")[0][1:]

            sleep_time = api_request_interval - (time.time() - start_time)
            if sleep_time > 0:
                time.sleep(sleep_time)

class BitbucketCrawler(threading.Thread):
    """
    Crawler that retrieves links to all of Bitbucket's public repositories.

    BitbucketCrawler is a threaded singleton that queries Bitbucket's API for
    urls to its public repositories, and inserts them as
    :class:`indexer.GitRepository` into a :class:`Queue.Queue` shared with
    :class:`indexer.GitIndexer`.

    :ivar clone_queue: (:class:`Queue.Queue`) The shared queue to insert
        :class:`indexer.GitRepository` repository urls into.
    """

    def __init__(self, clone_queue):
        """
        Create an instance of the singleton `BitbucketCrawler`.

        :param clone_queue: see :attr:`self.clone_queue`

        :type clone_queue: see :attr:`self.clone_queue`
        """

        self.clone_queue = clone_queue
        # logging.info("Starting %s." % self.__class__.__name__)
        super(BitbucketCrawler, self).__init__(name=self.__class__.__name__)

    def run(self):
        """
        Query  the Bitbucket API for data about every public repository.

        Query the Bitbucket API's "/repositories" endpoint and read its
        paginated responses in a loop; any "git" repositories have their
        clone-urls and names inserted into a :class:`indexer.GitRepository` in
        :attr:`self.clone_queue`.
        """

        next_api_url = "https://api.bitbucket.org/2.0/repositories"

        while True:
            response = requests.get(next_api_url).json()

            queue_percent_full = (float(self.clone_queue.qsize()) /
                    self.clone_queue.maxsize) * 100
            # logging.info("API call made. Queue-size: (%d%%) %d/%d" % (
                # queue_percent_full, self.clone_queue.qsize(),
                # self.clone_queue.maxsize))

            for repo in response["values"]:
                if repo["scm"] == "git":
                    while self.clone_queue.full():
                        time.sleep(1)

                    clone_links = repo["links"]["clone"]
                    clone_url = (clone[0]["href"] if clone[0]["name"] == "https"
                             else clone[1]["href"])
                    links.append("clone_url")
                    self.clone_queue.put(indexer.GitRepository(
                        clone_url, repo["full_name"], "Bitbucket"))

            next_api_url = response["next"]
