"""
:synopsis: Parent crawler module, which supervises all crawlers.

Contains functions for initializing all subsidiary, threaded crawlers.
"""

import logging, Queue

from bitshift.crawler import crawler, indexer

__all__ = ["crawl"]

def crawl():
    """
    Initialize all crawlers (and indexers).

    Start the:
    1. GitHub crawler, :class:`bitshift.crawler.crawler.GitHubCrawler`
    2. Git indexer, :class:`bitshift.crawler.indexer.GitIndexer`
    """

    MAX_URL_QUEUE_SIZE = 5e3
    DEBUG_FILE = "crawler.log"

    logging.basicConfig(filename=DEBUG_FILE,
            format="%(asctime)s:\t%(threadName)s:\t%(message)s",
            level=logging.DEBUG)

    repository_queue = Queue.Queue(maxsize=MAX_URL_QUEUE_SIZE)
    github_crawler = crawler.GitHubCrawler(repository_queue)
    git_indexer = indexer.GitIndexer(repository_queue)

    for thread in [github_crawler, git_indexer]:
        thread.start()
