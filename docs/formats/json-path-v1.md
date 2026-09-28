# BezierKit JSON path schema, version 1

The JSON representation is a language-neutral geometry interchange format. It
contains no economic concepts, canvas layout, renderer theme, or drawing
style. Producers must emit finite JSON numbers; consumers must reject unknown
schema versions.

```json
{
  "schema": "bezierkit.path",
  "version": 1,
  "dimension": 2,
  "subpaths": [
    {
      "closed": false,
      "segments": [
        [
          [0.0, 0.0],
          [1.0, 2.0],
          [3.0, 2.0],
          [4.0, 0.0]
        ]
      ]
    }
  ],
  "metadata": {}
}
```

Each segment contains exactly four control points. Each point contains exactly
`dimension` coordinates. Subpath order, segment order, and the `closed` flag
are significant. Metadata must be a JSON object and is passed through without
interpretation by BezierKit.

Version 1 is strict: adding required fields, changing closure semantics, or
changing the control-point layout requires a new version. Readers may ignore
unknown metadata keys but must not silently accept an unknown `version`.
