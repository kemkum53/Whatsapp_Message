from colorama import Fore as f

class TimeOutException(Exception):
    def __init__(self, message:str, code:int):
        self.message = f.RED + f'[ERR-T{str(code)}]' + f.RESET + ' ' + message
        super().__init__(self.message)
        
class NotFoundException(Exception):
    def __init__(self, message:str, code:int):
        self.message = f.RED + f'[ERR-N{str(code)}]' + f.RESET + ' ' + message
        super().__init__(self.message)
        
class LoginException(Exception):
    def __init__(self, code:int):
        self.message = f.RED + f'[ERR-L{str(code)}]' + f.RESET + ' ' + 'Login failed.'
        super().__init__(self.message)

class BrowserClosedException(Exception):
    def __init__(self, code:int):
        self.message = f.RED + f'[ERR-B{str(code)}]' + f.RESET + ' ' + 'Browser closed unexpectedly.'
        super().__init__(self.message)