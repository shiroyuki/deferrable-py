from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial
from unittest import IsolatedAsyncioTestCase

from deferrable import deferrable, defer
from deferrable.tools import NotDeferredError


class TestUnit(IsolatedAsyncioTestCase):
    async def test_defer_on_function__ok(self):
        @deferrable
        async def ex_compute_summation(numbers: list[int], result_collection: list[int]):
            """Example Function"""
            total = 0

            for i in numbers:
                total += i
                result_collection.append(i)
                defer(partial(lambda i: result_collection.append(i), i))
                defer(self._fake_cleanup)  # try adding a async callback.

            return total

        self.assertEqual(self.__module__, ex_compute_summation.__module__)
        self.assertEqual(ex_compute_summation.__name__, 'ex_compute_summation')
        self.assertEqual(ex_compute_summation.__doc__, 'Example Function')

        async def run_test_worker(samples: list[int], expected_result: int):
            exec_sequence = []
            result = await ex_compute_summation(samples, exec_sequence)

            # Ensure that the deferred ops are executed in the reversed order.
            self.assertEqual(exec_sequence, samples + [i for i in reversed(samples)])

            # Ensure that the result are not manipulated by the deferred operations.
            self.assertEqual(result, expected_result)

            return exec_sequence, result

        seq_1, result_1 = await run_test_worker([1, 3, 5, 7, 11], 27)
        seq_2, result_2 = await run_test_worker([2, 4, 6, 8], 20)

        self.assertNotEqual(seq_1, seq_2)
        self.assertNotEqual(result_1, result_2)

    async def test_defer_on_function_concurrent__ok(self):
        self.skipTest('Not ready')

        @deferrable
        def ex_compute_summation(numbers: list[int], result_collection: list[int]):
            """Example Function"""
            total = 0

            for i in numbers:
                total += i
                result_collection.append(i)
                defer(partial(lambda i: result_collection.append(i), i))

            return total

        async def run_test_worker(idx: int, samples: list[int], expected_result: int):
            exec_sequence = []
            result = await ex_compute_summation(samples, exec_sequence)

            # Ensure that the deferred ops are executed in the reversed order.
            self.assertEqual(exec_sequence, samples + [i for i in reversed(samples)])

            # Ensure that the result are not manipulated by the deferred operations.
            self.assertEqual(result, expected_result)

            return idx, exec_sequence, result

        sample_pairs = [
            (i, samples, sum(samples))
            for i, samples in enumerate([
                [1, 3, 5, 7, 11],
                [2, 4, 6, 8],
                [5, 10, 15, 20, 25, 30],
                [-2, -8, 15, 23, -7],
            ])
        ]

        expected_results = {
            i: expected
            for i, _, expected in sample_pairs
        }

        with ThreadPoolExecutor(max_workers=len(sample_pairs)) as executor:
            futures = []

            for i, samples, expected_result in sample_pairs:
                futures.append(executor.submit(run_test_worker, i, samples, expected_result))

            for f in as_completed(futures):
                i, _, expected = f.result()
                self.assertEqual(expected_results[i], expected)
        # end with
    # end def

    async def test_defer_on_instance_method__ok(self):
        class Obj:
            def __init__(self, x):
                self.x = x

            @deferrable
            async def temporarily_update(self, new_x: int):
                old_x = self.x
                self.x = new_x
                defer(lambda: setattr(self, 'x', old_x))
                return self.x

        original_value = 123
        temporary_value = original_value * 2

        obj = Obj(original_value)
        self.assertEqual(obj.x, original_value,
                         'Ensure that the original value is not changed BEFORE the deferrable invocation.')
        self.assertEqual(await obj.temporarily_update(temporary_value), temporary_value,
                         'The result should be returned as normal.')
        self.assertEqual(obj.x, original_value,
                         'Ensure that the original value is not changed AFTER the deferrable invocation.')

    async def _fake_cleanup(self):
        pass

    async def test_defer_handle_exception__rethrow_error_with_some_deferred_op_used(self):
        deferred_values = []

        @deferrable
        async def ex_power_odd_by_2(seed):
            if seed % 2 == 0:
                defer(lambda: deferred_values.append(seed))
                raise ValueError(seed)
            defer(lambda: deferred_values.append(seed * 2))
            return seed ** 2

        # Ensure that the seed is not in the list.
        self.assertEqual(await ex_power_odd_by_2(3), 9)
        self.assertNotIn(3, deferred_values)

        with self.assertRaises(ValueError):
            await ex_power_odd_by_2(2)

        self.assertIn(2, deferred_values)
        self.assertNotIn(4, deferred_values)

    async def test_defer_on_non_deferrable_callable__raise_error(self):
        async def target():
            defer(lambda: None)

        with self.assertRaises(NotDeferredError):
            await target()
