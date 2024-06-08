# Merge Request Labels

NOC development process is organized around [Merge Requests](https://docs.gitlab.com/ee/user/project/merge_requests/)
and is relying on [Labels](https://docs.gitlab.com/ee/user/project/labels.html).

[pri::*](#priority), [comp::*](#complexity)
and [kind](#kind) labels are required for every MR
to denote priority, complexity and kind of changes. Depending
of change additional [affected subsystems labels](#affected-subsystems-labels)
may be required.

## Affected Subsystems Labels

Following labels shows subsystems affected by MR. Any combination of labels is possible:

* `ansible` - Ansible Playbook
* `collections` - collections
* `core` - core modules
* `confdb` - [ConfDB syntax](../confdb-reference/query.md)
* `documentation` - documentation
* `ui` - User Interface
* `profiles` - SA Profiles
* `migration` - Database migrations
* `tests` - Unittests
* `nbi` - [NBI API](../nbi-api-reference/index.md)
* `rust` - Rust infrastructure and modules

## Priority

MR must be assigned with one of `pri::*` labels:

* `pri::p1` - Top priority, MR fixes critical problem affecting
  existing installations and must be reviewed, tested and merged
  as soon as possible
* `pri::p2` - High priority. MR fixes bug affecting existing installations.
  Though the workaround exists, MR should be processed in priority order
* `pri::p3` - Normal priority. MR should be processed in usual order
* `pri::p4` - Low priority. Insignificant cosmetic changes which
  can be processed in background order

Use `pri::p3` label if no other reasons present.

## Complexity

MR must be assigned with one of `comp::*` labels to denote
estimated complexity to reviewers and testers:

* `comp::trivial` - Trivial changes which can take up to 5 minutes
  to review and up to 15 minutes to test
* `comp::low` - Changes which can take up to 1 hour to test
* `comp::medium` - Changes which can take up to 1 day to test
* `comp::high` - Most complicated changes

Use `comp::medium` label if unsure

## Kind

MR must be assigned with one of `kind::*` labels to denote changes type

* `kind::feature` - functional changes improving existing feature
  or adding new one
* `kind::improvement` - Non-functional changes, including code and infrastructure optimization,
  requirements updates or additional documentation
* `kind::bug` - Bugfix
* `kind::cleanup` - Code cleanup. Non-functional changes not affecting existing behavior,
  like code formatting

## Backport

`backport` label means MR to be cherry-picked and backported
to previous generations. `backport` label is applicable only
to `kind::bug` label according to [Release Policy](../release-policy/index.md).
