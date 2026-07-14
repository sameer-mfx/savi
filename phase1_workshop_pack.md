# Phase 1 Workflow Validation Workshop Pack

System: `https://staging-savi-odoo.macrofix.com`  
Purpose: Approve existing workflows and decide what should be handled by configuration versus custom development.

## Workshop Rules

| Rule | Description |
|---|---|
| Keep each workshop short | Target 45-60 minutes per department. |
| Use live Odoo screens | Validate actual menus, records, states, and reports in the staging instance. |
| Decide, do not brainstorm endlessly | Every issue should be marked as `Accept As-Is`, `Configure`, `Develop`, `Train Users`, or `Out of Scope`. |
| Avoid development unless required | If Odoo can support the need through settings, stages, templates, activity plans, access rights, or reports, classify it as configuration first. |
| Capture sign-off | Each department must approve the final workflow before Phase 2 starts. |

## Decision Categories

| Category | Meaning | Example |
|---|---|---|
| Accept As-Is | Existing Odoo flow is good enough. | Standard quotation to sales order. |
| Configure | Existing feature needs setup or cleanup. | CRM stages, sources, reminders, approval routes. |
| Develop | Existing Odoo cannot meet the requirement without customization. | Installation daily site report with AM/PM photos and handover certificate. |
| Train Users | Feature exists, but users are not following the process. | SRN closure, delivery validation, check-out attendance. |
| Out of Scope | Requirement is policy/admin/content and should not be built now. | Motivation activities, employee personal conduct notes. |

---

# 1. Sales Workshop

## Objective

Approve the CRM-to-quotation workflow and decide how lead sources, stages, quotation reminders, ownership, and follow-up should work.

## Suggested Attendees

| Role |
|---|
| Sales Head |
| Presales |
| Sales Backend Coordinator |
| CRM Admin / Odoo Admin |
| Management representative |

## Current System Facts

| Item | Current Status |
|---|---|
| CRM records | 717 records |
| Opportunities | 444 |
| Leads | 273 |
| Won opportunities | 8 |
| CRM stages | `MOST IMP TO DO`, `New`, `Qualified`, `Proposition`, `Negotiation`, `Won` |
| Lead sources | Craigslist, Direct, Facebook, Glassdoor, Lead Recall, LinkedIn, Monster, Newsletter, Reference, Search engine, Twitter, email, existing |
| Sent quotations | 71 |
| Sent quotations with reminder interval | 0 |

## Live Odoo Screens to Review

| Menu / Screen | What to Validate |
|---|---|
| CRM > Sales > My Pipeline | Stage names, stage sequence, ownership, active leads. |
| CRM > Configuration > Pipeline > Stages | Whether current stages match SAVI sales process. |
| CRM > Configuration > Sources | Whether lead source names match actual enquiry sources. |
| CRM > Sales > My Activities | Whether follow-up activities are being used. |
| Sales > Orders > Quotations | Quotation states, reminder fields, quotation validity. |
| Sales email templates | Quotation, quotation reminder, order confirmation templates. |

## Validation Questions

| # | Question | Decision Needed |
|---|---|---|
| 1 | What are the final CRM stages from enquiry to order? | Configure |
| 2 | Should `MOST IMP TO DO` remain as a CRM stage? | Configure |
| 3 | What are the approved enquiry source values? | Configure |
| 4 | Should source be mandatory on every lead? | Configure / Develop |
| 5 | Should enquiry email/document attachment be mandatory? | Configure / Develop |
| 6 | Who owns a lead from enquiry to payment: salesperson, backend, or shared? | Process decision |
| 7 | Should quotations automatically get follow-up reminders? | Configure |
| 8 | What is the default reminder interval after sending quotation? | Configure |
| 9 | Should reminder escalation go to sales head/manager? | Configure / Develop |
| 10 | Should quotation show internal P&L/margin before sending? | Develop if beyond current margin fields |

## Configure vs Develop Recommendation

| Requirement | Recommendation | Notes |
|---|---|---|
| CRM stage cleanup | Configure | Rename/resequence stages. |
| Enquiry source cleanup | Configure | Replace generic/demo-style sources with SAVI terms. |
| Lost reason cleanup | Configure | Fix typo and add approved lost reasons. |
| Quotation reminder interval | Configure | Use existing reminder fields/template. |
| Mandatory source | Configure or small development | Depends whether view/settings can enforce it cleanly. |
| Enquiry attachment checklist | Develop if mandatory workflow is required | Standard chatter attachment exists, but checklist enforcement needs development. |
| Internal BOQ/P&L approval | Develop | Current sale margin exists, but formal BOQ/P&L approval is not present. |

## Sales Sign-Off Criteria

| Criteria | Status |
|---|---|
| CRM stages approved | Pending |
| Lead sources approved | Pending |
| Lost reasons approved | Pending |
| Quotation reminder rule approved | Pending |
| Lead ownership rule approved | Pending |
| Configuration/development items approved | Pending |

---

# 2. AMC / Service Workshop

## Objective

Approve AMC, service order, SRN, engineer allocation, check-in/out, feedback, repair, and renewal workflows.

## Suggested Attendees

| Role |
|---|
| Service Head |
| AMC Owner |
| Service Coordinator |
| Field Engineer representative |
| Finance/Billing representative |
| Odoo Admin |

## Current System Facts

| Item | Current Status |
|---|---|
| AMC orders | 49 |
| AMC states | 26 approved, 8 draft, 11 expired, 4 cancelled |
| AMC site visits | 12 |
| AMC expenses | 0 |
| AMC replacements | 0 |
| Service orders | 277 |
| Service order states | 102 approved, 154 to approve, 7 draft, 14 cancelled |
| SRNs | 108 |
| SRN states | 107 draft, 1 done |
| Helpdesk tickets | 226 |

## Live Odoo Screens to Review

| Menu / Screen | What to Validate |
|---|---|
| AMC Management > Orders | AMC lifecycle, start/end dates, expiry, visits, profitability. |
| AMC Management > Visits | Site visit process and feedback. |
| Service Orders > Orders | Approval states, engineer assignment, visit date, customer. |
| Service Orders > SRN | Job card/SRN creation and closure. |
| Helpdesk > Tickets | Ticket intake and assignment process. |
| Service Order check-in/out fields | Location, images, feedback, rating. |

## Validation Questions

| # | Question | Decision Needed |
|---|---|---|
| 1 | Should AMC order approval remain mandatory? | Process / Configure |
| 2 | Who creates AMC visits and who closes them? | Process |
| 3 | Should AMC expenses be mandatory for profitability? | Configure / Train |
| 4 | Should AMC replacements be tracked in Odoo? | Configure / Train |
| 5 | What should happen one month before AMC expiry? | Configure / Develop |
| 6 | Why are many service orders in `to_approve`? | Process / Train / Configure |
| 7 | Should service orders auto-approve after assignment? | Configure / Develop |
| 8 | Why are 107 SRNs still draft? | Train / Configure |
| 9 | Is SRN approval required, or should completion close SRN directly? | Process / Develop |
| 10 | What fields are mandatory for repair: issue photo, inspection, estimate, advance payment, solution photo? | Develop |
| 11 | Is engineer check-in/out mandatory for every visit? | Configure / Train |
| 12 | Should feedback email be sent automatically after SRN closure? | Configure / Develop |

## Configure vs Develop Recommendation

| Requirement | Recommendation | Notes |
|---|---|---|
| AMC order and visits | Accept As-Is + Train | Base custom flow exists. |
| AMC expiry and billing reminders | Configure first | Verify scheduled action and reminder rule. |
| AMC expense/replacement tracking | Train Users | Models exist but no records found. |
| Service order approval cleanup | Configure / Train | Decide whether `to_approve` is real approval or bottleneck. |
| SRN closure discipline | Train or Develop | If current states are too heavy, simplify workflow. |
| Engineer check-in/out | Train Users | Fields exist; adoption must be tested. |
| Repair estimate/advance/offsite flow | Develop | Current service flow is generic. |
| Completion certificate/job card format | Develop | If exact customer-facing document is required. |

## AMC / Service Sign-Off Criteria

| Criteria | Status |
|---|---|
| AMC lifecycle approved | Pending |
| AMC reminder rule approved | Pending |
| Service order approval rule approved | Pending |
| SRN closure rule approved | Pending |
| Engineer check-in/out rule approved | Pending |
| Repair workflow scope approved | Pending |

---

# 3. Store / Purchase Workshop

## Objective

Approve purchase approval, vendor comparison, receipts, serial tracking, dispatch, delivery validation, and defective goods process.

## Suggested Attendees

| Role |
|---|
| Purchase Head |
| Store Head |
| Finance representative |
| Sales/Backend representative |
| Odoo Admin |

## Current System Facts

| Item | Current Status |
|---|---|
| Purchase orders | 451 |
| PO states | 49 draft, 10 sent, 37 to approve, 156 purchase, 155 done, 44 cancelled |
| Purchase approval route field | Populated on 451 POs |
| Stock pickings | 346 |
| Picking types | 297 delivery orders, 46 receipts, 3 internal transfers |
| Picking states | 143 assigned, 136 cancelled, 26 confirmed, 22 waiting, 12 done, 7 draft |

## Live Odoo Screens to Review

| Menu / Screen | What to Validate |
|---|---|
| Purchase > Orders > Requests for Quotation | RFQ creation, vendor quote, approval route. |
| Purchase > Orders > Purchase Orders | PO approval and confirmation. |
| Inventory > Operations > Receipts | Goods receipt process. |
| Inventory > Operations > Deliveries | Dispatch and delivery validation. |
| Inventory > Products > Lots/Serial Numbers | Serial tracking discipline. |
| Inventory > Reporting > Stock | Stock visibility and audit. |

## Validation Questions

| # | Question | Decision Needed |
|---|---|---|
| 1 | Is the current PO approval route correct? | Configure |
| 2 | Who approves POs and at what amount limits? | Configure |
| 3 | Should vendor comparison be mandatory before PO? | Develop |
| 4 | Should vendor rotation be tracked or only reviewed manually? | Develop / Report |
| 5 | Should receipt validation be mandatory before vendor bill? | Configure |
| 6 | Why are only 12 stock pickings done? | Process / Train |
| 7 | Should delivery proof be mandatory before completing delivery? | Develop |
| 8 | What dispatch fields are required: courier, docket, e-way bill, documents, receipt proof? | Develop |
| 9 | How should defective/damaged stock be tracked? | Configure / Develop |
| 10 | Should monthly store audit be an Odoo checklist/report? | Develop / Report |

## Configure vs Develop Recommendation

| Requirement | Recommendation | Notes |
|---|---|---|
| PO approval route | Configure | Existing approval route field exists. |
| Receipt validation | Train / Configure | Existing inventory receipts available. |
| Serial number tracking | Configure / Train | Lots/serials exist. |
| Vendor comparison | Develop | Not available as formal SAVI workflow. |
| Vendor rotation | Develop / Report | Needs custom report or rule. |
| Dispatch checklist | Develop | Standard delivery exists, but checklist/proof is not enforced. |
| Damage/defective goods | Configure first, develop if RMA detail needed | Scrap/adjustment exists; RMA workflow needs customization. |

## Store / Purchase Sign-Off Criteria

| Criteria | Status |
|---|---|
| PO approval route approved | Pending |
| Receipt process approved | Pending |
| Delivery validation process approved | Pending |
| Serial tracking rule approved | Pending |
| Dispatch checklist scope approved | Pending |
| Defective goods/RMA scope approved | Pending |

---

# 4. Finance Workshop

## Objective

Confirm accounting usage scope and approve invoice, payment, GST, TDS, payroll statutory, MIS, and follow-up processes.

## Suggested Attendees

| Role |
|---|
| Finance Head |
| Billing user |
| Accounts payable user |
| Management representative |
| Odoo Admin |

## Current System Facts

| Item | Current Status |
|---|---|
| Customer/vendor invoices | 15 |
| Invoice states | 12 draft, 1 posted, 2 cancelled |
| Payments | 3 |
| Sales orders | 1,463 |
| Purchase orders | 451 |

## Live Odoo Screens to Review

| Menu / Screen | What to Validate |
|---|---|
| Accounting > Customers > Invoices | Invoice creation and posting. |
| Accounting > Vendors > Bills | Vendor bill process. |
| Accounting > Customers/Vendors > Payments | Payment registration. |
| Accounting > Reporting | P&L, balance sheet, partner ledger, tax report. |
| Accounting > Customers > Follow-up Reports | Payment follow-up process. |
| Payroll | Salary and statutory payroll flow if in scope. |

## Validation Questions

| # | Question | Decision Needed |
|---|---|---|
| 1 | Is Odoo intended to be the primary accounting system? | Scope decision |
| 2 | If yes, why are only 15 invoices and 3 payments present? | Process / Migration |
| 3 | Should invoices be generated from sales/delivery only? | Configure |
| 4 | Should vendor bills require receipt/PO validation? | Configure |
| 5 | What GST reports must be generated from Odoo? | Configure / Report |
| 6 | Are GST/TDS/PF/ESI portal filings expected inside Odoo? | Develop / Out of Scope |
| 7 | What monthly MIS pack is required? | Report / Develop |
| 8 | Should payment reminders be automated? | Configure / Develop |
| 9 | Should project/order P&L closure be approved by Finance? | Develop |

## Configure vs Develop Recommendation

| Requirement | Recommendation | Notes |
|---|---|---|
| Invoice and payment process | Configure / Train | Standard Odoo accounting exists. |
| Follow-up reports | Configure | Existing accounting follow-up can be used. |
| GST reporting | Configure / Validate | India localization exists. |
| TDS/PF/ESI portal filing | Out of Scope unless approved | Usually external/statutory portal process. |
| Daily/monthly MIS pack | Report / Develop | Need KPI format from management. |
| Project/order P&L closure | Develop | Formal audit closure is not standard. |

## Finance Sign-Off Criteria

| Criteria | Status |
|---|---|
| Accounting usage scope approved | Pending |
| Invoice posting workflow approved | Pending |
| Payment registration workflow approved | Pending |
| GST reporting scope approved | Pending |
| Payment reminder rule approved | Pending |
| MIS format approved | Pending |

---

# 5. HR Workshop

## Objective

Approve attendance, leave, payroll, performance review, scorecard, induction, and HR policy automation scope.

## Suggested Attendees

| Role |
|---|
| HR Head |
| Payroll user |
| Management representative |
| Odoo Admin |

## Current System Facts

| Item | Current Status |
|---|---|
| Employees | 24 |
| Attendance records | 3,931 |
| Attendance with check-in location | 3,923 |
| Attendance with check-out location | 1,376 |
| Open attendance records | 16 |
| Leave records | 2, both refused |
| Payslips | 4, all draft |
| HR rating technical issue | Employee rating computed field fails on bulk read |

## Live Odoo Screens to Review

| Menu / Screen | What to Validate |
|---|---|
| Employees | Employee master, department, job, work location. |
| Attendances | Check-in/out, open attendance, geolocation. |
| Time Off | Leave request and approval. |
| Payroll | Payslip creation, batches, salary rules. |
| Performance Review | Review templates, cycles, ratings, goals. |

## Validation Questions

| # | Question | Decision Needed |
|---|---|---|
| 1 | Is location-based attendance mandatory for all employees? | Configure / Train |
| 2 | Is check-out location mandatory? | Configure / Develop |
| 3 | Who reviews open attendances? | Process |
| 4 | Is leave approval active in Odoo? | Configure / Train |
| 5 | Is payroll expected to be generated from Odoo? | Scope decision |
| 6 | Should performance review be periodic or daily/weekly scorecard? | Configure / Develop |
| 7 | What KRA/KPI metrics are required? | Develop |
| 8 | Should memo/warning/penalty be tracked in Odoo? | Develop / Policy |
| 9 | Should induction checklist and exam be managed in Odoo? | Develop |
| 10 | Should birthday/anniversary emails remain automated? | Configure |

## Configure vs Develop Recommendation

| Requirement | Recommendation | Notes |
|---|---|---|
| Attendance usage | Train / Configure | Data exists and is widely used. |
| Check-out compliance | Train first, develop enforcement if needed | Only 1,376 records have checkout location. |
| Leave workflow | Configure / Train | Low usage currently. |
| Payroll workflow | Scope decision | Payslips exist but are draft. |
| Performance reviews | Configure existing module first | Custom review module exists. |
| Daily scorecard / traffic light | Develop | Beyond current periodic review behavior. |
| Memo/warning/penalty | Develop only after policy approval | Sensitive HR policy workflow. |
| Induction exam | Develop if required | Not covered by current HR flow. |
| HR rating computed-field issue | Technical fix | Must be fixed before HR scorecard expansion. |

## HR Sign-Off Criteria

| Criteria | Status |
|---|---|
| Attendance policy approved | Pending |
| Leave usage scope approved | Pending |
| Payroll usage scope approved | Pending |
| Performance review scope approved | Pending |
| Scorecard/KRA scope approved | Pending |
| HR technical fix approved | Pending |

---

# Consolidated Approval Tracker

| Department | Workflow Area | Decision Required | Recommended Category | Final Decision | Owner | Due Date |
|---|---|---|---|---|---|---|
| Sales | CRM stages | Approve final stages and sequence | Configure | Pending | Sales Head | TBD |
| Sales | Enquiry sources | Approve final source list | Configure | Pending | Sales Head | TBD |
| Sales | Quotation reminders | Approve default reminder interval/escalation | Configure | Pending | Sales Head | TBD |
| Sales | BOQ/P&L approval | Decide if formal internal approval is needed | Develop | Pending | Sales + Finance | TBD |
| AMC/Service | AMC lifecycle | Approve order, visit, billing, renewal flow | Accept As-Is / Configure | Pending | Service Head | TBD |
| AMC/Service | AMC reminder | Confirm reminder timing and recipients | Configure | Pending | AMC Owner | TBD |
| AMC/Service | Service order approval | Decide if approval step stays | Configure / Train | Pending | Service Head | TBD |
| AMC/Service | SRN closure | Decide closure rule and responsibility | Train / Develop | Pending | Service Head | TBD |
| AMC/Service | Repair workflow | Approve repair-specific fields/checklist | Develop | Pending | Service Head | TBD |
| Store/Purchase | PO approval | Approve approval route and amount limits | Configure | Pending | Purchase Head | TBD |
| Store/Purchase | Receipt validation | Decide mandatory receipt process | Configure / Train | Pending | Store Head | TBD |
| Store/Purchase | Dispatch checklist | Approve required dispatch proof fields | Develop | Pending | Store Head | TBD |
| Store/Purchase | Vendor comparison | Decide whether mandatory before PO | Develop | Pending | Purchase Head | TBD |
| Store/Purchase | Defective goods/RMA | Approve tracking process | Configure / Develop | Pending | Store + Purchase | TBD |
| Finance | Accounting scope | Confirm whether Odoo is primary accounting | Scope Decision | Pending | Finance Head | TBD |
| Finance | GST/TDS/statutory | Decide Odoo vs external portal scope | Configure / Out of Scope | Pending | Finance Head | TBD |
| Finance | Payment reminders | Approve reminder rules | Configure / Develop | Pending | Finance Head | TBD |
| Finance | MIS | Approve required KPI/report format | Report / Develop | Pending | Finance + Management | TBD |
| HR | Attendance policy | Approve check-in/out and location rules | Configure / Train | Pending | HR Head | TBD |
| HR | Leave/payroll | Confirm active usage scope | Configure / Train | Pending | HR + Finance | TBD |
| HR | Performance review | Decide periodic review vs daily scorecard | Configure / Develop | Pending | HR Head | TBD |
| HR | Memo/warning/penalty | Decide if system tracking is required | Develop / Policy | Pending | HR + Management | TBD |
| HR | Induction/exam | Decide if Odoo workflow is required | Develop | Pending | HR Head | TBD |

## Recommended Workshop Sequence

| Order | Workshop | Duration | Reason |
|---|---|---|---|
| 1 | Sales | 60 min | Sales pipeline drives downstream purchase, project, service, billing. |
| 2 | AMC / Service | 60 min | Largest workflow gap is SRN/service closure discipline and repair process. |
| 3 | Store / Purchase | 60 min | Depends on sales/service demand and affects billing. |
| 4 | Finance | 60 min | Needs decisions from sales, purchase, and service flows. |
| 5 | HR | 45 min | Can proceed independently except payroll/accounting overlap. |

## Output Expected After Workshops

| Output | Description |
|---|---|
| Approved workflow decisions | Each tracker line has a final decision. |
| Configuration backlog | Items that can be handled through Odoo setup. |
| Development backlog | Items that require custom modules or code changes. |
| Training backlog | Existing features that users need to adopt correctly. |
| Out-of-scope list | Items that should not be implemented in this phase. |
| Phase 2 readiness decision | Management approval to begin configuration cleanup and/or development. |
