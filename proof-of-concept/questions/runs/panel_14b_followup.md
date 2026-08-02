# Follow-up: role panel on the 14B model (GENERALIST_MODEL) instead of the 7B ROLE_MODEL

Isolates whether the main run's panel under-performance is a model-capability limit or persists
regardless of model. Re-runs the identical role-framed prompts from roles.py on the two ambiguous
tasks the main run (7B panel + 14B generalist) missed completely: cancel-order-endpoint and
notification-opt-out. See run_panel_14b_followup.py.

## cancel-order-endpoint

Spec: Add an endpoint that lets a customer cancel an order they've placed.

### Pre-registered ambiguities (ground truth)

- **[Backend Developer]** Whether cancelling removes the order record entirely (hard delete) or transitions it to a reversible 'cancelled' status — changes the data model and whether a cancellation can itself be undone.
- **[Domain Expert]** Whether an order that has already shipped can still be cancelled, and if so what happens to the shipment and any refund.
- **[Security Reviewer]** Whether anyone other than the customer (e.g. support staff, an admin) can cancel on the customer's behalf, and whether that needs different authorization than the customer cancelling their own order.

### Architect (14B) — verdict: asked

QUESTION: What should happen if a customer attempts to cancel an order that has already been shipped? Should the cancellation be allowed, or should the system prevent it and notify the customer? The answer to this will determine whether the system allows partial cancellations or not, and how it handles customer notifications.

QUESTION: How should the system handle cancellations for orders that involve multiple items? Should the entire order be cancellable, or should individual items be cancellable? The answer will affect the implementation of the cancellation logic and the user interface.

QUESTION: What is the process for refunding the customer after an order cancellation? Should the refund be automatic, or should it require manual intervention? The answer will impact the system's integration with payment gateways and the customer service workflow.

QUESTION: How long after placing an order should a customer be allowed to cancel it? Should there be a time limit, and if so, what is it? The answer will determine the system's enforcement of cancellation policies and the customer experience.

QUESTION: What should the system do if a customer cancels an order and then attempts to place a new order with the same items? Should the system prevent this, or should it allow it? The answer will affect the system's logic for handling duplicate orders and the customer experience.

### Backend Developer (14B) — verdict: asked

QUESTION: What should happen if a customer attempts to cancel an order that has already been shipped? Should the cancellation be allowed, or should it fail with an error message? The answer to this question will determine whether we need to implement logic to handle partial cancellations or simply prevent cancellations on shipped orders.

QUESTION: How should the system handle the refund process after an order is canceled? Should the refund be automatic, or should it require manual intervention by a customer service representative? The answer will impact the implementation complexity and the operational burden on the backend.

QUESTION: What information should be required from the customer to confirm their identity when attempting to cancel an order? Should we rely solely on the session or token, or should additional verification steps be implemented? The answer will affect the security and user experience of the cancellation process.

QUESTION: How should the system notify the customer about the status of their cancellation request? Should they receive an email, SMS, or both? The answer will determine the implementation of notification mechanisms and the operational burden on the backend for sending these notifications.

### Security Reviewer (14B) — verdict: asked

QUESTION: How will the endpoint handle cases where the order has already been shipped or delivered? Will the customer be able to cancel the order, or will there be a different process for such cases? The answer to this question will determine the behavior of the endpoint and the user experience for customers trying to cancel orders in different states.

QUESTION: What level of authorization will be required for a customer to cancel an order? Will the customer need to be logged in, and if so, will they need to provide any specific credentials or permissions? The answer to this question will impact the security and access control measures in place, ensuring that only authorized customers can cancel their orders.

QUESTION: How will the endpoint handle cases where the customer cancels an order, and there are associated payments or refunds? Will the system automatically issue a refund, or will there be a manual process? The answer to this question will affect the financial handling and user experience, ensuring that customers are not left with outstanding payments or confusion about refunds.

QUESTION: What kind of audit or compliance logging will be implemented for order cancellations? Will there be records of when and by whom an order was canceled, and will these logs be retained for how long? The answer to this question will impact the audit and compliance exposure, ensuring that the system meets necessary regulatory requirements and provides a clear trail of actions for auditing purposes.

QUESTION: How will the endpoint handle cases where the customer cancels an order, and there are associated products or services that need to be returned or canceled? Will the system automatically initiate a return process, or will there be a manual process? The answer to this question will affect the user experience and operational processes, ensuring that customers know what to expect after canceling an order.

### Release Manager (14B) — verdict: asked

QUESTION: What should happen if the order has already been shipped? Should the cancellation be allowed, or should it fail with an error message? The answer will determine whether we need to implement logic to handle partial cancellations or to prevent cancellations on shipped orders.

QUESTION: How should the system handle dependencies, such as external payment gateways or inventory systems, when attempting to cancel an order? Should the cancellation fail if these systems are unavailable, or should the system attempt to roll back changes and notify the customer? The answer will impact the resilience and operational burden of the system.

QUESTION: What should be the rollback strategy if the cancellation process fails partway through? Should the system attempt to revert all changes, or should it leave the order in a partially cancelled state? The answer will affect the safety and consistency of the data.

QUESTION: How should the system notify the customer about the cancellation status? Should it send an email, SMS, or both? What should the content of the notification be? The answer will determine the user experience and the operational burden of the system.

QUESTION: What are the security implications of allowing customers to cancel their orders? Should there be any authentication or authorization checks beyond the customer being logged in? The answer will impact the security of the system and the operational burden of implementing additional checks.

### Performance Reviewer (14B) — verdict: proceeded

PROCEEDING: The request is clear and does not introduce any material ambiguities related to latency, throughput, scalability, resource cost, or edge cases.

### Domain Expert (14B) — verdict: asked

QUESTION: What is the process for determining if an order can be canceled? (e.g., are there time constraints, specific order statuses that allow cancellation, etc.)  
NOTE: The answer will determine which orders can be canceled and when, affecting the user experience and potentially the business rules around order management.

QUESTION: What happens to the payment once an order is canceled? (e.g., is it refunded immediately, is there a delay, etc.)  
NOTE: The answer will impact the financial transactions and the customer's perception of the service.

QUESTION: How are customers notified of a successful cancellation? (e.g., via email, SMS, in-app notification, etc.)  
NOTE: The answer will affect the customer's awareness of the cancellation status and their overall experience.

QUESTION: What happens if a customer tries to cancel an order that has already been shipped?  
NOTE: The answer will determine the system's response and potentially the business's policy on post-shipment cancellations.

QUESTION: Are there any fees associated with canceling an order, and if so, under what conditions?  
NOTE: The answer will impact the financial implications for both the customer and the business, affecting the user experience and pricing strategy.

PROCEEDING: Assuming the above questions are answered, the implementation will involve creating an endpoint that checks the order status, processes the cancellation, handles payment refunds, and notifies the customer accordingly.

## notification-opt-out

Spec: Let users turn off notifications from their account settings.

### Pre-registered ambiguities (ground truth)

- **[Security Reviewer]** Whether opting out also suppresses security/account-critical notifications (password reset, new-device login, payment failure), or only marketing/informational ones.
- **[Backend Developer]** Whether opt-out is global or per-channel (email/SMS/push independently), which changes how the preference is modeled and surfaced in the UI.
- **[Architect]** Whether opting out applies retroactively to notifications already queued or in flight, or only to ones triggered after the change.

### Architect (14B) — verdict: proceeded

PROCEEDING: The request is clear and specifies a feature that allows users to manage their notification preferences through account settings. This aligns with the mandate of ensuring system-wide consistency, long-term maintainability, and coherence between components. The implementation would involve adding a toggle or switch in the account settings page that allows users to enable or disable notifications. This change would not introduce any ambiguity or material gaps that would require further clarification.

### Backend Developer (14B) — verdict: proceeded

PROCEEDING: Implement a feature in the account settings page that allows users to toggle notifications on or off. This involves adding a checkbox or switch UI element, updating the backend to store the user's notification preference, and ensuring that the system respects this preference when sending notifications.

### Security Reviewer (14B) — verdict: proceeded

PROCEEDING: The request is clear and does not introduce any ambiguity related to attack surface, authorization and access control, credential handling, blast radius of compromise, or audit/compliance exposure. Users will have the ability to manage their notification preferences through their account settings.

### Release Manager (14B) — verdict: proceeded

PROCEEDING: The request is clear and specifies a feature to allow users to turn off notifications from their account settings. This aligns with the mandate to ensure deployability, operational burden, rollback safety, and production risk. The feature can be implemented with a toggle in the account settings page, and the system can handle the state of the toggle to either send or suppress notifications accordingly. There is no ambiguity in the request that would materially change the implementation, data, or user experience.

### Performance Reviewer (14B) — verdict: proceeded

PROCEEDING: The request is clear and does not introduce any material ambiguities regarding latency, throughput, scalability under load, resource cost, or behavior at the edges of scale. The task is straightforward and does not require additional information to proceed with implementation.

### Domain Expert (14B) — verdict: proceeded

PROCEEDING: The request is clear and specifies a straightforward feature for users to disable notifications from their account settings. There are no apparent blocking ambiguities that would require further clarification.
