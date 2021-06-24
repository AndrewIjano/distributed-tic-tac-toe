# Distributed Tic-Tac-Toe Protocol -- DT3P

## Commands

### General structure

```
request := command <SP> argument <LF>

response := resp_code <SP> argument <LF>

argument :=  ITEM<HT>ITEM<LF> argument | ITEM | ""

command := USER | PASS | LGIN | LEAD | LIST | BGIN
    | SEND | ENDD | LOUT | HTBT | RSLT | ADDR | PING | PONG

resp_code := 200_OK | 201_CREATED | 401_UNAUTHENTICATED | 402_NOT_ACTIVE 

```


USER
PASS
LGIN
LEAD
LIST
BGIN
SEND
DLAY
ENDD
LOUT
EXIT

HTBT
LTNC
TBLE
RSLT
