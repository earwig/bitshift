"""
:synopsis: Parent crawler module, which supervises all crawlers.

Contains functions for initializing all subsidiary, threaded crawlers.
"""

import Queue

from bitshift.crawler import crawler
from bitshift.crawler import git_indexer

__all__ = ["crawl"]

MAX_URL_QUEUE_SIZE = 5e3

def crawl():
    """
    Initialize all crawlers (and indexers).

    Start the:
    1. GitHub crawler, :class:`bitshift.crawler.crawler.GitHubCrawler`
    2. Git indexer, :class:`bitshift.crawler.git_indexer.GitIndexer`
    """

    repository_queue = Queue.Queue(maxsize=MAX_URL_QUEUE_SIZE)
    github_crawler = crawler.GitHubCrawler(repository_queue)
    indexer = git_indexer.GitIndexer(repository_queue)

    for thread in [github_crawler, indexer]:
        thread.start()
