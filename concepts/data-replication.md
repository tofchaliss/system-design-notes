# Data replication

- It improves performance reliability, durability, and availability.

## Database durability

- Transaction failures
  - Network failures
- System failures
- Hardware failures

### State diagram for database durability

```mermaid
stateDiagram-v2

    [*] --> Running

    state Running {
        [*] --> Idle
        Idle --> Processing
        Processing --> Idle
    }

    Running --> Halt : Media Failure
    Halt --> Restart : Restore from backup
    Running --> Restart: System Failure
    Restart --> Recover: Read from safe last state
    Recover --> Abort: Read from commited transcation
    Abort --> Running: Undo uncommitted tranaction
    Running --> Abort: Transaction Failure
```

#### WAL (Write-Ahead Log)

```mermaid
flowchart TB
    %% Client Layer
    A[Client Application] -->|Write Request| B[Write Handler]

    %% RAM Layer
    subgraph RAM
        C[In-Memory DB MemTable]
        D[WAL Buffer Append Only]
    end

    %% HDD Layer
    subgraph HDD
        E[WAL Log Durable]
        F[LogDB Backup]
        G[Main DB SSTables]
    end

    %% Write Flow
    B -->|Process Write| C
    B -->|Append Log| D
    C -->|Sync to WAL Buffer| D

    %% WAL Persistence
    D -->|Flush fsync| E

    %% Replication
    E -->|Copy WAL| F

    %% Apply to DB
    E -->|Replay Logs| G

    %% Recovery
    E -.->|Redo| C
    F -.->|Restore| C
```

#### Replication

#### Async write

- Dont wait for all follower they got the data
- Check points:
  - Availability
  - Freshness
  - Consistency
  - Latency

#### Sync write

- wait for all follower that they got the data
  
### What happens if one follower is down?

- Backup / restore (snapshot)
- Sync from leader to get the latest data

### How to elect the leader?

- whoever has the latest data
- leader election protocols
- ZooKeeper, etcd, Consul

### How to know if leader is down?

- Heartbeat
- Election timeout

### Decoupling and replication

- Having WAL versions
- DB versions
- It should be compactible
- Havinf interface layer between log and db so that any log can be played against any db

### How to maintain replicated logs

- Timestamps and commands
- Decoupling with storage engine
- Trigger for replicate - Rows and conditions

