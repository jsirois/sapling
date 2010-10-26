from git.repo.base import Repo

def test_open_repo():
  assert len(Repo().branches) > 0
