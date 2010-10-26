from git.repo.base import Repo
from unittest import TestCase

class TestSequenceFunctions(TestCase):
    def test_open_repo(self):
        self.assertTrue(len(Repo().branches) > 0)
