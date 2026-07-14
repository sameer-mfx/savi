# SAVI Phase 2 Workflow Configuration

This module implements the first Phase 2 actions that are safe to package for review:

- Ensures approved SAVI CRM enquiry sources exist.
- Ensures approved CRM lost reasons exist.
- Adds a configurable default quotation reminder interval.
- Automatically applies the default reminder interval to future quotations when they move to `sent` and no interval is set.

The module does not delete or rename existing CRM sources, lost reasons, stages, quotations, or business records.
