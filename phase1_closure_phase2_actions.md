# Phase 1 Closure and Phase 2 Action Plan

System: `https://staging-savi-odoo.macrofix.com`  
Current status: Phase 1 validation completed. Proceeding to Phase 2 based on user instruction.

## Phase 1 Closure

Phase 1 covered validation of the current Odoo workflows against the SAVI process requirements. The review confirmed that the current system already has the core modules and several custom workflows in place:

| Area | Phase 1 Result |
|---|---|
| CRM / Sales | Available, active, and populated. Needs stage/source/reminder cleanup. |
| AMC | Available and active. Needs lifecycle validation and reminder confirmation. |
| Service / SRN | Available and active. Needs approval and closure discipline. |
| Store / Purchase | Available and active. Needs receipt/delivery validation review. |
| Finance | Available. Usage scope needs confirmation because invoice/payment volume is low. |
| HR / Attendance | Available and active. Attendance is used heavily; payroll/leave/review need scope confirmation. |
| Automation | Templates and server actions exist, but trigger coverage is incomplete. |

## Phase 1 Item Resolved

| Item | Resolution |
|---|---|
| HR employee performance rating compute error | Fixed locally in `service_order_mfx/models/employee.py` so the computed field handles multiple employees correctly. |

## Phase 2 Objective

Phase 2 should convert the validated gaps into implementation-ready work. The recommended order is:

1. Fix technical blockers.
2. Clean up configuration.
3. Train users on existing workflows.
4. Build only the customizations that cannot be handled by configuration or training.

---

# Phase 2 Backlog

## A. Technical Fixes

| Priority | Item | Type | Recommended Action |
|---|---|---|---|
| High | HR performance rating compute bug | Code fix | Fixed locally. Deploy/update `service_order_mfx` after testing. |
| High | Confirm scheduled actions for AMC/sale reminders | Configuration validation | Verify scheduled actions in UI and activate if missing. |
| Medium | Check service order checkout coordinate field types | Technical review | Normalize check-out latitude/longitude if map/reporting accuracy is required. |

## B. Configuration Cleanup

| Priority | Area | Configuration Item | Recommended Action |
|---|---|---|---|
| High | CRM | CRM stages | Replace/confirm stages: Enquiry/New, Qualified, Site Visit/Requirement, Quotation, Negotiation, Won, Lost. |
| High | CRM | Lead sources | Align source list with SAVI: Email, Reference, Telephonic, Field Manager Search, Website/Portal, Existing Customer, GEM/Tender, Walk-in/Other. |
| High | CRM | Lost reasons | Standardize and fix typo: Not Responding, Too Expensive, Not Enough Stock, No Budget, Competitor Selected, Requirement Deferred, Duplicate Lead, Not Relevant. |
| High | Sales | Quotation reminders | Set default reminder interval and escalation rule. Existing sent quotations currently have no reminder interval configured. |
| High | Purchase | Approval route | Review PO approval route and amount thresholds. |
| Medium | Inventory | Serial tracking | Audit tracked products and ensure serial selection is enforced where required. |
| Medium | Accounting | Follow-up levels | Configure customer payment follow-up levels and responsible users. |
| Medium | HR | Attendance policy | Define check-in/check-out and location compliance rule. |

## C. User Training / Adoption

| Priority | Area | Issue | Recommended Training |
|---|---|---|---|
| High | Service / SRN | 107 of 108 SRNs are draft. | Train service users on SRN approval/closure and customer feedback flow. |
| High | Service Orders | 154 service orders are in `to_approve`. | Train users/managers on approval step or simplify process if not required. |
| High | Inventory | Only 12 stock pickings are done out of 346. | Train store team on receipt/delivery validation. |
| Medium | AMC | AMC expenses/replacements have no usage. | Train AMC team on expense/replacement tracking for profitability. |
| Medium | HR | 16 open attendances and incomplete checkout locations. | Train employees/HR on checkout discipline and correction process. |
| Medium | Sales | Quotation reminder fields are unused. | Train sales/backend on reminder interval and follow-up process. |

## D. Development Candidates

These should be developed only after the configuration and training items above are confirmed.

| Priority | Module / Feature | Suggested Module Name | Scope |
|---|---|---|---|
| 1 | Message automation matrix | `savi_message_automation` | Enquiry acknowledgement, quotation reminders, order thanks, dispatch updates, service assignment, work completion, payment reminders, AMC due reminders. |
| 2 | Installation execution workflow | `savi_project_execution` | Daily AM/PM site report, photos, blockers, material usage, Gantt/customer timeline, handover checklist, completion certificate, project audit/P&L closure. |
| 3 | Repair workflow | `savi_service_repair` | Onsite/offsite repair, issue photos, inspection, estimate, advance payment, customer approval, solution photos, feedback, repair audit. |
| 4 | Dispatch control | `savi_dispatch_control` | Courier, docket, e-way bill reference, dispatch document checklist, customer receipt proof, delivery confirmation. |
| 5 | Purchase/vendor control | `savi_purchase_vendor_control` | Vendor comparison, credit-period comparison, vendor rating, vendor rotation, defective goods/RMA tracking. |
| 6 | Tender/GEM management | `savi_tender_management` | Tender/GEM source, portal registration, EMD, bid dates, bid documents, technical/commercial status, result tracking. |
| 7 | HR scorecard | `savi_hr_scorecard` | KRA/KPI scorecard, warning/memo records, induction checklist, training assessment, appointment confirmation gate. |

---

# Phase 2 Execution Sequence

## Step 1: Deploy Technical Fix

| Task | Output |
|---|---|
| Test patched HR performance rating compute. | Employee list/report should no longer fail on bulk read. |
| Update module in staging. | Technical blocker removed. |

## Step 2: Configuration Sprint

| Task | Output |
|---|---|
| Clean CRM stages/sources/lost reasons. | Approved CRM master setup. |
| Configure quotation reminder defaults. | Sales follow-up automation usable. |
| Verify AMC and sale reminder scheduled actions. | Reminder jobs active and traceable. |
| Review purchase approval route. | PO approval working as intended. |
| Configure payment follow-up levels. | Finance recovery workflow ready. |

## Step 3: Adoption Sprint

| Task | Output |
|---|---|
| Train Sales on quotation reminders. | Sent quotations have reminder rules. |
| Train Service on SRN closure. | Draft SRNs reduced and closure discipline improved. |
| Train Store on validating receipts/deliveries. | Done transfers increase; stock movement becomes reliable. |
| Train AMC team on expense/replacement tracking. | AMC profitability becomes meaningful. |
| Train HR on attendance corrections and checkout. | Open attendance and missing checkout locations reduced. |

## Step 4: Development Sprint Planning

| Task | Output |
|---|---|
| Finalize functional specification for `savi_message_automation`. | Approved automation trigger matrix. |
| Finalize functional specification for `savi_project_execution`. | Approved installation/project execution workflow. |
| Finalize functional specification for `savi_service_repair`. | Approved repair workflow. |

## Recommended First Development Sprint

Start with `savi_message_automation`, because it supports Sales, AMC, Service, Store, Finance, and HR coordination without changing the core transaction flow.

| Feature | Trigger | Output |
|---|---|---|
| Enquiry acknowledgement | Lead created | Email/WhatsApp message to customer. |
| Quote follow-up | Quotation sent + reminder interval | Reminder to customer and activity for salesperson. |
| Order thanks | Sales order confirmed | Message to customer and internal team. |
| Dispatch update | Delivery assigned/done | Dispatch details to customer and sales/backend. |
| Service assignment | Service order assigned | Message to engineer and customer. |
| Work completion | SRN/service completed | Completion message and feedback request. |
| Payment reminder | Invoice due/overdue | Reminder to customer and activity for finance/sales. |
| AMC due reminder | AMC nearing end date | Renewal reminder to customer and AMC owner. |

## Phase 2 Completion Criteria

| Criteria | Target |
|---|---|
| HR rating compute issue fixed in staging | Required |
| CRM stages/sources/lost reasons cleaned | Required |
| Quotation reminders actively used | Required |
| Service SRN closure process confirmed | Required |
| Inventory receipt/delivery validation process confirmed | Required |
| Accounting usage scope confirmed | Required |
| First development sprint scope approved | Required |
