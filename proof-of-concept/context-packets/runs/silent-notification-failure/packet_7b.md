# packet — silent-notification-failure

Question: Why might expense notifications fail silently under load, and what already exists in this codebase to prevent that?

Files included: ['conventions.md', 'http_client.py', 'CHANGELOG.md', 'README.md', 'notification_client.py', 'audit_log.py', 'config.py']

Wall time: 52.8s

Result ok: True

Usage: {"completion_tokens": 631, "prompt_tokens": 3805, "total_tokens": 4436, "prompt_tokens_details": {"cached_tokens": 0}}


## Answer

Expense notifications might fail silently under load due to the behavior of the vendor notification API, as described in the `http_client.py` file. Specifically, the vendor notification API can silently drop requests under load instead of returning an error or a 5xx status. It accepts the connection and never responds with anything meaningful, or it responds with a 200 and an empty body.

To prevent this issue, the codebase has a mechanism in place to handle such failures. The `http_client.py` file provides the `request_with_retry` function, which is designed to handle this specific problem. Here are the key details:

1. **Retrying Logic**: `request_with_retry` retries the HTTP call with exponential backoff and jitter. This means it will retry the call multiple times, with increasing delays between retries.
   ```python
   for attempt in range(MAX_RETRIES):
       try:
           response = requests.request(method, url, timeout=10, **kwargs)
           if _looks_like_silent_drop(response):
               stats.record(response.status_code, failed=True)
               raise UpstreamCallFailed(f"empty or 5xx response: {response.status_code}")
           stats.record(response.status_code, failed=False)
           return response
       except (requests.RequestException, UpstreamCallFailed) as exc:
           last_error = exc
           if not isinstance(exc, UpstreamCallFailed):
               stats.record(None, failed=True)
           delay = RETRY_BASE_DELAY_SECONDS * (2**attempt) + random.uniform(0, 0.25)
           logger.warning("retrying %s %s after error: %s (delay=%.2fs)", method, url, exc, delay)
           time.sleep(delay)
   ```

2. **Detecting Silent Drops**: The `_looks_like_silent_drop` function checks if the response is a 2xx status code with no meaningful body, which is a known failure mode of the vendor API.
   ```python
   def _looks_like_silent_drop(response: requests.Response) -> bool:
       """Detect the INC-482 failure signature: a 2xx with no meaningful body."""
       if response.status_code >= 500:
           return True
       if not response.content:
           return True
       return False
   ```

3. **Logging and Stats**: The `request_with_retry` function logs each attempt and records statistics for the host making the request. This helps in debugging and understanding the behavior under load.
   ```python
   def _stats_for(url: str) -> CallStats:
       host = url.split("/")[2] if "://" in url else url
       if host not in _STATS_BY_HOST:
           _STATS_BY_HOST[host] = CallStats(host=host)
       return _STATS_BY_HOST[host]
   ```

By using `request_with_retry` instead of making raw `requests` calls, the codebase ensures that failures due to silent drops are handled with retries, and the application is more resilient to load-induced issues with the vendor API.
