== Installation:

Install the python library and git porcelain script
$ sudo python setup.py install

Then link the porcelain into git-core
$ sudo sapling.py --install

Get help
$ git sap -h

== Development:

To run all tests, you can use something like:
$ PYTHONPATH=$PYTHONPATH:. py.test test/*.py -v

