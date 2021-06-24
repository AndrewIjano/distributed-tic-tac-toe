# Distributed Tic-Tac-Toe

A hybrid P2P system for a distributed tic-tac-toe game, made for the subject MAC0352 - Computer Network and Distributed Systems.

## Usage

### Server

Run the server passing its open data port `<port>` and protected data port `<port-tls>`:

```
    python server.py <port> <port-tls>
```

### Client

Run the client passing the host of the server (`localhost`) and its open data port `<port>` and protected data port `<port-tls>`:

For example, to run the broker on port 1883, execute:

```
    python client.py localhost <port> <port-tls>
    
```


## License

Licensed under the MIT license.
