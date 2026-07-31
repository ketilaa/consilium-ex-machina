# Baseline — How should agents coordinate for v1: in-process pub/sub, or an external message broker (e.g. NATS)?

Model: Qwen2.5-Coder-14B-Instruct (single agent, no lifecycle)

## Answer

**Decision:** Use an in-process pub/sub mechanism for the first working version (v1) of sw-foundry's agents.

**Justification:**

1. **Simplicity and Development Speed:** 
   - An in-process pub/sub mechanism is simpler to implement and requires less setup compared to an external message broker like NATS. This reduces development time and effort, allowing for a quicker iteration and deployment of the first working version.

2. **Single-Node Deployment Needs:**
   - Since v1 is intended to run as a single process on one machine, the overhead of managing an external message broker is unnecessary. In-process communication is more efficient and straightforward for a single-node environment.

3. **Reduced Complexity:**
   - Managing an external service introduces additional complexity, including configuration, monitoring, and potential network latency. For a minimal viable product (MVP), minimizing complexity is crucial to focus on core functionality.

4. **Scalability Considerations:**
   - While an in-process pub/sub is not suitable for multi-node or production environments, it can be a stepping stone to a more complex architecture. The design can be modular, allowing for the introduction of an external message broker in future iterations when the need arises.

**Main Risks:**
- **Limited Scalability:** The in-process mechanism will not support distributed systems or multi-node deployments, which could become a limitation as the system grows.
- **Single Point of Failure:** If the single process fails, all agents will be affected, leading to potential downtime.

**Alternatives Considered:**
- **External Message Broker (e.g., NATS):** This would provide better scalability and resilience for distributed systems. However, it introduces additional complexity in terms of setup, configuration, and operational overhead, which is not justified for a single-node MVP.

In conclusion, an in-process pub/sub mechanism is the most appropriate choice for the initial v1 release, balancing simplicity and speed with the specific needs of a single-node deployment.
