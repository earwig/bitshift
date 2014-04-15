import Queue

from bitshift.crawler import crawler
from bitshift.crawler import git_indexer

__all__ = ["crawl"]

def crawl():
    repository_queue = Queue.Queue()
    github_crawler = crawler.GitHubCrawler(repository_queue)
    indexer = git_indexer.GitIndexer(repository_queue)

    for thread in [github_crawler, indexer]:
        thread.start()
