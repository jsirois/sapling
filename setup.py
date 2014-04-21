from setuptools import setup

from sapversion import version

setup(
    name = 'sapling',
    version = version(),

    author = 'John Sirois',
    author_email = 'john.sirois@gmail.com',
    description = 'A git porcelain to manage bidirectional subtree syncing with foreign git '
                  'repositories',
    license = 'Apache License Version 2.0',
    url = 'http://github.com/jsirois/sapling',

    provides = 'sapling',
    install_requires = (
      'gitdb >= 0.5.1',
      'GitPython > 0.2, < 0.4',
    ),

    packages = [ 'saplib', 'sapversion' ],
    package_data = { 'sapversion': [ 'version.txt' ] },
    scripts = [ 'sapling.py' ],

    classifiers = [
      'Programming Language :: Python',
      'Programming Language :: Python :: 2.6',
      'Development Status :: 2 - Pre-Alpha',
      'Environment :: Console',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: Apache Software License',

      # TODO(jsirois): the sapling.py --install action is actually unix/symlink dependant -
      # perhaps detect windows and just copy the sapling.py script to git-core/git-sap ?
      'Operating System :: OS Independent',

      'Topic :: Software Development :: Version Control'
    ],
)
