from ..repository.manager import RepositoryManager

class Service:
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager