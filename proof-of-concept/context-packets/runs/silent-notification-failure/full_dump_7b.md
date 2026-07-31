# full_dump — silent-notification-failure

Question: Why might expense notifications fail silently under load, and what already exists in this codebase to prevent that?

Wall time: 59.7s

Result ok: True

Usage: {"completion_tokens": 178, "prompt_tokens": 8014, "total_tokens": 8192, "prompt_tokens_details": {"cached_tokens": 0}}


## Answer

Expense notifications can fail silently under load due to the behavior of the vendor notification API, which sometimes accepts connections under high load and responds with empty 200 OK responses instead of errors or timeouts. This can make it appear that the notifications were sent successfully, even though they were not delivered.

To prevent this issue, the codebase includes a `http_client.request_with_retry` function that handles retries with exponential backoff and jitter. This function specifically addresses the silent drop behavior of the vendor API by treating empty or 200 OK responses as failures worth retrying. Here are the key details:

1. **`http_client.request_with_retry` Function**:
   - This function is the only sanctioned way to make an outbound HTTP call in the codebase.
   - It retries with exponential backoff and jitter.
   - It treats an ambiguous/empty response as a failure worth
