# packet — silent-notification-failure

Question: Why might expense notifications fail silently under load, and what already exists in this codebase to prevent that?

Files included: ['conventions.md', 'http_client.py', 'CHANGELOG.md', 'README.md', 'notification_client.py', 'audit_log.py', 'config.py']

Wall time: 60.5s

Result ok: True

Usage: {"completion_tokens": 189, "prompt_tokens": 3805, "total_tokens": 3994, "prompt_tokens_details": {"cached_tokens": 0}}


## Answer

Expense notifications might fail silently under load due to the behavior of the vendor notification API, as described in the `http_client.py` file. Specifically, the vendor notification API can accept a connection under load but never respond with anything meaningful, or it can respond with a 200 and an empty body. This behavior makes it difficult to distinguish between a genuine success and a failure, leading to silent failures.

To prevent this, the codebase includes the `http_client.request_with_retry` function, which is designed to handle such scenarios. This function retries the request with exponential backoff and jitter, treating an ambiguous or empty response as a failure worth retrying rather than a success. The function is used in the `notification_client.py` module to ensure that all outbound HTTP calls for sending notifications go through this retry mechanism. This approach helps to mitigate the issue of silent failures under load by retrying the request multiple times before giving up.
