# Evaluation benchmarks

Run the batch evaluator benchmark from the repository root:

```bash
uv run python benchmarks/benchmark_evaluation.py
```

It measures the median of seven warm-process evaluations at 400, 10,000, and
100,000 parameter values. The JSON output records the Python, platform, and
NumPy versions, the speedup over the v0.2 scalar reference, and the maximum
difference between vectorized de Casteljau and Bernstein evaluation. Both
public strategies operate on complete NumPy batches; neither loops over
parameter values in Python.

The checked-in `results/` sample records the release benchmark environment. On
that run, vectorized de Casteljau was 51–72 times faster than the v0.2 scalar
implementation, with a maximum Bernstein difference below `3e-15`.

`DeCasteljauEvaluator` remains the stable default. `BernsteinEvaluator` is an
explicit alternative for low-degree renderer workloads and agrees with de
Casteljau to approximately machine precision for the cubic benchmark curve.
