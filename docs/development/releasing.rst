******************
Release Procedures
******************

The current release procedure for Astropy involves a combination of an
automated release script and some manual steps.  Future versions will automate
more of the process, if not all.

There are several different procedures below, depending on the situation:

* :ref:`release-procedure`
    - :ref:`release-procedure-beta-rc`
* :ref:`release-procedure-new-major`
* :ref:`release-procedure-bug-fix`
    - :ref:`release-procedure-bug-fix-backport`
    - :ref:`release-procedure-bug-fix-direct`
    - :ref:`release-procedure-bug-fix-release`

For a signed release, see :ref:`key-signing-info` for relevant setup
instructions.


.. _release-procedure:

Standard Release Procedure
==========================

This is the standard release procedure for releasing Astropy (or affiliated
packages that use the full bugfix/maintenance branch approach.)

#. Create a GitHub milestone for the next bugfix version, move any remaining
   issues from the version you are about to release, and close the milestone.
   When releasing a major release, close the last milestone on the previous
   maintenance branch, too.

   .. note::

      Creation of new milestone can be done as early as when you ping
      maintainers about their relevant pull requests, so that the maintainers
      have the option to re-milestone their work.

#. If there are any issues in the GitHub issue tracker that are labeled
   ``affects-dev`` but are issues that apply to this release, update them to
   ``affects-release``.  Similarly, if any issues remain open for this release,
   re-assign them to the next relevant milestone.

#. (Only for major versions) Make sure to update the "What's new"
   section with the stats on the number of issues, PRs, and contributors.  For
   the first two, the `astropy-procedures repository`_ script ``gh_issuereport.py``
   can provide the numbers since the last major release.  For the final one, you
   will likely need to update the Astropy ``.mailmap`` file, as there are often
   contributors who are not careful about using the same e-mail address for
   every commit.  The easiest way to do this is to run the command
   ``git shortlog -n -s -e`` to see the list of all contributors and their email
   addresses.  Look for any misnamed entries or duplicates, and add them to the
   ``.mailmap`` file (matched to the appropriate canonical name/email address.)
   Once you have finished this, you can count the number of lines in
   ``git shortlog -s`` to get the final contributor count.

#. Also be sure to update the ``docs/credits.rst`` file to include any new
   contributors from the above step. (This
   step is only required on major releases, but can be done for bugfix releases
   as time allows.)

#. (astropy specific) Ensure the built-in IERS earth rotation parameter and
   leap second tables are up to date by changing directory to
   ``astropy/utils/iers/data`` and executing ``update_builtin_iers.sh``.
   Check the result with ``git diff`` (do not be surprised to find many lines
   in the ``eopc04_IAU2000.62-now`` file change; those data are reanalyzed
   periodically) and committing.

#. Ensure you have a GPG key pair available for when git needs to sign the
   tag you create for the release.  See :ref:`key-signing-info` for more on
   this.

#. Obtain a *clean* version of the `astropy core repository`_.  That is, one
   where you don't have any intermediate build files.  Either use a fresh
   ``git clone`` or do ``git clean -dfx``.

#. Be sure you're on the branch appropriate for the version you're about to
   release.  For example, if releasing version 1.2.2 make sure to::

      $ git checkout v1.2.x

#. Make sure that the continuous integration services (e.g., GitHub Actions or CircleCI) are passing
   for the `astropy core repository`_ branch you are going to release. Also check that
   the `Azure core package pipeline`_ which builds wheels on the ``v*`` branches is passing.
   You may also want to locally run the tests (with remote data on to ensure all
   of the tests actually run), using tox to do a thorough test in an isolated
   environment::

      $ pip install tox --upgrade
      $ TEST_READ_HUGE_FILE=1 tox -e test-alldeps -- --remote-data=any

#. Render the changelog with towncrier, and confirm that the fragments can be
   deleted. (Note: update this when doing the next release!)
   ::

       towncrier [--draft] --version 4.3

#. Then add and commit those changes with::

      $ git add CHANGES.rst
      $ git commit -m "Finalizing changelog for v<version>"

#. Push the branch back to GitHub, e.g.::

      $ git push upstream v1.2.x

   and make sure that the CI services mentioned above (includnig the Azure pipeline)
   are still passing.

   .. note::

      You may need to replace ``upstream`` here with ``astropy`` or
      whatever remote name you use for the `astropy core repository`_.

#. Tag the commit with ``v<version>``, being certain to sign the tag with the
   ``-s`` option::

      $ git tag -s v<version> -m "Tagging v<version>"

#. Push up the tag to the `astropy core repository`_::

      $ git push upstream v<tag version>

   .. note::

      You may need to replace ``upstream`` here with ``astropy`` or
      whatever remote name you use for the `astropy core repository`_.
      Also, it might be tempting to use the ``--tags`` argument to ``git push``,
      but this should *not* be done, as it might push up some unintended tags.

   At this point if all goes well, the wheels and sdist will be build
   in the `Azure core package pipeline`_ and uploaded to PyPI!

#. In the event there are any issues with the wheel building for the tag
   (which shouldn't really happen if it was passing for the release branch),
   you'll have to fix whatever the problem is. First you will need to back out
   the release procedure by dropping the commits you made for release and
   removing the tag you created::

      $ git reset --hard HEAD^^^^ # you could also use the SHA hash of the commit before your first changelog edit
      $ git tag -d v<version>

   .. note::

      Any re-pushing the same tag back out to GitHub hereafter would be
      a force-push.

  Once the sdist and wheels are uploaded, the release is done!

Congratulations!  You have completed the release! Now there are just a few
clean-up tasks to finalize the process.

.. _post-release-procedure:

Post-Release procedures
-----------------------

#. Push up these changes to the `astropy core repository`_::

      $ git push upstream v<version branch>.x

#. If this is a release of the current release (i.e., not an LTS supported along
   side a more recent version), update the "stable" branch to point to the new
   release::

      $ git checkout stable
      $ git reset --hard v<version>
      $ git push upstream stable --force

#. Update Readthedocs so that it builds docs for the version you just released.
   You'll find this in the "admin" tab, with checkboxes next to each github tag.
   Also verify that the ``stable`` Readthedocs version builds correctly for
   the new version (it should trigger automatically once you've done the
   previous step).

#. When releasing a patch release, also set the previous RTD version in the
   release history to "protected".  For example when releasing v1.1.2, set
   v1.1.1 to "protected".  This prevents the previous releases from
   cluttering the list of versions that users see in the version dropdown
   (the previous versions are still accessible by their URL though).

#. Update the Astropy web site by editing the ``index.html`` page at
   https://github.com/astropy/astropy.github.com by changing the "current
   version" link and/or updating the list of older versions if this is an LTS
   bugfix or a new major version.  You may also need to update the contributor
   list on the web site if you updated the ``docs/credits.rst`` at the outset.

#. Cherry-pick the commit rendering the changelog and deleting the fragments and
   open a PR to the astropy *main* branch. Note: updating this when doing the
   next release with towncrier.
   In the same PR, you also have to update ``docs/whatsnew/index.rst`` and
   ``docs/whatsnew/X.Y.rst`` to link to "what's new" documentation in the
   released RTD branch, using the existing text as example. See
   `PR#12073 <https://github.com/astropy/astropy/pull/12073>`_ for an example.

#. ``conda-forge`` has a bot that automatically opens
   a PR from a new PyPI (stable) release, which you need to follow up on and
   merge. Meanwhile, for a LTS release, you still have to manually open a PR
   at `astropy-feedstock <https://github.com/conda-forge/astropy-feedstock/>`_.
   This is similar to the process for wheels.
   When the ``conda-forge`` package is ready, email the Anaconda maintainers
   about the release(s) so they can update the versions in the default channels.
   Typically, you should wait to make sure ``conda-forge`` and possibly
   ``conda`` works before sending out the public announcement
   (so that users who want to try out the new version can do so with ``conda``).

#. Upload the release to Zenodo by creating a GitHub Release off the GitHub tag.
   Click on the tag in https://github.com/astropy/astropy/tags and then click on
   the "Edit tag" button on the upper right. The release title is the same as the
   tag. In the description, you can copy and paste a description from the previous
   release, as it should be a one-liner that points to ``CHANGES.rst``. When you
   are ready, click "Publish release" (the green button on bottom left).
   A webhook to Zenodo will be activated and the release will appear under
   https://doi.org/10.5281/zenodo.4670728 . If you encounter problems during this
   step, please contact the Astropy Coordination Committee.

#. Once the release(s) are available on the default ``conda`` channels,
   prepare the public announcement. Use the previous announcement as a
   template, but link to the release tag instead of ``stable``.
   For a new major release, you should coordinate with the Astropy Coordinators.
   Meanwhile, for a bugfix release, you can proceed to send out an email
   to the ``astropy-dev`` and Astropy mailing lists.

.. _release-procedure-beta-rc:

Modifications for a beta/release candidate release
--------------------------------------------------

For major releases, we do beta and/or release candidates to have a chance to
catch significant bugs before the true release. If the release you are
performing is this kind of pre-release, some of the above steps need to be
modified.

The primary modifications to the release procedure are:

* When entering tagging the release, include a ``b?`` or ``rc??`` suffix after
  the version number, e.g. "1.2b1" or "1.2rc1".  It is critical that you follow this
  numbering scheme (``X.Yb#`` or ``X.Y.Zrc#``), as it will ensure the release
  is ordered "before" the main release by various automated tools, and also
  tells PyPI that this is a "pre-release."
* Do not do steps in :ref:`post-release-procedure`.

Once a release candidate is available, create a new Wiki page under
`Astropy Project Wiki <https://github.com/astropy/astropy/wiki>`_ with the
title "vX.Y RC testing" (replace "X.Y" with the release number) using the
`wiki of a previous RC <https://github.com/astropy/astropy/wiki/v3.2-RC-testing>`_
as a template.

.. _release-procedure-new-major:

Performing a Feature Freeze/Branching new Major Versions
========================================================

As outlined in
`APE2 <https://github.com/astropy/astropy-APEs/blob/main/APE2.rst>`_, astropy
releases occur at regular intervals, but feature freezes occur well before the
actual release.  Feature freezes are also the time when the main branch's
development separates from the new major version's maintenance branch.  This
allows new development for the next major version to continue while the
soon-to-be-released version can focus on bug fixes and documentation updates.

The procedure for this is straightforward:

#. Update your local main branch to use to the latest version from github::

      $ git fetch upstream --tags
      $ git checkout -B main upstream/main

#. Create a new branch from main at the point you want the feature freeze to
   occur::

      $ git branch v<version>.x

#. Render the changelog with towncrier, as above.

#. Tag this commit using the next major version followed by ``.dev``. For example,
   if you have just branched ``4.0``, create the ``v4.1.dev`` tag on the commit
   adding the ``4.1`` section to the changelog::

      $ git tag -s "v<next_version>.dev" -m "Back to development: v<next_version>"

#. Also update the "what's new" section of the docs to include a section for the
   next major version.  E.g.::

      $ cp docs/whatsnew/<current_version>.rst docs/whatsnew/<next_version>.rst

   You'll then need to edit ``docs/whatsnew/<next_version>.rst``, removing all
   the content but leaving the basic structure.  You may also need  to
   replace the "by the numbers" numbers with "xxx" as a reminder to update them
   before the next release. Then add the new version to the top of
   ``docs/whatsnew/index.rst``, update the reference in ``docs/index.rst`` to
   point to the that version, and commit these changes ::

      $ git add docs/whatsnew/<next_version>.rst
      $ git add docs/whatsnew/index.rst
      $ git add docs/index.rst
      $ git commit -m "Added <next_version> whats new section"

#. Push all of these changes up to github::

      $ git push upstream v<version>.x:v<version>.x
      $ git push upstream main:main

   .. note::

      You may need to replace ``upstream`` here with ``astropy`` or
      whatever remote name you use for the `astropy core repository`_.

#. On the github issue tracker, add a new milestone for the next major version.

.. _release-procedure-bug-fix:

Maintaining Bug Fix Releases
============================

.. note::

   Always start with LTS release, followed by, if necessary, a bugfix for
   stable release. If the releases are not done in that order, the change log
   entries on what goes where can get mixed up.

Astropy releases, as recommended for most Python projects, follows a
<major>.<minor>.<micro> version scheme, where the "micro" version is also
known as a "bug fix" release.  Bug fix releases should not change any user-
visible interfaces.  They should only fix bugs on the previous major/minor
release and may also refactor internal APIs or include omissions from previous
releases--that is, features that were documented to exist but were accidentally
left out of the previous release. They may also include changes to docstrings
that enhance clarity but do not describe new features (e.g., more examples,
typo fixes, etc).

Bug fix releases are typically managed by maintaining one or more bug fix
branches separate from the main branch (the release procedure below discusses
creating these branches).  Typically, whenever an issue is fixed on the Astropy
main branch a decision must be made whether this is a fix that should be
included in the Astropy bug fix release.  Usually the answer to this question
is "yes", though there are some issues that may not apply to the bug fix
branch.  For example, it is not necessary to backport a fix to a new feature
that did not exist when the bug fix branch was first created.  New features
are never merged into the bug fix branch--only bug fixes; hence the name.

In rare cases a bug fix may be made directly into the bug fix branch without
going into the main branch first.  This may occur if a fix is made to a
feature that has been removed or rewritten in the development version and no
longer has the issue being fixed.  However, depending on how critical the bug
is it may be worth including in a bug fix release, as some users can be slow to
upgrade to new major/micro versions due to API changes.

Issues are assigned to an Astropy release by way of the Milestone feature in
the GitHub issue tracker.  At any given time there are at least two versions
under development: The next major/minor version, and the next bug fix release.
For example, at the time of writing there are two release milestones open:
v1.2.2 and v0.3.0.  In this case, v1.2.2 is the next bug fix release and all
issues that should include fixes in that release should be assigned that
milestone.  Any issues that implement new features would go into the v0.3.0
milestone--this is any work that goes in the main branch that should not
be backported.  For a more detailed set of guidelines on using milestones, see
:ref:`milestones-and-labels`.


.. _release-procedure-bug-fix-backport:

Backporting fixes from main
---------------------------

.. note::

    The changelog script in ``astropy-procedures`` (``pr_consistency`` scripts
    in particular) does not know about minor releases, thus please be careful.
    For example, let's say we have two branches (``main`` and ``v1.2.x``).
    Both 1.2.0 and 1.2.1 releases will come out of the same v1.2.x branch.
    If a PR for 1.2.1 is merged into ``main`` before 1.2.0 is released,
    it should not be backported into v1.2.x branch until after 1.2.0 is
    released, despite complaining from the aforementioned script.
    This situation only arises in a very narrow time frame after 1.2.0
    freeze but before its release.

Most fixes are backported using the ``git cherry-pick`` command, which applies
the diff from a single commit like a patch.  For the sake of example, say the
current bug fix branch is 'v1.2.x', and that a bug was fixed in main in a
commit ``abcd1234``.  In order to backport the fix, checkout the v1.2.x
branch (it's also good to make sure it's in sync with the
`astropy core repository`_) and cherry-pick the appropriate commit::

    $ git checkout v1.2.x
    $ git pull upstream v1.2.x
    $ git cherry-pick abcd1234

Sometimes a cherry-pick does not apply cleanly, since the bug fix branch
represents a different line of development.  This can be resolved like any
other merge conflict:  Edit the conflicted files by hand, and then run
``git commit`` and accept the default commit message.  If the fix being
cherry-picked has an associated changelog entry in a separate commit make
sure to backport that as well.

What if the issue required more than one commit to fix?  There are a few
possibilities for this.  The easiest is if the fix came in the form of a
pull request that was merged into the main branch.  Whenever GitHub merges
a pull request it generates a merge commit in the main branch.  This merge
commit represents the *full* difference of all the commits in the pull request
combined.  What this means is that it is only necessary to cherry-pick the
merge commit (this requires adding the ``-m 1`` option to the cherry-pick
command).  For example, if ``5678abcd`` is a merge commit::

    $ git checkout v1.2.x
    $ git pull upstream v1.2.x
    $ git cherry-pick -m 1 5678abcd

In fact, because Astropy emphasizes a pull request-based workflow, this is the
*most* common scenario for backporting bug fixes, and the one requiring the
least thought.  However, if you're not dealing with backporting a fix that was
not brought in as a pull request, read on.

.. seealso::

    :ref:`merge-commits-and-cherry-picks` for further explanation of the
    cherry-pick command and how it works with merge commits.

If not cherry-picking a merge commit there are still other options for dealing
with multiple commits.  The simplest, though potentially tedious, is to
run the cherry-pick command once for each commit in the correct order.
However, as of Git 1.7.2 it is possible to merge a range of commits like so::

    $ git cherry-pick 1234abcd..56789def

This works fine so long as the commits you want to pick are actually congruous
with each other.  In most cases this will be the case, though some bug fixes
will involve followup commits that need to back backported as well.  Most bug
fixes will have an issues associated with it in the issue tracker, so make sure
to reference all commits related to that issue in the commit message.  That way
it's harder for commits that need to be backported from getting lost.


.. _release-procedure-bug-fix-direct:

Making fixes directly to the bug fix branch
-------------------------------------------

As mentioned earlier in this section, in some cases a fix only applies to a bug
fix release, and is not applicable in the mainline development.  In this case
there are two choices:

1. An Astropy developer with commit access to the `astropy core repository`_ may
   check out the bug fix branch and commit and push your fix directly.

2. **Preferable**: You may also make a pull request through GitHub against the
   bug fix branch rather than against main.  Normally when making a pull
   request from a branch on your fork to the `astropy core repository`_, GitHub
   compares your branch to Astropy's main.  If you look on the left-hand
   side of the pull request page, under "base repo: astropy/astropy" there is
   a drop-down list labeled "base branch: main".  You can click on this
   drop-down and instead select the bug fix branch ("v1.2.x" for example). Then
   GitHub will instead compare your fix against that branch, and merge into
   that branch when the PR is accepted.


.. _release-procedure-bug-fix-release:

Preparing the bug fix branch for release
----------------------------------------

There are two primary steps that need to be taken before creating a bug fix
release. The rest of the procedure is the same as any other release as
described in :ref:`release-procedure` (although be sure to provide the
right version number).

1. Any existing fixes to the issues assigned to a release milestone (and older
   LTS releases, if there are any), must be included in the maintenance branch
   before release.

2. The Astropy changelog must be updated to list all issues--especially
   user-visible issues--fixed for the current release.  The changelog should
   be updated in the main branch, and then merged into the bug fix branch.
   Most issues *should* already have changelog entries for them. But
   occasionally these are forgotten, so if doesn't exist yet please add one in
   the process of backporting.  See :ref:`changelog-format` for more details.

To aid this process, there are a series of related scripts in the
`astropy-procedures repository`_, in the ``pr_consistency`` directory.  These scripts
essentially check that the above two conditions are met. Detailed documentation
for these scripts is given in their repository, but here we summarize the basic
workflow.  Run the scripts in order (they are numbered ``1.<something>.py``,
``2.<something>.py``, etc.), entering your github login credentials as needed
(if you are going to run them multiple times, using a ``~/.netrc`` file is
recommended - see `this Stack Overflow post
<https://stackoverflow.com/questions/5343068/is-there-a-way-to-cache-github-credentials-for-pushing-commits/18362082#18362082>`_
for more on how to do that, or
`a similar github help page <https://help.github.com/en/articles/caching-your-github-password-in-git>`_).
The script to actually check consistency should be run like::

    $ python 4.check_consistency.py > consistency.html

Which will generate a simple web page that shows all of the areas where either
a pull request was merged into main but is *not* in the relevant release that
it has been milestoned for, as well as any changelog irregularities (i.e., PRs
that are in the wrong section for what the github milestone indicates).  You'll
want to correct those irregularities *first* before starting the backport
process (re-running the scripts in order as needed).

The end of the ``consistency.html`` page will then show a series of
``git cherry-pick`` commands to update the maintenance branch with the PRs that
are needed to make the milestones and branches consistent.  Make sure you're in
the correct maintenance branch with e.g.,

::

    $ git checkout v1.3.x
    $ git pull upstream v1.3.x  # Or possibly a rebase if conflicts exist

if you are doing bugfixes for the 1.3.x series. Go through the commands one at a
time, following the cherry-picking procedure described above. If for some reason
you determine the github milestone was in error and the backporting is
impossible, re-label the issue on github and move on.  Also, whenever you
backport a PR, it's useful to leave a comment in the issue along the lines of
"backported this to v1.3.x as <SHA>" so that it's clear that the backport
happened to others who might later look.

.. warning::

    Automated scripts are never perfect, and can either miss issues that need to
    be backported, or in some cases can report false positives.

    It's always a good idea before finalizing a bug fix release to look on
    GitHub through the list of closed issues in the release milestone and check
    that each one has a fix in the bug fix branch.  Usually a quick way to do
    this is for each issue to run::

        $ git log --oneline <bugfix-branch> | grep #<issue>

    Most fixes will mention their related issue in the commit message, so this
    tends to be pretty reliable.  Some issues won't show up in the commit log,
    however, as their fix is in a separate pull request.  Usually GitHub makes
    this clear by cross-referencing the issue with its PR.

Finally, not all issues assigned to a release milestone need to be fixed before
making that release.  Usually, in the interest of getting a release with
existing fixes out within some schedule, it's best to triage issues that won't
be fixed soon to a new release milestone.  If the upcoming bug fix release is
'v1.2.2', then go ahead and create a 'v1.2.3' milestone and reassign to it any
issues that you don't expect to be fixed in time for 'v1.2.2'.

.. _key-signing-info:

Creating a GPG Signing Key and a Signed Tag
===========================================

One of the main steps in performing a release is to create a tag in the git
repository representing the exact state of the repository that represents the
version being released.  For Astropy we will always use `signed tags`_: A
signed tag is annotated with the name and e-mail address of the signer, a date
and time, and a checksum of the code in the tag.  This information is then
signed with a GPG private key and stored in the repository.

Using a signed tag ensures the integrity of the contents of that tag for the
future.  On a distributed VCS like git, anyone can create a tag of Astropy
called "0.1" in their repository--and where it's easy to monkey around even
after the tag has been created.  But only one "0.1" will be signed by one of
the Astropy Project coordinators and will be verifiable with their public key.

Generating a public/private key pair
------------------------------------

Git uses GPG to created signed tags, so in order to perform an Astropy release
you will need GPG installed and will have to generated a signing key pair.
Most \*NIX installations come with GPG installed by default (as it is used to
verify the integrity of system packages).  If you don't have the ``gpg``
command, consult the documentation for your system on how to install it.

For OSX, GPG can be installed from MacPorts using ``sudo port install gnupg``.

To create a new public/private key pair, run::

    $ gpg --gen-key

This will take you through a few interactive steps. For the encryption
and expiry settings, it should be safe to use the default settings (I use
a key size of 4096 just because what does a couple extra kilobytes
hurt?) Enter your full name, preferably including your middle name or
middle initial, and an e-mail address that you expect to be active for a
decent amount of time. Note that this name and e-mail address must match
the info you provide as your git configuration, so you should either
choose the same name/e-mail address when you create your key, or update
your git configuration to match the key info. Finally, choose a very good
pass phrase that won't be easily subject to brute force attacks.


If you expect to use the same key for some time, it's good to make a backup of
both your public and private key::

    $ gpg --export --armor > public.key
    $ gpg --export-secret-key --armor > private.key

Back up these files to a trusted location--preferably a write-once physical
medium that can be stored safely somewhere.  One may also back up their keys to
a trusted online encrypted storage, though some might not find that secure
enough--it's up to you and what you're comfortable with.

Add your public key to a keyserver
----------------------------------
Now that you have a public key, you can publish this anywhere you like--in your
e-mail, in a public code repository, etc.  You can also upload it to a
dedicated public OpenPGP keyserver.  This will store the public key
indefinitely (until you manually revoke it), and will be automatically synced
with other keyservers around the world.  That makes it easy to retrieve your
public key using the gpg command-line tool.

To do this you will need your public key's keyname.  To find this enter::

    $ gpg --list-keys

This will output something like::

    /path/to/.gnupg/pubring.gpg
    ---------------------------------------------
    pub   4096D/1234ABCD 2012-01-01
    uid                  Your Name <your_email>
    sub   4096g/567890EF 2012-01-01

The 8 digit hex number on the line starting with "pub"--in this example the
"1234ABCD" unique keyname for your public key.  To push it to a keyserver
enter::

    $ gpg --send-keys 1234ABCD

But replace the 1234ABCD with the keyname for your public key.  Most systems
come configured with a sensible default keyserver, so you shouldn't have to
specify any more than that.

Create a tag
------------
Now test creating a signed tag in git.  It's safe to experiment with this--you
can always delete the tag before pushing it to a remote repository::

    $ git tag -s v0.1 -m "Astropy version 0.1"

This will ask for the password to unlock your private key in order to sign
the tag with it.  Confirm that the default signing key selected by git is the
correct one (it will be if you only have one key).

Once the tag has been created, you can verify it with::

    $ git tag -v v0.1

This should output something like::

    object e8e3e3edc82b02f2088f4e974dbd2fe820c0d934
    type commit
    tag v0.1
    tagger Your Name <your_email> 1339779534 -0400

    Astropy version 0.1
    gpg: Signature made Fri 15 Jun 2012 12:59:04 PM EDT using DSA key ID 0123ABCD
    gpg: Good signature from "Your Name <your_email>"

You can use this to verify signed tags from any repository as long as you have
the signer's public key in your keyring.  In this case you signed the tag
yourself, so you already have your public key.

Note that if you are planning to do a release following the steps below, you
will want to delete the tag you just created, because the release script does
that for you.  You can delete this tag by doing::

    $ git tag -d v0.1


.. _astropy core repository: https://github.com/astropy/astropy
.. _signed tags: https://git-scm.com/book/en/v2/Git-Basics-Tagging#Signed-Tags
.. _cython: http://www.cython.org/
.. _astropy-procedures repository: https://github.com/astropy/astropy-procedures
.. _Anaconda: https://conda.io/docs/
.. _twine: https://packaging.python.org/key_projects/#twine
.. _Azure core package pipeline: https://dev.azure.com/astropy-project/astropy/_build
