import git

class RepoFixture(object):

  # TODO(jsirois): Provide a way to easily build up a temporary repo to use for tests instead of
  # assuming this project is housed in a git repo.

  def repo(self):
    return git.Repo()
