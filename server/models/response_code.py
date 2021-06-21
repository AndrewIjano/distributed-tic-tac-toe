from enum import Enum

class ResponseCode(Enum):
    OK = "200_OK"
    CREATED = "201_CREATED"
    UNAUTHENTICATED = "401_UNAUTHENTICATED"
    NOT_ACTIVE = "402_NOT_ACTIVE"


    