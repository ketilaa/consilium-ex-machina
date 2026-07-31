# Baseline — Should the work-item graph (work items, decisions, questions, events, and their relations) be persisted in a relational database (e.g. Postgres) or a graph database (e.g. Neo4j) for v1?

Model: Qwen2.5-Coder-14B-Instruct (single agent, no lifecycle)

## Answer

**Decision:** Persist the work-item graph in a graph database (e.g., Neo4j) for v1.

**Justification:**

1. **Domain Model Alignment:** The core domain model is inherently a graph, with entities (work items, decisions, questions, events) and relationships between them. A graph database is designed to efficiently store and query graph structures, making it a natural fit for this domain.

2. **Query Efficiency:** Graph databases are optimized for traversing relationships, which is a common operation in this domain. This can lead to more efficient and performant queries compared to a relational database, especially as the complexity of the graph grows.

3. **Flexibility:** Graph databases allow for flexible schema design, which is beneficial given that query patterns are not yet well understood. This flexibility can accommodate changes in the domain model without significant restructuring.

4. **Community and Support:** Graph databases like Neo4j have strong community support and a rich ecosystem of tools and libraries, which can be advantageous for development and troubleshooting.

**Main Risks Considered:**

1. **Learning Curve:** The team may need to invest time in learning and adopting a new type of database, which could delay initial development.

2. **Vendor Lock-in:** Relying on a specific graph database vendor (like Neo4j) could lead to vendor lock-in, limiting future migration options.

**Alternatives Considered:**

1. **Relational Database:** While a relational database could be made to work, it would require complex schema design and potentially inefficient queries to represent the graph structure. This approach could lead to performance bottlenecks and increased development effort.

2. **NoSQL Document Store:** A document store like MongoDB could be used, but it would not inherently support the graph structure as efficiently as a graph database. It might require additional logic to handle relationships and queries.

Given the alignment with the domain model and the potential for more efficient querying, a graph database is the most suitable choice for v1.
