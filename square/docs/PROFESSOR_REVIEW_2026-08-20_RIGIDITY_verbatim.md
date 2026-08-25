ChatGPT said:
1. THEOREM AUDIT

Bottom line: this is now potentially a real theorem, not computational theater. But the theorem is only as good as the exact definition of the linearized feasibility problem. The main danger is not the computation; it is that the word "rigid" is silently proving something weaker than the geometric statement you want.

The scoped statement I would accept is something like:

For every subset 
𝐻
H of the 20 incumbent-active triangles with 
∣
𝐻
∣
≥
16
∣H∣≥16, the first-order feasible cone at the Comellas–Yebra configuration has trivial objective-improving directions if and only if 
𝐻
H contains one of three 
𝐷
4
D
4
	​

-classes of inclusion-minimal rigid cores; the minimum cardinality of such a core is 17.

That is a legitimate mathematical object. It is not yet a Heilbronn theorem. It is a theorem about the first-order active constraint system.

A referee will demand the following.

(a) The derivative framework must be nailed down

The triangle area constraint is

𝐴
𝑖
𝑗
𝑘
(
𝑥
)
=
1
2
∣
det
⁡
(
𝑝
𝑗
−
𝑝
𝑖
,
𝑝
𝑘
−
𝑝
𝑖
)
∣
.
A
ijk
	​

(x)=
2
1
	​

∣det(p
j
	​

−p
i
	​

,p
k
	​

−p
i
	​

)∣.

At a nondegenerate incumbent triangle,

det
⁡
(
𝑝
𝑗
−
𝑝
𝑖
,
𝑝
𝑘
−
𝑝
𝑖
)
≠
0
,
det(p
j
	​

−p
i
	​

,p
k
	​

−p
i
	​

)

=0,

so the absolute value is locally removable:

𝐴
𝑖
𝑗
𝑘
(
𝑥
)
=
±
1
2
det
⁡
(
𝑝
𝑗
−
𝑝
𝑖
,
𝑝
𝑘
−
𝑝
𝑖
)
A
ijk
	​

(x)=±
2
1
	​

det(p
j
	​

−p
i
	​

,p
k
	​

−p
i
	​

)

in a neighborhood preserving orientation.

Therefore the unsigned-area derivative is legitimate only because every active triangle is orientation-stable in the neighborhood considered.

The paper must explicitly state:

all active triangles have nonzero signed determinant;
the chosen orientation signs are frozen;
the radius of the neighborhood used later preserves those signs.

If a reviewer finds that the later "isolation radius" crosses an orientation-flip hypersurface, the entire second-order argument collapses.

This is a standard issue in rigidity theory: the infinitesimal rigidity matrix is meaningful only after the constraint manifold branch has been fixed. Compare the philosophy in:

Connelly, "Rigidity and energy", Invent. Math. 66 (1982), 11–33.
Asimow and Roth, "The rigidity of graphs", Trans. AMS 245 (1978), 279–289.
(b) The boundary cone model is the first serious referee attack

You say:

inward boundary normals only.

This is correct if and only if the only active geometric constraints at the incumbent are those boundary halfspaces.

The tangent cone of the feasible configuration space is not automatically:

𝑛
𝑖
⋅
𝑣
≤
0.
n
i
	​

⋅v≤0.

It is:

𝑇
𝐹
(
𝑥
)
=
{
𝑣
:
∇
𝑔
𝑗
(
𝑥
)
⋅
𝑣
≥
0
 for every active inequality 
𝑔
𝑗
}
.
T
F
	​

(x)={v:∇g
j
	​

(x)⋅v≥0 for every active inequality g
j
	​

}.

So the paper must list all non-area constraints:

box constraints,
symmetry normalization constraints,
any fixed-coordinate gauge conditions,
any quotienting by translations/rotations.

If you silently removed degrees of freedom by normalization, the boundary normals and the rank count change.

The statement:

"strictly negative on the 8 inward boundary normals"

is meaningful only after proving that those eight normals generate the entire active boundary cone.

This is the place where I would attack first.

(c) Independence from the five-boundary normal form

You specifically asked about this.

The theorem should not depend on the five-boundary normal form.

If the minimal-core result is true only after choosing a special coordinate representation of the incumbent, it is not intrinsic.

A referee will ask:

Is the five-boundary representation merely a coordinate gauge?
Does every 
𝐷
4
D
4
	​

-equivalent realization produce the same cone?
Are the normal vectors transformed correctly under symmetry?

The theorem should be stated invariantly:

configuration 
𝑋
0
X
0
	​

, quotient by Euclidean symmetries, active constraint gradients.

The normal form belongs in the proof, not the theorem.

(d) D4 classification completeness

This is a real theorem obligation.

"Three D4 classes" requires:

enumerate all 6196 subsets;
define the D4 action;
prove every minimal rigid subset maps into one representative;
prove representatives are inequivalent.

A table is not enough.

The referee will demand either:

canonical labeling algorithm with exact output, or
a Burnside/orbit argument.

The good news: this is probably the least dangerous part.

The gaps that would sink the theorem

Fatal:

Boundary cone incomplete.
You proved rigidity in a smaller cone than the actual feasible cone.

Orientation branch not certified.
Your derivatives may describe the wrong local branch.

Stress certificate not equivalent to objective obstruction.
The Stiemke/Farkas alternative must be written carefully.

Rank statement ambiguity.
"rank 16" of what matrix? After quotienting what motions?

Any one of these is a publication-killer.

If those are clean, the minimal-core theorem is a respectable computational rigidity result.

2. VERDICT AUDIT

Your word "TEETH" needs discipline.

Current evidence:

random global search: zero hits;
local basin perturbations: extreme recurrence;
every near-record point sampled activates the same hypergraph.

This is interesting.

But:

"TEETH" does not mean "global rigidity."

The correct statement is:

"The active-triangle rigidity mechanism has confirmed local obstruction power and deserves continuation."

Not:

"The problem has a unique basin."

Sampling cannot establish that.

The blind DE experiment is actually valuable because it killed one possibility:

easy remote optima.

But it says nothing about:

thin basins,
disconnected components,
highly anisotropic escape routes,
non-Gaussian neighborhoods.

Before "teeth" appears in a paper, I would demand one of:

Strong version

A theorem:

There exists 
𝜖
>
0
ϵ>0 such that every configuration within 
𝜖
ϵ of the orbit has a certified active-core obstruction.

Medium version

A complete local rigidity theorem:

The incumbent is an isolated local maximizer modulo symmetry.

Weak version

Call it:

"evidence for a rigidity mechanism."

The word "teeth" is acceptable only in the title if qualified:

"Local rigidity teeth."

Not:

"The rigidity solution."

3. CERTIFIED RADIUS

The clean route is not a pure Hessian argument.

The strongest route is:

Step 1: Convert the stress certificate into a scalar barrier

Let

𝐿
(
𝑥
)
=
∑
𝑖
𝑤
𝑖
𝐴
𝑖
(
𝑥
)
L(x)=
i
∑
	​

w
i
	​

A
i
	​

(x)

where the stress weights satisfy the equilibrium conditions.

At 
𝑥
0
x
0
	​

,

∇
𝐿
(
𝑥
0
)
=
boundary penalty direction
.
∇L(x
0
	​

)=boundary penalty direction.

You have:

∇
𝐿
(
𝑥
0
)
𝑣
≤
−
𝛾
∥
𝑣
∥
∇L(x
0
	​

)v≤−γ∥v∥

on feasible directions.

The margin 
𝛾
=
0.0363
γ=0.0363 is your first-order sharpness.

Step 2: Control nonlinear error

You need:

∣
𝐿
(
𝑥
)
−
𝐿
(
𝑥
0
)
−
∇
𝐿
(
𝑥
0
)
(
𝑥
−
𝑥
0
)
∣
≤
𝑀
2
∥
𝑥
−
𝑥
0
∥
2
.
∣L(x)−L(x
0
	​

)−∇L(x
0
	​

)(x−x
0
	​

)∣≤
2
M
	​

∥x−x
0
	​

∥
2
.

Then:

𝐿
(
𝑥
)
−
𝐿
(
𝑥
0
)
≤
−
𝛾
𝑟
+
𝑀
2
𝑟
2
.
L(x)−L(x
0
	​

)≤−γr+
2
M
	​

r
2
.

Therefore choose

𝑟
<
2
𝛾
𝑀
.
r<
M
2γ
	​

.

This is the isolation radius.

This is much cleaner than invoking generic Hoffman bounds.

Step 3: Handle quotient distance

Your distance must be:

𝑑
(
𝑥
,
𝐷
4
𝑋
0
)
d(x,D
4
	​

X
0
	​

)

not:

𝑑
(
𝑥
,
𝑋
0
)
.
d(x,X
0
	​

).

Otherwise symmetry copies become false counterexamples.

Standard traps
Trap 1: Degenerate directions

The stress kills first-order motion.

It does not automatically kill:

second-order flexes,
symmetry directions,
inactive constraints.

You need the full tangent cone analysis.

Trap 2: Boundary corners

Your feasible set is polyhedral locally.

The worst direction may live on a cone face.

A Hessian bound over the full box is safer than trying to diagonalize.

Trap 3: Tiny radius

Your margin:

𝛾
=
0.0363
γ=0.0363

is actually not bad.

The problem is 
𝑀
M.

For triangle area determinants, second derivatives are constant-scale because the determinant is quadratic.

So 
𝑀
M should be computable exactly.

My expectation:

radius 
10
−
2
10
−2
: plausible;
radius 
10
−
3
10
−3
: almost certainly;
radius 
10
−
5
10
−5
: technically possible but not interesting.

A published constant should probably not be:

𝑐
=
10
−
8
.
c=10
−8
.

That proves something but communicates nothing.

4. PAPER SHAPE

The strongest honest paper is not a Heilbronn solution paper.

It is:

Possible title

"Local Rigidity and Minimal Active Constraint Cores in the 12-Point Heilbronn Triangle Problem"

or

"Certified Active-Set Rigidity in an Extremal Triangle Packing Problem"

Structure
1. Introduction

Kill the overclaim immediately.

State:

no global optimality claim;
discovery of local rigidity mechanism.
2. The Comellas–Yebra configuration

Exact algebraic description.

3. Active triangle hypergraph

Define:

active set;
constraint gradients;
symmetry action.
4. Minimal-core theorem

Main theorem.

This is the contribution.

5. Certification methodology

Explain:

exact field arithmetic;
Stiemke alternatives;
rank certificates.
6. Local isolation theorem

If completed.

7. Computational exploration

Sampling only as motivation.

Not evidence.

8. Discussion

Relation to Heilbronn search.

Cut

The C4 Bernstein family bracket.

I would cut it.

Reason:

You are trying to publish one sharp idea.

The Bernstein/C4 story is a second paper.

Right now it weakens the narrative.

Venue

If only minimal-core:

Experimental Mathematics
Journal of Computational Geometry
SIAM Journal on Discrete Mathematics (possible)

If local isolation theorem is complete:

Advances in Computational Mathematics
Discrete & Computational Geometry

Not Inventiones.
Not JAMS.

The mathematical contribution is interesting but specialized.

Likely referee objections
"This proves only local structure, not the Heilbronn bound."

Answer:
Correct; say so.

"Why should this local maximum matter globally?"

Answer:
It does not; this is a rigidity result.

"Computer-assisted proof dependence."

Answer:
Exact certificates solve this.

5. WHAT IS MISSING

Ranking by value/week.

Rank 1 — Prove uniqueness of the size-17 stress

Highest ROI.

Question:

Is the stress cone one-dimensional?

If yes, you gain:

conceptual explanation;
robustness;
easier isolation theorem.

Cheap:

Compute exact nullspace dimension.

This should be done immediately.

Rank 2 — Complete second-order local isolation

Highest publication impact.

The paper changes from:

"interesting combinatorics"

to:

"certified isolated local extremum."

Rank 3 — Core intersection/hitting structure

You have three minimal cores.

Compute:

⋂
𝐶
𝑖
⋂C
i
	​


and the transversal number.

Questions:

Are all three forced by a smaller hidden motif?
Is there a 3–5 triangle "seed" generating rigidity?

This could produce the theoretical explanation missing today.

Rank 4 — Stress evolution under removing triangles

You know:

17 necessary.

Study:

For each triangle removed:

which rank fails?
which flex appears?
what geometric motion?

A single diagram showing the emerging flex would be more valuable than 100 pages of certificates.

Rank 5 — Finish C4 Bernstein bracket

Last.

Do it only after the rigidity paper.

Final referee verdict

The project has crossed the line from "numerical archaeology" into "a legitimate computational rigidity result."

But do not make the classic mistake now.

The theorem is:

"The Comellas–Yebra incumbent has a minimal 17-triangle first-order rigid core."

It is not:

"The Comellas–Yebra configuration is globally optimal."

The next two weeks should not be spent searching harder.

They should be spent proving:

the tangent cone is the correct one;
the stress is unique;
the local isolation radius is explicit.

If those three land, this becomes a publishable paper.

If they do not, the minimal-core computation remains an attractive but ultimately descriptive artifact.