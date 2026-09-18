"""Boundary and diagnostic tests for the explicitly specified RQ3 definition."""
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.rq3 import analyze_high_confidence_stable_errors as analysis
from scripts.shared.common import write_csv

UNIT = ('model_a', 'zero_shot', 'project_a', 'story_1', 'Atomic')
REFERENCE = {'project': 'project_a', 'story_id': 'story_1', 'qus_criterion': 'Atomic', 'decision': 'Violation'}


def runs(unit=UNIT):
    return [{**dict(zip(analysis.KEY, unit)), 'run': str(i), 'decision': 'No Violation', 'confidence': 'High'}
            for i in range(1, 6)]


class DefinitionTests(unittest.TestCase):
    def evaluate(self, rows, reference=None, expected=None):
        return analysis.analyze(rows, [REFERENCE] if reference is None else reference,
                                {UNIT} if expected is None else expected, {'Atomic': 'Syntactic'})

    def test_exact_definition_and_prompt_identity(self):
        other = (UNIT[0], 'one_shot', *UNIT[2:])
        result = self.evaluate(runs() + runs(other), expected={UNIT, other})
        self.assertEqual(sum(r['high_confidence_stable_incorrect'] for r in result), 2)
        self.assertEqual({r['prompt_profile'] for r in result}, {'zero_shot', 'one_shot'})

    def test_majority_wrong_is_not_unanimously_wrong(self):
        rows = runs()
        rows[0]['decision'] = 'Violation'
        self.assertEqual(self.evaluate(rows)[0]['high_confidence_stable_incorrect'], 0)

    def test_unanimous_correct_is_not_included(self):
        rows = runs()
        for row in rows:
            row['decision'] = 'Violation'
        result = self.evaluate(rows)[0]
        self.assertEqual((result['stable'], result['incorrect']), (1, 0))
        self.assertEqual(result['high_confidence_stable_incorrect'], 0)

    def test_confidence_is_literal_and_required_on_every_run(self):
        for confidence in ['Moderate', 'Low', '', 'high', ' High', 'High ']:
            with self.subTest(confidence=confidence):
                rows = runs()
                rows[0]['confidence'] = confidence
                result = self.evaluate(rows)[0]
                self.assertEqual(result['high_confidence_stable_incorrect'], 0)
                self.assertEqual(result['high_confidence_runs'], 4)
                self.assertEqual(bool(result['exclusion_reasons']), confidence not in {'Moderate', 'Low'})

    def test_missing_extra_duplicate_and_invalid_runs(self):
        duplicate = runs()
        duplicate[-1]['run'] = '4'
        invalid = runs()
        invalid[-1]['run'] = '6'
        for rows in [[], runs()[:4], runs() + [runs()[0]], duplicate, invalid]:
            with self.subTest(rows=rows):
                result = self.evaluate(rows)[0]
                self.assertEqual(result['complete_run_structure'], 0)
                self.assertEqual(result['high_confidence_stable_incorrect'], 0)
                self.assertTrue(result['exclusion_reasons'])
                self.assertEqual(result['number_of_runs'], len(rows))

    def test_ground_truth_missing_duplicate_conflicting_nonbinary(self):
        for refs in [[], [REFERENCE, REFERENCE], [REFERENCE, {**REFERENCE, 'decision': 'No Violation'}],
                     [{**REFERENCE, 'decision': 'Uncertain'}]]:
            with self.subTest(refs=refs):
                result = self.evaluate(runs(), reference=refs)[0]
                self.assertEqual(result['high_confidence_stable_incorrect'], 0)
                self.assertTrue(result['exclusion_reasons'])

    def test_invalid_predictions_and_unexpected_unit_are_diagnosed(self):
        rows = runs()
        rows[0]['decision'] = ''
        self.assertIn('invalid_prediction_label', self.evaluate(rows)[0]['exclusion_reasons'])
        result = self.evaluate(runs(), expected=set())[0]
        self.assertIn('unexpected_unit', result['exclusion_reasons'])
        self.assertEqual(result['high_confidence_stable_incorrect'], 0)

    def test_sorted_rows_and_zero_denominators(self):
        second = (*UNIT[:3], 'story_2', UNIT[4])
        a = self.evaluate(runs(second) + runs(), expected={UNIT, second})
        b = self.evaluate(list(reversed(runs() + runs(second))), expected={UNIT, second})
        self.assertEqual(a, b)
        self.assertEqual(analysis.percentage(0, 0), '')
        self.assertEqual(analysis.aggregate([], ['model'], [['model_a']])[0]['count'], 0)

    def test_aggregated_input_rejected_and_mismatch_outputs_written(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            predictions, reference = root / 'predictions.csv', root / 'reference.csv'
            write_csv(predictions, [{'model': 'model_a', 'prediction': 'No Violation'}], ['model', 'prediction'])
            with self.assertRaisesRegex(ValueError, 'individual runs'):
                analysis.load_table(predictions, analysis.KEY + ['run', 'decision', 'confidence'])
            write_csv(predictions, runs(), analysis.KEY + ['run', 'decision', 'confidence'])
            write_csv(reference, [REFERENCE], list(REFERENCE))
            with patch.dict(os.environ, {'TOSEM_OUTPUT_ROOT': str(root / 'generated')}), \
                 patch.object(analysis, 'expected_design', return_value={UNIT}), \
                 contextlib.redirect_stdout(io.StringIO()) as console:
                summary = analysis.run_analysis(predictions, reference)
                self.assertEqual(summary['status'], 'MISMATCH')
                self.assertEqual(summary['high_confidence_stable_incorrect_units'], 1)
                self.assertIn('WARNING: manuscript count not reproduced', console.getvalue())
                saved = root / 'generated/results/rq3/metrics' / (analysis.PREFIX + '_audit_summary.json')
                self.assertEqual(json.loads(saved.read_text())['difference'], 1 - 1910)
                self.assertTrue(saved.with_name(analysis.PREFIX + '_all_units_audit.csv').exists())
                self.assertTrue(saved.with_name(analysis.PREFIX + '_excluded_units.csv').exists())


if __name__ == '__main__':
    unittest.main()
