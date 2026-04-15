# Networking 101

## Network Layers

Three key layes most of the time need to be understand:

- Network layer [Layer 3]
- Transport layer [Layer 4]
- Application layer [Layer 7]

Network layer:

This layer, IP layer, is responsible for support routing, addressing to the network, and packet forwarding.

- IP address:
  - Can be uniquely identified by a 32 bit number (IPv4) or 128 bit number (IPv6).

There are other protocol like infiband which is used to support high speed data transfer. But more of this discussion is in IP layer.

Transport layer:

This layer, TCP/UDP layer, is responsible for support connection, data transfer, and error detection, flow control, and retransmission.

- TCP:
- QUIC:
- UDP:

Application layer:

This layer, HTTP layer, is responsible for support client-server interaction, data exchange, and data processing.

Protocols like DNS, SMTP, HTTP, and SSH are all application layer protocols.

### What happens when you type a URL to visit a website?

```mermaid
sequenceDiagram
    participant Client
    participant DNS as "DNS Server"
    participant Server

    Client->>+DNS: DNS lookup
    DNS->>-Client: IP address of server

    Client->>Server: SYN
    Server->>Client: SYN-ACK
    Client->>Server: ACK
    Client->>Server: HTTP request
    Server->>Client: HTTP response
    Client->>Server: Data transfer
    Client->>Server: FIN
    Server->>Client: ACK
    Server->>Client: FIN
    Client->>Server: ACK
```

Steps:

1. DNS Resolution: The client starts by resolving the domain name of the website to an IP address using DNS (Domain Name System).
2. TCP Handshake: The client initiates a TCP connection with the server using a three-way handshake:
3. SYN: The client sends a SYN (synchronize) packet to the server to request a connection.
4. SYN-ACK: The server responds with a SYN-ACK (synchronize-acknowledge) packet to acknowledge the request.
5. ACK: The client sends an ACK (acknowledge) packet to establish the connection.
6. HTTP Request: Once the TCP connection is established, the client sends an HTTP GET request to the server to request the web page.
7. Server Processing: The server processes the request, retrieves the requested web page, and prepares an HTTP response. (This is usually the only latency most SWE's think about and control!)
8. HTTP Response: The server sends the HTTP response back to the client, which includes the requested web page content.
9. TCP Teardown: After the data transfer is complete, the client and server close the TCP connection using a four-way handshake:
10. FIN: The client sends a FIN (finish) packet to the server to terminate the connection.
11. ACK: The server acknowledges the FIN packet with an ACK.
12. FIN: The server sends a FIN packet to the client to terminate its side of the connection.
13. ACK: The client acknowledges the server's FIN packet with an ACK.

### Hidden activities

- Application layer dont need to know the reliablity and ordering how the packet arrives at the destination.
- Network layer need to know the reliability and ordering how the packet arrives at the destination which is basically addressed when using TCP.
- For DNS query you just get the IP address.
- Many request and response in this use case which add more latency and processing required.
- State of the client and server should be maintained. HTTP keep-alive or HTTP2-Multiplexing.

## Network layer

Dominated by IP protocl this layer responsible for routing and addressing.

- DHCP server: Gives the IP address on bootup for you node/host if it is configured to get it automatically.
- The IP address need to be unique to each node/host and if it is public facing it should be know to everyone. RIR (Registry of Internet Resources) is used to register the IP address.
- Public IP address: 0.0.0.0 to 89.0.142.86 and 237.84.2.178 to 244.178.44.111

## Transport layer

Dominated by TCP protocl this layer responsible for connection, data transfer, and error detection, flow control, and retransmission.

- UDP: User Datagram Protocol (Fast and unreliable)
The UDP packet received will tell source IP and port number and destination IP and port number. Remaining are binary blob.

Features of UDP are:

- Connectionless
- No guarantee of delivery
- No guarantee of order
- Lower Latency

Speed vs reliability tradeoff. If speed is needed pick UDP elese TCP.

Uses in:
    -   Online Games
    -   Video Streaming
    -   VOIP
    -   WebRTC
    -   DNS
    -   DHCP

- TCP: Transmission Control Protocol (Reliable and ordered)
Everything on the internet works with TCP, reliable, ordered, error-checked delivery of data. Establish with 3 way handshake. One connection throughout the communication. This is called a *stream* and is a *stateful connection*.

Features of TCP are:

- Connection Oriented
- Guarantee of Delivery
- Flow Control
- Congestion Control

#### When to choose a specific protocol:

Most of the cases it will TCP unless specificed otherwise like:

- Low latency is critical (real-time applications, gaming)
- Some data loss is acceptable (media streaming)
- Handling high-volume telemetry or logs where occasional loss is acceptable
- If no need to support web browsers (or you have an alternative for that client)

#### TCP vs UDP comparison:

| Feature            | UDP                     | TCP                    |
|--------------------|-------------------------|------------------------|
| Congestion Control | No                      | Yes                    |
| Connection         | Connectionless          | Connection-oriented    |
| Flow Control       | No                      | Yes                    |
| Header Size        | 8 bytes                 | 20–60 bytes            |
| Ordering           | No ordering guarantees  | Maintains order        |
| Reliability        | Best-effort delivery    | Guaranteed delivery    |
| Speed              | Faster                  | Slower due to overhead |
| Use Cases          | Streaming, gaming, VoIP | Everything else        |

## Application layer

### HTTP: Hypertext Transfer Protocol

- Dominated by HTTP protocl this layer responsible for client-server interaction, data exchange, and data processing.
- Stateless protocol.
- Request and Response
- Key Concepts:
  - Request Method: GET, POST, PUT, DELETE
  - Status Code: 200, 404, 500 etc.
  - Headers: Content-Type, Content-Length, etc.
  - Body: Data sent in the request or response body.

Status Codes:

- 200: OK
- 201: Created
- 202: Accepted
- 204: No Content
- 301: Moved Permanently
- 302: Found
- 304: Not Modified
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error
- 502: Bad Gateway
- 503: Service Unavailable

HTTP headers:

HTTP headers are key-value pairs that are used to pass additional information about the request or response.

- Content-Encoding: gzip, deflate, br
- Content-Type: text/html, application/json, etc.
- Content-Length: number of bytes in the body

#### HTTPS: HTTP over TLS

- Transport Layer Security (TLS) is a security protocol that provides encryption and authentication for data transmitted over the internet.
- It is a secure protocol that uses public-key infrastructure (PKI) to establish a secure connection between a client and a server.
- It uses SSL (Secure Sockets Layer) and TLS (Transport Layer Security) protocols to establish a secure connection between a client and a server.
- It provides end-to-end encryption and authentication for data transmitted over the internet.

## Communication of the services:

### REST: Representational State Transfer:

- Consider of having action on resources and getting information from resources.
- Resource can be anything.
- Primary focus on stateless services and action perform on resources. Borrowed verbs from HTTP.
- JSON to represent resources.

Requesting a resource to GET resource id using *id*:

```json
GET /users/{id} -> User
```

Updating the resource to PUT resource id using *id*:

```json
PUT /users/{id} -> User
{
  "username": "john.doe",
  "email": "john.doe@example.com"
}
```

Where to use REST:

- Elastic search uses to manage document, configure indexes, etc.
- Not good option on high throughput services.
- Better default to REST + TCP, if not then gRPC, SSE, WebSockets