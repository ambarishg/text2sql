from abc import ABC, abstractmethod

class ILoadStatusHelper(ABC):
    
    @abstractmethod
    def get_file_load_status(self, filename: str, user_id: str, category: str):
        pass

    @abstractmethod
    def set_file_load_status(self, item_to_create: dict):
        pass
