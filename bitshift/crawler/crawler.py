"""
:synopsis: Main crawler module, to oversee all site-specific crawlers.

Contains all website/framework-specific Class crawlers.
"""

import requests, time, threading

import bitshift.crawler.indexer

from ..codelet import Codelet
from ..database import Database

class GitHubCrawler(threading.Thread):
    """
    Crawler that retrieves links to all of GitHub's public repositories.

    GitHubCrawler is a threaded singleton that queries GitHub's API for URLs
    to its public repositories, which it inserts into a :class:`Queue.Queue`
    shared with :class:`bitshift.crawler.indexer.GitIndexer`.

    :ivar repository_queue: (:class:`Queue.Queue`) Contains dictionaries with
        repository information retrieved by `GitHubCrawler`, and other Git
        crawlers, to be processed by
        :class:`bitshift.crawler.indexer.GitIndexer`.
    """

    def __init__(self, repository_queue):
        """
        Create an instance of the singleton `GitHubCrawler`.

        :param repository_queue: A queue containing dictionaries of  repository
            metadata retrieved by `GitHubCrawler`, meant to be processed by an
            instance of :class:`bitshift.crawler.indexer.GitIndexer`.

            .. code-block:: python
                sample_dict = {
                    "url" : "https://github.com/user/repo",
                    "name" : "repo",
                    "framework_name" : "GitHub"
                }

        :type repository_queue: :class:`Queue.Queue`
        """

        self.repository_queue = repository_queue
        super(GitHubCrawler, self).__init__()

    def run(self):
        """
        Query the GitHub API for data about every public repository.

        Pull all of GitHub's repositories by making calls to its API in a loop,
        accessing a subsequent page of results via the "next" URL returned in an
        API response header. Uses Severyn Kozak's (sevko) authentication
        credentials.
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

            for repo in response.json():
                while self.repository_queue.full():
                    pass

                self.repository_queue.put({
                    "url" : repo["html_url"],
                    "name" : repo["name"],
                    "framework_name" : "GitHub"
                })

            if int(response.headers["x-ratelimit-remaining"]) == 0:
                time.sleep(int(response.headers["x-ratelimit-reset"]) -
                           time.time())

            next_api_url = response.headers["link"].split(">")[0][1:]

            sleep_time = api_request_interval - (time.time() - start_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
