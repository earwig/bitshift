# Refresh database with test repos:
mysql bitshift -e "CALL empty_database();"
python -m bitshift.crawler.crawl earwig/mwparserfromhell earwig/earwigbot earwig/git-repo-updater earwig/bitshift sevko/.dotfiles sevko/stuybooks sevko/termcrate sevko/graphics-engine cahnda/tour-de-city Riamse/ceterach Hypersonic/Starlorn  # small-to-medium-sized repos with personal connections
python -m bitshift.crawler.crawl kennethreitz/requests rg3/youtube-dl pypa/pip ipython/ipython matplotlib/matplotlib mitsuhiko/flask python/cpython  # major python repos
python -m bitshift.crawler.crawl ruby/ruby rails/rails rubygems/rubygems jekyll/jekyll puppetlabs/puppet sass/sass Homebrew/homebrew  # major ruby repos
python -m bitshift.crawler.crawl ???  # major java repos

# Count codelets:
mysql bitshift -e "SELECT COUNT(*) AS 'number of codelets' FROM codelets;"

# Count repos:
mysql bitshift -e "SELECT COUNT(*) AS 'number of repos' FROM (SELECT 1 FROM codelets GROUP BY REPLACE(SUBSTRING(SUBSTRING_INDEX(codelet_name, ': ', 1), 1), ': ', '')) AS repos;"

# Show repos:
mysql bitshift -e "SELECT REPLACE(SUBSTRING(SUBSTRING_INDEX(codelet_name, ': ', 1), 1), ': ', '') AS repo, COUNT(*) AS 'number of codelets' FROM codelets GROUP BY repo ORDER BY COUNT(*) DESC;"
