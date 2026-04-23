# Caching

## Cache types

### External caching

- external cache is a standalone cache service that your application talks to over the network.
- stores in *Redis or memcached* 
- support eviction policies like LRU and expiration via TTL so your memory footprint is small.

```mermaid
flowchart LR

    C[Client] -->|Request| APP[Application]

    %% Read Path
    APP -->|Read: Check Cache| CACHE[(Cache<br/>Key-Value Store)]
    CACHE -->|Hit| APP
    CACHE -->|Miss| DB[(Database<br/>SQL)]

    DB -->|Fetch Data| APP
    APP -->|Populate Cache| CACHE
    APP -->|Response| C

    %% Write Path
    APP -->|Write| DB
    APP -->|Invalidate / Update Cache| CACHE
```

#### CDN: Content Delivery Network

- A CDN is a geographically distributed network of servers that caches content close to users. 
- Instead of every request traveling to your origin server, a CDN stores copies of your content at edge servers around the world.
  
### client side caching

- Client-side caching stores data close to the requester to avoid unnecessary network calls. 
- means the user's device, like a browser (HTTP cache, localStorage) or mobile app using local memory or on-device storage.
- Example: Strava App for running updating the data while offline, Redis client of metadata of the cluster node to connect directly

```mermaid
flowchart LR

    C[Client] --> APP[Application]

    APP --> ICACHE[(Internal Cache<br/>App-managed)]

    ICACHE -->|Hit| APP
    ICACHE -->|Miss| DB[(Database)]

    DB --> ICACHE
    APP --> C
```

### In-Process caching

- Cache lives inside each app instance memory
- No sharing between instances

```mermaid
flowchart LR

    C --> APP1[App Instance 1]
    C --> APP2[App Instance 2]

    APP1 --> LC1[(Local Cache<br/>In-Memory)]
    APP2 --> LC2[(Local Cache<br/>In-Memory)]

    LC1 -->|Miss| DB[(Database)]
    LC2 -->|Miss| DB

    DB --> LC1
    DB --> LC2
```

## Cache Architecture

### Lazy-Aside Caching (Lazy Loading)

Explained under this link: [Cache-aside (Lazy Loading)](concepts/core-concepts.md#cache-aside-lazy-loading)

### Write-Through Caching

Explained under this link: [Write-Through Caching](concepts/core-concepts.md#write-through-caching)

### Write-Behind Caching

Explained under this link: [Write-Behind Caching](concepts/core-concepts.md#write-behind-caching)

### Read-Through Caching

Explained under this link: [Read-Through Caching](concepts/core-concepts.md#read-through-caching)

## Cache Eviction Policies

### LRU (Least Recently Used)

- It is the default in many systems because it adapts well to most workloads where recently used data is likely to be used again

### LFU (Least Frequently Used)

- This works well when certain keys are consistently popular over time, like trending videos or top playlists.
- Some implementations use approximate LFU to avoid the cost of precise frequency tracking.

### FIFO (First In First Out)

- Because it may evict items that are still hot, it is rarely used in real systems beyond simple caching layers.
  
### TTL (Time To Live)

- TTL is not an eviction policy by itself.
- combined with LRU or LFU to balance freshness and memory usage.

## Caching Problems

### Cache Stampede

- There is a brief window, even if only a second, where every request misses the cache and goes straight to the database. 
- Instead of one query, you suddenly have hundreds or thousands, which can overload the database.

```mermaid
flowchart LR

    subgraph Clients
        C1[Client 1]
        C2[Client 2]
        C3[Client 3]
        C4[Client 4]
    end

    subgraph App Layer
        APP[Application]
    end

    subgraph Cache Layer
        CACHE[(Cache<br/>Expired Entry)]
    end

    subgraph DB Layer
        DB[(Database)]
    end

    %% All clients send requests at same time
    C1 --> APP
    C2 --> APP
    C3 --> APP
    C4 --> APP

    %% All hit cache
    APP --> CACHE

    %% Cache miss for all
    CACHE -->|Miss| APP

    %% Stampede: all hit DB
    APP -->|Concurrent Queries| DB

    %% DB responds
    DB --> APP

    %% Cache gets repopulated (but too late)
    APP --> CACHE
```

### How to handle

#### Cache stampede

- Request coalescing (single flight): reduce the number of concurrent requests to the database.
- Cache warming: pre-populate the cache with data from the database before the TTL expires.

#### Cache Consistency

- *Cache invalidation on writes*: Delete the cache entry after updating the database so it gets repopulated with fresh data.
- *Short TTLs for stale tolerance*: Let slightly stale data live temporarily if eventual consistency is acceptable.
- *Accept eventual consistency*: For feeds, metrics, and analytics, a short delay is usually fine.

#### Hot Keys

- A hot key is a cache entry that receives a huge amount of traffic compared to everything else.

How to Handle Hot Keys:

- Replicate hot keys: Store the same value on multiple cache nodes and load balance reads across them.
- Add a local fallback cache: Keep extremely hot values in-process to avoid pounding Redis.
- Apply rate limiting: Slow down abusive traffic patterns on specific keys.

## Summary

```mermaid
mindmap
  root((Introducing Caching Strategically))

    Step 1: Justify Caching
      Read-heavy workload
      Expensive queries
      High DB CPU usage
      Strict latency requirements
      Signal
        "This endpoint is read-heavy, so caching can reduce DB load and latency"

    Step 2: Identify Bottleneck
      Slow queries
      High DB latency
      Repeated identical reads
      Hot keys
      Signal
        "The bottleneck is database reads for frequently accessed data"

    Step 3: Decide What to Cache
      Query results
      Aggregations
      User sessions
      Frequently accessed objects
      Signal
        "We’ll cache user profiles and feed responses"

    Step 4: Choose Cache Architecture
      External Cache
        Shared, scalable 
      Internal Cache
        App-managed
      In-Process Cache
        Fastest, per instance
      Signal
        "We’ll use Redis as a distributed cache for scalability"

    Step 5: Define Eviction Policy
      TTL (expiry-based)
      LRU (least recently used)
      LFU (least frequently used)
      Signal
        "We’ll use TTL with slight jitter to avoid synchronized expiry"

    Step 6: Address Downsides (Critical for Interviews)

      Cache Invalidation
        Problem
          Stale data
        Strategies
          Invalidate on write
          TTL expiry
          Eventual consistency
        Example
          "On profile update, we delete cache so next read is fresh"

      Cache Failures
        Problem
          Cache unavailable
        Impact
          DB traffic spike
        Mitigation
          Fallback to DB
          Circuit breaker
          Rate limiting
          In-process fallback cache
        Signal
          "If cache fails, DB handles traffic with protection mechanisms"

      Thundering Herd (Stampede)
        Problem
          Many requests on cache miss
        Impact
          DB overload
        Mitigation
          Request coalescing
          Probabilistic early expiration
          Locking / single-flight
        Signal
          "Only one request fetches data, others wait"

    Step 7: Conclude with Trade-offs
      Benefits
        Lower latency
        Reduced DB load
      Costs
        Complexity
        Consistency challenges
      Signal
        "We accept eventual consistency for better performance"
```

