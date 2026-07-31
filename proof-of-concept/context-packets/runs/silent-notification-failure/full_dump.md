# full_dump — silent-notification-failure

Question: Why might expense notifications fail silently under load, and what already exists in this codebase to prevent that?

Wall time: 31.3s

Result ok: True

Usage: {"completion_tokens": 229, "prompt_tokens": 8014, "total_tokens": 8243, "prompt_tokens_details": {"cached_tokens": 7988}}


## Answer

Expense notifications might fail silently under load due to the behavior of the vendor notification API, as described in the background section of `http_client.py`. Specifically, the vendor API silently drops requests under load instead of returning an error or a 5xx status. It accepts the connection but never responds with anything meaningful, or times out with no body. This makes it difficult to distinguish between a genuinely successful, empty-body response and a failure.

To prevent this issue, the codebase uses the `http_client.request_with_retry` function. This function is designed to handle the silent drop behavior by retrying requests with exponential backoff and jitter. It treats an ambiguous/empty response as a failure worth retrying rather than a success. This ensures that transient failures due to load are mitigated by retrying the request, rather than being silently ignored.

The `request_with_retry` function is used in `notification_client.py` to send notifications, ensuring that any issues with the vendor API are handled appropriately. This aligns with the convention that all outbound HTTP calls must go through `http_client.request_with_retry`, as specified in `conventions.md`.
