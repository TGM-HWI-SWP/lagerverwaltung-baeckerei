import os

from ..adapters.repository import RepositoryFactory
from ..services import WarehouseService

repository_type = os.getenv("REPOSITORY_TYPE", "memory")
_repository = RepositoryFactory.create_repository(repository_type)
service = WarehouseService(_repository)
