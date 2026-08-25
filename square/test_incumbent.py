"""Regression tests for the exact and independent incumbent reconstructions."""

from fractions import Fraction
from itertools import combinations, product
import unittest
from unittest.mock import patch

import numpy as np

from calibration import CASES, minimum_area, n8_template, n9_template, n10_template, triples
import c2_boundary_search
import c4_interval_certificate
import c4_symmetry_search
import decimal_verifier
import d4_interval_certificate
import frozen_boundary_search
import global_interval_branch
import global_mccormick_relaxation
import global_normal_form_search
import highs_milp
import tangent_certificate
import transversal_free_search
import transversal_search
import transversal_interval
from incumbent import (
    Qx,
    active_hitting_sets,
    active_structure,
    algebraic_bounds,
    cubic,
    decimal_string,
    incumbent_points,
    incumbent_analysis,
    incumbent_value,
    record_cubic,
    root_bounds,
    sign,
    verify_rational_candidate,
)
from n11_insertion import solve_insertion


class IncumbentTests(unittest.TestCase):
    def test_calibration_templates_reproduce_known_values(self) -> None:
        known_parameters = {
            "n8": np.array((0.7675918792439982, 0.18858048469644506, 0.2324081207560018, 0.3771609693928901)),
            "n9": np.array((0.1937742251701451, 0.17344355629253624, 0.2601653344388044, 0.17344355629253624, 0.6531128874149275)),
            "n10": np.array((0.15780556880430557, 0.74761263246063, 0.15780556880430557, 0.2523873675393699, 0.6843888623913889, 0.31561113760861115)),
        }
        for name, parameters in known_parameters.items():
            case = CASES[name]
            self.assertAlmostEqual(
                minimum_area(parameters, case.template, triples(case.n)),
                case.target,
                delta=case.tolerance,
            )

    def test_calibration_templates_stay_in_the_unit_square(self) -> None:
        for template, dimensions in ((n8_template, 4), (n9_template, 5), (n10_template, 6)):
            points = template(np.full(dimensions, 0.37))
            self.assertTrue(np.all(points >= 0.0))
            self.assertTrue(np.all(points <= 1.0))

    def test_frozen_boundary_incumbent_round_trip(self) -> None:
        self.assertAlmostEqual(
            frozen_boundary_search.minimum_area(frozen_boundary_search.incumbent_interior()),
            0.032598858691819698,
            delta=1e-15,
        )

    def test_frozen_boundary_coordinates_match_selected_score(self) -> None:
        raw = np.arange(8, dtype=float)
        polished = raw + 10.0
        stage, selected = frozen_boundary_search.select_candidate(0.2, raw, 0.1, polished)
        self.assertEqual(stage, "de")
        np.testing.assert_array_equal(selected, raw)
        stage, selected = frozen_boundary_search.select_candidate(0.1, raw, 0.2, polished)
        self.assertEqual(stage, "epigraph")
        np.testing.assert_array_equal(selected, polished)

    def test_size5_strata_have_expected_dimensions_and_incumbent_embedding(self) -> None:
        transversals = set(active_hitting_sets(5))
        expected_dimensions = {
            "four-interiors-plus-boundary": 9,
            "two-boundary-three-interior-a": 8,
            "two-boundary-three-interior-b": 8,
        }
        for name, stratum in transversal_search.STRATA.items():
            self.assertIn(stratum.moved_labels, transversals)
            self.assertEqual(stratum.dimensions, expected_dimensions[name])
            points = transversal_search.configuration(stratum, transversal_search.incumbent_parameters(stratum))
            np.testing.assert_allclose(points, transversal_search._INCUMBENT_POINTS, atol=0.0, rtol=0.0)
            self.assertAlmostEqual(transversal_search.minimum_area(points), 0.032598858691819698, delta=1e-15)

    def test_size5_orbit_distance_identifies_the_incumbent(self) -> None:
        self.assertEqual(transversal_search.incumbent_orbit_distance(transversal_search._INCUMBENT_POINTS), 0.0)
        changed = transversal_search._INCUMBENT_POINTS.copy()
        changed[0, 0] += 1e-4
        self.assertGreater(transversal_search.incumbent_orbit_distance(changed), 0.0)

    def test_size5_interval_exploration_reports_incomplete_work_honestly(self) -> None:
        result = transversal_interval.explore(
            transversal_search.STRATA["four-interiors-plus-boundary"],
            slack_bits=20,
            root_bisections=64,
            max_boxes=1,
        )
        self.assertEqual(result.visited_boxes, 1)
        self.assertGreater(result.target_upper, result.record_lower)
        self.assertFalse(result.complete)
        self.assertGreater(result.pending_boxes, 0)

    def test_size5_vertex_hull_bounds_every_coordinate_box_determinant(self) -> None:
        root_bisections = 96
        enclosed = transversal_interval.incumbent_interval_points(root_bisections)
        for exact_point, interval_point in zip(incumbent_points(), enclosed):
            for exact_coordinate, (lower, upper) in zip(exact_point, interval_point):
                self.assertGreaterEqual(sign(exact_coordinate - Qx.rational(lower)), 0)
                self.assertLessEqual(sign(exact_coordinate - Qx.rational(upper)), 0)

        for stratum in transversal_search.STRATA.values():
            root = transversal_interval.root_box(stratum)
            left, right = transversal_interval.split(root)
            split_left, _ = transversal_interval.split(left)
            for box in (root, left, right, split_left):
                points = transversal_interval.points_for_box(stratum, box, root_bisections)
                for triangle in transversal_interval.TRIANGLES:
                    i, j, k = triangle
                    coordinates = points[i] + points[j] + points[k]
                    midpoint = tuple((lower + upper) / 2 for lower, upper in coordinates)
                    xi, yi, xj, yj, xk, yk = midpoint
                    midpoint_determinant = xj * yk - xj * yi - xi * yk - yj * xk + yj * xi + yi * xk
                    vertex_upper = transversal_interval.double_area_vertex_upper(points, triangle)
                    direct_vertex_upper = Fraction(0)
                    for endpoints in product((0, 1), repeat=6):
                        endpoint_values = tuple(interval[endpoint] for interval, endpoint in zip(coordinates, endpoints))
                        xi, yi, xj, yj, xk, yk = endpoint_values
                        determinant = xj * yk - xj * yi - xi * yk - yj * xk + yj * xi + yi * xk
                        direct_vertex_upper = max(direct_vertex_upper, abs(determinant))
                    natural_upper = transversal_interval.absolute_upper(
                        transversal_interval.double_area_interval(points, triangle)
                    )
                    self.assertLessEqual(abs(midpoint_determinant), vertex_upper)
                    self.assertEqual(vertex_upper, direct_vertex_upper)
                    self.assertLessEqual(vertex_upper, natural_upper)

    def test_global_mccormick_n6_witness_lift_and_spatial_boxes(self) -> None:
        witness = global_mccormick_relaxation.verify_witness(
            global_mccormick_relaxation.n6_calibration_witness()
        )
        self.assertEqual(witness.minimum_area, Fraction(1, 8))
        self.assertEqual(witness.checked_products, 30)
        self.assertEqual(witness.checked_triangles, 20)

        root = global_mccormick_relaxation.root_spatial_box(6)
        left, right = global_mccormick_relaxation.split_spatial_box(root, "x_5")
        self.assertEqual(left.coordinate_bounds["x_5"], (Fraction(0), Fraction(1, 2)))
        self.assertEqual(right.coordinate_bounds["x_5"], (Fraction(1, 2), Fraction(1)))
        self.assertEqual(left.depth, 1)
        self.assertEqual(right.depth, 1)

        model = global_mccormick_relaxation.build_model(6, spatial_box=left)
        self.assertEqual(len(model.triangles), 20)
        self.assertEqual(model.product_count, 30)
        self.assertEqual(model.binary_count, 9)
        self.assertEqual(model.coordinate_bounds["x_5"], (Fraction(0), Fraction(1, 2)))
        self.assertIn("fixed_positive_0_1_2", model.text)
        self.assertIn("fixed_negative_0_4_5", model.text)
        self.assertIn("area_upper_0_1_2", model.text)
        self.assertNotIn(" b_0_1_2\n", model.text)

        x_bounds = (Fraction(1, 4), Fraction(3, 4))
        y_bounds = (Fraction(1, 3), Fraction(2, 3))
        for x in (x_bounds[0], sum(x_bounds) / 2, x_bounds[1]):
            for y in (y_bounds[0], sum(y_bounds) / 2, y_bounds[1]):
                self.assertTrue(global_mccormick_relaxation.mccormick_contains(x, y, x * y, x_bounds, y_bounds))

        lower_target = Fraction(1, 31)
        self.assertEqual(global_mccormick_relaxation.strip_count_for_target(lower_target), 16)
        self.assertEqual(global_mccormick_relaxation.published_nine_point_upper_bound(), Fraction(549, 10_000))
        self.assertEqual(global_mccormick_relaxation.area_upper_bound(9), Fraction(1, 7))
        self.assertEqual(global_mccormick_relaxation.area_upper_bound(10), Fraction(549, 10_000))
        self.assertEqual(global_mccormick_relaxation.area_upper_bound(12), Fraction(549, 10_000))
        self.assertEqual(len(global_mccormick_relaxation.ordered_product_links(12)), 90)
        self.assertEqual(
            len(
                global_mccormick_relaxation.rectangle_rlt_links(
                    12, global_mccormick_relaxation.canonical_coordinate_bounds(12)
                )
            ),
            8,
        )
        self.assertEqual(
            global_mccormick_relaxation.target_x_spacing_pairs(12),
            ((4, 5), (5, 7), (6, 8), (7, 9), (8, 10), (9, 11)),
        )
        self.assertEqual(
            global_mccormick_relaxation.target_left_strip_exclusion_indices(12),
            (1, 2, 3, 5, 6, 7, 8, 9, 10, 11),
        )
        tightened_bounds = global_mccormick_relaxation.target_tightened_coordinate_bounds(
            12,
            global_mccormick_relaxation.canonical_coordinate_bounds(12),
            lower_target,
        )
        self.assertEqual(tightened_bounds["x_1"][0], Fraction(2, 31))
        self.assertEqual(tightened_bounds["y_0"][1], Fraction(23, 25))
        self.assertEqual(tightened_bounds["y_4"][0], Fraction(2, 25))
        self.assertEqual(tightened_bounds["x_5"], (Fraction(2, 31), Fraction(25, 31)))
        self.assertEqual(tightened_bounds["x_11"], (Fraction(8, 31), Fraction(1)))
        self.assertEqual(
            global_mccormick_relaxation.left_chord_span_bounds(tightened_bounds, lower_target),
            (Fraction(2, 31), Fraction(1)),
        )
        self.assertEqual(
            global_mccormick_relaxation.ordered_difference_span_bounds(
                12, "x", 4, 5, tightened_bounds, lower_target
            ),
            (Fraction(2, 31), Fraction(25, 31)),
        )
        self.assertEqual(
            global_mccormick_relaxation.target_ordered_span_lower_bound(12, "x", 4, 11, lower_target),
            Fraction(8, 31),
        )
        self.assertEqual(len(global_mccormick_relaxation.transitive_x_ordered_pairs(12)), 21)
        self.assertEqual(len(global_mccormick_relaxation.transitive_x_ordered_product_links(12)), 210)
        impossible_bounds = global_mccormick_relaxation.canonical_coordinate_bounds(12)
        impossible_bounds["x_5"] = (Fraction(0), Fraction(1, 20))
        with self.assertRaises(ValueError):
            global_mccormick_relaxation.target_tightened_coordinate_bounds(12, impossible_bounds, lower_target)
        chord_tightening_bounds = global_mccormick_relaxation.canonical_coordinate_bounds(12)
        chord_tightening_bounds["y_0"] = (Fraction(0), Fraction(0))
        chord_tightening_bounds["y_4"] = (Fraction(2, 31), Fraction(1, 2))
        chord_tightening_bounds["x_1"] = (Fraction(2, 31), Fraction(1, 5))
        chord_tightened = global_mccormick_relaxation.target_tightened_coordinate_bounds(
            12, chord_tightening_bounds, lower_target
        )
        self.assertEqual(chord_tightened["x_1"][0], Fraction(4, 31))
        self.assertEqual(chord_tightened["y_4"][0], Fraction(10, 31))
        impossible_chord_bounds = global_mccormick_relaxation.canonical_coordinate_bounds(12)
        impossible_chord_bounds["y_0"] = (Fraction(0), Fraction(0))
        impossible_chord_bounds["y_4"] = (Fraction(1, 10), Fraction(1, 10))
        impossible_chord_bounds["x_1"] = (Fraction(1, 10), Fraction(1, 10))
        with self.assertRaises(ValueError):
            global_mccormick_relaxation.target_tightened_coordinate_bounds(
                12, impossible_chord_bounds, lower_target
            )
        equality_chord_bounds = global_mccormick_relaxation.canonical_coordinate_bounds(12)
        equality_chord_bounds["y_0"] = (Fraction(0), Fraction(0))
        equality_chord_bounds["y_4"] = (Fraction(1), Fraction(1))
        equality_chord_bounds["x_1"] = (Fraction(2, 31), Fraction(2, 31))
        with self.assertRaises(ValueError):
            global_mccormick_relaxation.target_tightened_coordinate_bounds(
                12, equality_chord_bounds, lower_target
            )
        snapped_incumbent = global_normal_form_search.dyadic_snap(
            global_normal_form_search.canonical_incumbent_points(), 20
        )
        snapped_minimum, _ = verify_rational_candidate(snapped_incumbent)
        self.assertGreater(snapped_minimum, lower_target)
        pinned_incumbent_bounds = {
            f"{axis}_{index}": (coordinate, coordinate)
            for index, point in enumerate(snapped_incumbent)
            for axis, coordinate in zip(("x", "y"), point)
        }
        self.assertEqual(
            global_mccormick_relaxation.target_tightened_coordinate_bounds(
                12, pinned_incumbent_bounds, lower_target
            ),
            pinned_incumbent_bounds,
        )
        constrained = global_mccormick_relaxation.build_model(12, lower_target=lower_target)
        self.assertEqual(constrained.binary_count, 203 + 2 * 12 * 16)
        self.assertIn("target_floor", constrained.text)
        self.assertIn("strip_capacity_x_0", constrained.text)
        self.assertIn("strip_capacity_y_15", constrained.text)
        self.assertIn("rlt_x_1_3_0_lower", constrained.text)
        self.assertIn("rlt_y_0_4_1_upper", constrained.text)
        self.assertIn("rlt_bound_y_0_4_1_lower", constrained.text)
        self.assertIn("rectangle_rlt_x_1_3_y_0_4_lower", constrained.text)
        self.assertIn("rectangle_rlt_x_4_5_y_0_4_y_span", constrained.text)
        self.assertIn("packing_x_left_strip_1", constrained.text)
        self.assertIn("packing_x_span_4_5", constrained.text)
        self.assertIn("left_chord_mccormick_1_0", constrained.text)
        self.assertIn("rlt_mccormick_x_1_3_0_1", constrained.text)
        self.assertIn("rlt_mccormick_transitive_x_4_11_0_1", constrained.text)
        self.assertIn("rectangle_mccormick_transitive_x_4_11_1", constrained.text)
        combined = global_mccormick_relaxation.build_model(
            12,
            lower_target=lower_target,
            additional_strip_counts=(20,),
        )
        self.assertEqual(combined.additional_strip_counts, (20,))
        self.assertEqual(combined.binary_count, 203 + 2 * 12 * (16 + 20))
        self.assertIn("strip_capacity_x_20_0", combined.text)

        def subject_rows(model):
            lines = model.text.splitlines()
            return tuple(lines[lines.index("Subject To") + 1 : lines.index("Bounds")])

        base_rows = subject_rows(constrained)
        combined_rows = subject_rows(combined)
        self.assertTrue(set(base_rows).issubset(set(combined_rows)))
        row_names = tuple(row.split(":", 1)[0].strip() for row in combined_rows)
        self.assertEqual(len(row_names), len(set(row_names)))

        combined_lift = global_mccormick_relaxation.verify_canonical_incumbent_lift(
            lower_target,
            additional_strip_counts=(20,),
        )
        self.assertEqual(combined_lift.additional_strip_counts, (20,))
        self.assertEqual(len(combined_lift.additional_x_strips), 1)
        self.assertEqual(len(combined_lift.additional_y_strips), 1)

        lift = global_mccormick_relaxation.verify_canonical_incumbent_lift(lower_target)
        self.assertEqual(lift.strip_count, 16)
        self.assertTrue(all(lift.x_strips.count(strip) <= 2 for strip in range(lift.strip_count)))
        self.assertTrue(all(lift.y_strips.count(strip) <= 2 for strip in range(lift.strip_count)))
        lift20 = global_mccormick_relaxation.verify_canonical_incumbent_lift(lower_target, strip_count=20)
        self.assertEqual(lift20.strip_count, 20)
        self.assertTrue(all(lift20.x_strips.count(strip) <= 2 for strip in range(lift20.strip_count)))
        self.assertTrue(all(lift20.y_strips.count(strip) <= 2 for strip in range(lift20.strip_count)))

        piecewise = global_mccormick_relaxation.build_model(
            12,
            lower_target=lower_target,
            piecewise_strip_products=True,
        )
        self.assertTrue(piecewise.piecewise_strip_products)
        self.assertEqual(piecewise.piecewise_cell_count, 16)
        self.assertIsNone(piecewise.piecewise_product_pairs)
        self.assertEqual(piecewise.binary_count, constrained.binary_count)
        self.assertIn("piecewise_x_1_2_8_0", piecewise.text)
        self.assertGreater(
            sum(line.strip().startswith("piecewise_") for line in piecewise.text.splitlines()),
            10_000,
        )
        self.assertEqual(
            global_mccormick_relaxation.verify_canonical_incumbent_piecewise_lift(lower_target),
            lift,
        )
        coarse_piecewise = global_mccormick_relaxation.build_model(
            12,
            lower_target=lower_target,
            piecewise_strip_products=True,
            piecewise_cell_count=4,
        )
        self.assertEqual(coarse_piecewise.piecewise_cell_count, 4)
        self.assertIn("piecewise_x_1_2_2_0", coarse_piecewise.text)
        self.assertEqual(
            global_mccormick_relaxation.verify_canonical_incumbent_piecewise_lift(
                lower_target, piecewise_cell_count=4
            ),
            lift,
        )
        targeted_pairs = ((10, 9), (1, 9), (7, 6), (8, 6))
        targeted_piecewise = global_mccormick_relaxation.build_model(
            12,
            lower_target=lower_target,
            piecewise_strip_products=True,
            piecewise_cell_count=4,
            piecewise_product_pairs=targeted_pairs,
        )
        self.assertEqual(targeted_piecewise.piecewise_product_pairs, tuple(sorted(targeted_pairs)))
        self.assertEqual(
            sum(line.strip().startswith("piecewise_") for line in targeted_piecewise.text.splitlines()),
            128,
        )
        self.assertIn("piecewise_x_1_9_2_0", targeted_piecewise.text)
        self.assertNotIn("piecewise_x_2_1_2_0", targeted_piecewise.text)
        self.assertEqual(
            global_mccormick_relaxation.verify_canonical_incumbent_piecewise_lift(
                lower_target,
                piecewise_cell_count=4,
                piecewise_product_pairs=targeted_pairs,
            ),
            lift,
        )
        audited = global_mccormick_relaxation.verify_canonical_incumbent_model_lift(
            lower_target,
            additional_strip_counts=(20,),
            piecewise_strip_products=True,
            piecewise_cell_count=4,
        )
        self.assertEqual(audited.additional_strip_counts, (20,))
        targeted_audit = global_mccormick_relaxation.verify_canonical_incumbent_model_lift(
            lower_target,
            piecewise_strip_products=True,
            piecewise_cell_count=4,
            piecewise_product_pairs=targeted_pairs,
        )
        self.assertEqual(targeted_audit.strip_count, 16)

        joint_piecewise = global_mccormick_relaxation.build_model(
            12,
            lower_target=lower_target,
            additional_strip_counts=(20,),
            joint_piecewise_strip_products=True,
            piecewise_cell_count=4,
            piecewise_product_pairs=targeted_pairs,
        )
        self.assertFalse(joint_piecewise.piecewise_strip_products)
        self.assertTrue(joint_piecewise.joint_piecewise_strip_products)
        self.assertIn("joint_cell_assignment_1_9", joint_piecewise.text)
        self.assertIn("joint_piecewise_1_9_2_3_0", joint_piecewise.text)
        self.assertIn("0 <= g_1_9_2_3 <= 1", joint_piecewise.text)
        self.assertEqual(
            sum(
                line.strip().startswith(("joint_cell_", "joint_piecewise_"))
                for line in joint_piecewise.text.splitlines()
            ),
            4 * (4 * 4 * 7 + 1),
        )
        self.assertNotIn(" g_1_9_2_3\n", joint_piecewise.text.split("Binary\n", 1)[1])
        self.assertEqual(
            global_mccormick_relaxation.verify_canonical_incumbent_joint_piecewise_lift(
                lower_target,
                piecewise_cell_count=4,
                piecewise_product_pairs=targeted_pairs,
            ),
            lift,
        )
        joint_audit = global_mccormick_relaxation.verify_canonical_incumbent_model_lift(
            lower_target,
            additional_strip_counts=(20,),
            joint_piecewise_strip_products=True,
            piecewise_cell_count=4,
            piecewise_product_pairs=targeted_pairs,
        )
        self.assertEqual(joint_audit.additional_strip_counts, (20,))
        parsed_joint = highs_milp.parse_model(joint_piecewise)
        self.assertEqual(len(parsed_joint.row_names), len(subject_rows(joint_piecewise)))
        self.assertEqual(int(np.count_nonzero(parsed_joint.integrality)), joint_piecewise.binary_count)
        self.assertIn("g_1_9_2_3", parsed_joint.variable_names)
        with self.assertRaises(ValueError):
            global_mccormick_relaxation.build_model(
                12,
                lower_target=lower_target,
                piecewise_product_pairs=targeted_pairs,
            )
        with self.assertRaises(ValueError):
            global_mccormick_relaxation.build_model(
                12,
                joint_piecewise_strip_products=True,
            )

    def test_highs_bridge_diagnoses_relaxation_gap(self) -> None:
        report = highs_milp.solve_highs(global_mccormick_relaxation.build_model(6), time_limit_seconds=15)
        self.assertEqual(report.status, 0)
        self.assertAlmostEqual(report.objective, 0.25)
        self.assertAlmostEqual(report.maximization_dual_bound, 0.25)
        self.assertAlmostEqual(report.geometric_minimum_area, 0.125)
        # The n=6 relaxation has symmetric alternate optima, so the argmin
        # triangle label is a solver artifact: HiGHS returns (0, 1, 4) on
        # macOS arm64 and (0, 1, 2) on Linux x86_64 at the same objective.
        # Assert the solver-independent argmin property instead: whichever
        # triangle is reported must attain the minimum over all 20 triangles
        # of the returned point configuration.
        self.assertIn(report.geometric_minimum_triangle, set(combinations(range(6), 3)))
        for triangle in combinations(range(6), 3):
            self.assertLessEqual(
                report.geometric_minimum_area,
                abs(float(global_mccormick_relaxation.signed_area(report.points, triangle))),
            )
        # Float residuals of `matrix @ values` differ across platforms and
        # alternate optima (Linux x86_64 returned 3.3306690738754696e-16
        # where macOS arm64 returned exactly 0.0), so assert solver-level
        # feasibility instead.  The 1e-9 bound sits between the machine-eps
        # scale actually observed and HiGHS's 1e-7 default feasibility
        # tolerance: loose enough for cross-platform residuals, tight enough
        # to catch a genuinely infeasible or fractional returned point.
        self.assertLessEqual(report.maximum_constraint_violation, 1e-9)
        self.assertLessEqual(report.maximum_integrality_violation, 1e-9)
        self.assertGreater(report.largest_product_gaps[0][0], 0.2)

    def test_global_interval_branch_stays_exact_and_reports_incompleteness(self) -> None:
        self.assertTrue(global_interval_branch.root_covers_canonical_incumbent())
        root = global_interval_branch.target_root_spatial_box()
        self.assertEqual(root.coordinate_bounds["x_1"][0], 2 * global_interval_branch.TARGET)
        self.assertGreater(global_interval_branch.TARGET, Fraction(1, 31))
        self.assertEqual(root.coordinate_bounds["x_4"], (Fraction(0), Fraction(0)))
        upper, witness = global_interval_branch.minimum_area_upper(root)
        self.assertIsInstance(upper, Fraction)
        self.assertIn(witness, global_interval_branch.TRIANGLES)
        self.assertFalse(global_interval_branch.cannot_strictly_beat_incumbent(upper))
        self.assertEqual(global_interval_branch._widest_variable(root.coordinate_bounds, (0, 4, 5)), "y_0")
        left, right = global_mccormick_relaxation.split_spatial_box(root, "x_5")
        self.assertEqual(left.depth, 1)
        self.assertEqual(right.depth, 1)
        self.assertLessEqual(global_interval_branch.minimum_area_upper(left)[0], upper)
        self.assertLessEqual(global_interval_branch.minimum_area_upper(right)[0], upper)
        propagated_children = global_interval_branch.split_target_spatial_box(root, "x_5")
        self.assertEqual(len(propagated_children), 2)
        self.assertIn(Fraction(7, 16), global_interval_branch.CAPACITY_SPLIT_BOUNDARIES)
        x5_lower, x5_upper = root.coordinate_bounds["x_5"]
        x5_midpoint = (x5_lower + x5_upper) / 2
        self.assertEqual(
            {child.coordinate_bounds["x_5"] for child in propagated_children},
            {(x5_lower, x5_midpoint), (x5_midpoint, x5_upper)},
        )
        capacity_children = global_interval_branch.split_target_spatial_box(
            root, "x_5", split_strategy="capacity"
        )
        self.assertEqual(
            {child.coordinate_bounds["x_5"] for child in capacity_children},
            {(x5_lower, Fraction(7, 16)), (Fraction(7, 16), x5_upper)},
        )
        self.assertTrue(
            all(global_interval_branch.target_propagated_box(child) == child for child in propagated_children)
        )
        self.assertTrue(
            all(child.coordinate_bounds["x_5"][0] >= 2 * global_interval_branch.TARGET for child in propagated_children)
        )
        shifted_partition = global_interval_branch.shifted_strip_partition(16, Fraction(1, 32))
        self.assertEqual(len(shifted_partition) - 1, 17)
        self.assertTrue(
            all(
                right - left <= Fraction(1, 16)
                for left, right in zip(shifted_partition, shifted_partition[1:])
            )
        )
        shifted_only_bounds = dict(root.coordinate_bounds)
        for name, value in (("x_1", Fraction(101, 1000)), ("x_3", Fraction(126, 1000)), ("x_5", Fraction(151, 1000))):
            shifted_only_bounds[name] = (value, value)
        self.assertFalse(
            global_interval_branch.strip_capacity_feasible(
                global_mccormick_relaxation.SpatialBox(shifted_only_bounds)
            )
        )
        self.assertTrue(global_interval_branch.rectangle_capacity_feasible(root))
        exact_incumbent_bounds = {
            f"{axis}_{index}": algebraic_bounds(coordinate, 96)
            for index, point in enumerate(global_mccormick_relaxation.canonical_incumbent_points())
            for axis, coordinate in zip(("x", "y"), point)
        }
        self.assertEqual(
            sign(incumbent_value() - Qx.rational(global_interval_branch.TARGET)),
            1,
        )
        self.assertTrue(
            global_interval_branch.rectangle_capacity_feasible(
                global_mccormick_relaxation.SpatialBox(exact_incumbent_bounds)
            )
        )
        rectangle_overload_bounds = global_mccormick_relaxation.root_spatial_box(12).coordinate_bounds
        rectangle_overload_bounds = dict(rectangle_overload_bounds)
        rectangle_overload_bounds["y_0"] = (Fraction(0), Fraction(0))
        rectangle_overload_bounds["y_4"] = (Fraction(1, 8), Fraction(1, 8))
        rectangle_overload_bounds["x_5"] = (Fraction(1, 8), Fraction(1, 8))
        rectangle_overload_bounds["y_5"] = (Fraction(1, 16), Fraction(1, 16))
        self.assertTrue(
            global_interval_branch.strip_capacity_feasible(
                global_mccormick_relaxation.SpatialBox(rectangle_overload_bounds)
            )
        )
        self.assertFalse(
            global_interval_branch.rectangle_capacity_feasible(
                global_mccormick_relaxation.SpatialBox(rectangle_overload_bounds)
            )
        )
        result = global_interval_branch.explore(max_boxes=1)
        self.assertEqual(result.visited_boxes, 1)
        self.assertFalse(result.complete)
        self.assertGreater(result.pending_boxes, 0)
        self.assertIsNotNone(result.largest_pending_upper)
        self.assertEqual(result.strict_improvements, ())
        breadth_first = global_interval_branch.explore(max_boxes=40, queue_policy="breadth")
        depth_first = global_interval_branch.explore(max_boxes=40, queue_policy="depth")
        self.assertEqual(breadth_first.visited_boxes, depth_first.visited_boxes)
        self.assertEqual(depth_first.visited_boxes, 40)
        self.assertFalse(breadth_first.complete)
        self.assertFalse(depth_first.complete)
        self.assertGreater(depth_first.maximum_depth, breadth_first.maximum_depth)
        self.assertGreater(depth_first.discarded_boxes, breadth_first.discarded_boxes)
        with self.assertRaises(ValueError):
            global_interval_branch.explore(max_boxes=1, queue_policy="unknown")

        # A finite synthetic cover checks the policy-independent completion
        # invariant directly, without asking the production 19-dimensional
        # tree to terminate.  Every nonterminal has exactly the listed two
        # children and every leaf is pruned by the same exact predicate.
        toy_boxes = {
            name: global_mccormick_relaxation.SpatialBox(
                {"id": (Fraction(identifier), Fraction(identifier))},
                depth,
            )
            for name, identifier, depth in (
                ("root", 0, 0),
                ("left", 1, 1),
                ("right", 2, 1),
                ("left_left", 3, 2),
                ("left_right", 4, 2),
            )
        }
        children = {
            0: (toy_boxes["left"], toy_boxes["right"]),
            1: (toy_boxes["left_left"], toy_boxes["left_right"]),
        }

        def toy_upper(box: global_mccormick_relaxation.SpatialBox) -> tuple[Fraction, tuple[int, int, int]]:
            identifier = box.coordinate_bounds["id"][0]
            return (Fraction(1) if identifier in children else Fraction(0), (0, 1, 2))

        def toy_children(
            box: global_mccormick_relaxation.SpatialBox,
            variable: str,
            *,
            split_strategy: str,
        ) -> tuple[global_mccormick_relaxation.SpatialBox, ...]:
            self.assertEqual(variable, "id")
            self.assertEqual(split_strategy, "midpoint")
            return children[int(box.coordinate_bounds["id"][0])]

        patches = (
            patch.object(global_interval_branch, "root_covers_canonical_incumbent", return_value=True),
            patch.object(global_interval_branch, "target_root_spatial_box", return_value=toy_boxes["root"]),
            patch.object(global_interval_branch, "minimum_area_upper", side_effect=toy_upper),
            patch.object(global_interval_branch, "rectangle_capacity_feasible", return_value=True),
            patch.object(global_interval_branch, "strip_capacity_feasible", return_value=True),
            patch.object(global_interval_branch, "cannot_strictly_beat_incumbent", side_effect=lambda upper: upper == 0),
            patch.object(global_interval_branch, "_widest_variable", return_value="id"),
            patch.object(global_interval_branch, "split_target_spatial_box", side_effect=toy_children),
        )
        for active_patch in patches:
            active_patch.start()
        try:
            toy_breadth = global_interval_branch.explore(max_boxes=None, queue_policy="breadth")
            toy_depth = global_interval_branch.explore(max_boxes=None, queue_policy="depth")
        finally:
            for active_patch in reversed(patches):
                active_patch.stop()
        self.assertTrue(toy_breadth.complete)
        self.assertTrue(toy_depth.complete)
        self.assertEqual(toy_breadth.pending_boxes, toy_depth.pending_boxes)
        self.assertEqual(toy_breadth.strict_improvements, toy_depth.strict_improvements)
        self.assertEqual(
            sorted(discarded.box.coordinate_bounds["id"][0] for discarded in toy_breadth.discarded),
            sorted(discarded.box.coordinate_bounds["id"][0] for discarded in toy_depth.discarded),
        )

    def test_anchor_triangle_propagation_is_exact_sign_agnostic_and_keeps_the_incumbent(self) -> None:
        threshold = 2 * global_interval_branch.TARGET

        def box_contains_incumbent(bounds) -> bool:
            for index, point in enumerate(global_mccormick_relaxation.canonical_incumbent_points()):
                for axis, coordinate in zip(("x", "y"), point):
                    lower, upper = bounds[f"{axis}_{index}"]
                    if sign(coordinate - Qx.rational(lower)) < 0 or sign(Qx.rational(upper) - coordinate) < 0:
                        return False
            return True

        def certify_trims(trims) -> None:
            for trim in trims:
                recomputed = global_interval_branch.double_area_vertex_upper(
                    global_interval_branch.points_for_box(trim.removed_box), trim.triangle
                )
                self.assertEqual(recomputed, trim.removed_supremum)
                self.assertLessEqual(recomputed, threshold)
                self.assertIn(trim.triangle, global_interval_branch.TRIANGLES)

        with self.assertRaises(ValueError):
            global_interval_branch.anchor_triangle_propagated_box(
                global_interval_branch.target_root_spatial_box(), scope="unknown"
            )
        with self.assertRaises(ValueError):
            global_interval_branch.anchor_triangle_propagated_box(
                global_interval_branch.target_root_spatial_box(), passes=0
            )
        # All 220 triples except the C(7, 3) = 35 taken from the free points.
        self.assertEqual(len(global_interval_branch.anchored_triangles()), 220 - 35)

        # Gate: the exact incumbent enclosure survives, both at the global
        # root and on a tight exact algebraic bracket of the incumbent.
        root = global_interval_branch.target_root_spatial_box()
        self.assertTrue(box_contains_incumbent(root.coordinate_bounds))
        propagated_root = global_interval_branch.anchor_triangle_propagated_box(root)
        self.assertIsNotNone(propagated_root.box)
        self.assertTrue(box_contains_incumbent(propagated_root.box.coordinate_bounds))
        certify_trims(propagated_root.trims)

        tight_incumbent_bounds = {
            f"{axis}_{index}": algebraic_bounds(coordinate, 96)
            for index, point in enumerate(global_mccormick_relaxation.canonical_incumbent_points())
            for axis, coordinate in zip(("x", "y"), point)
        }
        tight_box = global_mccormick_relaxation.SpatialBox(tight_incumbent_bounds)
        propagated_tight = global_interval_branch.anchor_triangle_propagated_box(tight_box, scope="all")
        self.assertIsNotNone(propagated_tight.box)
        self.assertTrue(box_contains_incumbent(propagated_tight.box.coordinate_bounds))
        certify_trims(propagated_tight.trims)

        # Gate: equality endpoints.  With the left chord pinned to height one,
        # triangle (0, 4, 5) has determinant exactly -x_5.  A box reaching the
        # threshold exactly is removable in full (the rule is one-sided on
        # strict improvers), and the named certificate is exact equality.
        chord_bounds = dict(global_mccormick_relaxation.root_spatial_box(12).coordinate_bounds)
        chord_bounds["y_0"] = (Fraction(0), Fraction(0))
        chord_bounds["y_4"] = (Fraction(1), Fraction(1))
        chord_bounds["x_5"] = (Fraction(0), threshold)
        pruned = global_interval_branch.anchor_triangle_propagated_box(
            global_mccormick_relaxation.SpatialBox(chord_bounds)
        )
        self.assertIsNone(pruned.box)
        self.assertEqual(pruned.prune_triangle, (0, 4, 5))
        self.assertEqual(pruned.prune_supremum, threshold)
        certify_trims(pruned.trims)

        # Gate: strictly above the threshold the box survives, the forced
        # branch is the *negative* orientation (sign-agnostic path), and the
        # kept interval retains the closed equality endpoint exactly.
        epsilon = Fraction(1, 10**9)
        strict_bounds = dict(chord_bounds)
        strict_bounds["x_5"] = (Fraction(0), threshold + epsilon)
        trimmed = global_interval_branch.anchor_triangle_propagated_box(
            global_mccormick_relaxation.SpatialBox(strict_bounds)
        )
        self.assertIsNotNone(trimmed.box)
        self.assertEqual(trimmed.box.coordinate_bounds["x_5"], (threshold, threshold + epsilon))
        x5_trims = [trim for trim in trimmed.trims if trim.variable == "x_5"]
        self.assertEqual(len(x5_trims), 1)
        self.assertEqual(x5_trims[0].triangle, (0, 4, 5))
        self.assertEqual(x5_trims[0].removed, (Fraction(0), threshold))
        self.assertEqual(x5_trims[0].removed_supremum, threshold)
        certify_trims(trimmed.trims)

        # Negative control: forcing the wrong orientation on a box that
        # contains the incumbent must trip the exactness gates instead of
        # silently emitting a wrong-side trim.  Triangle (0, 4, 5) has a
        # strictly negative determinant at the incumbent.
        with self.assertRaises(AssertionError):
            global_interval_branch._forced_positive_trims(
                dict(tight_incumbent_bounds), (0, 4, 5), (0, 4, 5), threshold, []
            )

        # A second pass may only refine the first: the crafted boxes keep
        # their single-pass outcome (same prune certificate, same kept
        # interval) and every additional trim is certified the same way.
        pruned_twice = global_interval_branch.anchor_triangle_propagated_box(
            global_mccormick_relaxation.SpatialBox(chord_bounds), passes=2
        )
        self.assertIsNone(pruned_twice.box)
        self.assertEqual(pruned_twice.prune_triangle, pruned.prune_triangle)
        self.assertEqual(pruned_twice.prune_supremum, pruned.prune_supremum)
        certify_trims(pruned_twice.trims)
        trimmed_twice = global_interval_branch.anchor_triangle_propagated_box(
            global_mccormick_relaxation.SpatialBox(strict_bounds), passes=2
        )
        self.assertIsNotNone(trimmed_twice.box)
        self.assertEqual(
            trimmed_twice.box.coordinate_bounds["x_5"], trimmed.box.coordinate_bounds["x_5"]
        )
        self.assertGreaterEqual(len(trimmed_twice.trims), len(trimmed.trims))
        certify_trims(trimmed_twice.trims)

        # The explore() integration must surface the propagation's own
        # certificate, not the box's larger minimum-area upper bound: a
        # scripted prune of the root records the named triangle with
        # witness_upper equal to the certified area supremum, and the trim
        # audit trail survives into the returned exploration.
        scripted = global_interval_branch.AnchorPropagation(
            None, (x5_trims[0],), (0, 4, 5), threshold
        )
        seen_scopes = []

        def scripted_propagation(box, *, scope, passes):
            seen_scopes.append(scope)
            return scripted

        with patch.object(
            global_interval_branch, "anchor_triangle_propagated_box", side_effect=scripted_propagation
        ):
            integrated = global_interval_branch.explore(max_boxes=1, anchor_propagation="all")
        self.assertEqual(seen_scopes, ["all"])
        self.assertEqual(integrated.discarded_boxes, 1)
        self.assertEqual(integrated.discarded[0].reason, "anchor-triangle")
        self.assertEqual(integrated.discarded[0].witness, (0, 4, 5))
        self.assertEqual(integrated.discarded[0].witness_upper, threshold / 2)
        self.assertLessEqual(integrated.discarded[0].witness_upper, global_interval_branch.TARGET)
        self.assertEqual(integrated.anchor_trims, 1)
        self.assertEqual(integrated.anchor_trim_records, (x5_trims[0],))

        # The unscripted path at the same tiny budget stays exact and honest.
        baseline = global_interval_branch.explore(max_boxes=2, queue_policy="breadth")
        propagating = global_interval_branch.explore(
            max_boxes=2, queue_policy="breadth", anchor_propagation="anchored"
        )
        self.assertEqual(propagating.visited_boxes, baseline.visited_boxes)
        self.assertFalse(propagating.complete)
        self.assertEqual(propagating.anchor_trims, len(propagating.anchor_trim_records))
        certify_trims(propagating.anchor_trim_records)
        self.assertEqual(baseline.anchor_trims, 0)
        self.assertEqual(baseline.anchor_trim_records, ())
        with self.assertRaises(ValueError):
            global_interval_branch.explore(max_boxes=1, anchor_propagation="unknown")

    def test_rigidity_core_certificates_are_exact_and_two_sided(self) -> None:
        import rigidity_core

        data = rigidity_core.active_data()
        self.assertEqual(len(data.triangles), 20)
        self.assertEqual(len(data.free_rows[0]), 16)
        self.assertEqual(len(data.inward_rows[0]), 8)
        self.assertEqual(len(data.d4_index_maps), 8)
        self.assertIn(tuple(range(20)), data.d4_index_maps)

        # Runs every positive and negative control, including the mis-signed
        # stress and the untouched-boundary-normal witness.
        rigidity_core.full_set_controls(data)

        # The committed all-20 orbit-weight stress must verify through this
        # module's own checker with the committed inward normal exactly.
        committed = [rigidity_core.ORBIT_WEIGHTS[data.orbit_of[member]] for member in range(20)]
        _, normals = rigidity_core._verify_stress(tuple(range(20)), data, committed)
        for normal in normals:
            self.assertTrue((normal - rigidity_core.INWARD_NORMAL).is_zero())

        # Below sixteen triangles the rank certificate must refuse rigidity.
        fifteen = rigidity_core.classify(tuple(range(15)), data)
        self.assertEqual(fifteen.status, rigidity_core.NONRIGID)
        self.assertIsNotNone(fifteen.witness)

        # A truncated scan must say so and make no minimality claim.
        result = rigidity_core.scan(data, sizes=(16,), max_subsets=2)
        self.assertFalse(result["complete"])
        self.assertEqual(result["processed"], 2)

    def test_rigidity_sampling_matches_the_incumbent_frame_descriptively(self) -> None:
        import global_normal_form_search as gnfs
        import rigidity_sampling

        incumbent = rigidity_sampling.incumbent_float_points()
        self.assertEqual(incumbent.shape, (12, 2))
        distance, label_map = rigidity_sampling.match_to_incumbent(incumbent, incumbent)
        self.assertLess(distance, 1e-18)
        self.assertEqual(sorted(label_map), list(range(12)))

        # A D4 image with shuffled labels still matches the orbit, and the
        # induced label map carries its near-active triangles back onto the
        # exact active set (which is D4-invariant).
        rng = np.random.default_rng(20260820)
        permutation = list(rng.permutation(12))
        image = rigidity_sampling.D4_COORDINATE_MAPS[5](incumbent)[permutation]
        distance, label_map = rigidity_sampling.match_to_incumbent(image, incumbent)
        self.assertLess(distance, 1e-12)
        minimum = float(np.min(np.abs(gnfs.signed_areas(image))))
        mapped = {
            tuple(sorted(label_map[vertex] for vertex in triangle))
            for triangle in rigidity_sampling.near_active(image, minimum, 1e-6)
        }
        _, active, _ = incumbent_analysis()
        self.assertEqual(mapped, set(active))

        # A configuration far from the orbit must not match.
        grid = np.array([[0.05 + 0.3 * (index % 4), 0.05 + 0.3 * (index // 4)] for index in range(12)])
        far_distance, _ = rigidity_sampling.match_to_incumbent(grid, incumbent)
        self.assertGreater(far_distance, 1e-2)

        cores = rigidity_sampling.parse_cores("0,1,2;3,4", tuple(active))
        self.assertEqual(len(cores), 2)
        self.assertEqual(cores[0], (active[0], active[1], active[2]))
        with self.assertRaises(ValueError):
            rigidity_sampling.parse_cores("0,99", tuple(active))

        # A tiny perturbation must polish back into the incumbent orbit and
        # keep the sample above the loosest professor threshold.
        trial = rigidity_sampling.run_perturbed_trial(20260820, sigma=1e-3)
        lower, upper = algebraic_bounds(incumbent_value(), 96)
        incumbent_float = float((lower + upper) / 2)
        self.assertGreater(trial.minimum_area, incumbent_float - 1e-4)
        perturbed_distance, _ = rigidity_sampling.match_to_incumbent(
            np.asarray(trial.points, dtype=float), incumbent
        )
        self.assertLess(perturbed_distance, 1e-6)

    def test_global_mccormick_glpk_parser_keeps_lp_and_mip_results_distinct(self) -> None:
        model = global_mccormick_relaxation.build_model(6)
        timed_out_without_incumbent = """
OPTIMAL LP SOLUTION FOUND
+ 300: mip =     not found yet <=   1.000000000e-01        (1; 0)
TIME LIMIT EXCEEDED; SEARCH TERMINATED
"""
        report = global_mccormick_relaxation._parse_glpsol_report(model, (), 0, timed_out_without_incumbent)
        self.assertEqual(report.status, "time-limit")
        self.assertIsNone(report.incumbent)
        self.assertEqual(report.reported_upper, 0.1)

        timed_out_with_incumbent = """
OPTIMAL LP SOLUTION FOUND
+ 73492: >>>>>   3.906250000e-02 <=   1.000000000e-01 156.0% (1; 0)
+ 93224: mip =   3.906250000e-02 <=   1.000000000e-01 156.0% (1; 0)
TIME LIMIT EXCEEDED; SEARCH TERMINATED
"""
        report = global_mccormick_relaxation._parse_glpsol_report(model, (), 0, timed_out_with_incumbent)
        self.assertEqual(report.status, "time-limit")
        self.assertEqual(report.incumbent, 0.0390625)
        self.assertEqual(report.reported_upper, 0.1)

        integer_optimal = """
OPTIMAL LP SOLUTION FOUND
+     9: mip =     not found yet <=              +inf        (1; 0)
+     9: >>>>>   1.250000000e-01 <=   1.250000000e-01   0.0% (1; 0)
+     9: mip =   1.250000000e-01 <=     tree is empty   0.0% (0; 1)
INTEGER OPTIMAL SOLUTION FOUND
"""
        report = global_mccormick_relaxation._parse_glpsol_report(model, (), 0, integer_optimal)
        self.assertEqual(report.status, "optimal")
        self.assertEqual(report.incumbent, 0.125)
        self.assertEqual(report.reported_upper, 0.125)
        self.assertEqual(
            global_mccormick_relaxation._MIP_PROGRESS.search("mip = not found yet <= +inf").group("upper"),
            "+inf",
        )

        integer_optimal_without_parseable_incumbent = """
* 9: obj = 1.000000000e-01 inf = 0.0
OPTIMAL LP SOLUTION FOUND
INTEGER OPTIMAL SOLUTION FOUND
"""
        report = global_mccormick_relaxation._parse_glpsol_report(
            model, (), 0, integer_optimal_without_parseable_incumbent
        )
        self.assertEqual(report.status, "optimal-unparsed")
        self.assertIsNone(report.incumbent)
        self.assertEqual(report.reported_upper, 0.1)

        timed_out_after_only_infinite_tree_bound = """
* 9: obj = 1.000000000e-01 inf = 0.0
OPTIMAL LP SOLUTION FOUND
Integer optimization begins...
+ 9: mip = not found yet <= +inf (1; 0)
| 42: obj = 2.000000000e-02 inf = 0.0
TIME LIMIT EXCEEDED; SEARCH TERMINATED
"""
        report = global_mccormick_relaxation._parse_glpsol_report(
            model, (), 0, timed_out_after_only_infinite_tree_bound
        )
        self.assertEqual(report.status, "time-limit")
        self.assertIsNone(report.incumbent)
        self.assertEqual(report.reported_upper, 0.1)

        timed_out_before_root_lp_optimality = """
0: obj = 2.000000000e-02 inf = 1.0
TIME LIMIT EXCEEDED; SEARCH TERMINATED
"""
        report = global_mccormick_relaxation._parse_glpsol_report(
            model, (), 0, timed_out_before_root_lp_optimality
        )
        self.assertEqual(report.status, "time-limit")
        self.assertIsNone(report.incumbent)
        self.assertIsNone(report.reported_upper)

    def test_unrestricted_normal_form_parameterization_and_exact_snap(self) -> None:
        incumbent = global_normal_form_search.canonical_incumbent_points()
        self.assertTrue(global_normal_form_search.is_normal_form(incumbent))
        parameters = global_normal_form_search.parameters_for_points(incumbent)
        self.assertEqual(parameters.shape, (19,))
        np.testing.assert_allclose(global_normal_form_search.configuration(parameters), incumbent, atol=0.0, rtol=0.0)
        self.assertAlmostEqual(
            global_normal_form_search.minimum_area(incumbent),
            0.032598858691819698,
            delta=1e-15,
        )

        random = np.random.default_rng(2026081601).uniform(0.0, 1.0, size=19)
        normalized = global_normal_form_search.normalize_parameters(random)
        normalized_points = global_normal_form_search.configuration(normalized)
        self.assertTrue(global_normal_form_search.is_normal_form(normalized_points))
        np.testing.assert_array_equal(normalized, global_normal_form_search.normalize_parameters(random))

        raw = np.zeros(19)
        polished = np.ones(19)
        stage, selected_area, selected = global_normal_form_search.select_candidate(0.2, raw, 0.1, polished)
        self.assertEqual((stage, selected_area), ("differential-evolution", 0.2))
        np.testing.assert_array_equal(selected, raw)
        stage, selected_area, selected = global_normal_form_search.select_candidate(0.1, raw, 0.2, polished)
        self.assertEqual((stage, selected_area), ("epigraph", 0.2))
        np.testing.assert_array_equal(selected, polished)

        snapped = global_normal_form_search.dyadic_snap(incumbent, 20)
        self.assertTrue(all(value.denominator <= 2**20 for point in snapped for value in point))
        snap_report = global_normal_form_search.exact_snap_report(incumbent, 20)
        self.assertFalse(snap_report.strictly_beats_incumbent)

    def test_c4_symmetry_family_contains_the_incumbent(self) -> None:
        parameters = c4_symmetry_search.canonical_incumbent_parameters()
        points = c4_symmetry_search.configuration(parameters)
        self.assertEqual(parameters.shape, (6,))
        self.assertTrue(c4_symmetry_search.is_c4_configuration(points))
        self.assertAlmostEqual(
            c4_symmetry_search.minimum_area(points),
            0.032598858691819698,
            delta=1e-15,
        )
        broken = points.copy()
        broken[5, 0] += 0.01
        self.assertFalse(c4_symmetry_search.is_c4_configuration(broken))
        rational_seeds = (
            (Fraction(5, 7), Fraction(2, 7)),
            (Fraction(6, 7), Fraction(1)),
            (Fraction(6, 7), Fraction(0)),
        )
        rational_points = tuple(
            point
            for x, y in rational_seeds
            for point in ((x, y), (1 - y, x), (1 - x, 1 - y), (y, 1 - x))
        )
        self.assertEqual(verify_rational_candidate(rational_points)[0], Fraction(3, 98))

    def test_c2_boundary_family_contains_the_incumbent_without_c4_locking(self) -> None:
        parameters = c2_boundary_search.canonical_incumbent_parameters()
        points = c2_boundary_search.configuration(parameters)
        self.assertEqual(parameters.shape, (8,))
        self.assertTrue(c2_boundary_search.is_c2_boundary_configuration(points))
        self.assertAlmostEqual(c2_boundary_search.minimum_area(points), 0.032598858691819698, delta=1e-15)
        self.assertEqual(len(c2_boundary_search.active_triangles(points, tolerance=1e-10)), 20)
        polished_area, polished_parameters, polished_success = c2_boundary_search.epigraph_polish(parameters)
        self.assertTrue(polished_success)
        self.assertAlmostEqual(polished_area, 0.032598858691819698, delta=1e-15)
        np.testing.assert_allclose(polished_parameters, parameters, atol=0.0, rtol=0.0)
        broken = points.copy()
        broken[7, 0] -= 0.01
        self.assertFalse(c2_boundary_search.is_c2_boundary_configuration(broken))
        raw = np.zeros(8)
        polished = np.ones(8)
        stage, area, selected = c2_boundary_search.select_candidate(0.2, raw, 0.1, polished)
        self.assertEqual((stage, area), ("differential-evolution", 0.2))
        np.testing.assert_array_equal(selected, raw)
        stage, area, selected = c2_boundary_search.select_candidate(0.1, raw, 0.2, polished)
        self.assertEqual((stage, area), ("epigraph", 0.2))
        np.testing.assert_array_equal(selected, polished)

    def test_c4_bernstein_interval_engine_keeps_dependence_and_scope_exact(self) -> None:
        self.assertTrue(c4_interval_certificate.root_covers_canonical_incumbent())
        root = c4_interval_certificate.root_box()
        upper, witness = c4_interval_certificate.minimum_area_upper(root)
        self.assertEqual((upper, witness), (Fraction(1, 8), (0, 4, 8)))
        self.assertEqual(len(c4_interval_certificate.TRIANGLE_C4_ORBITS), 55)
        self.assertEqual(
            set(triangle for orbit in c4_interval_certificate.TRIANGLE_C4_ORBITS for triangle in orbit),
            set(c4_interval_certificate.TRIANGLES),
        )
        heuristic = c4_interval_certificate.heuristic_area_uppers(root)
        self.assertEqual(heuristic.shape, (55,))
        self.assertAlmostEqual(float(np.min(heuristic)), float(upper))
        for index, triangle in enumerate(c4_interval_certificate.REPRESENTATIVE_TRIANGLES):
            self.assertAlmostEqual(heuristic[index], float(c4_interval_certificate.area_upper_for_triangle(root, triangle)))
        self.assertTrue(c4_interval_certificate.strip_capacity_feasible(c4_interval_certificate.spatial_box(root)))

        radial_target = Fraction(1, 20)
        inside_disk_parameters = list(root.parameters)
        inside_disk_parameters[0] = (Fraction(1, 2), Fraction(3, 5))
        inside_disk_parameters[1] = (Fraction(2, 5), Fraction(1, 2))
        inside_disk = c4_interval_certificate._target_propagation(
            c4_interval_certificate.Box(tuple(inside_disk_parameters)), radial_target
        )
        self.assertIsNone(inside_disk.box)
        self.assertEqual((inside_disk.reason, inside_disk.triangle, inside_disk.upper), ("orbit-triangle", (0, 1, 2), Fraction(1, 50)))

        seed_rectangle_parameters = list(root.parameters)
        seed_rectangle_parameters[0] = (Fraction(3, 4), Fraction(3, 4))
        seed_rectangle_parameters[2] = (Fraction(4, 5), Fraction(4, 5))
        seed_rectangle_parameters[4] = (Fraction(19, 20), Fraction(1))
        for index in (1, 3, 5):
            seed_rectangle_parameters[index] = (Fraction(3, 20), Fraction(1, 2))
        seed_rectangle = c4_interval_certificate._target_propagation(
            c4_interval_certificate.Box(tuple(seed_rectangle_parameters)), radial_target
        )
        self.assertIsNone(seed_rectangle.box)
        self.assertEqual(
            (seed_rectangle.reason, seed_rectangle.triangle, seed_rectangle.upper),
            ("seed-triangle-rectangle", (0, 4, 8), Fraction(7, 160)),
        )

        radial_parameters = list(root.parameters)
        radial_parameters[1] = (Fraction(1, 2), Fraction(1, 2))
        radial = c4_interval_certificate.target_propagated_box(
            c4_interval_certificate.Box(tuple(radial_parameters)), radial_target, sqrt_bits=16
        )
        self.assertIsNotNone(radial)
        self.assertGreater(radial.parameters[0][0], Fraction(1, 2))
        self.assertLessEqual((radial.parameters[0][0] - Fraction(1, 2)) ** 2, radial_target)
        radial_valid_point = (Fraction(3, 4), Fraction(1, 2), Fraction(1), Fraction(0), Fraction(1), Fraction(0))
        self.assertTrue(
            all(lower <= value <= upper for value, (lower, upper) in zip(radial_valid_point, radial.parameters))
        )
        propagated_strict_orbit_points = 0
        for horizontal_values in product((Fraction(1, 2), Fraction(3, 4), Fraction(1)), repeat=3):
            if tuple(sorted(horizontal_values)) != horizontal_values:
                continue
            for vertical_values in product((Fraction(0), Fraction(1, 4), Fraction(1, 2)), repeat=3):
                parameter_point = tuple(value for pair in zip(horizontal_values, vertical_values) for value in pair)
                if any(
                    (horizontal - Fraction(1, 2)) ** 2 + (Fraction(1, 2) - vertical) ** 2 <= radial_target
                    for horizontal, vertical in zip(horizontal_values, vertical_values)
                ):
                    continue
                if abs(c4_interval_certificate.evaluate_determinant(parameter_point, (0, 4, 8))) / 2 <= radial_target:
                    continue
                interval_box = c4_interval_certificate.Box(
                    tuple(
                        (
                            max(Fraction(1, 2) if index % 2 == 0 else Fraction(0), value - Fraction(1, 64)),
                            min(Fraction(1) if index % 2 == 0 else Fraction(1, 2), value + Fraction(1, 64)),
                        )
                        for index, value in enumerate(parameter_point)
                    )
                )
                preserved = c4_interval_certificate.target_propagated_box(interval_box, radial_target)
                self.assertIsNotNone(preserved)
                self.assertTrue(
                    all(lower <= value <= upper for value, (lower, upper) in zip(parameter_point, preserved.parameters))
                )
                propagated_strict_orbit_points += 1
        self.assertGreater(propagated_strict_orbit_points, 0)

        right_child = c4_interval_certificate.split(root, 0)[1]
        self.assertEqual(right_child.parameters[0], (Fraction(3, 4), Fraction(1)))
        self.assertEqual(right_child.parameters[2][0], Fraction(3, 4))
        self.assertEqual(right_child.parameters[4][0], Fraction(3, 4))
        order_probe_parameters = list(root.parameters)
        order_probe_parameters[4] = (Fraction(1, 2), Fraction(3, 5))
        order_probe = c4_interval_certificate._ordered_box(c4_interval_certificate.Box(tuple(order_probe_parameters)))
        self.assertIsNotNone(order_probe)
        self.assertEqual(order_probe.parameters[0][1], Fraction(3, 5))
        self.assertEqual(order_probe.parameters[2][1], Fraction(3, 5))
        capacity_probe_parameters = list(root.parameters)
        capacity_probe_parameters[0] = (Fraction(1, 2), Fraction(2, 3))
        capacity_probe = c4_interval_certificate.Box(tuple(capacity_probe_parameters))
        self.assertEqual(
            c4_interval_certificate.split(capacity_probe, 0, split_strategy="midpoint")[0].parameters[0][1],
            Fraction(7, 12),
        )
        self.assertEqual(
            c4_interval_certificate.split(capacity_probe, 0, split_strategy="capacity")[0].parameters[0][1],
            Fraction(19, 32),
        )

        sample_box = c4_interval_certificate.Box(
            (
                (Fraction(1, 2), Fraction(3, 4)),
                (Fraction(0), Fraction(1, 4)),
                (Fraction(3, 4), Fraction(1)),
                (Fraction(1, 4), Fraction(1, 2)),
                (Fraction(3, 4), Fraction(1)),
                (Fraction(0), Fraction(1, 4)),
            )
        )
        triangle = (0, 4, 8)
        bound = c4_interval_certificate.double_area_bernstein_upper(sample_box, triangle)
        for endpoints in product((0, 1), repeat=6):
            parameters = tuple(interval[endpoint] for interval, endpoint in zip(sample_box.parameters, endpoints))
            self.assertLessEqual(abs(c4_interval_certificate.evaluate_determinant(parameters, triangle)), bound)
        midpoint = tuple(sum(interval) / 2 for interval in sample_box.parameters)
        self.assertLessEqual(abs(c4_interval_certificate.evaluate_determinant(midpoint, triangle)), bound)

        negative_control = (
            Fraction(5, 7),
            Fraction(2, 7),
            Fraction(6, 7),
            Fraction(0),
            Fraction(1),
            Fraction(1, 7),
        )
        pinned = c4_interval_certificate.Box(tuple((value, value) for value in negative_control))
        self.assertEqual(c4_interval_certificate.minimum_area_upper(pinned)[0], Fraction(3, 98))
        rational_points = tuple(
            point
            for horizontal, vertical in zip(negative_control[::2], negative_control[1::2])
            for point in (
                (horizontal, vertical),
                (1 - vertical, horizontal),
                (1 - horizontal, 1 - vertical),
                (vertical, 1 - horizontal),
            )
        )
        for triangle in c4_interval_certificate.TRIANGLES:
            first, second, third = (rational_points[index] for index in triangle)
            direct = (second[0] - first[0]) * (third[1] - first[1]) - (second[1] - first[1]) * (
                third[0] - first[0]
            )
            self.assertEqual(c4_interval_certificate.evaluate_determinant(negative_control, triangle), direct)

        result = c4_interval_certificate.explore(slack_bits=12, root_bisections=64, max_boxes=1)
        self.assertEqual(result.visited_boxes, 1)
        self.assertFalse(result.complete)
        self.assertEqual(result.discarded_boxes, 0)
        self.assertGreater(result.pending_boxes, 0)
        self.assertEqual(result.strict_improvements, ())
        best_upper = c4_interval_certificate.explore(
            slack_bits=12, root_bisections=64, max_boxes=1, queue_strategy="best-upper"
        )
        self.assertEqual((best_upper.visited_boxes, best_upper.pending_boxes), (1, 2))
        with self.assertRaises(ValueError):
            c4_interval_certificate.explore(slack_bits=12, root_bisections=64, max_boxes=1, queue_strategy="invalid")
        coarse_complete = c4_interval_certificate.explore(slack_bits=4, root_bisections=64, max_boxes=None)
        self.assertTrue(coarse_complete.complete)
        self.assertGreater(coarse_complete.visited_boxes, 0)
        self.assertGreater(coarse_complete.discarded_boxes, 0)
        self.assertEqual(coarse_complete.pending_boxes, 0)
        self.assertEqual(coarse_complete.strict_improvements, ())

    def test_free_size5_transversal_search_lifts_the_incumbent_without_edge_locking(self) -> None:
        transversals = set(active_hitting_sets(5))
        for stratum in transversal_free_search._selected_strata(tuple(transversal_free_search.STRATA)):
            self.assertIn(stratum.moved_labels, transversals)
            coordinates = transversal_free_search.parameter_coordinates(stratum)
            self.assertEqual(len(coordinates), 10)
            points = transversal_free_search.configuration(stratum, transversal_free_search.incumbent_parameters(stratum))
            np.testing.assert_allclose(points, transversal_free_search._INCUMBENT_POINTS, atol=0.0, rtol=0.0)
            self.assertAlmostEqual(transversal_free_search.minimum_area(points), 0.032598858691819698, delta=1e-15)

        raw = np.zeros(10)
        polished = np.ones(10)
        stage, selected_area, selected = transversal_free_search.select_candidate(0.2, raw, 0.1, polished)
        self.assertEqual((stage, selected_area), ("differential-evolution", 0.2))
        np.testing.assert_array_equal(selected, raw)
        stage, selected_area, selected = transversal_free_search.select_candidate(0.1, raw, 0.2, polished)
        self.assertEqual((stage, selected_area), ("epigraph", 0.2))
        np.testing.assert_array_equal(selected, polished)

    def test_global_mccormick_lp_rounding_enlarges_the_exact_relaxation(self) -> None:
        value = Fraction(1, 31)
        self.assertLess(Fraction(global_mccormick_relaxation._decimal(value, "down")), value)
        self.assertGreater(Fraction(global_mccormick_relaxation._decimal(value, "up")), value)
        self.assertEqual(global_mccormick_relaxation._decimal(Fraction(1, 2), "down"), "0.5")
        self.assertEqual(global_mccormick_relaxation._decimal(Fraction(1, 2), "up"), "0.5")

        model = global_mccormick_relaxation.build_model(
            12,
            lower_target=value,
            additional_strip_counts=(20,),
        )
        target_floor = next(row for row in model.text.splitlines() if row.strip().startswith("target_floor:"))
        self.assertLess(Fraction(target_floor.rsplit(" ", 1)[1]), value)
        strip_upper = next(
            row for row in model.text.splitlines() if row.strip().startswith("strip_upper_x_20_5_2:")
        )
        self.assertGreater(Fraction(strip_upper.rsplit(" ", 1)[1]), Fraction(23, 20))
        sign_positive = next(
            row for row in model.text.splitlines() if row.strip().startswith("sign_positive_0_1_5:")
        )
        self.assertIn(f"{global_mccormick_relaxation._decimal(model.big_m, 'down')} b_0_1_5", sign_positive)
        self.assertTrue(sign_positive.endswith(f"<= {global_mccormick_relaxation._decimal(model.big_m, 'up')}"))

    def test_d4_interval_certificate_brackets_incumbent(self) -> None:
        certificate = d4_interval_certificate.certify(slack_bits=32, root_bisections=96)
        self.assertLess(certificate.record_lower, certificate.record_upper)
        self.assertLess(certificate.record_upper, certificate.target_upper)
        self.assertLess(certificate.target_upper - certificate.record_lower, Fraction(1, 2**31))
        self.assertGreater(certificate.visited_boxes, 1)
        self.assertEqual((certificate.visited_boxes + 1) // 2, certificate.discarded_boxes)

    def test_d4_interval_certificate_documented_precision(self) -> None:
        certificate = d4_interval_certificate.certify()
        self.assertLess(certificate.target_upper - certificate.record_lower, Fraction(1, 2**79))
        self.assertEqual(certificate.visited_boxes, 1843)
        self.assertEqual(certificate.discarded_boxes, 922)
        self.assertEqual(certificate.maximum_depth, 155)

    def test_d4_interval_contains_every_exact_triangle_at_a_sample_point(self) -> None:
        box = d4_interval_certificate.Box(
            (Fraction(1, 8), Fraction(1, 4)),
            (Fraction(1, 10), Fraction(1, 5)),
        )
        sample = d4_interval_certificate.Box(
            (Fraction(1, 6), Fraction(1, 6)),
            (Fraction(1, 7), Fraction(1, 7)),
        )
        bounding_points = d4_interval_certificate.d4_points(box)
        exact_points = tuple(
            (coordinate[0], ordinate[0])
            for coordinate, ordinate in d4_interval_certificate.d4_points(sample)
        )
        for triangle in d4_interval_certificate.TRIANGLES:
            lower, upper = d4_interval_certificate.double_area_interval(bounding_points, triangle)
            i, j, k = triangle
            xi, yi = exact_points[i]
            xj, yj = exact_points[j]
            xk, yk = exact_points[k]
            determinant = (xj - xi) * (yk - yi) - (yj - yi) * (xk - xi)
            self.assertLessEqual(lower, determinant)
            self.assertLessEqual(determinant, upper)

    def test_root_interval_is_rigorous(self) -> None:
        lower, upper = root_bounds(192)
        self.assertLess(cubic(lower), 0)
        self.assertGreater(cubic(upper), 0)
        self.assertLess(upper - lower, Fraction(1, 2**192))

    def test_cubic_field_inversion(self) -> None:
        value = Qx(Fraction(7, 5), Fraction(3, 7), Fraction(-1, 3))
        self.assertEqual(value * value.inverse(), Qx.rational(1))

    def test_enumeration_matches_published_formula(self) -> None:
        minimum, active, tiers = incumbent_analysis()
        self.assertTrue((minimum - incumbent_value()).is_zero())
        self.assertTrue(record_cubic(minimum).is_zero())
        self.assertEqual(len(active), 20)
        self.assertGreater(sign(tiers[1] - minimum), 0)
        self.assertTrue(decimal_string(minimum, 18).startswith("0.032598858691819698"))

    def test_active_hypergraph_structure(self) -> None:
        orbits, hitting_sets = active_structure()
        self.assertEqual(sorted(len(orbit) for orbit in orbits), [4, 8, 8])
        for size in range(4):
            self.assertEqual(active_hitting_sets(size), ())
        self.assertEqual(hitting_sets, ((8, 9, 10, 11),))

    def test_first_order_tangent_certificate(self) -> None:
        certificate = tangent_certificate.certificate()
        self.assertEqual(len(certificate.orbit_weights), 3)
        self.assertTrue(all(sign(weight) > 0 for weight in certificate.orbit_weights))
        self.assertLess(sign(certificate.inward_normal), 0)
        self.assertGreater(sign(certificate.critical_minor), 0)
        for point_index in range(4):
            self.assertTrue(certificate.weighted_gradient[point_index][0].is_zero())
        for point_index in range(4, 8):
            self.assertTrue(certificate.weighted_gradient[point_index][1].is_zero())
        for point_index in range(8, 12):
            self.assertTrue(all(component.is_zero() for component in certificate.weighted_gradient[point_index]))

    def test_independent_decimal_reconstruction(self) -> None:
        exact_minimum, exact_active, tiers = incumbent_analysis()
        decimal_minimum, decimal_active, decimal_second = decimal_verifier.analysis(70)
        self.assertEqual(decimal_active, exact_active)
        self.assertLess(abs(decimal_minimum - decimal_verifier.Decimal(decimal_string(exact_minimum, 65))), decimal_verifier.Decimal("1e-60"))
        self.assertLess(abs(decimal_second - decimal_verifier.Decimal(decimal_string(tiers[1], 65))), decimal_verifier.Decimal("1e-60"))

    def test_rational_verifier_rejects_invalid_candidate(self) -> None:
        duplicate = [(Fraction(0), Fraction(0))] * 12
        with self.assertRaises(ValueError):
            verify_rational_candidate(duplicate)

    def test_exact_n11_insertion_no_go(self) -> None:
        result = solve_insertion()
        self.assertEqual(result.point, (Fraction(1, 2), Fraction(1, 9)))
        self.assertEqual(result.new_double_minimum, Fraction(1, 27))
        self.assertEqual(result.full_minimum_area, Fraction(1, 54))
        self.assertLess(sign(Qx.rational(result.full_minimum_area) - incumbent_value()), 0)


if __name__ == "__main__":
    unittest.main()
