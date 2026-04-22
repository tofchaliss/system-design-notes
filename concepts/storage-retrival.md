# Storage and Retrival

## BitCask: A key value store

- A log-structured key-value storage engine designed for fast writes and simple reads
- The map will be having the key against the position of the key in the 2d array(basically, starting point of the key).
- Kind of append only type of data structure
- In-memory hash table.

Actions performed:

- All writes are append-only to disk
- Keeps an in-memory hash map (key → file offset)
- Reads are:
  - Look up key in memory
  - Jump directly to disk location

- Search
- Update
- Compaction
- Delete

Pain points:

- Need to more segemts as it scales. Need to introduce compaction.

Pros and Cons:

- fast read and write because (sequential write and offset to read)
- No complex data structure to maintain on disk (append-only)

Cons:

- Less scalable.

Example:

-

## SSTable: Sorted String Table

- Sorted by key
- Immutable (read-only after write)
- Stored on disk
- Supports efficient sequential and range reads
- Used in LSM Trees (Log-Structured Merge-Tree)
  - Writes go to memory (memtable)
  - Then flushed to disk as SSTables
  - Later merged/compacted
- Tree structure , In-memory writer
- Implemented by Red-Black Tree | Balanced Binary Tree.
- Faster because of the skip list.
- Memtable in Inmemory Table and flush it to SSD/HDD.
- Garbage collector with compaction on SSD/HDD.
- If multiple sgments exists , uses external sorting to merge them. (Merge Tree + Merge sorting)
- MemTable + Logging + copies to SSD/HDD.
  - Log using Write Ahead Logging (WAL)

### Internal Structure of SSTable

- Data blocks → actual key-value pairs (sorted)
- Index block → helps locate keys quickly
- Bloom filter → avoids unnecessary disk reads
- Metadata → stats, compression info

```mermaid
flowchart LR

    %% Main vertical structure
    subgraph SST["SSTable File"]
        direction TB

        DB["Data Blocks\nData Block 1\n..."]
        FB["Filter Block\nBloom Filter"]
        IB["Index Block"]
        FT["Footer\nOffsets for blocks"]

    end

    %% Descriptions on right side
    DB -->|"Key-value pairs stored in sorted order"| D1["Sorted KV data"]
    FB -->|"Bloom filter"| D2["Membership check"]
    IB -->|"Key to data block mapping"| D3["Index lookup"]
    FT -->|"Block offsets + metadata"| D4["Magic number and metadata"]
```

### Write Path

```mermaid  
flowchart LR
    W["Write Request"] --> WAL["Write Ahead Log"]
    WAL --> MEM["MemTable in memory"]
    MEM -->|"Flush when full"| SST["SSTable on disk"]
```

### Read Path

Search order:

- MemTable
- Newer SSTables
- Older SSTables

```mermaid
flowchart LR
    R["Read Request"] --> MEM["MemTable"]
    MEM -->|"Miss"| SST1["SSTable Level 0"]
    SST1 --> SST2["SSTable Level 1"]
    SST2 --> SST3["SSTable Level N"]
```

### Compaction

Since SSTables are immutable:

- New writes create new SSTables
- Old data becomes stale
- System runs compaction:

### Trade-offs

- Read amplification (check multiple SSTables)
- Compaction overhead
- Storage amplification

### SSTables directly impact

- Latency → read amplification
- Failure handling → WAL + immutable files = durability
- Regional systems → used in distributed DBs (Cassandra)
- Caching → Bloom filters reduce unnecessary reads

## Bloom Filter

- O(1) lookup and datastructure
- Reduce False positives
- Logic: If key present - Probablistic, if key not present - Deterministic
- Used in
  - malicous site identification
  - Unique username

### How it works

- 2 hashes and big Array to identify the bool probablity
- Hashes increases accuracy more hases increase computation
- Array Filter

Links:

- [Bloom filter visualization](https://hur.st/bloomfilter/)

## Merkle Tree

- Consists of leaves, internal nodes, root node
- Root = single has representing data
- Leaf = hash of data block
- Internal node = hash of child nodes
- Any byte changes root of hash changes
- Merkle Tree = a hierarchical checksum that lets you verify any piece of data with only O(log n) information.

Why it used:

- Efficient integrity verification
  - To prove D3 is part of the dataset, you don’t need all data—only a Merkle proof.
- Tamper detection
  - Change in any leaf propagates up → root mismatch
- Bandwidth savings
  - Only send:
    - Hash of the target data block
    - Hash of a small set of sibling hashes

```mermaid
flowchart TB

    %% Leaf level
    D1["D1"] --> H1["H1 = Hash(D1)"]
    D2["D2"] --> H2["H2 = Hash(D2)"]
    D3["D3"] --> H3["H3 = Hash(D3)"]
    D4["D4"] --> H4["H4 = Hash(D4)"]

    %% Intermediate level
    H1 --> H12["H12 = Hash(H1 + H2)"]
    H2 --> H12

    H3 --> H34["H34 = Hash(H3 + H4)"]
    H4 --> H34

    %% Root
    H12 --> ROOT["Merkle Root = Hash(H12 + H34)"]
    H34 --> ROOT
```

- Split data into chunks: D1, D2, D3, D4
- Hash each:
  - 1 = H(D1), H2 = H(D2), ...
- Pair and hash again:
  - H12 = H(H1 || H2), H34 = H(H3 || H4)
- Continue until one value remains → Merkle Root

### Where it’s used

- Blockchains (e.g., Bitcoin)
- Transactions in a block → Merkle root stored in block header
- Distributed systems / P2P sync
- Efficiently detect differences between replicas
- Git-like systems
- Content-addressable storage (tree of hashes)
- CDNs / storage systems
- Data integrity and deduplication

## Mental Model of Database

```mermaid
flowchart TB

    APP["Application"] --> QUERY["SQL Query"]

    QUERY --> OPT["Query Optimizer"]
    OPT --> EXEC["Execution Engine"]

    EXEC --> IDX["Index B+ Tree"]
    EXEC --> TABLE["Table Storage"]

    IDX --> BUF["Buffer Cache (RAM)"]
    TABLE --> BUF

    BUF --> DISK["Disk (Pages / Files)"]
```

### Layer of the Database

- Application Layer

Sends the SQL query:

```text
SELECT * FROM users WHERE user_id = 1
```

- Query Optimizer Layer

Decide:

- Use index
- Full Table scan

- Execution Engine Layer

  - Actually runs the plan
  - Calls:
    - Index Lookup
    - Table Tech

- Index Layer (B+ Tree)

```mermaid
flowchart TB
    ROOT["Root"] --> I["Internal Node"]
    I --> LEAF["Leaf Node"]
    LEAF -->|"key → row pointer"| ROW["Row Location"]
```

- Fast lookup
- Leaf gives

```text
key → primary key OR row pointer
```

- Table Storage

  Two models:
  - Heap (PostgreSQL style)
    Rows stored unordered
    Index → points to row location
  - Clustered (InnoDB style)
    Table itself is a B+ Tree
    Leaf = actual row data

- Buffer Layer

  - RAM layer between DB and disk
  - Stores frequently used pages

- Disk Layer
Data stored as pages (4KB–16KB)
  Includes:
  - Table pages
  - Index pages
  - WAL logs

### Data in B-Tree

- Data pointer
- Record pointer
- Key

Data Lookup:

```mermaid
flowchart TB
    R["Root"] --> I1["Internal node"]
    I1 -->|"key < K"| L1["Leaf page"]
    I1 -->|"key >= K"| L2["Leaf page"]

    L1 -->|"found key → row pointer"| ROW["Fetch row (table)"]
```

Steps:

- Binary search within node (in-memory after page read)
- Follow pointer to next node
- Repeat until leaf → get row pointer (or the row itself if it’s a clustered index)
- Cost: O(log_b N) page reads (b = fan-out, often 100+)

## Database Indexing

- Single or Multi-level indexing
  - Single use primary keys or secondary keys or by clustering
  - Multi-level index: Composite index (user_id + timestamp)
- Multi-level indexing for faster searching uses B-Tree or B+Tree
Why B-Tree?

- High fan-out ⇒ very low height ⇒ few I/Os
- Sorted order ⇒ efficient range queries (BETWEEN, ORDER BY)
- Page locality ⇒ good cache behavior

Why B+Tree?

- B+-Tree optimizes both point lookups and range scans with minimal disk I/O and excellent locality.
  
### Comparison B-Tree vs B+-Tree

| Feature           | B-Tree              | B+-Tree        |
|------------------|--------------------|---------------|
| Data location    | Internal + leaf    | Leaf only     |
| Range scan       | Poor               | Excellent     |
| Tree height      | Higher             | Lower         |
| Disk I/O         | More               | Less          |
| Sequential access| Weak               | Strong        |
| DB usage         | Rare               | Standard      |

Examples:

- MySQL InnoDB → clustered B+-Tree
- PostgreSQL → B+-Tree indexes
- SQLite → B+-Tree

### B Tree

```mermaid
flowchart TB

    %% Root Node
    ROOT["Root Node| K1 | K2 |"]

    %% Level 1
    C1["Child 1| less than K1 |"]
    C2["Child 2| K1 = K2 |"]
    C3["Child 3| > K2 |"]

    ROOT --> C1
    ROOT --> C2
    ROOT --> C3

    %% Level 2 (Leaves)
    L1["Leaf| k1 k2 k3 |"]
    L2["Leaf| k4 k5 |"]
    L3["Leaf| k6 k7 |"]
    L4["Leaf| k8 k9 |"]

    C1 --> L1
    C1 --> L2
    C2 --> L3
    C3 --> L4
```

- Every node in a B-tree follows strict rules:
- All leaf nodes must be at the same depth
- Each node can contain between m/2 and m keys (where m is the order of the tree)
- A node with k keys must have exactly k+1 children
- Keys within a node are kept in sorted order

Why B-Tree

- They maintain sorted order, making range queries and ORDER BY operations efficient
- They're self-balancing, ensuring predictable performance even as data grows
- They minimize disk I/O by matching their structure to how databases store data
- They handle both equality searches (email = 'x') and range searches (age > 25) equally well
- They remain balanced even with random inserts and deletes, avoiding the performance cliffs you might see with simpler tree structures

Examples:

- PostgreSQL automatically creates two B-tree indexes: one for the primary key and one for the unique email constraint. These B-trees maintain sorted order, which is crucial for both uniqueness checks and range queries.
- DynamoDB organizes items within a partition in sort-key order, enabling efficient range queries within that partition. Its storage internals aren’t publicly documented in detail, but it’s widely understood to use an LSM-style storage architecture rather than a B-tree for its underlying engine.
- Even MongoDB, with its document model, uses B-trees (specifically B+ trees, a variant where all data is stored in leaf nodes) for its indexes.

### LSM Tree: Log-Structured Merge Tree

- Combination of SSTables and MemTables (No inplace update)
- LSM = Memtable + SStable + WAL + compaction
- LSM Tree = “Write everything fast in memory, flush to disk in sorted chunks, and continuously merge to stay efficient.”
- It is not implemeneted a B-Tree, rather ain tree structure

In-memory Updates::

Typically implemented as:

- Skip list (most common)
- Balanced tree (sometimes)

LSM Approach:

``` text
Write → MemTable → SSTable → Compaction → Merged SSTables
```

B-Tree Approach:

```text
Write → Find node → Modify node → Rebalance tree
```

Why LSM avoids B-Trees

- Problem with B-Trees
- Random disk I/O (slow on SSD/HDD for writes)
- Frequent node splits

LSM solution

- Sequential writes only
- Batch compaction later

### Flow diagram

```mermaid
flowchart TB

    %% Write Path
    W["Write"] --> WAL["WAL Log (Disk)"]
    W --> MEM["MemTable (RAM)"]

    %% Flush
    MEM -->|"Flush & Compaction"| L0SST["Level 0 SSTable"]
    MEM -->|"Flush & Compaction"| L0IDX["Level 0 Index"]

    %% Levels (Disk)
    subgraph DISK["Disk Storage"]
        direction TB

        subgraph L0["Level 0"]
            L0IDX
            L0SST
        end

        subgraph L1["Level 1"]
            L1IDX1["Index"]
            L1SST1["SSTable"]
            L1IDX2["Index"]
            L1SST2["SSTable"]
        end

        subgraph LN["Level N"]
            LNIDX1["Index"]
            LNSST1["SSTable"]
            LNIDX2["Index"]
            LNSST2["SSTable"]
        end
    end

    %% Compaction
    L0SST -->|"Major Compaction"| L1SST1
    L1SST1 -->|"Compaction"| LNSST1

    %% Read Path
    R["Read"] --> BF["Bloom Filter (RAM)"]
    R --> MEM

    BF --> L0SST
    BF --> L1SST1
    BF --> LNSST1

    %% Optional direct read fallback
    R --> LNSST1
```

- what happens when you write to a database that uses LSM trees:
  - Memtable (Memory Component): New writes go into an in-memory structure called a memtable, typically implemented as a sorted data structure like a red-black tree or skip list. This is extremely fast since it's all in RAM.
  - Write-Ahead Log (WAL): To ensure durability, every write is also appended to a write-ahead log on disk. This is a sequential append operation, which is much faster than random writes.
  - Flush to SSTable: Once the memtable reaches a certain size (often a few megabytes), it's frozen and flushed to disk as an immutable Sorted String Table (SSTable). This is a single sequential write operation that can write megabytes of data at once.
  - Compaction: Over time, you accumulate many SSTables on disk. A background process called compaction periodically merges these files, removing duplicates and deleted entries. This keeps the number of files manageable and maintains read performance.

- When you query for a specific key, the database must check multiple places:
  - First, the memtable: Is the data in the current in-memory buffer?
  - Then, immutable memtables: Any memtables waiting to be flushed?
  - Finally, all SSTables on disk: Starting from the newest (most likely to have recent data) and working backwards

- LSM trees typically employ several optimizations:
  - Bloom Filters: Each SSTable has an associated bloom filter - a probabilistic data structure that can quickly tell you if a key is definitely NOT in that file. This lets you skip most SSTables without reading them. If the bloom filter says "maybe", you still need to check, but it eliminates the definite misses.
  - Sparse Indexes: Since SSTables are sorted, they maintain sparse indexes that tell you the range of keys in each block. If you're looking for user_id=500 and an SSTable only contains keys 1000-2000, you can skip it entirely.
  - Compaction Strategies: Different compaction strategies optimize for different workloads. Size-tiered compaction minimizes write amplification but can lead to more files to check. Leveled compaction maintains fewer files but requires more frequent rewrites.

- Write path
  - Write → WAL (durability)
  - Write → MemTable (RAM)
  - MemTable → flushed to Level 0 SSTables
- Storage layout
  - Levels: L0 → L1 → LN
  - Each level has:
    - SSTables
    - Index blocks
- Compaction
  - L0 → L1 → LN (progressive merge)
- Read path
  - Read → MemTable (fastest)
  - Read → Bloom Filter (avoid unnecessary disk hits)
  - Then → SSTables (newer to older)

### Hash Index

Hash Index works for exact matching of what we are looking for. Though this capability is still in parity with postgresql with B-tree.

```mermaid

flowchart LR
    A[Query Key] --> B[Hash Function]
    B --> C[Hash Value]
    C --> D[Bucket]

    D --> E1[Entry 1]
    D --> E2[Entry 2]
    D --> E3[Entry 3]

    E1 --> F1[Row Pointer]
    E2 --> F2[Row Pointer]
    E3 --> F3[Row Pointer]
```

- The database maintains an array of buckets, where each bucket can store multiple key-location pairs.
- When indexing a value, the database hashes it to determine which bucket should store the pointer to the row data.

Examples:

- Used in redis for primary key lookup in in-memory.

### Geo-Spatial Index

As B-tree cant solve 2-D space indexing there are few indexing that helps that which includes:

- Geohash
- R-Tree
- Quad-Tree


- If we use the latitude index first, we'll find all restaurants in the right latitude range - but that's a long strip spanning the entire globe at that latitude! Then for each of those restaurants, we need to check if they're also in the right longitude range. Our index on longitude isn't helping because we're not doing a range scan - we're doing point lookups for each restaurant we found in the latitude range.
- If we try to be clever and use both indexes together (via an index intersection), the database still has to merge two large sets of results - all restaurants in the right latitude range and all restaurants in the right longitude range. This creates a rectangular search area much larger than our actual circular search radius, and we still need to filter out results that are too far away.


#### GeoHash

- One space will be divided as Four blocks.
- If entered to one quater then that will be divided again into four.
- This keep going on, but the each cell will be having a seperate string and each string which is near will be having almost same string using base32.
- Now complete map will be marked as string and use *B-tree* for search queries, with prefix match and range.

```text
GEOADD restaurants -122.4194 37.7749 "Restaurant A"
GEOSEARCH restaurants FROMLONLAT -122.4194 37.7749 BYRADIUS 5 mi
```

- Limitation:

  - On the boundaries in the same street you might have 2 different string but physically very close or just opposite.

#### QuadTree

- QuadTree is similar kind of GeoHash except the the data structure is a tree.
- Each space is divided to 4 quadrants,
- More dense parts will be again divided to 4 again. In this way dense will have quadrants and sparse will heaving only minimal.

```mermaid
flowchart TD
    R["Root (Whole Space)"]

    R --> Q1["NW Quadrant"]
    R --> Q2["NE Quadrant"]
    R --> Q3["SW Quadrant"]
    R --> Q4["SE Quadrant"]

    %% Only one quadrant subdivides further (adaptive behavior)
    Q2 --> Q21["NE-NW"]
    Q2 --> Q22["NE-NE"]
    Q2 --> Q23["NE-SW"]
    Q2 --> Q24["NE-SE"]

    %% Leaf nodes with data
    Q1 --> P1["Points"]
    Q3 --> P3["Points"]
    Q4 --> P4["Points"]

    Q21 --> P21["Points"]
    Q22 --> P22["Points"]
    Q23 --> P23["Points"]
    Q24 --> P24["Points"]
```

#### R-Tree

- R-tree is a tree-based index for multi-dimensional spatial data (points, rectangles, polygons)
- Uses Minimum Bounding Rectangles (MBRs) to represent and group objects
- Organized hierarchically: parent MBRs fully contain child MBRs
- Balanced tree structure (like B-tree) → consistent query performance
- Insertion uses least-area enlargement heuristic to keep nearby objects together
- Node splits aim to minimize overlap, area, and perimeter between regions
- Query execution is based on MBR intersection checks, not linear ordering
- Enables efficient range queries, spatial joins, and nearest-neighbor searches
- Overlap between nodes can cause multiple branches to be explored (main limitation)
- Widely used in databases like PostgreSQL (via GiST/PostGIS) for real-world geospatial workloads

```mermaid
flowchart TD
    Root["Root MBR (covers everything)"]

    Root --> A["Region A (MBR)"]
    Root --> B["Region B (MBR)"]

    A --> A1["Obj 1 MBR"]
    A --> A2["Obj 2 MBR"]

    B --> B1["Obj 3 MBR"]
    B --> B2["Obj 4 MBR"]
```

### Inverted Index

- B-tree excel for exact match, either prefix match or suffix match of the pattern
- Inverted index support pattern matching anywhere in the content

```text
SELECT * FROM posts WHERE content LIKE '%database%';
```

``` text
doc1: "B-trees are fast and reliable"
doc2: "Hash tables are fast but limited"
doc3: "B-trees handle range queries well"
```

Invert index create mapping

```text
b-trees  -> [doc1, doc3]
fast     -> [doc1, doc2]
reliable -> [doc1]
hash     -> [doc2]
tables   -> [doc2]
limited  -> [doc2]
handle   -> [doc3]
range    -> [doc3]
queries  -> [doc3]
```

Analysis pipeline

- Breaking text into tokens (words or subwords)
- Converting to lowercase
- Removing common "stop words" like "the" or "and"
- Often applying stemming (reducing words to their root form)

Trade-Off:

- More space
- Updating as the document get updated

Real Example

- Elastic search

### Index Optimization

- processing overhead of common queries
- checking query plans and database metrics using those check bottleneck
- Indexing strategies
- understand access pattern and indexing approach

#### Composite Index

- Rather than having index for single column it will mix of multiple columns and create a composite index in specific order.

```text
CREATE INDEX idx_user_time ON posts(user_id, created_at);
```

- creating a B-tree where each node's key is a concatenation of our indexed columns.
- B-tree maintains these keys in sorted order based on user_id first, then created_at

``` text
(1, 2024-01-01)
(1, 2024-01-02)
(2, 2024-01-01)
(2, 2024-01-02)
(3, 2024-01-01)
``` 

- B-tree to find the first entry for user_id=123, then scan sequentially through the index entries for that user until it finds entries beyond our date range. 
- Entries are already sorted by created_at within each user_id group, we get both our filtering and sorting for free.

##### Order Index

- Order columns from most selective to least selective.
- Our index on (user_id, created_at) is great for queries that filter on user_id first, but it's not helpful for queries that only filter on created_at.
- This follows from how B-trees work - we can only use the index efficiently for prefixes of our column list.
- 


#### Covering Index

- covering index will have all the columns in the index

``` text
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INT,
    title TEXT,
    content TEXT,
    likes INT,
    created_at TIMESTAMP
);

-- Regular index
CREATE INDEX idx_user_time ON posts(user_id, created_at);

-- Covering index includes likes column
CREATE INDEX idx_user_time_likes ON posts(user_id, created_at) INCLUDE (likes);
```

- Aoid lot of extra disk reads.

Trade-off

- Covering indexes are larger because they store extra columns

## Choices of Indexing


```mermaid
flowchart TD

    A[Need efficient data access?] --> B{Table size > 10k rows?}

    B -->|No| FT[Full Table Scan]
    B -->|Yes| C{What type of data are you querying?}

    C --> D{Full text search?}
    D -->|Yes| INV[Inverted Index]
    D -->|No| E{Location data?}

    E -->|Yes| GEO[Geospatial Index]
    E -->|No| F{In-memory exact matches?}

    F -->|Yes| HASH[Hash Index]
    F -->|No| BT[B-Tree]

    BT --> G{Multiple columns queried together?}
    G -->|Yes| COMP[Consider Composite Index]

    COMP --> H{Heavy reads on few columns?}
    G -->|No| H

    H -->|Yes| COV[Consider Covering Index]
    H -->|No| END[Done]
```
