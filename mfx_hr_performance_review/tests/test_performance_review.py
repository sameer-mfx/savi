from datetime import date, timedelta

from odoo.exceptions import ValidationError, UserError
from odoo.tests.common import TransactionCase


class TestPerformanceReview(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.department = cls.env['hr.department'].create({
            'name': 'Test Department',
        })

        cls.manager_user = cls.env['res.users'].create({
            'name': 'Test Manager',
            'login': 'test_manager_perf',
            'email': 'manager@test.com',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('mfx_hr_performance_review.group_performance_hr').id,
            ])],
        })

        cls.employee_user = cls.env['res.users'].create({
            'name': 'Test Employee',
            'login': 'test_employee_perf',
            'email': 'employee@test.com',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('mfx_hr_performance_review.group_performance_user').id,
            ])],
        })

        cls.manager = cls.env['hr.employee'].create({
            'name': 'Test Manager',
            'user_id': cls.manager_user.id,
            'department_id': cls.department.id,
            'work_email': 'manager@test.com',
        })

        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Employee',
            'user_id': cls.employee_user.id,
            'department_id': cls.department.id,
            'parent_id': cls.manager.id,
            'work_email': 'employee@test.com',
        })

        cls.template = cls.env['hr.review.template'].create({
            'name': 'Test Template',
            'criteria_ids': [
                (0, 0, {
                    'name': 'Job Knowledge',
                    'category': 'performance',
                    'weight': 40.0,
                }),
                (0, 0, {
                    'name': 'Communication',
                    'category': 'communication',
                    'weight': 30.0,
                }),
                (0, 0, {
                    'name': 'Teamwork',
                    'category': 'teamwork',
                    'weight': 30.0,
                }),
            ],
        })

        cls.cycle = cls.env['hr.review.cycle'].create({
            'name': 'Annual Review 2026',
            'cycle_type': 'annual',
            'date_start': date(2026, 1, 1),
            'date_end': date(2026, 12, 31),
            'self_review_deadline': date(2026, 3, 15),
            'manager_review_deadline': date(2026, 3, 31),
            'template_id': cls.template.id,
        })

    def test_01_template_weight_validation(self):
        """Test that template criteria weights must equal 100%."""
        with self.assertRaises(ValidationError):
            self.env['hr.review.template'].create({
                'name': 'Bad Template',
                'criteria_ids': [
                    (0, 0, {
                        'name': 'Criteria 1',
                        'category': 'performance',
                        'weight': 50.0,
                    }),
                ],
            })

    def test_02_cycle_date_validation(self):
        """Test that cycle end date must be after start date."""
        with self.assertRaises(ValidationError):
            self.env['hr.review.cycle'].create({
                'name': 'Bad Cycle',
                'cycle_type': 'annual',
                'date_start': date(2026, 12, 31),
                'date_end': date(2026, 1, 1),
                'template_id': self.template.id,
            })

    def test_03_review_creation_with_sequence(self):
        """Test that reviews get a proper sequence reference."""
        review = self.env['hr.performance.review'].create({
            'employee_id': self.employee.id,
            'manager_id': self.manager.id,
            'cycle_id': self.cycle.id,
        })
        self.assertTrue(review.name.startswith('PR/'))
        self.assertEqual(review.state, 'draft')

    def test_04_review_auto_generate_rating_lines(self):
        """Test that rating lines are auto-generated from template."""
        review = self.env['hr.performance.review'].create({
            'employee_id': self.employee.id,
            'manager_id': self.manager.id,
            'cycle_id': self.cycle.id,
        })
        self.assertEqual(len(review.rating_line_ids), 3)
        criteria_names = review.rating_line_ids.mapped('criteria_id.name')
        self.assertIn('Job Knowledge', criteria_names)
        self.assertIn('Communication', criteria_names)
        self.assertIn('Teamwork', criteria_names)

    def test_05_review_workflow(self):
        """Test the full review workflow: draft -> self_review -> manager_review -> hr_review -> done."""
        review = self.env['hr.performance.review'].create({
            'employee_id': self.employee.id,
            'manager_id': self.manager.id,
            'cycle_id': self.cycle.id,
        })

        # Draft -> Self-Review
        review.action_start_self_review()
        self.assertEqual(review.state, 'self_review')

        # Fill self scores
        for line in review.rating_line_ids:
            line.write({'self_score': 4.0, 'self_comment': 'Good work'})

        review.write({'self_summary': 'I did well this year.'})

        # Self-Review -> Manager Review
        review.action_submit_self_review()
        self.assertEqual(review.state, 'manager_review')

        # Fill manager scores
        for line in review.rating_line_ids:
            line.write({'manager_score': 3.5, 'manager_comment': 'Solid performance'})

        review.write({'manager_summary': 'Good performer'})

        # Manager Review -> HR Review
        review.action_submit_manager_review()
        self.assertEqual(review.state, 'hr_review')

        # HR Review -> Done
        review.action_approve()
        self.assertEqual(review.state, 'done')
        self.assertGreater(review.final_rating, 0)

    def test_06_rating_computation(self):
        """Test that ratings are computed correctly based on weighted scores."""
        review = self.env['hr.performance.review'].create({
            'employee_id': self.employee.id,
            'manager_id': self.manager.id,
            'cycle_id': self.cycle.id,
        })

        # Set scores: Job Knowledge (40%), Communication (30%), Teamwork (30%)
        lines = review.rating_line_ids.sorted('criteria_id')
        for line in lines:
            if line.criteria_id.name == 'Job Knowledge':
                line.write({'self_score': 5.0, 'manager_score': 4.0})
            elif line.criteria_id.name == 'Communication':
                line.write({'self_score': 3.0, 'manager_score': 3.0})
            elif line.criteria_id.name == 'Teamwork':
                line.write({'self_score': 4.0, 'manager_score': 5.0})

        # Self rating = (5*40 + 3*30 + 4*30) / 100 = (200 + 90 + 120) / 100 = 4.10
        self.assertAlmostEqual(review.self_rating, 4.10, places=1)

        # Manager rating = (4*40 + 3*30 + 5*30) / 100 = (160 + 90 + 150) / 100 = 4.00
        self.assertAlmostEqual(review.manager_rating, 4.00, places=1)

    def test_07_final_rating_label(self):
        """Test the final rating label assignment."""
        review = self.env['hr.performance.review'].create({
            'employee_id': self.employee.id,
            'manager_id': self.manager.id,
            'cycle_id': self.cycle.id,
        })

        for line in review.rating_line_ids:
            line.write({'self_score': 5.0, 'manager_score': 5.0})

        self.assertEqual(review.final_rating_label, 'Outstanding')

    def test_08_score_validation(self):
        """Test that scores must be between 0 and 5."""
        review = self.env['hr.performance.review'].create({
            'employee_id': self.employee.id,
            'manager_id': self.manager.id,
            'cycle_id': self.cycle.id,
        })

        with self.assertRaises(ValidationError):
            review.rating_line_ids[0].write({'self_score': 6.0})

        with self.assertRaises(ValidationError):
            review.rating_line_ids[0].write({'manager_score': -1.0})

    def test_09_goal_creation_and_progress(self):
        """Test goal creation, progress tracking, and achievement."""
        review = self.env['hr.performance.review'].create({
            'employee_id': self.employee.id,
            'manager_id': self.manager.id,
            'cycle_id': self.cycle.id,
        })

        goal = self.env['hr.review.goal'].create({
            'name': 'Complete Project X',
            'employee_id': self.employee.id,
            'review_id': review.id,
            'goal_type': 'project',
            'deadline': date(2026, 6, 30),
            'metric': 'Deliver all milestones on time',
        })

        self.assertEqual(goal.state, 'draft')

        goal.action_start()
        self.assertEqual(goal.state, 'in_progress')

        goal.write({'progress': 75.0})
        self.assertEqual(goal.progress, 75.0)

        goal.action_achieve()
        self.assertEqual(goal.state, 'achieved')
        self.assertEqual(goal.progress, 100.0)

    def test_10_goal_progress_validation(self):
        """Test that goal progress must be between 0 and 100."""
        goal = self.env['hr.review.goal'].create({
            'name': 'Test Goal',
            'employee_id': self.employee.id,
            'goal_type': 'performance',
        })

        with self.assertRaises(ValidationError):
            goal.write({'progress': 150.0})

        with self.assertRaises(ValidationError):
            goal.write({'progress': -10.0})

    def test_11_generate_reviews_wizard(self):
        """Test bulk review generation via wizard."""
        wizard = self.env['hr.generate.reviews.wizard'].create({
            'cycle_id': self.cycle.id,
            'department_ids': [(6, 0, [self.department.id])],
        })

        wizard.action_generate()

        reviews = self.env['hr.performance.review'].search([
            ('cycle_id', '=', self.cycle.id),
        ])
        # Should create reviews for both employee and manager
        self.assertGreaterEqual(len(reviews), 1)

    def test_12_employee_review_count(self):
        """Test that employee review and goal counts are computed correctly."""
        self.env['hr.performance.review'].create({
            'employee_id': self.employee.id,
            'manager_id': self.manager.id,
            'cycle_id': self.cycle.id,
        })
        self.assertGreaterEqual(self.employee.review_count, 1)

    def test_13_cancel_and_reset(self):
        """Test cancel and reset-to-draft functionality."""
        review = self.env['hr.performance.review'].create({
            'employee_id': self.employee.id,
            'manager_id': self.manager.id,
            'cycle_id': self.cycle.id,
        })

        review.action_cancel()
        self.assertEqual(review.state, 'cancelled')

        review.action_reset_to_draft()
        self.assertEqual(review.state, 'draft')

    def test_14_workflow_state_guards(self):
        """Test that workflow transitions are properly guarded."""
        review = self.env['hr.performance.review'].create({
            'employee_id': self.employee.id,
            'manager_id': self.manager.id,
            'cycle_id': self.cycle.id,
        })

        # Cannot submit self-review from draft
        with self.assertRaises(UserError):
            review.action_submit_self_review()

        # Cannot submit manager review from draft
        with self.assertRaises(UserError):
            review.action_submit_manager_review()

        # Cannot approve from draft
        with self.assertRaises(UserError):
            review.action_approve()

    def test_15_employee_hr_review_rating_update(self):
        """Test that approving a review updates the employee's hr_review_rating."""
        review = self.env['hr.performance.review'].create({
            'employee_id': self.employee.id,
            'manager_id': self.manager.id,
            'cycle_id': self.cycle.id,
        })

        review.action_start_self_review()
        for line in review.rating_line_ids:
            line.write({'self_score': 4.0})
        review.action_submit_self_review()
        for line in review.rating_line_ids:
            line.write({'manager_score': 4.0})
        review.action_submit_manager_review()
        review.action_approve()

        self.assertGreater(self.employee.hr_review_rating, 0)

    def test_16_cycle_cannot_start_without_reviews(self):
        """Test that a cycle cannot start without generated reviews."""
        empty_cycle = self.env['hr.review.cycle'].create({
            'name': 'Empty Cycle',
            'cycle_type': 'quarterly',
            'date_start': date(2026, 4, 1),
            'date_end': date(2026, 6, 30),
            'template_id': self.template.id,
        })

        with self.assertRaises(ValidationError):
            empty_cycle.action_start()

    def test_17_cycle_cannot_complete_with_pending(self):
        """Test that a cycle cannot complete if reviews are still pending."""
        review = self.env['hr.performance.review'].create({
            'employee_id': self.employee.id,
            'manager_id': self.manager.id,
            'cycle_id': self.cycle.id,
        })

        self.cycle.write({'state': 'in_progress'})

        with self.assertRaises(ValidationError):
            self.cycle.action_complete()
