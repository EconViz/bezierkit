# Geometry exporters and adapters

BezierKit exporters preserve cubic controls. They serialize geometry and do
not choose a color palette, theme, axis, label, canvas, or economic meaning.

## TikZ

`bezierkit.export.tikz.to_tikz` emits one `\draw` command per subpath and one
native `.. controls ... and ... ..` command per segment. Callers may pass an
explicit TikZ option string; no option is selected by default. Precision and a
2D point transform are configurable.

## SVG

`to_svg_path_data` emits only portable absolute `M`, `C`, and `Z` commands.
It does not emit an SVG document or styling. `from_svg_path_data` parses this
same deterministic subset for geometry round trips.

Rounding is the only exporter error. If coordinates are rounded to `p` decimal
places, each scalar control coordinate differs by at most `0.5 * 10^-p`.
Conformance tests use dense sampling with a tolerance derived from the chosen
precision; they never compare screenshots with environment-dependent fonts or
antialiasing.

## Matplotlib

Install the optional adapter with:

```bash
pip install "bezierkit[matplotlib]"
```

`from_path` preserves `MOVETO`, `LINETO`, `CURVE3`, `CURVE4`, and `CLOSEPOLY`.
Lines and quadratics are elevated exactly to cubic controls. Affine transforms
are exact because they apply directly to every control point.

A non-affine transform generally does not map a cubic to another cubic.
`from_path` therefore rejects it. Call `approximate_path` with an explicit
geometric tolerance to opt into adaptive sampling and approximation; that API
does not claim exactness.
