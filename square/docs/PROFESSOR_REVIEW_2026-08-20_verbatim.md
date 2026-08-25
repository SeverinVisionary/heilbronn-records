1. VERDICT

The global n=12 track is a dead end and here is why: you are applying coordinate-wise exact branch-and-bound to a 19-dimensional semialgebraic feasibility problem with weak local bounds, an equality case on the boundary of feasibility, and no theorem forcing the search into a small number of combinatorial types. Exact arithmetic makes the failure trustworthy. It does not make the method viable.

Comellas and Yebra presented their n=12 configuration as a new lower bound and explicitly stated that they had no proof of optimality. The construction remains the listed record, while exact global certification in the square currently stops at n=9; even n=10 is still open. You are attempting to jump four continuous coordinates beyond an already-unresolved n=10 problem. 
Emis
+3

What is genuinely valuable

The exact incumbent reconstruction is useful infrastructure, not a result. Comellas–Yebra already gave exact algebraic coordinates. Rechecking all 220 areas and identifying the 20 active triangles is excellent due diligence. By itself, nobody cites that. The active-triangle hypergraph and its 8+8+4 orbit decomposition become valuable only when converted into a rigidity or stability theorem.

The exact tangent-cone certificate is real mathematics. This is the strongest thing in the branch. If the linearized feasible cone at the incumbent is exactly zero after accounting for boundary constraints and symmetries, then the incumbent is locally isolated in the record superlevel set. Turn that into a theorem with an explicit neighborhood and a quantitative error bound. That is citable.

The “move at most three labelled points” theorem is substantive but narrow. It is stronger than infinitesimal rigidity because those moved points range globally. It belongs in a rigidity paper, not as a standalone flagship result.

A completed C4-family theorem would be citable. Proving that the Comellas–Yebra configuration uniquely maximizes the minimum area within the full three-orbit C4 family, with equality classification, is a legitimate restricted extremal theorem. It would be a modest paper, but a real one. The completed two-parameter D4 result is already a useful component.

The Goldberg-plus-one-point result is a lemma. It disposes of an obvious construction route. It is not a paper. If its proof exposes a general insertion obstruction, keep it. If it is merely a large exhaustive computation showing 1/54, give it two pages and move on.

What is competent engineering of no mathematical consequence

The exact Fraction branch-and-bound, the certificate bookkeeping, the endpoint tests, the negative controls, and the re-certification of trimmed slabs are all necessary for trustworthy software. They are not mathematical progress until the queue empties or they produce a reusable theorem.

“A trustworthy nonterminating search” is still a nonterminating search.

The anchor-triangle propagation has not demonstrated an improvement. At the same 1,000-node budget, the depth-first run with anchors leaves 399 pending boxes and reaches depth 625, whereas the run without anchors leaves 33 pending boxes and reaches depth 53. Those are different trees, so this does not prove anchors are harmful. It does prove that “1,856 exact trims” is a vanity metric. A trim matters only if it reduces the final certificate size by orders of magnitude.

The McCormick/RLT MILP bound far above the incumbent is scientifically worthless. Calling it “diagnostic only” is honest, but do not spend another week on it unless a specific strengthening produces a dramatic bound jump. Generic McCormick refinement will not do that.

The rectangle-capacity constraint itself is already a known elementary observation: any rectangle of area below twice the target can contain at most two points. Implementing more grids is engineering unless the collection of grids yields a global counting theorem. 
arXiv

What is self-deception

Treating depth 625 as progress is self-deception. It means the algorithm is chasing a pathological sliver. It does not mean the global domain is being conquered.

Treating exactness as a substitute for convergence is self-deception. Exact arithmetic answers “are the prunes valid?” It does not answer “will there ever be enough prunes?”

Treating finite symmetry quotienting as salvation is self-deception. The five-boundary labeling and x-ordering already remove most of the D4 and label symmetry. Even if the entire remaining factor of 
8
⋅
7
!
=
40,320
8⋅7!=40,320 were still available, that is less than the factor 
2
19
=
524,288
2
19
=524,288 incurred by adding one extra binary refinement bit in every coordinate. Full missing finite symmetry would not buy even one global bit of resolution.

Treating the success of the symmetric-family searches as evidence for the global cover is self-deception. Imposing C4 symmetry collapses the dimension because it is a mathematical assumption. You are not allowed to impose it globally unless you first prove a symmetry theorem.

Is there any plausible route to termination?

Not with the present representation and pruning family.

A crude uniform division into only 16 intervals per coordinate already gives

16
19
=
2
76
≈
7.56
×
10
22
16
19
=2
76
≈7.56×10
22

cells. At 64 intervals per coordinate it is

64
19
=
2
114
≈
2.08
×
10
34
.
64
19
=2
114
≈2.08×10
34
.

These are not rigorous lower bounds for an adaptive tree. They are scale indicators. Given that breadth-first search discards nothing through depth 9 and depth-first search creates slivers hundreds of levels deep, any planning estimate below 
10
20
10
20
 boxes is fantasy. The first honest planning range for the present method is roughly 
10
23
10
23
–
10
35
10
35
 terminal boxes, before accounting for equality neighborhoods.

[VERIFY: this box-count range is a complexity extrapolation, not a theorem. Test it by running breadth-frontier profiles at 10,000, 100,000, and 1,000,000 nodes and measuring survival as a function of balanced coordinate diameter.]

A thousandfold improvement changes nothing. A millionfold improvement roughly compensates for one extra refinement bit in every coordinate. You need fourteen to twenty-five orders of magnitude, not a faster determinant routine.

There are only two plausible ways back to n=12:

Prove a structural theorem reducing every hypothetical near-record configuration to finitely many combinatorial types with at most about six to eight genuine continuous parameters.

Produce a global algebraic certificate—an exact Positivstellensatz, sparse SOS certificate, resultant decomposition, or equivalent—that excludes whole sign/order cells rather than metric boxes.

Ordinary symmetry breaking, more shifted grids, better split scores, and stronger single-triangle interval bounds will not change enough orders of magnitude.

There is also an equality problem. A strict upper-bound proof must eliminate configurations with every area greater than 
𝑧
0
z
0
	​

, while retaining the incumbent at equality. Boxes around the incumbent will refine forever unless the local tangent-cone result is converted into an explicit terminal certificate: a certified radius in which every nonincumbent configuration has a triangle below 
𝑧
0
z
0
	​

. The current local theorem may contain the ingredients, but an existential local-isolation statement is not yet a terminal rule.

Final verdict: salvage the exact local and symmetric results into a paper. Kill the unrestricted 19-dimensional cover. Resume it only after a theorem removes at least ten effective degrees of freedom or replaces boxes by whole-cell algebraic certificates.

2. CONDITIONALITY AUDIT

The five-boundary reduction is not nonsense. Using it as a black box is unacceptable.

Sudermann-Merx proves that the square is a minimum-area parallelogram containing the convex hull of an optimizer and then invokes Lemma 2 of Zeng and Chen to conclude that, for 
𝑛
≥
5
n≥5, at least five distinct hull vertices lie on the square boundary. The same paper then assigns two selected vertices to the left edge, one to each other edge, and orders the remaining points by x-coordinate. 
arXiv
+1

The load-bearing older reference is Z. Zeng and L. Chen, “On the Heilbronn Optimal Configuration of Seven Points in the Square,” in Automated Deduction in Geometry, LNCS 6301, Springer, 2011, pp. 196–224. 
Springer Nature Link

What exactly must be proved

First, existence and positivity. The optimum must be attained, and its value must be positive. Positivity rules out coincident points and collinear triples. Compactness gives existence. This part is straightforward and already written correctly in the 2026 paper. 
arXiv

Second, the given square—not merely some parallelogram—must be a minimum-area covering parallelogram of the optimizer’s hull. The affine expansion argument establishes this: a smaller enclosing parallelogram could be mapped onto the unit square, strictly increasing every triangle area.

Third, the complete contact classification must be true. The quoted classification has three cases: no common vertices, one common vertex, or two diagonally opposite common vertices. Before trusting it, the repo must explicitly handle or exclude:

two adjacent common vertices;
three or four common vertices;
the case in which the hull itself is a parallelogram or equals the square;
nonunique minimum-area covering parallelograms;
contacts occurring at corners rather than in relative edge interiors;
contacts along an entire hull edge.

Do not write “these cases cannot occur” without proof. This is precisely where classical minimum-enclosing-polygon lemmas acquire hidden genericity assumptions.

Fourth, five contacts must yield five distinct point roles. “At least five boundary vertices” does not automatically imply that one can choose distinct labels

𝑝
1
,
𝑝
5
∈
left
,
𝑝
2
∈
bottom
,
𝑝
3
∈
right
,
𝑝
4
∈
top
.
p
1
	​

,p
5
	​

∈left,p
2
	​

∈bottom,p
3
	​

∈right,p
4
	​

∈top.

Corners belong to two edges. A single corner cannot silently fill two labelled roles. Prove the required matching between boundary vertices and edge roles, either directly by cases or through Hall’s condition. Also prove that the chosen five occur in the claimed cyclic order.

Fifth, the symmetry-breaking statement must include ties. The correct theorem should assert the existence of a D4 image and a relabeling satisfying something of the form

𝑥
1
=
𝑥
5
=
0
,
𝑦
2
=
0
,
𝑥
3
=
1
,
𝑦
4
=
1
,
x
1
	​

=x
5
	​

=0,y
2
	​

=0,x
3
	​

=1,y
4
	​

=1,

with 
𝑝
1
,
…
,
𝑝
5
p
1
	​

,…,p
5
	​

 distinct hull vertices in cyclic order,

𝑦
1
≤
𝑦
5
,
𝑥
2
≤
𝑥
4
,
𝑥
6
≤
𝑥
7
≤
⋯
≤
𝑥
12
.
y
1
	​

≤y
5
	​

,x
2
	​

≤x
4
	​

,x
6
	​

≤x
7
	​

≤⋯≤x
12
	​

.

The inequalities ordering free points must be non-strict. Equal x-coordinates occur in real extremal configurations. A strict ordering loses solutions.

Sixth, “at least five boundary points” must not become “exactly five.” Points 
𝑝
6
,
…
,
𝑝
12
p
6
	​

,…,p
12
	​

 must remain allowed on the boundary. Any code path that declares them interior has strengthened the theorem without justification.

Seventh, sign fixing must follow from the proved cyclic order. It is not enough that five points lie somewhere on the boundary. The fixed signs for their determinants require a specific counterclockwise labeling and distinctness. Corner cases must be included.

Eighth, the quantifier logic must be correct. The normal form is a theorem about an optimizer, not an arbitrary configuration whose triangles exceed the record. The valid contradiction is:

Assume 
Δ
12
>
𝑧
0
Δ
12
	​

>z
0
	​

. By compactness, choose an optimizer 
𝑃
∗
P
∗
. Apply the normal-form theorem to 
𝑃
∗
P
∗
. The completed cover excludes its normalized representative. Contradiction.

The invalid shortcut is:

Take an arbitrary counterexample and apply an arbitrary affine normalization.

An arbitrary affine map does not preserve the unit square and need not preserve the target normalization.

What usually goes wrong

The standard failures are exactly the dangerous ones here:

replacing an existence statement about one optimal representative by a statement about every optimizer or every near-optimizer;
counting edge contacts rather than distinct points;
double-counting corners;
silently assuming generic contacts;
dropping configurations with coordinate ties;
fixing determinant signs before proving cyclic order;
forcing all unselected points into the interior;
confusing 
>
 ⁣
𝑧
0
>z
0
	​

 with 
≥
𝑧
0
≥z
0
	​

;
mishandling points lying exactly on strip or grid boundaries;
assuming that a symmetry which preserves the objective also preserves a chosen normal form without relabeling.
What I would demand inside the repo

I would demand a self-contained “Five-contact normal-form theorem” of three to five pages. It must re-prove the minimum-parallelogram argument, the entire contact classification, the distinct-role assignment, the D4 canonicalization, the tie cases, and the determinant signs.

The 2026 paper itself says that the boundary argument is essentially due to Amirali Modir, communicated using Zeng–Chen’s lemma. That makes independent reconstruction more necessary, not less. 
arXiv

I would also demand:

a diagram for every contact case;
an explicit treatment of all corner-sharing possibilities;
a machine-checkable but human-readable canonicalization routine;
a proof that every search constraint follows from the theorem;
a standalone verifier that checks a final cover without trusting the search program;
exact endpoint conventions for every partition and matching constraint.

Tests are supplementary evidence. Tests are not a proof of the normal-form theorem.

Without this material, even an empty queue would establish only a conditional computational statement. It would not establish 
Δ
12
≤
𝑧
0
Δ
12
	​

≤z
0
	​

.

3. WHAT WOULD I DO INSTEAD?

First, correct the asymptotic literature. The prompt’s 
8
/
7
8/7-era benchmark is stale. Cohen, Pohoata, and Zakharov now prove

Δ
𝑛
≤
𝑛
−
7
/
6
+
𝑜
(
1
)
.
Δ
n
	​

≤n
−7/6+o(1)
.

The precise reference is A. Cohen, C. Pohoata, and D. Zakharov, “Lower bounds for incidences,” Inventiones Mathematicae 240 (2025), 1045–1118. The paper uses incidence geometry, projection theory, Frostman-type regularity, and a high-low argument—not a finite-dimensional SDP. 
Springer Nature Link

1. Close the exact n=8 unit-triangle problem

Mathematical target. Prove that the exact optimum is the specified real root of the septic, construct the optimizer in its number field, verify all 56 triangle inequalities exactly, prove that the eleven claimed critical triangles are simultaneously minimal, and give an exact global upper certificate.

Why this is valuable. This is a clean, currently open exact statement. Sudermann-Merx has numerically certified global optimality for the unit right triangle through n=8 and reconstructed the septic root to 250 digits, but explicitly states that the exact n=8 identification remains “narrow but real.” Exact values are known only through n=7. This problem is almost perfectly matched to your algebraic-number and exact interval machinery. 
arXiv

First two weeks.

Week 1: isolate the relevant septic root exactly; reconstruct every coordinate in 
𝑄
(
𝛼
)
Q(α); saturate the equal-area ideal to remove spurious components; isolate every real solution branch; verify all 56 signed areas in the correct order.

Week 2: import the published 
1
/
32
1/32-scale localization, replace the numerical solver certificate by an exact Bernstein/CAD/interval cover, and write a tiny independent verifier.

Kill criterion. Kill this route if the localized exact cover still requires more than roughly 
10
7
10
7
 boxes, or if saturation leaves a large positive-dimensional component that cannot be separated from the candidate branch. Do not spend months rebuilding the global MIQCP.

2. Turn the n=12 material into a restricted rigidity paper

Mathematical target. Prove a coherent package:

the Comellas–Yebra configuration is the unique maximizer in the complete C4 three-orbit family, modulo D4 and relabeling;
the exact D4-family theorem;
no simultaneous movement of at most three labelled points improves it;
the incumbent is locally isolated among all configurations;
preferably, an explicit sharpness estimate
min
⁡
𝑇
𝐴
𝑇
(
𝑃
)
≤
𝑧
0
−
𝑐
 
dist
⁡
(
𝑃
,
𝐷
4
𝑃
∗
)
T
min
	​

A
T
	​

(P)≤z
0
	​

−cdist(P,D
4
	​

P
∗
)
in a certified neighborhood.

Why this is valuable. This converts scattered computational negatives into a structural theorem about the record configuration. Anyone attacking n=12 later will cite the symmetric-family classification and local rigidity. The paper will not solve n=12, but it will say something precise and nontrivial about why the incumbent is hard to perturb.

First two weeks.

Week 1: freeze all general engine work. Decompose the residual C4 domain into exact order/sign cells. Use resultants or regular chains near the incumbent and Bernstein bounds away from it. Extract a minimal active-triangle subsystem proving local isolation.

Week 2: empty the C4 queue, classify all equality branches, produce an explicit local radius, and reduce the certificate to a standalone manifest with an independent checker.

Kill criterion. If exact sign-cell decomposition does not reduce the near-record remainder to finitely many algebraic neighborhoods within two weeks, stop at the D4 theorem plus local rigidity. Do not respond by adding another generic interval heuristic.

3. Attempt n=10 global optimality—with a brutal feasibility gate

Mathematical target. Prove that the Comellas–Yebra n=10 configuration is globally optimal and classify all equality configurations modulo D4 and relabeling.

Why this is valuable. This is the first unresolved square case after n=9. A proof would be the most important small-n Heilbronn result currently within conceivable computational reach. The 2026 square paper says n=10 “appears within reach,” but Monji–Modir–Kocuk’s best n=10 run used two unproved structural assumptions and still failed to produce a matching upper bound. That is the actual state of play. 
arXiv
+1

The normal form leaves 15 rather than 19 free coordinates, and there are 120 rather than 220 triangles. That is still difficult, but it is not the absurdity of n=12.

First two weeks.

Week 1: reconstruct the incumbent’s active hypergraph, tangent cone, and explicit local neighborhood. Port every exact prune to the 15-dimensional model. Enumerate numerical near-optimal sign and occupancy patterns.

Week 2: demand an exact completed cover at a deliberately easier threshold, for example incumbent plus 
10
−
4
10
−4
. Measure balanced-frontier growth, not depth-first anecdotes.

Kill criterion. Stop the exact global cover if it cannot eliminate “incumbent plus 
10
−
4
10
−4
” in fewer than 
10
7
10
7
 nodes, or if the extrapolated equality-level cover remains above 
10
9
10
9
–
10
10
10
10
 terminal certificates. Do not reinterpret partial progress as evidence that another six months will work.

4. Attack n=11 through a structural counting theorem, not 17-dimensional boxes

Mathematical target. Prove 
Δ
11
=
1
/
27
Δ
11
	​

=1/27, or prove that every hypothetical configuration with minimum area greater than 
1
/
27
1/27 belongs to a finite collection of occupancy/order types, each with at most six to eight continuous parameters.

Why this is valuable. Goldberg’s rational 
1
/
27
1/27 construction remains the listed record. A proof would be a major small-n result. Its layered rational structure makes a capacity or matching argument more plausible than for n=12. 
Emis
+1

First two weeks.

Week 1: build an exact finite occupancy model using horizontal, vertical, shifted, and selected oblique strips at target 
1
/
27
1/27. Solve the resulting packing/dual LP and SAT problems. Extract rational dual certificates rather than relying on solver output.

Week 2: determine whether the constraints force the Goldberg row pattern or a short list of alternatives. For each surviving pattern, calculate its remaining geometric dimension and attempt symbolic elimination.

Kill criterion. Kill the route if the capacity model leaves more than roughly 
10
4
10
4
 qualitatively different occupancy types or fails to reduce the continuous dimension below about eight. Under no circumstances replace this failed structural attack with a 17-dimensional copy of the n=12 tree.

5. Produce exact, independently checkable classifications for small square cases

Mathematical target. Enumerate every optimizer modulo 
𝐷
4
×
𝑆
𝑛
D
4
	​

×S
n
	​

 for n=7 and n=8, including all equality components, and provide an exact cover and a tiny verifier that does not trust Gurobi, floating-point tolerances, or numerical reconstruction.

Why this is valuable. Current work gives global certification and exact coordinates through n=9, including a one-parameter n=6 family and asserted uniqueness for n=8 and n=9. Merely recomputing the same numbers adds nothing. A truly exact all-orbits classification with a compact proof object would be useful both mathematically and as a standard for computer-assisted geometry. 
arXiv
+1

First two weeks.

Week 1: run the exact normal-form cover for n=7 or n=8; canonicalize all D4 and label orbits; separately track boxes that can contain equality.

Week 2: identify every equality component algebraically, prove completeness, and make a second implementation verify the certificate.

Kill criterion. Kill it if the deliverable is merely another optimizer coordinate list or another solver transcript. The result must classify all optimizers or establish a reusable exact certificate standard.

Moves that should not become the main program

n=13 record search: acceptable as a two-week lottery. Search heuristically, and exactly certify any construction beating the listed approximately 0.02702 record by a robust margin. Stop immediately if there is no improvement. Do not attempt a 21-dimensional global proof. 
Erich Friedman

Arbitrary convex-domain variants: this is a dead end and here is why. An arbitrary convex domain introduces an infinite-dimensional shape variable and destroys the square’s boundary normal form. Work on a fixed affine class—triangles, parallelograms—or a tightly parametrized one-dimensional family. The exact unit-triangle n=8 gap is vastly better.

The asymptotic Roth/CPZ direction: extraordinarily valuable mathematics, but it is not a continuation of this codebase. It requires becoming an incidence geometer: projection estimates, multiscale regularity, high-low decompositions, and Szemerédi–Trotter barriers. Generic SDP experiments will not improve the 
7
/
6
7/6 exponent. Unless there is a serious collaborator in incidence geometry, this is not an available project; it is a field change.

Finite-n SDP/SOS: useful only as a component of the n=10 or n=11 attacks. Run degree-4 and degree-6 pilots. If the bound remains more than roughly 10% above the incumbent, kill it. Do not build a hierarchy because hierarchies are fashionable.

4. THE HARSH QUESTION

“Stop trying to prove n=12 with a 19-dimensional box cover. It is a dead end, and your own measurements already say so. You have enough material for a respectable restricted-rigidity paper: finish the C4 theorem or cut it, write the local-isolation theorem properly, and move to the exact n=8 unit-triangle gap or to n=10. Return to global n=12 only after you prove a structural theorem that removes at least ten continuous degrees of freedom. Until then, ‘keeping going’ is not persistence. It is sunk-cost behavior with exact fractions.”

5. NEW AVENUES

Finite D4 quotienting is not a new avenue. Another grid is not a new avenue. The following are actual mathematical levers.

5.1 Active-triangle hypergraph rigidity and quantitative stability

Treat the 20 active triangles as an area-tensegrity hypergraph.

For each active triangle 
𝑒
e, fix its orientation near the incumbent and write

𝑔
𝑒
(
𝑥
)
=
𝑠
𝑒
𝐷
𝑒
(
𝑥
)
−
2
𝑧
0
,
g
e
	​

(x)=s
e
	​

D
e
	​

(x)−2z
0
	​

,

where 
𝐷
𝑒
D
e
	​

 is the signed determinant. Form the exact rigidity matrix whose rows are 
∇
𝑔
𝑒
(
𝑥
∗
)
∇g
e
	​

(x
∗
), together with active boundary normals.

What must be proved first.

Find a minimal subhypergraph 
𝐻
0
H
0
	​

 for which the tangent cone

{
𝑣
:
∇
𝑔
𝑒
(
𝑥
∗
)
⋅
𝑣
≥
0
 for all 
𝑒
∈
𝐻
0
}
{v:∇g
e
	​

(x
∗
)⋅v≥0 for all e∈H
0
	​

}

is zero after the normal-form constraints. Produce a strictly positive dual stress—a conic combination of the active gradients and boundary normals summing to zero—with an exact separation margin.

Then upgrade this to an explicit nonlinear error bound. Because the determinant constraints have bounded Hessians, an exact first-order angular margin should yield a certified radius and constant 
𝑐
>
0
c>0 for local sharpness.

The global objective is stronger: prove that every configuration with minimum area at least 
𝑧
0
−
𝜀
z
0
	​

−ε has a set of near-active triangles containing a copy of 
𝐻
0
H
0
	​

. That would force every near-record configuration into a small neighborhood of the incumbent.

The importance of critical-triangle structure is already recognized in the current square literature, which explicitly asks for structural bounds on the number of critical triangles. 
arXiv

Two-week teeth test.

Compute exact ranks and positive stresses for the full active set and every orbit-deleted subsystem. Search for the smallest rigid core. In parallel, generate hundreds of independently optimized configurations at thresholds 
𝑧
0
−
10
−
4
z
0
	​

−10
−4
, 
𝑧
0
−
10
−
5
z
0
	​

−10
−5
, and 
𝑧
0
−
10
−
6
z
0
	​

−10
−6
, quotient them by D4, and compare their near-active hypergraphs.

This avenue has teeth if a small rigid core recurs in every near-record sample and has a large exact dual margin. It is dead if near-record configurations exhibit many unrelated flexible hypergraphs.

Why it changes complexity. It replaces a 19-dimensional metric cover by a finite search over candidate hypergraphs plus certified local neighborhoods.

5.2 Work in signed-area coordinates and exploit Grassmann–Plücker relations

The 220 signed double areas are not independent. If

𝐷
𝑖
𝑗
𝑘
=
det
⁡
(
1
	
𝑥
𝑖
	
𝑦
𝑖


1
	
𝑥
𝑗
	
𝑦
𝑗


1
	
𝑥
𝑘
	
𝑦
𝑘
)
,
D
ijk
	​

=det
	​

1
1
1
	​

x
i
	​

x
j
	​

x
k
	​

	​

y
i
	​

y
j
	​

y
k
	​

	​

	​

,

then every four labels satisfy the exact linear identity

𝐷
𝑗
𝑘
𝑙
−
𝐷
𝑖
𝑘
𝑙
+
𝐷
𝑖
𝑗
𝑙
−
𝐷
𝑖
𝑗
𝑘
=
0.
D
jkl
	​

−D
ikl
	​

+D
ijl
	​

−D
ijk
	​

=0.

The full collection also satisfies quadratic Grassmann–Plücker relations. The coordinate branch-and-bound currently ignores almost all of this global algebraic coupling.

Fixing an order type fixes the signs of the 
𝐷
𝑖
𝑗
𝑘
D
ijk
	​

. The counterexample condition then becomes a collection of linear lower bounds

𝑠
𝑖
𝑗
𝑘
𝐷
𝑖
𝑗
𝑘
>
2
𝑧
0
s
ijk
	​

D
ijk
	​

>2z
0
	​


together with linear four-point identities, Plücker quadrics, boundary normalizations, and realizability constraints.

What must be proved first.

Determine whether the strip, boundary, and order constraints force a manageable set of partial chirotopes near the record. Derive the exact area-coordinate constraints implied by the five-boundary normal form. Establish which subset of Plücker relations is sufficient to recover or tightly relax realizability.

Two-week teeth test.

Take the incumbent order type and the handful of order types produced by near-record numerical searches. Solve an exact LP using the four-point identities and area bounds. Then add a low-level sparse SDP for selected Plücker quadrics.

This has teeth if the LP or degree-2/4 relaxation gives an upper bound within about 
10
−
3
10
−3
 in triangle area and yields a sparse rational dual certificate. It is dead if the relaxation still permits determinants near their trivial maximum or if the near-record order-type count explodes.

Why it changes complexity. A successful dual certificate excludes an entire order-type cell at once. There is no coordinate resolution parameter and no microscopic box refinement.

5.3 Convert capacity constraints into a global finite counting theorem

The current strip and rectangle constraints are being used one box at a time. That wastes their mathematical content.

For a strict counterexample at target 
𝑧
0
z
0
	​

, every region whose maximal inscribed triangle has area at most 
𝑧
0
z
0
	​

 has point capacity two. The goal is to choose several shifted and oblique partitions whose simultaneous capacity constraints either:

prove that at most eleven points can be placed; or
force a short list of twelve-point occupancy templates, ideally the incumbent template.

A naive fractional cover by tiny rectangles is a dead end: area alone forces too much total covering weight. The leverage must come from overlapping partitions, pair-dependent forbidden strips, or matching constraints across several directions.

A particularly promising formulation is pair-based. Every pair 
𝑝
𝑖
,
𝑝
𝑗
p
i
	​

,p
j
	​

 creates an exclusion strip around its line: all other points must remain farther than

2
𝑧
0
∥
𝑝
𝑖
−
𝑝
𝑗
∥
∥p
i
	​

−p
j
	​

∥
2z
0
	​

	​


in perpendicular distance. Sum or dualize these pair-exclusion conditions over several direction classes.

What must be proved first.

Prove a finite combinatorial lemma saying that every twelve-point placement satisfying selected capacity constraints has one of finitely many occupancy codes. The partitions must have exact boundary ownership, so points on cell boundaries cannot evade or duplicate constraints.

Two-week teeth test.

Generate candidate rational partitions and solve the resulting exact occupancy ILP and its dual. Inspect the dual, not just the primal optimum. Search for a small rational combination of capacity inequalities that proves 
𝑛
≤
11
n≤11 or forces fewer than roughly ten occupancy templates.

This avenue has teeth if the dual almost proves the desired count or forces the incumbent’s two-points-per-edge plus central-four pattern. It is dead if thousands of unconstrained templates survive after adding several directions.

Why it changes complexity. A global dual counting certificate prunes the continuum without subdividing coordinates. Even a theorem reducing the search to ten occupancy templates would be worth more than every anchor trim currently in the branch.

The correct n=12 program is therefore: hypergraph rigidity, area-coordinate algebra, and global capacity duality. Until one of those produces a theorem-level reduction, the unrestricted box cover stays dead.
