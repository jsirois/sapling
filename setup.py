from distutils.core import setup

setup(
    name = 'git-sap',
    version = '0.0.1',

    author = "John Sirois",
    author_email = "john.sirois@gmail.com",
    description = "A git porcelain to manage bidirectional subtree syncing with foreign git " +
                  "repositories",
    license = "Apache License Version 2.0",

    provides = "gitsap",
    requires = [
      "GitPython (>= 0.3)"
    ],

    packages = [ 'gitsap' ],
    scripts = [ 'git-sap.py' ],

    classifiers = [
      "Programming Language :: Python",
      "Programming Language :: Python :: 2.6",
      "Development Status :: 2 - Pre-Alpha",
      "Environment :: Console",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: Apache Software License",

      # TODO(jsirois): the git-sap.py --install action is actually unix/symlink dependant - perhaps
      # detect windows and just copy the git-sap.py script to git-core/git-sap ?
      "Operating System :: OS Independent",

      "Topic :: Software Development :: Version Control"
    ],
)
