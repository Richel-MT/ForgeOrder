from ..repository.manager import RepositoryManagerBase

class ServiceBase:
    def __init__(self, repositoryManager: RepositoryManagerBase):
        self.repositoryManager = repositoryManager

        self.repos = repositoryManager

