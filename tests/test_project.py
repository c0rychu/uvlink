"""Test for uvlink/project.py"""

from uvlink.project import Project


class TestProject:
    def test_hash_path(self):
        assert Project.hash_path("/") == "8a5edab28263"
