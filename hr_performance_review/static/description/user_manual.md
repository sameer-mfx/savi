# HR Performance Review Module — User Manual

**Module:** HR Performance Review
**Version:** 17.0.1.0.0
**Platform:** Odoo 17 Community Edition
**Author:** Macrofix

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [User Roles & Permissions](#2-user-roles--permissions)
3. [Module Navigation](#3-module-navigation)
4. [Phase 1 — Initial Setup](#4-phase-1--initial-setup)
5. [Phase 2 — Creating a Review Cycle](#5-phase-2--creating-a-review-cycle)
6. [Phase 3 — Generating Reviews](#6-phase-3--generating-reviews)
7. [Phase 4 — Starting the Review Cycle](#7-phase-4--starting-the-review-cycle)
8. [Phase 5 — Employee Self-Review](#8-phase-5--employee-self-review)
9. [Phase 6 — Manager Review](#9-phase-6--manager-review)
10. [Phase 7 — HR Review & Approval](#10-phase-7--hr-review--approval)
11. [Phase 8 — Completing the Review Cycle](#11-phase-8--completing-the-review-cycle)
12. [Goal Tracking](#12-goal-tracking)
13. [Employee Performance History](#13-employee-performance-history)
14. [Rating System & Formula](#14-rating-system--formula)
15. [Email Notifications](#15-email-notifications)
16. [Frequently Asked Questions (FAQ)](#16-frequently-asked-questions-faq)

---

## 1. Introduction

The HR Performance Review module provides a complete performance management system for your organization. It enables structured employee evaluations through configurable review cycles, weighted evaluation criteria, goal tracking, and a multi-stage approval workflow.

### Key Features

- **Review Cycles** — Quarterly, Semi-Annual, Annual, or Custom review periods
- **Customizable Templates** — Define evaluation criteria with weighted scoring categories
- **Multi-Stage Workflow** — Draft → Self-Review → Manager Review → HR Review → Completed
- **Goal Tracking** — Set, track, and measure employee goals with progress tracking
- **Automated Scoring** — Weighted final rating calculated automatically
- **Email Notifications** — Automatic notifications at each stage of the review process
- **Performance History** — Track employee ratings across multiple review cycles
- **Role-Based Access** — Separate views and permissions for Employees, Managers, and HR Officers

---

## 2. User Roles & Permissions

The module has three security roles, each with increasing levels of access:

| Role | Who Should Have It | What They Can Do |
|------|-------------------|------------------|
| **Employee (Self-Review)** | All employees | View and submit their own reviews; view and manage their own goals |
| **Manager** | Team leads, supervisors | Everything an Employee can do, plus: manage reviews for their direct reports; create and assign goals to team members |
| **HR Officer** | HR department staff | Full access to everything: manage all reviews, cycles, templates, goals; approve and complete reviews |

### How to Assign Roles

1. Navigate to **Settings** → **Users & Companies** → **Users**
2. Select the user
3. Scroll down to the **Performance Reviews** section
4. Select the appropriate role: Employee, Manager, or HR Officer
5. Click **Save**

> **Note:** Each role includes the permissions of the roles below it. An HR Officer automatically has Manager and Employee permissions.

---

## 3. Module Navigation

After installation, you will find the **Performance** application in the main menu. The menu structure is organized as follows:

```
Performance
├── My
│   ├── My Reviews          ← Employee's own performance reviews
│   └── My Goals            ← Employee's personal goals
├── Team                    ← Visible to Managers only
│   └── Team Reviews        ← Reviews of the manager's direct reports
├── Reviews                 ← Visible to HR Officers only
│   ├── All Reviews         ← All performance reviews across the organization
│   ├── All Goals           ← All goals across the organization
│   └── Review Cycles       ← Manage review cycle periods
└── Configuration           ← Visible to HR Officers only
    └── Review Templates    ← Define evaluation criteria templates
```

---

## 4. Phase 1 — Initial Setup

Before starting your first review cycle, you need to create a Review Template. Templates define the evaluation criteria and their weights that will be used to score employee performance.

### Step 1: Create a Review Template

1. Navigate to **Performance** → **Configuration** → **Review Templates**
2. Click **New**
3. Fill in the following fields:

| Field | Description | Required |
|-------|-------------|----------|
| **Template Name** | A descriptive name for the template (e.g., "Standard Annual Review") | Yes |
| **Company** | The company this template applies to (visible only in multi-company setups) | No |
| **Applicable Departments** | Restrict template to specific departments. Leave empty to apply to all departments. | No |
| **Applicable Job Positions** | Restrict template to specific job positions. Leave empty to apply to all positions. | No |
| **Description** | A brief description of the template's purpose | No |

### Step 2: Add Evaluation Criteria

In the **Evaluation Criteria** tab, add the criteria by which employees will be evaluated. Each criterion requires:

| Field | Description |
|-------|-------------|
| **Criteria Name** | The name of the evaluation criteria (e.g., "Job Knowledge") |
| **Category** | The type of criteria: Job Performance, Core Competencies, Behavioral, Leadership, Teamwork, Communication, Innovation, or Other |
| **Weight (%)** | The percentage weight of this criteria in the overall score |
| **Description** | Optional detailed description of what this criteria evaluates |

> **Important:** The total weight of all criteria must equal exactly **100%**. The system will show an error if the weights do not add up to 100%.

### Example Template

Here is a sample template configuration:

| Criteria Name | Category | Weight (%) |
|--------------|----------|------------|
| Job Knowledge | Job Performance | 25 |
| Communication Skills | Communication | 20 |
| Teamwork & Collaboration | Teamwork | 20 |
| Problem Solving | Core Competencies | 15 |
| Initiative & Innovation | Innovation | 10 |
| Punctuality & Attendance | Behavioral | 10 |
| **Total** | | **100** |

4. Click **Save**

> **Tip:** You can create multiple templates for different departments, job positions, or review types (e.g., one for sales staff, another for engineers).

---

## 5. Phase 2 — Creating a Review Cycle

A Review Cycle defines the time period for performance reviews and links to a template. All reviews within a cycle use the same evaluation criteria.

### Step 1: Create a New Cycle

1. Navigate to **Performance** → **Reviews** → **Review Cycles**
2. Click **New**
3. Fill in the following fields:

| Field | Description | Required |
|-------|-------------|----------|
| **Cycle Name** | A descriptive name (e.g., "Annual Review 2026", "Q1 2026 Review") | Yes |
| **Cycle Type** | Quarterly, Semi-Annual, Annual, or Custom | Yes |
| **Start Date** | The beginning of the review period | Yes |
| **End Date** | The end of the review period (must be after Start Date) | Yes |
| **Self-Review Deadline** | Deadline for employees to complete their self-assessment | No |
| **Manager Review Deadline** | Deadline for managers to complete their evaluation | No |
| **Review Template** | The evaluation template to use for this cycle | Yes |
| **Departments** | Restrict the cycle to specific departments. Leave empty for all departments. | No |

4. Click **Save**

The cycle is now in **Draft** status and is ready for review generation.

---

## 6. Phase 3 — Generating Reviews

Once a cycle is created, you need to generate individual reviews for employees. This creates one review record per employee.

### Step 1: Open the Generate Reviews Wizard

1. Open the review cycle you created
2. Click the **Generate Reviews** button in the top-left corner
3. A dialog window (wizard) will appear

### Step 2: Configure Generation Options

| Field | Description |
|-------|-------------|
| **Departments** | Pre-filled from the cycle settings. You can adjust if needed. Leave empty for all departments. |
| **Specific Employees** | Select specific employees to generate reviews for. Leave empty to include all employees in the selected departments. |
| **Skip Existing Reviews** | When checked (default), employees who already have a review in this cycle will be skipped. This prevents duplicates if you run the wizard multiple times. |

### Step 3: Generate

1. Click **Generate**
2. A success notification will appear showing:
   - How many reviews were created
   - How many employees were skipped (if any already had reviews)
3. You will be taken to the list of generated reviews

### Step 4: Verify

1. Go back to the review cycle form
2. Click the **Reviews** stat button (top of the form) to see all generated reviews
3. Each review will show:
   - The employee's name
   - Their manager (auto-assigned from the employee's manager field)
   - Status: **Draft**

> **Note:** The wizard automatically assigns each employee's direct manager as the reviewer. If an employee has no manager assigned, the Manager field will be empty and should be filled in manually before starting the cycle.

---

## 7. Phase 4 — Starting the Review Cycle

Starting the cycle activates all reviews and notifies employees to begin their self-assessments.

### Step 1: Start the Cycle

1. Open the review cycle
2. Click the **Start Cycle** button
3. A confirmation dialog will appear: *"This will start the review cycle and notify all employees. Continue?"*
4. Click **OK** to confirm

### What Happens Automatically

- The cycle status changes from **Draft** to **In Progress**
- All draft reviews within the cycle move to the **Self-Review** stage
- Each employee receives an **email notification** requesting them to complete their self-assessment

> **Important:** You cannot start a cycle that has no reviews. Generate reviews first using the wizard.

---

## 8. Phase 5 — Employee Self-Review

This is the employee's turn to evaluate their own performance.

### For the Employee

1. Navigate to **Performance** → **My** → **My Reviews**
2. Open the review with status **Self-Review**

### Step 1: Rate Yourself on Each Criteria

1. Go to the **Evaluation Criteria** tab
2. For each criteria row, enter:

| Field | Description |
|-------|-------------|
| **Self Score** | Your self-rating on a scale of **0 to 5** (0 = Not Applicable, 1 = Poor, 5 = Excellent) |
| **Self Comment** | Optional comments explaining your self-rating |

> **Note:** The criteria, category, and weight columns are read-only — they are set by the template and cannot be changed.

### Step 2: Write Your Self-Assessment

1. Go to the **Self-Assessment** tab
2. Fill in the following text fields:

| Field | Description |
|-------|-------------|
| **Employee Self-Assessment Summary** | A summary of your overall performance during the review period |
| **Self-Identified Strengths** | Areas where you believe you excelled |
| **Areas for Improvement (Self)** | Areas where you see room for growth |

### Step 3: Submit

1. Click the **Submit Self-Review** button
2. The review status changes to **Manager Review**
3. Your manager receives an email notification that your self-review is ready for their evaluation

> **Note:** Once submitted, the self-assessment fields become read-only. Make sure you have completed everything before submitting.

---

## 9. Phase 6 — Manager Review

The manager now evaluates the employee's performance, having visibility into the employee's self-scores for reference.

### For the Manager

1. Navigate to **Performance** → **Team** → **Team Reviews**
2. Open the review with status **Manager Review**

### Step 1: Review Employee's Self-Assessment

- The **Evaluation Criteria** tab shows the employee's self-scores and comments
- The **Self-Assessment** tab shows the employee's written self-assessment
- Use these as reference points for your own evaluation

### Step 2: Provide Manager Ratings

1. In the **Evaluation Criteria** tab, for each criteria row, enter:

| Field | Description |
|-------|-------------|
| **Manager Score** | Your assessment on a scale of **0 to 5** |
| **Manager Comment** | Optional comments justifying your rating |

### Step 3: Write Manager Assessment

1. Go to the **Manager Assessment** tab (now visible)
2. Fill in:

| Field | Description |
|-------|-------------|
| **Manager Assessment Summary** | Your overall assessment of the employee's performance |
| **Strengths (Manager)** | Key strengths you have observed |
| **Areas for Improvement (Manager)** | Areas where the employee should focus on improving |

### Step 4: Submit

1. Click the **Submit Manager Review** button
2. The review status changes to **HR Review**

---

## 10. Phase 7 — HR Review & Approval

HR performs the final review, adds any comments, and approves the review to complete the process.

### For the HR Officer

1. Navigate to **Performance** → **Reviews** → **All Reviews**
2. Open the review with status **HR Review**

### Step 1: Review the Rating Summary

At the top of the form, the **Rating Summary** section displays automatically calculated scores:

| Field | Description |
|-------|-------------|
| **Self Rating** | Weighted average of the employee's self-scores |
| **Manager Rating** | Weighted average of the manager's scores |
| **Goal Achievement (%)** | Average progress across all linked goals |
| **Final Rating** | Overall rating calculated using the formula (see Section 14) |
| **Performance Level** | Label based on the final rating (e.g., "Exceeds Expectations") |

### Step 2: Add HR Comments (Optional)

1. Go to the **HR Comments** tab (visible only to HR Officers)
2. Enter any final notes, observations, or recommendations

### Step 3: Approve

1. Click the **Approve & Complete** button
2. The review status changes to **Done**
3. The employee's **HR Review Rating** on their employee record is automatically updated with the final rating
4. The employee receives an **email notification** confirming the review is completed, along with their final rating and performance level

---

## 11. Phase 8 — Completing the Review Cycle

Once all individual reviews in a cycle are completed, the cycle itself can be marked as completed.

### Step 1: Complete the Cycle

1. Navigate to **Performance** → **Reviews** → **Review Cycles**
2. Open the cycle
3. Click **Complete Cycle**
4. The cycle status changes to **Completed**

> **Important:** You cannot complete a cycle if any reviews are still pending (not in "Done" or "Cancelled" status). The system will display an error message showing how many reviews are still pending.

### Cancelling a Review or Cycle

- **Cancel a single review:** Open the review and click **Cancel**. The review can be reset to Draft later if needed.
- **Cancel an entire cycle:** Open the cycle and click **Cancel**. This will cancel all reviews within the cycle that are not already completed.
- **Reset to Draft:** Both cancelled reviews and cancelled cycles can be reset to Draft status to start over.

---

## 12. Goal Tracking

Goals can be created independently or linked to a specific performance review. When linked, goal progress contributes to the final rating calculation.

### Creating a Goal

1. Navigate to **Performance** → **My** → **My Goals** (for employees) or **Performance** → **Reviews** → **All Goals** (for HR)
2. Click **New**
3. Fill in:

| Field | Description | Required |
|-------|-------------|----------|
| **Goal Title** | A clear, specific title for the goal | Yes |
| **Employee** | The employee this goal is assigned to | Yes |
| **Assigned By** | The manager who assigned this goal (auto-filled with current user) | No |
| **Performance Review** | Link to a specific review (optional) | No |
| **Goal Type** | Performance, Development, Project, Learning, or Behavioral | Yes |
| **Priority** | Low, Medium, High, or Critical | No |
| **Deadline** | Target completion date | No |
| **Success Metric** | How the goal will be measured (e.g., "Close 10 deals", "Complete certification") | No |
| **Description** | Detailed description of the goal | No |

4. Click **Save**

### Goal Lifecycle

Goals follow this workflow:

```
Draft → In Progress → Achieved / Partially Achieved / Not Achieved
                   ↘ Cancelled
```

| Action | Button | Effect |
|--------|--------|--------|
| **Start** | Click **Start** | Moves from Draft to In Progress |
| **Update Progress** | Edit the **Progress (%)** field | Update the completion percentage (0-100%) |
| **Mark Achieved** | Click **Mark Achieved** | Sets status to Achieved and progress to 100% |
| **Partially Achieved** | Click **Partially Achieved** | Sets status to Partially Achieved at current progress |
| **Not Achieved** | Click **Not Achieved** | Sets status to Not Achieved |
| **Cancel** | Click **Cancel** | Cancels the goal |
| **Reset** | Click **Reset** | Returns to Draft and resets progress to 0% (Manager only) |

### Notes

- Both employees and managers can add notes on the **Notes** tab
- **Employee Notes:** Progress updates, challenges, milestones
- **Manager Notes:** Feedback, guidance, observations (visible only to managers and above)

### Goal Impact on Rating

If goals are linked to a performance review, their average progress contributes **10%** to the final rating calculation. See Section 14 for the full formula.

---

## 13. Employee Performance History

The module adds performance tracking information to each employee's record.

### Viewing Performance Data

1. Navigate to **Employees** → open any employee
2. At the top of the form, you will see two new stat buttons:
   - **Reviews** — Click to view all performance reviews for this employee
   - **Goals** — Click to view all goals for this employee

3. Scroll to the **Performance** tab (visible to Managers and HR Officers) to see:

| Field | Description |
|-------|-------------|
| **Last Review Date** | The date of the most recently completed review |
| **Last Review Rating** | The final rating from the most recent completed review |
| **Average Rating** | The average of all completed review final ratings across all cycles |

4. Below these fields, a **review history table** shows all reviews with:
   - Reference number, review cycle, review date
   - Self rating, manager rating, final rating
   - Performance level label and status

---

## 14. Rating System & Formula

### Scoring Scale

All individual criteria are scored on a **0 to 5** scale:

| Score | Meaning |
|-------|---------|
| 0 | Not Applicable / Not Rated |
| 1 | Needs Significant Improvement |
| 2 | Below Expectations |
| 3 | Meets Expectations |
| 4 | Exceeds Expectations |
| 5 | Outstanding / Exceptional |

### Weighted Score Calculation

**Self Rating** and **Manager Rating** are each calculated as weighted averages:

```
Rating = Sum of (Score x Weight) / Total Weight
```

**Example:**

| Criteria | Weight | Manager Score | Weighted |
|----------|--------|---------------|----------|
| Job Knowledge | 25% | 4 | 100 |
| Communication | 20% | 3 | 60 |
| Teamwork | 20% | 5 | 100 |
| Problem Solving | 15% | 4 | 60 |
| Initiative | 10% | 3 | 30 |
| Punctuality | 10% | 5 | 50 |
| **Total** | **100%** | | **400** |

**Manager Rating = 400 / 100 = 4.00**

### Final Rating Formula

The final rating combines three components:

```
Final Rating = (Manager Rating x 70%) + (Self Rating x 20%) + (Goal Score x 10%)
```

Where:

```
Goal Score = (Average Goal Progress % / 100) x 5.0
```

**Example:**

| Component | Value | Weight | Contribution |
|-----------|-------|--------|-------------|
| Manager Rating | 4.00 | 70% | 2.80 |
| Self Rating | 4.10 | 20% | 0.82 |
| Goal Score (80% progress = 4.0) | 4.00 | 10% | 0.40 |
| **Final Rating** | | | **4.02** |

### Performance Level Labels

The final rating is automatically mapped to a performance level:

| Final Rating | Performance Level |
|-------------|-------------------|
| 4.50 — 5.00 | Outstanding |
| 3.50 — 4.49 | Exceeds Expectations |
| 2.50 — 3.49 | Meets Expectations |
| 1.50 — 2.49 | Below Expectations |
| 0.00 — 1.49 | Needs Improvement |

---

## 15. Email Notifications

The module sends automatic email notifications at key stages:

| Stage | Recipient | When | Content |
|-------|-----------|------|---------|
| **Self-Review Request** | Employee | When the cycle is started or review moves to Self-Review | Requests the employee to complete their self-assessment |
| **Manager Review Request** | Manager | When the employee submits their self-review | Notifies the manager that the self-review is ready for evaluation |
| **Review Completed** | Employee | When HR approves and completes the review | Notifies the employee of their final rating and performance level |

### Deadline Reminders

A daily automated task checks for upcoming deadlines and sends reminders **3 days before**:

- **Self-Review Deadline:** Reminds employees who haven't submitted their self-review
- **Manager Review Deadline:** Reminds managers who haven't submitted their evaluation

---

## 16. Frequently Asked Questions (FAQ)

### General

**Q: Can I create a review for an employee without a review cycle?**
> Yes. You can create individual reviews from **Performance** → **Reviews** → **All Reviews** → **New**. However, you will need to assign a cycle that has a template for the criteria to be generated.

**Q: What happens if an employee has no manager assigned?**
> The review will be created with an empty Manager field. HR should manually assign a reviewer before the cycle starts. The Manager can be edited while the review is in Draft status.

**Q: Can I change the evaluation criteria after reviews are generated?**
> No. The evaluation criteria are copied from the template at the time of review creation. Changing the template afterward will not affect existing reviews. This ensures consistency within a cycle.

### Scoring

**Q: What if a manager doesn't score all criteria?**
> Criteria with a score of 0 will still be included in the weighted average, which will lower the overall rating. Managers should score all criteria for an accurate assessment.

**Q: Why is the final rating showing 0 even after I entered scores?**
> The final rating requires the **manager rating** to be greater than 0. If only self-scores are entered, the final rating will equal the self-rating. The full formula applies only when manager scores are present.

**Q: Can we change the rating formula (70/20/10 split)?**
> The current formula is fixed at 70% Manager, 20% Self, 10% Goals. If you need a different split, please contact your system administrator.

### Goals

**Q: Do goals have to be linked to a review?**
> No. Goals can exist independently and be tracked on their own. However, only goals linked to a specific review will contribute to that review's goal achievement percentage and final rating.

**Q: Can an employee create their own goals?**
> Employees with the Employee role can view and manage their own goals. The ability to create new goals depends on the security configuration. By default, Managers and HR Officers can create goals.

### Workflow

**Q: Can a review be sent back to a previous stage?**
> Reviews cannot be sent backward through the workflow. However, they can be cancelled and then reset to Draft to start over.

**Q: What if the cycle deadline passes but reviews are incomplete?**
> The system will continue to send deadline reminders. Reviews can still be completed after the deadline — the deadlines are informational and do not block the workflow.

**Q: Can I delete a review?**
> Only HR Officers can delete reviews, and only if the review is in Draft or Cancelled status.

---

## Quick Reference — Complete Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    HR OFFICER SETUP                          │
│                                                             │
│  1. Create Review Template (criteria + weights = 100%)      │
│  2. Create Review Cycle (dates, deadlines, template)        │
│  3. Generate Reviews (wizard → select departments/people)   │
│  4. Start Cycle (notifies all employees)                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    EMPLOYEE                                  │
│                                                             │
│  5. Opens My Reviews → fills Self Scores + Self-Assessment  │
│  6. Clicks "Submit Self-Review"                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    MANAGER                                   │
│                                                             │
│  7. Opens Team Reviews → reviews self-scores                │
│  8. Fills Manager Scores + Manager Assessment               │
│  9. Clicks "Submit Manager Review"                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    HR OFFICER                                │
│                                                             │
│  10. Reviews Rating Summary (auto-calculated)               │
│  11. Adds HR Comments (optional)                            │
│  12. Clicks "Approve & Complete"                            │
│  13. Employee's rating is updated + completion email sent   │
│  14. Complete the Review Cycle when all reviews are done    │
└─────────────────────────────────────────────────────────────┘
```

---

*This document was prepared for user training purposes.*
*Module Version: 17.0.1.0.0 | Macrofix*
