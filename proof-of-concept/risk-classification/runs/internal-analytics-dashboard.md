# internal-analytics-dashboard

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


## Mechanism A: baseline 3-way classifier (no RISK option)


### Repeat 1

Item 1 (Security Reviewer):
The dashboard's admin panel has no rate limiting on login attempts, which could allow a brute-force attack against internal team credentials.
[BLOCKING] -- This is a genuine security vulnerability that can be addressed by implementing rate limiting.

Item 2 (Security Reviewer):
Data in transit between the dashboard and its database is not encrypted.
[BLOCKING] -- This is a genuine security issue that can be resolved by implementing encryption for data in transit.

Item 3 (Backend Developer):
The monthly aggregation query groups events by calendar month using the event's server-received timestamp rather than its original client-side event timestamp. Whenever there is any processing delay, this undercounts events from the last day of each month, silently and consistently underreporting monthly totals by a small but real margin every single month.
[BLOCKING] -- This is a genuine data accuracy issue that can be fixed by using the original client-side event timestamp for grouping.

Item 4 (Performance Reviewer):
The dashboard reloads its entire multi-year dataset into memory on every page refresh instead of caching it, which is fine at current usage but will become painfully slow if the dataset grows much larger or if concurrent usage increases significantly.
[BLOCKING] -- This is a genuine performance issue that can be addressed by implementing caching mechanisms.

Parsed tags: ['BLOCKING', 'BLOCKING', 'BLOCKING', 'BLOCKING']


### Repeat 2

Item 1: [BLOCKING] -- This is a genuine security vulnerability that can be addressed by implementing rate limiting on login attempts.

Item 2: [BLOCKING] -- This is a genuine security issue that can be resolved by encrypting data in transit.

Item 3: [BLOCKING] -- This is a genuine data accuracy issue that can be addressed by using the original client-side event timestamp for grouping events by calendar month.

Item 4: [NON-BLOCKING] -- This is a valid performance concern, but it does not block the decision as it can be addressed in the future if the dataset grows significantly or concurrent usage increases.

Parsed tags: ['BLOCKING', 'BLOCKING', 'BLOCKING', 'NON-BLOCKING']


### Repeat 3

Item 1: [BLOCKING] -- This is a genuine security vulnerability that can be addressed by implementing rate limiting.

Item 2: [BLOCKING] -- This is a genuine security vulnerability that can be addressed by enabling encryption for data in transit.

Item 3: [BLOCKING] -- This is a genuine data accuracy issue that can be addressed by using the original client-side event timestamp for grouping events by calendar month.

Item 4: [NON-BLOCKING] -- This is a valid performance concern, but it is not critical for the initial implementation and can be addressed in future iterations as usage grows.

Parsed tags: ['BLOCKING', 'BLOCKING', 'BLOCKING', 'NON-BLOCKING']


## Mechanism B: 4-way classifier with RISK option + risk profile


### Repeat 1

Item 1 (Security Reviewer):
The dashboard's admin panel has no rate limiting on login attempts, which could allow a brute-force attack against internal team credentials.
**[BLOCKING]** -- This is a plain correctness defect in security.

Item 2 (Security Reviewer):
Data in transit between the dashboard and its database is not encrypted.
**[BLOCKING]** -- This is a plain correctness defect in security.

Item 3 (Backend Developer):
The monthly aggregation query groups events by calendar month using the event's server-received timestamp rather than its original client-side event timestamp. Whenever there is any processing delay, this undercounts events from the last day of each month, silently and consistently underreporting monthly totals by a small but real margin every single month.
**[BLOCKING]** -- This is a plain correctness defect in data accuracy.

Item 4 (Performance Reviewer):
The dashboard reloads its entire multi-year dataset into memory on every page refresh instead of caching it, which is fine at current usage but will become painfully slow if the dataset grows much larger or if concurrent usage increases significantly.
**[RISK]** -- This is a valid concern, but addressing it now is disproportionate to the current risk profile. Trigger condition: if the dataset size increases by an order of magnitude or the number of concurrent users increases significantly.

Parsed tags: ['BLOCKING', 'BLOCKING', 'BLOCKING', 'RISK']


### Repeat 2

Item 1 (Security Reviewer):
The dashboard's admin panel has no rate limiting on login attempts, which could allow a brute-force attack against internal team credentials.
[BLOCKING] -- This is a plain correctness defect in security, regardless of the current risk profile.

Item 2 (Security Reviewer):
Data in transit between the dashboard and its database is not encrypted.
[BLOCKING] -- This is a plain correctness defect in security, regardless of the current risk profile.

Item 3 (Backend Developer):
The monthly aggregation query groups events by calendar month using the event's server-received timestamp rather than its original client-side event timestamp. Whenever there is any processing delay, this undercounts events from the last day of each month, silently and consistently underreporting monthly totals by a small but real margin every single month.
[BLOCKING] -- This is a plain correctness defect in data accuracy, regardless of the current risk profile.

Item 4 (Performance Reviewer):
The dashboard reloads its entire multi-year dataset into memory on every page refresh instead of caching it, which is fine at current usage but will become painfully slow if the dataset grows much larger or if concurrent usage increases significantly.
[RISK] -- The performance impact is only a problem if the dataset grows much larger or if concurrent usage increases significantly.

Parsed tags: ['BLOCKING', 'BLOCKING', 'BLOCKING', 'RISK']


### Repeat 3

Item 1: [BLOCKING] -- Brute-force attacks are a genuine security risk that can be mitigated with rate limiting.

Item 2: [BLOCKING] -- Unencrypted data in transit is a security vulnerability that can be addressed by implementing encryption.

Item 3: [BLOCKING] -- This is a plain correctness defect, causing consistent underreporting of monthly totals.

Item 4: [RISK] -- While not ideal, this is not a blocking issue given the current risk profile. It should be revisited if the dataset size grows significantly or concurrent usage increases substantially.

Parsed tags: ['BLOCKING', 'BLOCKING', 'BLOCKING', 'RISK']
