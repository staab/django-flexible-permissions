# How to contribute

Here are a few guidelines to follow when contributing to Flexible Permissions.

## Getting Started

* Make sure you have a [GitHub account](https://github.com/signup/free)
* Submit an issue for your issue, assuming one does not already exist.
  * Clearly describe the issue including steps to reproduce when it is a bug.
  * Make sure you fill in the earliest version that you know has the issue.
* Fork the repository on GitHub

## Making Changes

* Create a feature branch from where you want to base your work.
  * The base branch is usually the master branch.
  * To quickly create a topic branch based on master; `git checkout -b
    feature/my_contribution master`. Please avoid working directly on the
    `master` branch.
* Make commits of logical units.
* Make sure your commit messages are succinct and helpful, and have a reference to related issues, using a "#" symbol and the issue number.
* Make sure you have added the necessary tests for your changes.
* Run _all_ the tests to assure nothing else was accidentally broken.

## Making Trivial Changes

### Documentation

For changes of a trivial nature to comments and documentation, it is not
always necessary to create a new issue on GitHub.

## Submitting Changes

* Push your changes to a feature branch in your fork of the repository.
* Submit a pull request to the repository.
* Update your GitHub issue to mark that you have submitted code and are ready for it to be reviewed.
  * Include a link to the pull request in the ticket.