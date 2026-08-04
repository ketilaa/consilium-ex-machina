# pilot-program-customer-portal (round 2)

Decision: Build a self-service customer portal for the upcoming pilot program


Risk profile: Currently used only by 4 internal test accounts during development. However, the team has already committed to onboarding the first cohort of 10 external pilot customers on March 1st, six weeks away, at which point the portal will store and display those customers' real names, email addresses, and billing history.


## Items (fixed, pre-registered ground truth)


### Item 1 (Security Reviewer) -- ground truth: **BLOCKING**

The proposal logs full account details, including billing history, at INFO level for debugging, with no redaction of personal information such as names, emails, or billing history.


### Item 2 (Backend Developer) -- ground truth: **RISK**

The proposal does not address how the portal would handle being accessed in multiple languages or locales; right now all interface text is hardcoded in English.


### Item 3 (Release Manager) -- ground truth: **WORK_ITEM**

The proposal does not specify what customer support tooling will be used to look up a specific pilot customer's account when they call in with an issue.


## Mechanism A: round-1's 4-way classifier (no WORK_ITEM option)


### Repeat 1

Item 1: [BLOCKING] -- Logging personal information at INFO level is a clear security and privacy violation.

Item 2: [RISK] -- This is a real concern, but it is disproportionate to the current risk profile, which is only for internal test accounts and a small pilot group.  This should be revisited if the pilot program expands beyond the initial 10 customers.

Item 3: [RISK] -- This is a legitimate concern, but it is disproportionate to the current risk profile, which is only for internal test accounts and a small pilot group.  This should be revisited if the pilot program expands beyond the initial 10 customers.

Parsed tags: ['BLOCKING', 'RISK', 'RISK']


### Repeat 2

Item 1: [BLOCKING] -- Logging personal information at INFO level is a clear security and privacy violation.

Item 2: [RISK] -- The portal is currently only used by internal test accounts, and the first external cohort is English-speaking; this should be revisited if the pilot program expands to non-English-speaking customers.

Item 3: [RISK] -- The pilot program is small and just starting, so this can wait; this should be revisited if the number of pilot customers grows significantly or if the pilot program is extended.

Parsed tags: ['BLOCKING', 'RISK', 'RISK']


### Repeat 3

Item 1: [BLOCKING] -- Logging personal information at INFO level is a plain correctness defect that violates privacy principles.

Item 2: [RISK] -- The pilot program is only six weeks away, and the team has not committed to supporting multiple languages or locales. Trigger condition: The team commits to supporting multiple languages or locales for the pilot program.

Item 3: [BLOCKING] -- The proposal lacks a critical component for customer support, which is essential for the pilot program.

Parsed tags: ['BLOCKING', 'RISK', 'BLOCKING']


## Mechanism B: round-2's 5-way classifier (WORK_ITEM + phrasing-neutral fix + future-plan handling)


### Repeat 1

Item 1: [BLOCKING] -- Logging personal information at INFO level is a plain correctness defect, regardless of risk profile.

Item 2: [WORK_ITEM] -- Internationalization / localization -- this is a real, legitimate concern that should be addressed at some point, but does not block this decision, as the pilot is only for a small, internal cohort.

Item 3: [BLOCKING] -- The team has already committed to onboarding external customers, so they will need a way to look up accounts when those customers call in with issues.

Parsed tags: ['BLOCKING', 'WORK_ITEM', 'BLOCKING']


### Repeat 2

Item 1: [BLOCKING] -- logging personal information at INFO level is a plain correctness defect.

Item 2: [WORK_ITEM] -- add internationalization support for multiple languages and locales -- this is a real, legitimate concern that should be addressed, but not before the pilot program starts.

Item 3: [BLOCKING] -- the portal must have a way to look up customer accounts for support, and this must be specified before the pilot program starts.

Parsed tags: ['BLOCKING', 'WORK_ITEM', 'BLOCKING']


### Repeat 3

Item 1: [BLOCKING] -- Logging personal information at INFO level is a plain correctness defect.

Item 2: [WORK_ITEM] -- "Add localization support for future versions" -- This is a real, legitimate concern that should be addressed eventually, but it is not a blocker for the initial version.

Item 3: [BLOCKING] -- The portal is intended to be used by customers, and thus must have a way to support them; this is a plain correctness defect.

Parsed tags: ['BLOCKING', 'WORK_ITEM', 'BLOCKING']
