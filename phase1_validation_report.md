# Phase 1 Validation Report - Existing Workflow Review

System reviewed: `https://staging-savi-odoo.macrofix.com`  
Odoo version: 17.0  
Validation mode: Read-only `execute_kw` checks. No business records or configuration were changed.

## Executive Summary

Phase 1 confirms that the current instance already has the main operational applications and custom flows needed for SAVI's core business: CRM, Sales, Purchase, Inventory, Accounting, AMC, Service Orders, SRN, Helpdesk, HR, Attendance, Payroll, and messaging templates.

The main issue is not missing base modules. The main issue is process readiness: several workflows exist technically, but need configuration cleanup, user validation, or operational discipline before Phase 2 development starts.

## Phase 1 Findings by Area

| Area | Current Validation Result | Risk / Gap | Recommended Phase 1 Action |
|---|---|---|---|
| CRM to quotation | 717 CRM records found: 444 opportunities and 273 leads. CRM stages exist: `MOST IMP TO DO`, `New`, `Qualified`, `Proposition`, `Negotiation`, `Won`. 13 lead sources exist. | CRM stages include a non-standard stage name and may not fully match the PPT process. Only 8 won opportunities were found, which may indicate incomplete stage usage or data migration behavior. | Conduct sales workflow validation with users. Finalize stage names, source list, lost reasons, and mandatory fields. |
| Lead source tracking | Sources exist: Craigslist, Direct, Facebook, Glassdoor, Lead Recall, LinkedIn, Monster, Newsletter, Reference, Search engine, Twitter, email, existing. | PPT sources are email, reference, telephonic, field manager search, website/portal. Current source list contains generic/demo-style sources that do not fully match business terminology. | Clean up lead sources and map them to SAVI source categories. |
| Lost reasons | 4 lost reasons exist: Not enough stock, Too expensive, We don't have people/skills, he is not respodning. | Typo and limited business coverage. Missing reasons such as competitor, price mismatch, no budget, delayed requirement, duplicate enquiry. | Standardize lost reasons and correct typo. |
| Quotation follow-up | 71 quotations are in `sent` state. 0 sent quotations have reminder interval configured. Sale quotation reminder template exists. | Reminder functionality exists but is not being used on sent quotations. This directly impacts the PPT requirement for auto follow-up. | Configure default reminder rules or make reminder interval mandatory before sending quotation. |
| Sales order usage | 1,463 sale orders found: 44 draft, 71 sent, 167 sale, 1,181 cancelled. | High cancellation count needs user confirmation. Could be historical testing, migration cleanup, or process misuse. | Review cancelled orders with sales/admin before cleanup. Do not delete without approval. |
| AMC workflow | 49 AMC orders found: 26 approved, 8 draft, 11 expired, 4 cancelled. AMC site visits exist: 6 done, 5 draft, 1 cancelled. AMC templates exist for proposal, customer send, and satisfaction survey. | AMC flow exists and is active. AMC expenses and replacements show 0 records, so profitability and replacement tracking may not be fully used. | Validate one real AMC lifecycle: order, visit, expense, replacement, quotation, billing, renewal reminder. |
| AMC reminders | Server actions exist: AMC Billing Reminders and Update AMC Validity. | No relevant scheduled cron records were returned in the validation pull, so reminder execution schedule needs UI confirmation. | Check Scheduled Actions in UI and confirm whether AMC reminders are active and timed correctly. |
| Service order workflow | 277 service orders found: 102 approved, 154 to approve, 7 draft, 14 cancelled. | Large number in `to_approve` suggests service orders may be waiting for approval or users are not completing the approval step. | Review approval responsibility and decide whether service orders should auto-approve or require manager approval. |
| SRN workflow | 108 SRNs found: 107 draft, 1 done. | SRN closure is not being used consistently. This is a major service process gap because SRN completion links to job completion and customer satisfaction. | Train service users to approve/close SRNs, or simplify SRN states if the approval step is unnecessary. |
| Helpdesk | 226 helpdesk tickets found. Helpdesk ticket templates exist for assignment, stage change, and close notification. | Helpdesk stages returned 0 through the validation model check, while menus exist. This may be due to module/model difference or configuration issue. | Verify Helpdesk stages in UI and confirm whether tickets are managed through helpdesk stage or alternate service workflow. |
| Engineer check-in/out | Service orders support check-in/out time, images, latitude/longitude, rating, and feedback. Attendance also has location fields. | Technical fields exist, but adoption needs validation. | Test engineer mobile flow with one service order from assignment to check-out and feedback. |
| Purchase workflow | 451 purchase orders found: 49 draft, 10 sent, 37 to approve, 156 purchase, 155 done, 44 cancelled. All 451 have approval-route field populated. | Purchase approval is configured, but pending approvals exist. Need to confirm approval matrix and SLA. | Validate purchase approval route with purchase head and finance. |
| Inventory / delivery | 346 stock pickings found: 297 delivery orders, 46 receipts, 3 internal transfers. States: 143 assigned, 136 cancelled, 26 confirmed, 22 waiting, 12 done, 7 draft. | Very low done count compared to assigned/cancelled indicates delivery/receipt completion may not be consistently validated in Odoo. | Review delivery completion process with store team. Confirm whether users are validating transfers or only using Odoo for document preparation. |
| Accounting | 15 customer/vendor invoices found: 12 draft, 1 posted, 2 cancelled. 3 payments found. | Accounting transaction usage appears limited compared to sales/purchase volume. May indicate invoicing is handled outside Odoo or not fully migrated. | Confirm whether Odoo is intended as primary accounting system. If yes, validate invoice posting, payment registration, GST reports, and follow-up reports. |
| HR / Attendance | 24 employees, 3,931 attendance records. 3,923 records have check-in location. 1,376 have check-out location. 16 open attendance records exist. | Check-in location is widely captured, but check-out location is less complete. Open attendances need review. | Review attendance policy, checkout discipline, and automated attendance action. |
| Leave / Payroll | 2 leave records, both refused. 4 payslips, all draft. | HR/payroll modules exist but limited transaction usage. | Confirm payroll go-live scope and whether leave/payroll are actively used. |
| HR performance review | Existing employee rating fields caused a singleton error when read in bulk. | There is an existing custom code issue in employee performance rating computation. This can affect HR list views or reports that read multiple employees. | Fix computed-field logic before extending HR scorecard. |
| Automation | 40 mail templates exist. Relevant server actions exist for sale reminders, purchase reminders, AMC, birthday/anniversary, attendance, and performance review reminders. Only 1 automation rule was found: auto-fill reference on new activity. | Automation assets exist, but scheduled execution and business-trigger coverage are not yet strong enough for the PPT requirement. | Prepare automation matrix in Phase 2 after workflow owners approve triggers. |

## Immediate Phase 1 Action List

| Priority | Action | Owner / Department | Expected Output |
|---|---|---|---|
| High | Validate CRM stages and enquiry source list. | Sales Head / CRM Admin | Approved CRM pipeline and source master. |
| High | Decide quotation reminder rule. | Sales Head | Default reminder interval and escalation rule. |
| High | Validate one complete AMC cycle. | AMC / Service / Accounts | Confirmed AMC order-to-renewal process. |
| High | Validate one complete service/SRN cycle. | Service Head | Confirmed service order, engineer assignment, SRN closure, feedback flow. |
| High | Review SRNs stuck in draft. | Service Head | Decision: train users, simplify workflow, or automate closure. |
| High | Review stock pickings stuck in assigned/waiting/cancelled. | Store / Operations | Confirm whether inventory validation is being used correctly. |
| Medium | Confirm accounting usage scope. | Finance | Decision whether Odoo is primary accounting or operational-only. |
| Medium | Validate purchase approval route. | Purchase / Finance | Approved PO workflow and approval SLA. |
| Medium | Review open attendance and checkout discipline. | HR | Clean attendance process and policy. |
| Medium | Fix HR performance computed-field issue. | Technical / HR | Stable HR employee list/report behavior. |

## Recommended Phase 1 Workshops

| Workshop | Participants | Agenda |
|---|---|---|
| Sales CRM Workshop | Sales Head, Presales, Backend Coordinator, CRM Admin | CRM stages, enquiry sources, lead ownership, quotation follow-up, lost reasons. |
| AMC Workshop | AMC owner, Service Head, Finance | AMC order, visits, billing schedule, renewal reminders, expenses, replacements, profitability. |
| Service / Repair Workshop | Service Head, Service Coordinator, Engineers | Service order, SRN, check-in/out, photos, repair estimate, feedback, closure. |
| Store / Purchase Workshop | Store, Purchase Head, Finance | PO approval, receipt, dispatch, serials, delivery validation, defective goods. |
| Finance Workshop | Finance Head, Billing, Management | Invoice posting, payment registration, GST reports, MIS, follow-up reports. |
| HR Workshop | HR, Payroll, Management | Attendance, location, open attendance, leave, payroll, performance review. |

## Phase 1 Exit Criteria

Phase 1 should be considered complete only when these items are confirmed:

| # | Exit Criteria | Status |
|---|---|---|
| 1 | CRM stages and lead sources finalized. | Pending user validation |
| 2 | Quotation reminder rule finalized. | Pending user validation |
| 3 | One real AMC transaction validated end-to-end. | Pending user validation |
| 4 | One real service/SRN transaction validated end-to-end. | Pending user validation |
| 5 | Store confirms whether deliveries/receipts should be validated in Odoo. | Pending user validation |
| 6 | Finance confirms accounting usage scope. | Pending user validation |
| 7 | HR confirms attendance/payroll usage scope. | Pending user validation |
| 8 | HR computed-field issue is fixed or accepted as known risk. | Pending technical fix |

## Recommendation Before Phase 2

Do not start large custom development immediately. First, run the Phase 1 workshops and confirm whether the current workflows are intended to be used as-is. The biggest opportunities before development are:

1. Clean CRM stages, sources, and lost reasons.
2. Activate/default quotation reminders.
3. Resolve SRN closure discipline.
4. Validate inventory delivery/receipt completion.
5. Confirm accounting usage scope.
6. Fix the HR employee performance rating computed-field issue.

After these are confirmed, Phase 2 should focus on configuration cleanup and small workflow improvements before building the larger custom modules.
