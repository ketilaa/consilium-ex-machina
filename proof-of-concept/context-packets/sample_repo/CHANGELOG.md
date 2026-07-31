# Changelog

## 2024-11

- Added second-approver requirement for expenses at/above the FIN-112 threshold.
- Fixed INC-510: boundary value at exactly the threshold was being auto-approved
  with a single approver. Regression test added.

## 2024-08

- Migrated all outbound HTTP calls to `http_client.request_with_retry` after
  INC-482 (vendor API silently dropping requests under load). Previously each
  client module made raw `requests` calls with no shared retry behavior.

## 2024-05

- Added audit logging for all state-changing endpoints, following a compliance
  finding where an approval could not be traced back to an actor because the
  original async audit writer lost its queue during a deploy.

## 2024-02

- Initial release: submit, approve, reject. No reminders, no second-approver
  workflow, no audit logging. (Both were added later — see above.)

## 2023-11

- Legacy CSV importer added for the one-time migration off the old expense
  system. Not part of the running service; kept for reference.
