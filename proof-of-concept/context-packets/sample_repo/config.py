"""Static configuration for the expense approval service.

Values here are compiled in at deploy time from the environment-specific config
repo; nothing in this file should be treated as user-editable at runtime.
"""

# Number of times to retry a failed outbound HTTP call before giving up.
MAX_RETRIES = 3

# Base delay (seconds) for exponential backoff between retries.
RETRY_BASE_DELAY_SECONDS = 0.5

# Expenses at or above this amount require a second approver, per Finance policy FIN-112.
# This is in CENTS, like every other monetary value in this codebase (see conventions.md).
# $5,000.00 -> 500000 cents.
APPROVAL_THRESHOLD_CENTS = 500_000

# How long a pending expense can sit before we send a reminder notification.
REMINDER_AFTER_HOURS = 48

# Expenses older than this are auto-flagged for the finance team's monthly
# stale-expense report (a separate batch job, not part of this service's
# request-handling path).
STALE_REPORT_AFTER_DAYS = 30

# Maximum number of line-item attachments (receipts) allowed per expense.
MAX_ATTACHMENTS_PER_EXPENSE = 10

# Default currency for expenses submitted without an explicit currency code.
# Multi-currency support is on the roadmap but not implemented; every amount
# in the system today is assumed USD.
DEFAULT_CURRENCY = "USD"

VENDOR_NOTIFICATION_API_BASE_URL = "https://notifications.vendor.example.com/v1"
