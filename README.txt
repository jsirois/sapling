== Installation:

To install the python library you can do one of the following:
1.) use easy_install to install from the PyPI registry: http://pypi.python.org/pypi/sapling
$ sudo easy_install sapling
2.) use pip to install from PyPI
$ sudo pip install sapling
3.) Or you can get the source distribution and run the following from its root:
$ sudo python setup.py install

Then to link the porcelain into git-core, do:
$ sudo sapling.py --install

Get help
$ git sap -h

== Configuration

Sapling (git sap) is configured with a .saplings file at the root of your git repository.  Here's
an example .saplings configuration for a scala project with common component and a hack component
that uses it:

common = {
  # The logical name of the split - listed by git sap.
  'name': 'common',

  # The paths that comprise this split.  These paths will form the saplings split from and merged
  # into your repository when using git sap --split and git sap --merge respectively
  'paths': [
    'project',
    'src/main/scala/com/twitter/common',
    'src/main/resources/com/twitter/common',
    'src/test/scala/com/twitter/common',
  ]
}

hack = {
  'name': 'hack',
  'paths': [
    'project',
    'src/main/scala/com/twitter/hack',
  ]
}

# This is all git sap looks for - a list of splits named 'splits'.  Each split in the list must be
# a dict with the keys shown/described above.
splits = [
  common,
  hack
]

== Use

To verify your .saplings is correct, you can view the current splits (assuming .saplings above)
with:
$ git sap
common
hack

You could split out the common split to a new repo like so:
$ git sap --split common
$ git push git@github.com:jsirois/common.git sapling_split_common:master

You can merge changes back in from a split branch or repo using standard git tools:
$ git pull git@github.com:jsirois/common.git master

This will maintain a parallel history of changes to the split which can make for confusing looking
"double commits".  An alternative that allows for more controlled imports is to apply patches from
the split onto the mainline using a combination of:
1.) (split branch)$ git format-patch ... \
  --ignore-if-in-upstream ..[remote split tracking branch] > /tmp/mbox
2.) (master)$ git am -k ... < /tmp/mbox

== Development:

To run all tests, you can use something like:
$ PYTHONPATH=$PYTHONPATH:. py.test test/*.py -v

== Known Issues:

There is no way currently to do differential splits.  Although a split for fixed branch/split config
will always produce the same split branch (identical shas), it will always re-run over the entire
source branch which can take a long time for big branches.

== Roadmap:

0.1.x
 + support differential splitting
 + built in support for patch merging strategy

