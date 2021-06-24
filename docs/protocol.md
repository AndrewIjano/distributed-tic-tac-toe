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

### Client-server

```
LIST\n
LEAD\n
ADDR <user>\n
RSLT <user1> <user2> <foi empate>\n
USER <user> <password>\n
PASS <user> <password> <user2>\n
LGIN <user> <password>\n
LOUT <user> <password>\n
HTBT\n
```

### Reponse examples
```
200_OK user1 0\tuser2 1\n
401_UNAUTHENTICATED\n
```
### P2P
```
SEND <row> <column>\n
BGIN <username>\n
ENDD\n
PING\n
PONG\n
ACPT (WAIT|PLAY)\n
```