# app/exceptions.py
class CustomExceptionA(Exception):
    def __init__(self, detail: str = "Condition A failed"):
        self.detail = detail
        self.status_code = 400

class CustomExceptionB(Exception):
    def __init__(self, detail: str = "Resource not found"):
        self.detail = detail
        self.status_code = 404