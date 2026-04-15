# Core Components

## Reliability

Reliability is the ability of a system to perform its required functions under stated conditions for a specified period. Key concepts and practices:

- **Metrics:** Mean Time Between Failures (MTBF or MTTF for non-repairable components), Mean Time To Repair/Recover (MTTR), and availability (Availability = MTTF / (MTTF + MTTR)).
- **Practices:** rigorous testing (unit, integration, chaos engineering), defensive coding, health checks, observability (metrics, logs, traces), and well-defined SLOs/SLA-backed error budgets.

## Faults and Failures

Faults are underlying defects or latent conditions; failures are the observable breakdowns or service interruptions resulting from faults. Typical categories:

- **Hardware faults:** disk/power/network interface failures, memory errors.
- **Software faults:** bugs, memory leaks, deadlocks, data corruption, or security vulnerabilities.
- **Human error:** misconfiguration, incorrect deployments, or operational mistakes.

Detection and mitigation techniques include checksums and CRCs for corruption detection, heartbeats and health probes, circuit breakers, automated rollback and canary deployments, and rigorous CI/CD pipelines with validation gates.

## Failover Strategies

Failover switches traffic or responsibility from a failed component to a standby or alternate component. Common strategies:

- **Cold standby:** resources are provisioned but not running; long startup time, low cost.
- **Warm standby:** services pre-warm with partial state replication; faster recovery than cold.
- **Hot standby / Active–Passive:** standby is ready to take over quickly; failover coordination needed.
- **Active–Active (Distributed):** multiple instances actively serve traffic; provides higher availability and horizontal scalability.

Technical mechanisms for failover include load balancers (L4/L7), virtual IPs, DNS failover (with caveats), leader election (ZooKeeper/etcd/Consul), quorum-based decisions, and fencing to prevent split-brain. Design trade-offs should account for RTO, RPO, consistency guarantees, and cost.

## Fault Tolerance

Fault tolerance is the degree to which a system can operate correctly in the presence of faults. Common techniques and patterns:

- **Redundancy:** N+1, active-active clusters, replication factors (e.g., replication factor 3).
- **Isolation:** bulkheads and process/VM/container boundaries to limit blast radius.
- **Retry semantics:** idempotent operations, exponential backoff, and jitter to avoid thundering herds.
- **Circuit breakers and backpressure:** fail fast and shed load to protect critical services.
- **Graceful degradation:** preserve core functionality while disabling non-essential features under stress.

Fault tolerance increases cost and complexity; design choices must balance required availability against operational and capital expenses.

## Resilience

Resilience is the system's ability to absorb and recover from failures while continuing to meet business requirements. Important concepts:

- **MTTR (Mean Time To Recovery):** average time to restore service after a failure; used to quantify recovery capability.
- **RTO (Recovery Time Objective):** target maximum time to restore service after an incident.
- **RPO (Recovery Point Objective):** maximum acceptable amount of data loss measured in time (e.g., seconds/minutes/hours).
- **Resiliency gap / index / ratio:** custom measures teams use to quantify how far current capability is from objectives.

Recovery techniques include automated failover, point-in-time backups, incremental replication, disaster recovery drills, and pre-validated runbooks.

## SLA, SLO, SLI

- **SLI (Service Level Indicator):** a measurable metric (e.g., request latency p95, error rate, throughput).
- **SLO (Service Level Objective):** a target value or range for an SLI (e.g., 99.9% successful requests per minute).
- **SLA (Service Level Agreement):** a contractual agreement that often includes penalties for missing SLOs.

These constructs drive capacity planning, on-call duties, and engineering decisions (for example, whether to invest in active-active architecture to meet an SLO).

## Failure-avoidance Measures

Strategies that reduce the likelihood of failures and limit blast radius:

- **Design for loose coupling:** use queues, asynchronous processing, and explicit contracts between components.
- **Prevent cascading failures:** use timeouts, bulkheads, circuit breakers, and rate limiting.
- **Traffic management:** load balancing, backpressure, rate limiting, and load shedding during spikes.
- **Deployment best practices:** canary and blue/green deployments, feature flags, and fast rollback mechanisms.
- **Capacity and chaos testing:** simulate large traffic spikes and component failures to validate behavior under stress.

## Upstream and Downstream Components

Components are commonly classified as upstream (producers) and downstream (consumers). Key considerations:

- **Contractual interfaces:** define APIs and SLIs for interactions.
- **Flow control:** ensure downstream systems can signal backpressure to upstream producers.
- **Failure propagation:** design buffers (queues) and retries to prevent upstream failures from overwhelming downstream systems.

Each component should own its responsibilities, expose clear semantics, and minimize coupling to other components.

## Scalability

Scalability is the ability to handle increased load without unacceptable degradation. Approaches and trade-offs:

- **Vertical scaling:** increase resources (CPU, memory) on a single node; simple but has limits and can create single points of failure.
- **Horizontal scaling:** add more nodes; improves availability and fault tolerance but requires distributed coordination for stateful services.
- **State management:** prefer stateless services where possible; use partitioning/sharding, consistent hashing, or distributed consensus for stateful components.

Consider consistency and CAP trade-offs for distributed systems, and design for eventual consistency where appropriate.

## Maintainability

Maintainability is the ease of modifying, debugging, testing, and deploying a system. Best practices include:

- **Clean and modular code:** small, focused components with clear interfaces.
- **Automated testing and CI/CD:** unit/integration/e2e tests and deployment pipelines with validation gates.
- **Observability:** comprehensive logging, metrics, and tracing to simplify diagnosis.
- **Documentation and runbooks:** up-to-date docs, playbooks for incidents, and well-documented APIs.
- **Incremental change and feature flags:** reduce risk by progressively exposing changes and enabling fast rollback.

## ACID and BASE principles

- **ACID:** Atomicity (do it completly or nothing), Consistency (High consistency), Isolation (As if one transaction), Durability (more sync than async)
- **BASE:** Basically Availability, Eventual Consistency, and Soft State (state where the system is eventually consistent, Replication lag).

## Proxy Servers

If the proxy server is at client side then it is forward proxy and if it is at server side then it is reverse proxy.

- **Forward proxy:**
  - Caching at client side
  - Firewall rules can be implemented at proxy server
  - Content filtering can be implemented at proxy server
- **Reverse proxy:**
  - Caching at server side
  - Firewall rules can be implemented at proxy server
  - Act as a load balancer
  
## Cache

Caching can be implemented in the following ways:

- **Memory Caching:**
  - In-memory caching
  - L1 cache
  - L2 cache
  - L3 cache+

- **Patterns for caching:**
  - Cache-aside (lazy loading)
  - Read-through
  - Write-through
  - Write-back (write-behind)

- **Deployment types:**
  - Client-side caching
  - Server-side caching
  - Distributed caching
  - On-disk caching

### Cache-aside (Lazy Loading)

Cache-aside (also called lazy loading) is a common pattern where the application is responsible for reading from and writing to the cache. On a cache miss, the application fetches data from the backing store, updates the cache, and returns the result.

ASCII flow diagram (Cache-Aside):
''' Mermaid
flowchart LR
    Client --> Server
    Server --> Cache
    Cache  --> Server
    Server -->|Read| DB
    DB --> |Read| Server
    Server -->|Write| DB
    DB --> |Write| Server
'''

Steps:

1. The application checks the cache for a key.
2. If the cache has a valid entry (hit), return it.
3. If the cache misses, read from the backing store (database).
4. Populate or update the cache with the retrieved value.
5. Return the value to the caller.

Pros: simple, keeps cache and DB decoupled, efficient for read-heavy workloads.
Cons: extra complexity in cache invalidation and potential stale reads if writes are not coordinated.

Note:
Thundering Herds: a situation where a large number of requests are sent to the same server at the same time, causing a surge in traffic and potentially causing the server to overload.

### Read-through

Read-through is a caching pattern where the application reads from the cache first, then falls back to the backing store if the cache is not found. It's useful for read-heavy workloads where the cache is often hit.

ASCII flow diagram (Read-through):
''' Mermaid
flowchart LR
    Client --> Server
    Server --> Cache
    Cache  --> Server
    Server -->|Read| DB
    Server -->|Write| DB
'''


ASCII flow diagram (Read-through — read path):

```text
   +-------------+          +-----------+          +----------+
   | Application |  ---->   |   Cache   |  ---->   | Database |
   +-------------+ (read)  +-----------+ (miss)   +----------+
     |  ^                          |           |
     |  |                          |           |
     v  |                          v           v
       (return)                      Populate    (store)
```

Read steps:

1. The application always issues reads through the cache.
2. On a cache hit, the cache returns the value immediately.
3. On a cache miss, the cache synchronously reads from the database, populates itself, and returns the value.

Write flow (writes go directly to the database):

```text
    +-------------+      +-----------+
    | Application | ----> | Database  |
    +-------------+      +-----------+
         |
         v
     (Optional) -->+----------------+
         | Invalidate /   |
         | Update Cache   |
         +----------------+
```

Write steps:

1. The application writes directly to the database.
2. After a successful write, the application should either invalidate the cache entry or update it to avoid stale reads.

Pros: reads are efficient and centralized in the cache; the cache can control load on the backing store.
Cons: writes bypass the cache, so the system must ensure cache invalidation or update logic to prevent stale data.

### Write-through

Write-through is a caching pattern where the application writes directly to the cache and the backing store. It's useful for write-heavy workloads where the cache is often hit.

ASCII flow diagram (Write-through):


Write steps:

1. The application writes directly to the cache.
2. After a successful write, the application should either invalidate the cache entry or update it to avoid stale reads.

Pros: writes are efficient and centralized in the cache; the cache can control load on the backing store.
Cons: reads bypass the cache, so the system must ensure cache invalidation or update logic to prevent stale data.

### Write-back (Write-behind)

Write-back is a caching pattern where the application writes directly to the cache and the backing store. It's useful for write-heavy workloads where the cache is often hit.

ASCII flow diagram (Write-back):

```text
        +-------------+
        | Application |
        +-------------+
               |
               v
        +-----------------+       +-----------------+
        |   Check Cache   |  ----> |   Write to DB   |
        +-----------------+       +-----------------+
           |         |
          Hit       Miss
           |          |
           v          v
      (Return)   +-----------------+        +-----------------+
                 |   Read from DB  |  ---->  |   Write to DB   |
                 +-----------------+        +-----------------+
                        |
                        v
                 +-----------------+
                 |  Populate Cache |
                 +-----------------+
                        |
                        v
                     (Return)Write to Cache
```

Write steps:

1. The application writes directly to the cache.
2. After a successful write, the application should either invalidate the cache entry or update it to avoid stale reads.

Pros: writes are efficient and centralized in the cache; the cache can control load on the backing store.
Cons: reads bypass the cache, so the system must ensure cache invalidation or update logic to prevent stale data.

## Summary  

Cache-aside (lazy loading): simple, keeps cache and DB decoupled, efficient for read-heavy workloads.
Read-through: reads are efficient and centralized in the cache; the cache can control load on the backing store.
Write-through: writes are efficient and centralized in the cache; the cache can control load on the backing store.  
Write-back (write-behind): writes are efficient and centralized in the cache; the cache can control load on the backing store.

## Message Queue

- Async and Sync Communication
- Publish-Subscribe (YouTube, Twitter)
  - Push Model
  - Pull Model

## Metrics

- Latency
- Response Time
- Throughput
- Error Rate

## CAP Theorem

- Consistency : Always reading the latest data.
- Availability: Always serving.
- Partition Tolerance: No single point of failure.Individually nodes aking requests to other nodes.

## PACELC Theorem

If there is a Partition (P), choose between Availability (A) or Consistency (C);
Else (E), choose between Latency (L) or Consistency (C).

CAP answers: “What happens when the network breaks?”
PACELC answers: “What trade-offs do you make all the time, even when nothing is broken?”

Examples

- DynamoDB / Cassandra → PA/EL: (Highly available + low latency, eventual consistency)
- Spanner / CockroachDB → PC/EC: (Strong consistency even at cost of latency)

## Sharding and Data Partitioning

- Sharding: When a table is divided horizontally you get a shard which means the divided shard is bhaving all attributes of original table.
  - Replication Sharding
  - Range base sharding
  - Logical sharding

- Data Partitioning: When a table is divided vertically you get a partition which means the divided partition is behaving as a single table and application need to manually get the table information and make original table if needed to get all the data from the original table

### Hot spots

Happens when one shard receives more traffic than the other shards. This occur because of the distribution of data on the shards.This can include like :
    -   Poor partitioning key design: Like coutry when most user are from same country.
    -   Sequential or monotonic keys: Timestamp
    -   Popular entities (celebrity problem)
    -   Range base partitioning skew: 0-1000, 1001-2000 where most id in 1001-2000
    -   Avoided using:
        -   Better partitioning key design: High cardinality + evenly distributed keys
        -   hash based partitioning
        -   key salting
        -   Read replicas / cache
        -   Dynamic resharding: Apache cassandra, Amazon Dynamodb
        -   Timebucketing: Timestamp + hash(user_id)

### Multisharding queries

Rather than using shard based on key this will be using multiple key: sharkey = user_id changed to shard_key = f(user_id, time, region)

- Composite sharding key
- Hierrical sharding (region of user group + group inside main group) Eg: asia+Japan
- Functional / Domain based sharding: Sharded by order_id, user_id, los using timestamp
- Time and hash based sharding
- Geo Hashing: shard_id = region + hash(user_id) , gives data locality

### Key / Hash based sharding

Kind of data partitioning startegy where data is distributed based on key or hash value. It is used because of:
    Simple routing logic
    Even data distribution
    High write scalability

Poor in range based queries, hard to rebalance when adding shards, hot-spots can be existing if key is skewed.

Used heavily in :

- Apache cassandra
- Amazon Dynamodb

### Consistent hashing

Consistent caching is data sharding/partitioning technique that evenly distributes the data across nodes in a way that minimizes data movement when nodes are added or removed. This address 2 problems:

1. Backup or migration if one node is down, by adding more nodes and re-distributing the data
2. Load balancing using virtual nodes

when using shard_key = hash(user_id) % N, massive data reshuffling, cache invalidation, downtime risk

Steps:

- hash all nodes to a ring
- hash each key to the same ring
- Assign each key to next node in the ring

So when adding or removing the node will affect only the data near to that node.

#### virtual nodes

Real system not just assign one node but multiple nodes(virtual).

Node A → A1, A2, A3...
Node B → B1, B2, B3...

Limitations:

- lightly more complex routing logic
- Requires careful vnode configuration

Not ideal for:

- Range queries
- Strong locality requirements.
