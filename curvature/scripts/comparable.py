#!/usr/bin/env python3
"""Fingerprinted values: a comparison asserts the configurations match except on the declared axis.

WHY THIS EXISTS. In one evening the same error appeared FIVE times, on five different axes, and every
instance was invisible in a table that shows only ratios:

    1  A+dK margins / A-alone floor                 axis BASIS
    2  A+dK/floor_A vs B+dK/floor_B                 axis ENSEMBLE
    3  margins at 90/9000 / floor at 40/3000        axis RUN PARAMETERS   (caught by luck --
                                                       the wrong mode happened to be the SLOW one)
    4  margins at seed 0 / floor at seed 1          axis SEED
    5  min over 4 directions / min over all         axis READOUT

Four of the five were caught by a peer reading the work, not by any document -- including catalogue
entries written by their own author hours earlier describing the exact move. The axis list is OPEN
(integrator, precision, code version, chi/eps grid ...), so an enumeration cannot close it: an
enumeration and a class behave identically on every instance already seen. A fingerprint closes it
mechanically, because it asserts at the moment of COMPARISON without anyone remembering the class.

TRANSPORTABILITY (the positive half): a ratio taken WITHIN one configuration is self-normalising --
whatever the parameters were, they appear in numerator and denominator and cancel. Such a value is
transportable and is marked `within=True`. A value compared ACROSS configurations is not, unless the
axes match. This is why `f = a*chi + b` survived a relaunch that invalidated the absolute numbers it
was combined with.

TRANSPORTABILITY IS PER-AXIS, NOT GLOBAL. Measured, after this module was first written:

    the same statistic, same object, across EXPRESSION TREES (a 1-ulp perturbation)   33%
    the same statistic, same object, across EPS within ONE tree                        2.2%

The noise source is the ARGMIN over near-degenerate directions, and it reshuffles when the PROBLEM is
perturbed -- a different tree, a different ulp -- not when eps is varied inside one. So a ratio
cancels noise ALONG THE AXIS THE NOISE IS CONSTANT IN, and `within=True` is a claim about one axis
rather than about configurations in general. A ratio that is transportable along eps may be worthless
along tree.

AND THE STRONGEST FORM IS NOT A RATIO AT ALL: scoring a KNOWN direction instead of minimising over
the basis avoids the argmin entirely -- measured stable to 0.05% against the minimiser's 33%, a
factor of ~650. Where the candidate is known in advance, score it; the minimum answers "what is the
best-conserved thing in this basis", scoring answers "how conserved is THIS thing".
"""
from __future__ import annotations


class Mismatch(AssertionError):
    pass


class Value:
    """A number plus the configuration that produced it."""

    __slots__ = ("x", "cfg", "within", "label")

    def __init__(self, x, label="", within=False, **cfg):
        self.x, self.cfg, self.within, self.label = float(x), dict(cfg), bool(within), label

    def __repr__(self):
        return f"Value({self.x:.6g}, {self.label!r}, {'within' if self.within else 'cross'}, {self.cfg})"

    def ratio(self, other, axis=()):
        """self / other, asserting the fingerprints agree off the declared axis."""
        check(self, other, axis)
        return Value(self.x / other.x, f"{self.label}/{other.label}", within=True,
                     **{k: v for k, v in self.cfg.items() if k not in set(axis)})


def check(a: Value, b: Value, axis=()):
    """Raise unless a.cfg and b.cfg agree on every key outside `axis`."""
    declared = {axis} if isinstance(axis, str) else set(axis)
    keys = set(a.cfg) | set(b.cfg)
    bad = {k: (a.cfg.get(k, "<missing>"), b.cfg.get(k, "<missing>"))
           for k in keys - declared if a.cfg.get(k, "<missing>") != b.cfg.get(k, "<missing>")}
    if bad:
        raise Mismatch(
            f"cannot compare {a.label!r} with {b.label!r}: declared axis {sorted(declared)}, "
            f"but configurations differ on {sorted(bad)} -> "
            + "; ".join(f"{k}: {v[0]!r} vs {v[1]!r}" for k, v in sorted(bad.items())))
    return True
