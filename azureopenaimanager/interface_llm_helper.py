from abc import ABC, abstractmethod

class ILLMHelper(ABC):
    
    @abstractmethod
    def generate_answer(self, conversation):
        pass
    
    @abstractmethod
    def generate_answer_document(self, query):
        pass
    
    @abstractmethod
    def create_prompt(self, context, query):
        pass
    
    @abstractmethod
    def generate_reply_from_context(self, user_input, content, conversation):
        pass
    
    @abstractmethod
    def get_image_analysis(self, prompt, data):
        pass