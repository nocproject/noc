

# test


## Name
`noc test` - Run testing suite

## Synopsis

    noc test run [-v|--verbose]
                 [--test-db=DBNAME]
                 [--coverage-report=PATH]
                 [--idea-bookmarks=PATH]
                 [--statistics]
                 [TEST_NAME ...]


## Description
Runs testing suite and reports errors or warnings.
Options:

* `-v|--verbose` - Verbose output
* `--test-db=DBNAME` - Use `DBNAME` as testing database. Generate temporary
    database when not set.
* `--coverage-report=PATH` - Generate coverage report to directory `PATH`.
    Coverage report is the set of self-containing user-viewable HTML files.
* `--idea-bookmarks=PATH` - Generate IntelliJ IDEA-compatible bookmarks XML
    containing links to all warnings noted during the test run. Resulting
    XML may be placed into the `<component name="BookmarkManager">` of
    `.idea/workspace.xml` file.
* `--statistics` - Dump detailed statistics summary on the end of the tests.
* `TEST_NAME` - Run all test suite when empty. May contain one or more
    item:
  * `path` - Run all tests from python file `path`
  * `path::func` - Run single testing function `func` from python file `path`

## Examples

    $ ./noc test

    $ ./noc test --summary

    $ ./noc test -v tests/test_0001_migrate.py::test_database_migrations

## See also
* `pytest documentation <https://docs.pytest.org/en/latest/>`_
