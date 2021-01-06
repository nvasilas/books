# books

This is a Python 3.6+ script to open my collection of books, papers and manuals.
It is tested on Linux. It can work on Windows with little modifications.

It is expected that the folders are divided based on the subject of the books
and papers they contain. Also, both the files and the folders should follow a
predefined naming scheme.

## Naming scheme for Books/Papers

For folders the naming scheme is:

  `subject__keyword`

Notice the `__` to separate the subject and the keyword. For instance, if the
subject is optimization and the chosen keyword is opt then the name scheme would
be

  `optimzation__opt`

For files the name scheme is:

  `author1_author2__filename`

Again notice the `__` to separate the authors and the filename.

## Manuals

Just place the manual to a folder. There is no need for a specific naming scheme.


## Install

 - add this folder to `PYTHONPATH`
 - edit the scripts from `./bin` to specify the location of books, papers, etc.
 - copy the scripts from `./bin` to your `PATH`.
