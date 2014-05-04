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
    :ivar _logger: (:class:`logging.Logger`) A class-specific logger object.
    """

    AUTHENTICATION = {
        "client_id" : "436cb884ae09be7f2a4e",
        "client_secret" : "8deeefbc2439409c5b7a092fd086772fe8b1f24e"
    }

    def __init__(self, clone_queue):
        """
        Create an instance of the singleton `GitHubCrawler`.

        :param clone_queue: see :attr:`self.clone_queue`

        :type clone_queue: see :attr:`self.clone_queue`
        """

        self.clone_queue = clone_queue
        self._logger = logging.getLogger("%s.%s" %
                (__name__, self.__class__.__name__))
        self._logger.info("Starting.")
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
        api_request_interval = 5e3 / 60 ** 2

        while len(next_api_url) > 0:
            start_time = time.time()

            try:
                resp = requests.get(next_api_url, params=self.AUTHENTICATION)
            except ConnectionError as excep:
                self._logger.warning("API %s call failed: %s: %s",
                        next_api_url, excep.__class__.__name__, excep)
                time.sleep(0.5)
                continue

            queue_percent_full = (float(self.clone_queue.qsize()) /
                    self.clone_queue.maxsize) * 100
            self._logger.info("API call made. Queue size: %d/%d, %d%%." %
                    ((self.clone_queue.qsize(), self.clone_queue.maxsize,
                    queue_percent_full)))

            repo_names = [repo["full_name"] for repo in resp.json()]
            repo_stars = self._get_repositories_stars(repo_names)

            for repo in resp.json():
                while self.clone_queue.full():
                    time.sleep(1)

                self.clone_queue.put(indexer.GitRepository(
                        repo["html_url"], repo["full_name"].replace("/", ""),
                        "GitHub", repo_stars[repo["full_name"]]))

            if int(resp.headers["x-ratelimit-remaining"]) == 0:
                time.sleep(int(resp.headers["x-ratelimit-reset"]) -
                        time.time())

            next_api_url = resp.headers["link"].split(">")[0][1:]

            sleep_time = api_request_interval - (time.time() - start_time)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _get_repositories_stars(self, repo_names):
        """
        Return the number of stargazers for several repositories.

        Queries the GitHub API for the number of stargazers for any given
        repositories, and blocks if the query limit is exceeded.

        :param repo_names: An array of repository names, in
            `username/repository_name` format.

        :type repo_names: str

        :return: A dictionary with repository name keys, and corresponding
            stargazer count values.

            Example dictionary:
            .. code-block:: python
                {
                    "user/repository" : 100
                }

        :rtype: dictionary
        """

        API_URL = "https://api.github.com/search/repositories"
        REPOS_PER_QUERY = 25

        repo_stars = {}
        for names in [repo_names[ind:ind + REPOS_PER_QUERY] for ind in
                xrange(0, len(repo_names), REPOS_PER_QUERY)]:
            query_url = "%s?q=%s" % (API_URL,
                "+".join("repo:%s" % name for name in names))

            params = self.AUTHENTICATION
            resp = requests.get(query_url,
                    params=params,
                    headers={
                        "Accept" : "application/vnd.github.preview"
                    })

            if int(resp.headers["x-ratelimit-remaining"]) == 0:
                sleep_time = int(resp.headers["x-ratelimit-reset"]) - \
                        time.time() + 1
                if sleep_time > 0:
                    logging.info("API quota exceeded. Sleep time: %d." %
                            sleep_time)
                    time.sleep(sleep_time)

            for repo in resp.json()["items"]:
                rank = float(repo["stargazers_count"]) / 1000
                repo_stars[repo["full_name"]] = rank if rank < 1.0 else 1.0

        for name in repo_names:
            if name not in repo_stars:
                repo_stars[name] = 0.5

        return repo_stars

class BitbucketCrawler(threading.Thread):
    """
    Crawler that retrieves links to all of Bitbucket's public repositories.

    BitbucketCrawler is a threaded singleton that queries Bitbucket's API for
    urls to its public repositories, and inserts them as
    :class:`indexer.GitRepository` into a :class:`Queue.Queue` shared with
    :class:`indexer.GitIndexer`.

    :ivar clone_queue: (:class:`Queue.Queue`) The shared queue to insert
        :class:`indexer.GitRepository` repository urls into.
    :ivar _logger: (:class:`logging.Logger`) A class-specific logger object.
    """

    def __init__(self, clone_queue):
        """
        Create an instance of the singleton `BitbucketCrawler`.

        :param clone_queue: see :attr:`self.clone_queue`

        :type clone_queue: see :attr:`self.clone_queue`
        """

        self.clone_queue = clone_queue
        self._logger = logging.getLogger("%s.%s" %
                (__name__, self.__class__.__name__))
        self._logger.info("Starting.")
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
            try:
                response = requests.get(next_api_url).json()
            except ConnectionError as exception:
                time.sleep(0.5)
                self._logger.warning("API %s call failed: %s: %s",
                        next_api_url, excep.__class__.__name__, excep)
                continue

            queue_percent_full = (float(self.clone_queue.qsize()) /
                    self.clone_queue.maxsize) * 100
            self._logger.info("API call made. Queue size: %d/%d, %d%%." %
                    ((self.clone_queue.qsize(), self.clone_queue.maxsize,
                    queue_percent_full)))

            for repo in response["values"]:
                if repo["scm"] == "git":
                    while self.clone_queue.full():
                        time.sleep(1)

                    clone_links = repo["links"]["clone"]
                    clone_url = (clone_links[0]["href"] if
                            clone_links[0]["name"] == "https" else
                            clone_links[1]["href"])
                    links.append("clone_url")

                    try:
                        watchers = requests.get(
                                repo["links"]["watchers"]["href"])
                        rank = len(watchers.json()["values"]) / 100
                    except ConnectionError as exception:
                        time.sleep(0.5)
                        self._logger.warning("API %s call failed: %s: %s",
                                next_api_url, excep.__class__.__name__, excep)
                        continue

                    self.clone_queue.put(indexer.GitRepository(
                        clone_url, repo["full_name"], "Bitbucket"),
                        rank if rank < 1.0 else 1.0)

            next_api_url = response["next"]
            time.sleep(0.2)
