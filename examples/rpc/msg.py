from rose import Message

class AddIntsReq(Message):
    a: int
    b: int

class AddIntsRes(Message):
    sum: int

class DivFloatsReq(Message):
    a: float
    b: float

class DivFloatsRes(Message):
    quotient: float
