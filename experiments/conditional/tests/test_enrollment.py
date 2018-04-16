# coding=utf-8
from __future__ import absolute_import

from model_mommy import mommy
from django.test import TestCase

from experiments.conditional.enrollment import Experiments
from experiments.tests.testing_2_3 import mock


class ConditionalEnrollmentTestCase(TestCase):
    maxDiff = None

    def setUp(self):
        self.request = mock.MagicMock()
        self.context = {'request': self.request}

    def test_report(self):
        experiments = Experiments(self.context)
        instance = mock.MagicMock()
        instance.name = "mock_experiment"
        active = True
        variate = 'mock_variate'
        experiments._report(instance, active, variate)
        self.assertIn(
            'mock_experiment', experiments.report['conditional'])
        expected_report = {
            'disabled': False,
            'enrolled_alternative': 'mock_variate',
        }
        self.assertEqual(
            expected_report,
            experiments.report['conditional']['mock_experiment']
        )

    def test_evaluate_conditionals_wo_instances(self):
        experiments = Experiments(self.context)
        experiments.experiment_names = []
        experiments.report = {'conditional': {}}
        with mock.patch.object(experiments, 'get_participant'):
            experiments._evaluate_conditionals()
            experiments.get_participant.assert_not_called()
        expected_report = {'conditional': {}}
        self.assertEqual(expected_report, experiments.report)

    def test_evaluate_conditionals_wo_experiments(self):
        experiments = Experiments(self.context)
        self.assertEqual({'conditional': {}}, experiments.report)

    def test_evaluate_conditionals_w_instances(self):
        exp1_alternatives = {
            'variate_for_exp_1': {
                'default': True, 'enabled': True, 'weight': 50
            },
            'control': {'enabled': True, 'weight': 50},
        }
        exp1 = mommy.make(
            'experiments.Experiment',
            name='exp_1',
            alternatives=exp1_alternatives)
        mommy.make('experiments.AdminConditional', experiment=exp1)
        exp2 = mommy.make('experiments.Experiment', name='exp_2')  # noqa
        experiments = Experiments(self.context)
        expected_report = {
            'conditional': {
                'exp_1': {
                    'disabled': True,
                    'enrolled_alternative': 'variate_for_exp_1',
                },
                'exp_2': {
                    'disabled': False,
                    'enrolled_alternative': None,
                },
            },
        }
        self.assertEqual(experiments.report, expected_report)
        disabled_list = ['exp_1', ]
        self.assertEqual(experiments.disabled_experiments, disabled_list)
