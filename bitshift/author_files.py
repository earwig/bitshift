"""
Output author/date information about the latest files in a Git repository.

When executed inside a Git archive, prints a single line of metadata for every
file in the work tree. A given line contains the file's filename, authors,
and Unix timestamps for the file's time of creation and last modification; the
separate entries are null-delimited.

Sample output:
	socket_io.c\x00John Doe Jane Doe\x001384488690\x001384534626
	# filename: socket_io.c
	# Author Names:
"""

import fileinput, subprocess

git_log = subprocess.check_output("git --no-pager log --name-only \
	--pretty=format:'%n%n%an%n%at' -z", shell=True)

commits = []
for commit in git_log.split("\n\n"):
	fields = commit.split("\n")
	if len(fields) > 2:
		commits.append({
			"author" : fields[0],
			"timestamp" : int(fields[1]),
			"filenames" : fields[2].split("\0")[:-2]
		})


tracked_files = subprocess.check_output("perl -le 'for (@ARGV){ print if -f && \
	T }' $(find . -type d -name .git -prune -o -print)", shell=True)
tracked_files = [filename[2:] for filename in tracked_files.split("\n")[:-1]]

file_authors = {}
for commit in commits:
	for filename in commit["filenames"]:
		if filename in tracked_files:
			if filename not in file_authors.keys():
				file_authors[filename] = {
					"authors" : [commit["author"]],
					"timestamps" : [commit["timestamp"]]
				}
			else:
				if commit["author"] not in file_authors[filename]["authors"]:
					file_authors[filename]["authors"].append(commit["author"])
				file_authors[filename]["timestamps"].append(commit["timestamp"])

for filename in file_authors.keys():
	authors = "\0".join(file_authors[filename]["authors"])
	time_created = min(file_authors[filename]["timestamps"])
	time_last_modified = max(file_authors[filename]["timestamps"])
	print "%s\0%s\0%d\0%d" % (filename, authors, time_created, time_last_modified)
