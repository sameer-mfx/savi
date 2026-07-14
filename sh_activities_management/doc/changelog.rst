Changelog
==================
17.0.1 (Date : 22th Nov 2023)
---------------------------------------
Initial Release


17.0.2(Date 27th Nov 2023)
==================================
[FIX]Added portal view issue.

17.0.3(Date: 30th Nov 2023)
==============================
[ADD]Multi Select Issue solved.

17.0.4[Date: 6th Dec 2023]
======================
[FIX]feedback done activity bootstrap model issue fixed.

17.0.5(Date: 8th Dec 2023)
===================================
[FIX]FIx Mail Mixin Issue .

17.0.6(Date: 22nd December 2023)
=====================================
[FIX]Added rec_name if exist instead of name that bug solved portal side.

17.0.7(Date: 25th December 2023)
=====================================
[FIX]Portal side assingned followers only activity is created.

17.0.8(Date: 14th March 2024)
=====================================
[ADD] Dashboard feature added.

17.0.9 (Date: 13th April 2024)
---------------------------------------
[ADD] add reminder field in the activity view.

17.0.10 (Date: 16th April 2024)
---------------------------------------
[Fix] fix domain filter in activity type in dashboard.
[Fix] Resolve the issue with the Activity Document Model Configuration to accurately showcase activities model by model, ensuring that only selected models are displayed in the dashboard.

17.0.11 (Date: 30th April 2024)
---------------------------------------
[Fix] Add new python file to inherite mail.activity.schedule model and display fields in 'Schedule Activity' wizard and add _action_schedule_activities method to pass data added in schedule activity wizard.

17.0.12 (Date: 9th May 2024)
--------------------------------------
[Add] Add Mark as done Button in Create Multiple activities feature.

17.0.13 (Date: 24th July 2024)
--------------------------------------
[Fix] Add the 'sh_date_deadline' field in mail.activity.schedule and display the sh_date_deadline field in the Schedule Activity Form View and Activities Form View.
Fix the issue to display the "Activity Reminder" Popup notification.

17.0.14 (Date: 1st August 2024)
--------------------------------------
[Fix] Fix the issue of display feedback using standard odoo chatter. ( in mail.activity model action_feedback())

17.0.15 (Date: 14th August 2024)
--------------------------------------
[Fix] Fix the issue of display feedback using standard odoo chatter when Click 'Done & Schedule Next' Button. ( in mail.activity model _action_done())

17.0.16 (Date: 6th November 2024)
---------------------------------------
[FIX] warning of required field

17.0.17 (Date: 18th November 2024)
-------------------------------------
[FIX] error on mass done activities.

17.0.18 (Date: 21st November 2024)
-------------------------------------
[FIX] issue of wrong counts.

17.0.19 (Date: 12th December 2024)
-------------------------------------
[FIX] Access right issue fixed.

17.0.20 (Date: 19th December 2024)
-------------------------------------
[FIX] Updated the code to filter data by due date and completion date when applying filters.

17.0.21 (Date: 27th December 2024)
-------------------------------------
[FIX] warnings.

17.0.22 (Date: 24th January 2025)
-------------------------------------
[FIX] Fixed the warning of use 'name_get' method deprected in mail activity _compute_res_name().

17.0.23 (Date: 28th April 2025)
-------------------------------------
[FIX] activity delete issue fixed while recruitment application moved to the refuse.

17.0.24 (Date: 6th May 2025)
-------------------------------------
[FIX] added fields to optional in tree view

17.0.25 (Date: 4th June 2025)
-------------------------------------
[Update] -When an activity is created, the Supervisor field will be automatically filled with the currently logged-in user.


17.0.26 (Date: 5th June 2025)
-------------------------------------
[Update] -Automatic assign Supervisor in Activity.

17.0.27 (Date: 16th July 2025)
-------------------------------------
[FIX] - error on load dashboard with developer mode.

17.0.28 (Date: 6th August 2025)
-------------------------------------
[FIX] - Fix issue of create multi-activity when ticked 'Individual activities for multi users ?' boolean .

17.0.29 (Date: 19th August 2025)
-------------------------------------
[FIX] - Made multi_users field readonly when activity created.
[FIX] - made 'Individual activity for multi users' filed invisible when 'Display Multi Users' boolean not Ticked.
[FIX] - Removed Related Document Model field and made 'Related Document' field required.

17.0.30 (Date: 29th August 2025)
-------------------------------------
[FIX] - Fixed issue of Activity Reminder with timezone.

17.0.31 (Date: 16th September 2025)
-------------------------------------
[FIX] - Fixed the issue with the “Assigned to” field in the Activities Search Panel — it now respects Odoo’s default limit.

17.0.32 (Date: 17th September 2025)
-------------------------------------
[FIX] - Fixed the default company issue and added a server action to update activities.

17.0.33 (Date: 18th September 2025)
-------------------------------------
[FIX] - Fixed the company issue using the update activities server action.

17.0.34 (Date: 23rd September 2025)
-------------------------------------
[FIX] - Updated the code to fix the company issue by using the 'Update Activities' server action.

17.0.35 (Date: 27th September 2025)
-------------------------------------
[FIX] - Fixed the issue where only allowed activity models are displayed in the 'Mass Activities Dynamic Action' model.

17.0.36 (Date: 1st October 2025)
-------------------------------------
[FIX] - Fixed the issue of 'Done & Schedule Next' Button From 'Mass Activities Dynamic Action' model.
[FIX] - Remove 'Related Document' field required and Add Warning if not Related Document or Model.

17.0.37 (Date: 8th October 2025)
-------------------------------------
[FIX] - Fixed the issue of canceling activities from the chatter.
