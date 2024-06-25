from azure.storage.queue import QueueServiceClient, QueueClient, QueueMessage
from azure.core.exceptions import ResourceExistsError

class AzureQueueService:
    def __init__(self, 
                 account_name,
                 account_key,queue_name):
        self.queue_service_client = QueueServiceClient(account_url=f"https://{account_name}.queue.core.windows.net/",
                                                       credential=account_key)
        self.queue_client = self.queue_service_client.get_queue_client(queue_name)
        
    def create_queue(self):
        try:
            self.queue_client.create_queue()
        except ResourceExistsError:
            print(f"The queue '{self.queue_client.queue_name}' already exists.")

    def send_message(self, message):
        if not message:
            raise ValueError("Message cannot be empty")
        self.queue_client.send_message(message)

    def receive_message(self):
        messages = self.queue_client.receive_messages(messages_per_page=1,
                                                      visibility_timeout=1)
        message = next(messages, None)
        return message

    def receive_messages(self, max_messages):
        if max_messages <= 0:
            raise ValueError("Max messages must be greater than 0")
        messages = self.queue_client.receive_messages(messages_per_page=max_messages)
        return [message for message in messages]

    def delete_message(self, message):
        if not message:
            raise ValueError("Message cannot be empty")
        self.queue_client.delete_message(message.id, message.pop_receipt)

    def peek_message(self):
        messages = self.queue_client.peek_messages(max_messages=1)
        message = next(messages, None)
        return message

    def peek_messages(self, max_messages):
        if max_messages <= 0:
            raise ValueError("Max messages must be greater than 0")
        messages = self.queue_client.peek_messages(max_messages=max_messages)
        return [message for message in messages]
