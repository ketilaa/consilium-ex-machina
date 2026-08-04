# internal-analytics-dashboard (round 2)

Decision: Build an internal dashboard for exploring engagement metrics


Risk profile: Internal-only tool used by approximately 5 people on the data team. No external users, not customer-facing. Reads from an already-public, anonymized dataset -- no customer data, no regulated data.


## Items (fixed, pre-registered ground truth)


### Item 1 (Security Reviewer) -- ground truth: **RISK**

The dashboard's admin panel has no rate limiting on login attempts, which could allow a brute-force attack against internal team credentials.


### Item 2 (Security Reviewer) -- ground truth: **RISK**

Data in transit between the dashboard and its database is not encrypted.


### Item 3 (Backend Developer) -- ground truth: **BLOCKING**

The monthly aggregation query groups events by calendar month using the event's server-received timestamp rather than its original client-side event timestamp. Whenever there is any processing delay, this undercounts events from the last day of each month, silently and consistently underreporting monthly totals by a small but real margin every single month.


### Item 4 (Performance Reviewer) -- ground truth: **RISK**

The dashboard reloads its entire multi-year dataset into memory on every page refresh instead of caching it, which is fine at current usage but will become painfully slow if the dataset grows much larger or if concurrent usage increases significantly.


### Item 5 (Backend Developer) -- ground truth: **WORK_ITEM**

The proposal does not specify what testing framework or CI setup will be used for the dashboard's own codebase. Some automated testing should exist eventually, but the dashboard can be built and used by the data team without it existing on day one.


## Mechanism A: round-1's 4-way classifier (no WORK_ITEM option)


### Repeat 1

Item 1 (Security Reviewer):
The dashboard's admin panel has no rate limiting on login attempts, which could allow a brute-force attack against internal team credentials.
[BLOCKING] -- This is a genuine security vulnerability that can be addressed through better engineering judgment.

Item 2 (Security Reviewer):
Data in transit between the dashboard and its database is not encrypted.
[BLOCKING] -- This is a genuine security vulnerability that can be addressed through better engineering judgment.

Item 3 (Backend Developer):
The monthly aggregation query groups events by calendar month using the event's server-received timestamp rather than its original client-side event timestamp. Whenever there is any processing delay, this undercounts events from the last day of each month, silently and consistently underreporting monthly totals by a small but real margin every single month.
[BLOCKING] -- This is a plain correctness defect that can be addressed through better engineering judgment.

Item 4 (Performance Reviewer):
The dashboard reloads its entire multi-year dataset into memory on every page refresh instead of caching it, which is fine at current usage but will become painfully slow if the dataset grows much larger or if concurrent usage increases significantly.
[RISK] -- This is a legitimate concern, but addressing it now is disproportionate to the current risk profile. Revisit if the dataset size increases significantly or if concurrent usage grows beyond the current team of 5.

Item 5 (Backend Developer):
The proposal does not specify what testing framework or CI setup will be used for the dashboard's own codebase. Some automated testing should exist eventually, but the dashboard can be built and used by the data team without it existing on day one.
[NON-BLOCKING] -- This is a valid point, but it is not critical for the initial implementation.

Parsed tags: ['BLOCKING', 'BLOCKING', 'BLOCKING', 'RISK', 'NON-BLOCKING']


### Repeat 2

Item 1 (Security Reviewer):
The dashboard's admin panel has no rate limiting on login attempts, which could allow a brute-force attack against internal team credentials.
[BLOCKING] -- This is a plain security defect.

Item 2 (Security Reviewer):
Data in transit between the dashboard and its database is not encrypted.
[BLOCKING] -- This is a plain security defect.

Item 3 (Backend Developer):
The monthly aggregation query groups events by calendar month using the event's server-received timestamp rather than its original client-side event timestamp. Whenever there is any processing delay, this undercounts events from the last day of each month, silently and consistently underreporting monthly totals by a small but real margin every single month.
[BLOCKING] -- This is a plain correctness defect.

Item 4 (Performance Reviewer):
The dashboard reloads its entire multi-year dataset into memory on every page refresh instead of caching it, which is fine at current usage but will become painfully slow if the dataset grows much larger or if concurrent usage increases significantly.
[RISK] -- This is a real concern, but the current risk profile is low. Revisit if the number of users increases beyond 5 or the dataset size grows significantly.

Item 5 (Backend Developer):
The proposal does not specify what testing framework or CI setup will be used for the dashboard's own codebase. Some automated testing should exist eventually, but the dashboard can be built and used by the data team without it existing on day one.
[NON-BLOCKING] -- This is a valid point but not critical for the initial implementation.

Parsed tags: ['BLOCKING', 'BLOCKING', 'BLOCKING', 'RISK', 'NON-BLOCKING']


### Repeat 3

Item 1: [BLOCKING] -- Brute-force attacks are a genuine security risk that can be mitigated with proper rate limiting.

Item 2: [BLOCKING] -- Data in transit should always be encrypted to prevent potential eavesdropping or man-in-the-middle attacks.

Item 3: [BLOCKING] -- This is a plain correctness defect that will consistently misreport metrics.

Item 4: [RISK] -- Performance issues are a legitimate concern, but addressing them now is disproportionate to the current risk profile. Trigger condition: if the dataset size grows significantly or concurrent usage increases.

Item 5: [NON-BLOCKING] -- While automated testing is important, the lack of it does not block the initial implementation for internal use.

Parsed tags: ['BLOCKING', 'BLOCKING', 'BLOCKING', 'RISK', 'NON-BLOCKING']


## Mechanism B: round-2's 5-way classifier (WORK_ITEM + phrasing-neutral fix + future-plan handling)


### Repeat 1

Item 1 (Security Reviewer):
The dashboard's admin panel has no rate limiting on login attempts, which could allow a brute-force attack against internal team credentials.
[BLOCKING] -- The dashboard is not secure against brute-force attacks.

Item 2 (Security Reviewer):
Data in transit between the dashboard and its database is not encrypted.
[BLOCKING] -- Data in transit should be encrypted to prevent eavesdropping.

Item 3 (Backend Developer):
The monthly aggregation query groups events by calendar month using the event's server-received timestamp rather than its original client-side event timestamp. Whenever there is any processing delay, this undercounts events from the last day of each month, silently and consistently underreporting monthly totals by a small but real margin every single month.
[BLOCKING] -- The current implementation is incorrect and will consistently misreport metrics.

Item 4 (Performance Reviewer):
The dashboard reloads its entire multi-year dataset into memory on every page refresh instead of caching it, which is fine at current usage but will become painfully slow if the dataset grows much larger or if concurrent usage increases significantly.
[RISK] -- revisit if the dataset size or concurrent usage increases significantly.

Item 5 (Backend Developer):
The proposal does not specify what testing framework or CI setup will be used for the dashboard's own codebase. Some automated testing should exist eventually, but the dashboard can be built and used by the data team without it existing on day one.
[WORK_ITEM] -- implement automated testing and CI setup at some point.

Parsed tags: ['BLOCKING', 'BLOCKING', 'BLOCKING', 'RISK', 'WORK_ITEM']


### Repeat 2

Item 1 (Security Reviewer):
The dashboard's admin panel has no rate limiting on login attempts, which could allow a brute-force attack against internal team credentials.
[BLOCKING] -- A brute-force attack vulnerability is a plain correctness defect.

Item 2 (Security Reviewer):
Data in transit between the dashboard and its database is not encrypted.
[BLOCKING] -- Unencrypted data in transit is a plain correctness defect.

Item 3 (Backend Developer):
The monthly aggregation query groups events by calendar month using the event's server-received timestamp rather than its original client-side event timestamp. Whenever there is any processing delay, this undercounts events from the last day of each month, silently and consistently underreporting monthly totals by a small but real margin every single month.
[BLOCKING] -- This is a plain correctness defect.

Item 4 (Performance Reviewer):
The dashboard reloads its entire multi-year dataset into memory on every page refresh instead of caching it, which is fine at current usage but will become painfully slow if the dataset grows much larger or if concurrent usage increases significantly.
[RISK] -- This is a legitimate concern, but it is disproportionate to the current risk profile. Trigger condition: If the dataset size or concurrent usage increases significantly.

Item 5 (Backend Developer):
The proposal does not specify what testing framework or CI setup will be used for the dashboard's own codebase. Some automated testing should exist eventually, but the dashboard can be built and used by the data team without it existing on day one.
[WORK_ITEM] -- Implement automated testing and CI setup for the dashboard's codebase.

Parsed tags: ['BLOCKING', 'BLOCKING', 'BLOCKING', 'RISK', 'WORK_ITEM']


### Repeat 3

Item 1 (Security Reviewer):
The dashboard's admin panel has no rate limiting on login attempts, which could allow a brute-force attack against internal team credentials.
[BLOCKING] -- This is a plain correctness defect, not a matter of proportionate hardening or scheduling.

Item 2 (Security Reviewer):
Data in transit between the dashboard and its database is not encrypted.
[BLOCKING] -- This is a plain correctness defect, not a matter of proportionate hardening or scheduling.

Item 3 (Backend Developer):
The monthly aggregation query groups events by calendar month using the event's server-received timestamp rather than its original client-side event timestamp. Whenever there is any processing delay, this undercounts events from the last day of each month, silently and consistently underreporting monthly totals by a small but real margin every single month.
[BLOCKING] -- This is a plain correctness defect, not a matter of proportionate hardening or scheduling.

Item 4 (Performance Reviewer):
The dashboard reloads its entire multi-year dataset into memory on every page refresh instead of caching it, which is fine at current usage but will become painfully slow if the dataset grows much larger or if concurrent usage increases significantly.
[RISK] -- This is a real, legitimate concern, but addressing it right now is disproportionate to the work's current risk profile. Trigger: revisit if the dataset size grows significantly or concurrent usage increases.

Item 5 (Backend Developer):
The proposal does not specify what testing framework or CI setup will be used for the dashboard's own codebase. Some automated testing should exist eventually, but the dashboard can be built and used by the data team without it existing on day one.
[WORK_ITEM] -- This is a real, legitimate concern describing concrete engineering work that should genuinely happen at some point, unconditionally. Follow-up engineering work: Implement automated testing framework and CI setup.

Parsed tags: ['BLOCKING', 'BLOCKING', 'BLOCKING', 'RISK', 'WORK_ITEM']
