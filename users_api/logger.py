import logging

class UsersLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create a console handler and set the level to INFO
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Create a formatter and add it to the handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        
        # Add the handler to the logger
        self.logger.addHandler(ch)
    
    def get_logger(self):
        return self.logger
