# Consistency Availability Partition-Tolerance

```mermaid
flowchart TB

    %% Core theorem
    CAP["CAP Theorem<br/>In a distributed system,<br/>during a network partition,<br/>you must choose between:<br/><br/>Consistency OR Availability"]

    %% Three properties
    C["Consistency (C)<br/>Every read gets the latest write"]
    A["Availability (A)<br/>Every request gets a response"]
    P["Partition Tolerance (P)<br/>System survives network splits"]

    CAP --> C
    CAP --> A
    CAP --> P

    %% Partition event
    P --> NET["Network Partition Occurs"]

    %% Decision
    NET --> DECIDE{"Choose Priority"}

    %% CP
    DECIDE --> CP["CP System"]
    CP --> CP1["Preserve correct & synchronized data"]
    CP --> CP2["Reject or delay requests if needed"]
    CP --> CP3["Some users may see timeout/errors"]

    %% AP
    DECIDE --> AP["AP System"]
    AP --> AP1["Always respond to requests"]
    AP --> AP2["Some responses may be stale"]
    AP --> AP3["Nodes synchronize later"]

    %% Impossible area
    DECIDE --> IMP["C + A together during partition"]
    IMP --> IMP1["Impossible"]
    IMP --> IMP2["This is the CAP tradeoff"]

    %% Examples
    CP --> CPX["Examples:<br/>ZooKeeper<br/>HBase"]
    AP --> APX["Examples:<br/>Cassandra<br/>Riak"]

    %% Styling
    classDef theorem fill:#1e293b,color:#fff,stroke:#0f172a,stroke-width:2px;
    classDef property fill:#0f766e,color:#fff,stroke:#134e4a;
    classDef cp fill:#1d4ed8,color:#fff,stroke:#1e3a8a;
    classDef ap fill:#9333ea,color:#fff,stroke:#581c87;
    classDef warn fill:#b91c1c,color:#fff,stroke:#7f1d1d;
    classDef neutral fill:#334155,color:#fff,stroke:#0f172a;

    class CAP theorem;
    class C,A,P property;
    class CP,CP1,CP2,CP3,CPX cp;
    class AP,AP1,AP2,AP3,APX ap;
    class IMP,IMP1,IMP2 warn;
    class NET,DECIDE neutral;
```

## Explanantions

- Consistency: All nodes see the same data at the same time. When a write is made to one node, all subsequent reads from any node will return that updated value.
  - Consistency: Every read gets the latest write.
- Availability: Every request to a non-failing node receives a response, without the guarantee that it contains the most recent version of the data.
  - Availability: Every request gets a response.
- Partition Tolerance: The system continues to operate despite arbitrary message loss or failure of part of the system (i.e., network partitions between nodes).
  - Partition Tolerance: System survives network splits.
- *In a distributed system, during a network partition, you must choose between Consistency OR Availability.*

### Example

```mermaid
sequenceDiagram

    autonumber

    participant U1 as User-1 (India)
    participant DC1 as Datacenter-1
    participant DB1 as Replica-1

    participant NET as Network Link

    participant U2 as User-2 (US)
    participant DC2 as Datacenter-2
    participant DB2 as Replica-2

    %% =====================================================
    %% SUNNY DAY SCENARIO
    %% =====================================================

    rect rgb(220,235,255)

    Note over U1,DB2: Sunny Day Scenario (No Network Partition)

    U1->>DC1: Update profile photo
    DC1->>DB1: Write latest profile
    DB1->>DB2: Replicate update
    DB2-->>DB1: Replication ACK

    U2->>DC2: Read user profile
    DC2->>DB2: Fetch latest data

    DB2-->>DC2: Updated profile returned
    DC2-->>U2: User sees latest profile

    end

    %% =====================================================
    %% PARTITION STARTS
    %% =====================================================

    rect rgb(255,230,230)

    Note over DB1,DB2: Network Partition Occurs

    DB1 -x DB2: Replication broken

    end

    %% =====================================================
    %% CP SYSTEM
    %% =====================================================

    rect rgb(220,240,255)

    Note over U1,U2: CP Choice (Consistency + Partition Tolerance)

    U1->>DC1: Update profile name
    DC1->>DB1: Write update

    DB1-xDB2: Cannot synchronize

    U2->>DC2: Read profile
    DC2->>DB2: Fetch latest profile

    DB2-->>DC2: Data may be stale

    Note over DC2: System refuses response<br/>to avoid inconsistency

    DC2-->>U2: ERROR / RETRY / TIMEOUT

    Note over U2: Availability sacrificed<br/>for correctness

    end

    %% =====================================================
    %% AP SYSTEM
    %% =====================================================

    rect rgb(240,220,255)

    Note over U1,U2: AP Choice (Availability + Partition Tolerance)

    U1->>DC1: Update profile photo
    DC1->>DB1: Save new update

    DB1-xDB2: Replication unavailable

    U2->>DC2: Read profile
    DC2->>DB2: Fetch profile

    DB2-->>DC2: Older profile returned

    DC2-->>U2: SUCCESS with stale data

    Note over U2: Availability preserved<br/>but data is inconsistent

    end

    %% =====================================================
    %% RECOVERY
    %% =====================================================

    rect rgb(220,255,220)

    Note over DB1,DB2: Partition Healed

    DB1->>DB2: Synchronize latest profile
    DB2-->>DB1: ACK

    Note over DB1,DB2: Eventual consistency restored

    end
```

### Choosing Availability Versus Consistency

- If Consistency more important than availability
  - Some systems absolutely require consistency, even at the cost of availability:
    - Ticket Booking Systems: Imagine if User A booked seat 6A on a flight, but due to a network partition, User B sees the seat as available and books it too. You'd have two people showing up for the same seat!
    - E-commerce Inventory: If Amazon has one toothbrush left and the system shows it as available to multiple users during a network partition, they could oversell their inventory.
    - Financial Systems: Stock trading platforms need to show accurate, up-to-date order books. Showing stale data could lead to trades at incorrect prices.

  - Distributed Transactions: Ensuring multiple data stores (like cache and database) remain in sync through two-phase commit protocols. This adds complexity but guarantees consistency across all nodes. This means users will likely experience higher latency as the system ensures data is consistent across all nodes.
  - Single-Node Solutions: Using a single database instance to avoid propagation issues entirely. While this limits scalability, it eliminates consistency challenges by having a single source of truth.

  - Technology choices
    - Postgresql, Google Spanner, DynamoDB

- If Availability is more important than consistency
  - Systems which need availability
    - Social Media: If User A updates their profile picture, it's perfectly fine if User B sees the old picture for a few minutes.
    - Content Platforms (like Netflix): If someone updates a movie description, showing the old description temporarily to some users isn't catastrophic.
    - Review Sites (like Yelp): If a restaurant updates their hours, showing slightly outdated information briefly is better than showing no information at all.
  - Multiple Replicas: Scaling to additional read replicas with asynchronous replication, allowing reads to be served from any replica even if it's slightly behind. This improves read performance and availability at the cost of potential staleness.
  - Change Data Capture (CDC): Using CDC to track changes in the primary database and propagate them asynchronously to replicas, caches, and other systems. This allows the primary system to remain available while updates flow through the system eventually.

  - Technology choices:
    - Cassandra, Amazon DynamoDB, Redis

*Note:* In a product it can be like some feature follow availability other feature follow consistency.
        For Example: Ticket Master: Showing seat available will be with availability but tickt booking will be with consistency.

### Consistency Levels

- Strong Consistency
  All reads reflect the most recent write. This is the most expensive consistency model in terms of performance, but is necessary for systems that require absolute accuracy like bank account balances. This is what we have been discussing so far.
- Causal Consistency
  Related events appear in the same order to all users. This ensures logical ordering of dependent actions, such as ensuring comments on a post must appear after the post itself.
- Read Your Write Consistency
  Users always see their own updates immediately, though other users might see older versions. This is commonly used in social media platforms where users expect to see their own profile updates right away.
- Eventual Consistency
  The system will become consistent over time but may temporarily have inconsistencies. This is the most relaxed form of consistency and is often used in systems like DNS where temporary inconsistencies are acceptable. This is the default behavior of most distributed databases and what we are implicitly choosing when we prioritize availability.

## Summary

```mermaid
mindmap
  root((CAP Theorem))

    Core Idea
      "Distributed systems face tradeoffs"
      "During network partition choose:"
        "Consistency"
        "Availability"
      "Partition tolerance is mandatory"

    Consistency (C)
      "All nodes see latest write"
      "Reads return most recent value"
      "Strong correctness guarantees"
      "Reject requests if unsure"
      "Typical behavior"
        "Timeouts"
        "Retries"
        "Write blocking"
      "Use cases"
        "Banking"
        "Inventory"
        "Ticket booking"
        "Authentication"

    Availability (A)
      "Every request gets response"
      "System remains operational"
      "May return stale data"
      "Prioritizes uptime"
      "Typical behavior"
        "Stale reads"
        "Conflicting versions"
        "Eventually synchronized"
      "Use cases"
        "Social feeds"
        "Messaging"
        "Recommendations"
        "Analytics dashboards"

    Partition Tolerance (P)
      "System survives network failures"
      "Nodes cannot communicate"
      "Most important reality of distributed systems"
      "Examples"
        "Datacenter isolation"
        "Router failure"
        "High latency"
        "Packet loss"

    Sunny Day Scenario
      "No partition"
      "Can achieve both consistency and availability"
      "Replication works normally"
      "Users see same data globally"

    Partition Scenario
      "Replication breaks"
      "Nodes diverge"
      "CAP tradeoff activates"

    CP Systems
      "Consistency + Partition tolerance"
      "Sacrifice availability"
      "Reject requests during partition"
      "Guarantee correctness"
      "Examples"
        "ZooKeeper"
        "etcd"
        "Google Spanner"

    AP Systems
      "Availability + Partition tolerance"
      "Sacrifice immediate consistency"
      "Always respond"
      "Reconcile later"
      "Eventual consistency"
      "Examples"
        "Cassandra"
        "DynamoDB"
        "Riak"

    Eventual Consistency
      "Nodes temporarily inconsistent"
      "Converge after recovery"
      "Good for user-facing systems"

    Important Clarifications
      "CAP applies during failures"
      "Not same as ACID consistency"
      "Not simply choose any 2 of 3"
      "Real choice is:"
        "Consistency vs Availability"

    PACELC
      "Extension of CAP"
      "During Partition:"
        "Availability or Consistency"
      "Else:"
        "Latency or Consistency"

    Interview Thinking
      "Explain user impact"
      "Discuss failure behavior"
      "Mention stale reads vs timeouts"
      "Tie tradeoff to business requirement"
```
