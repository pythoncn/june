# Contributing

First, please do contribute! There are three ways to contribute:

- introduce June to your friends
- discuss June, and submit bugs with Github issues
- send patch with Github pull request


## Codebase

You should follow the code style.

A little hint to make things simple:

- when you cloned this repo, run `make`, it will prepare everything for you
- check the code style with `make lint`
- check the test case with `make testing`


## Writing Patches / Sending Pull Requests

Consider contributing patches back to June? That's great. Here are some basic principles that will help maintainers / reviewers and your future self:

- break your changes to separate patches
- a patch should include only one functional change / fix
- state clear what's changed and why it should be changed like that in commit message
- arrange your patches so they don't break bisection

Following the above principles, you should be able to:

- run `git log` and know exactly what's going on in each patch without even looking at the code
- run `git bisect` and easily find out which commit breaks things


## Basic Git Workflow

You should always create a dedicated branch for your need, whether it's for bug fix or new feature. Then you should rebase your changes on top of upstream master branch before sending pull request.

Example of workflow ("origin" refers to upstream remote):

```
$ git branch [feature-name]
$ git checkout [feature-name]
...DEVELOPMENT...
$ git fetch origin
$ git rebase origin/master
$ git push [your-repository] [feature-name]
```

It's all set! After that you can send a pull request to upstream.

## Checklist

We are still in development, and this is a total rewrite of June in Flask.
