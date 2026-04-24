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
