# Export Variations — Substance Painter Plugin

A Substance Painter plugin that automatically exports texture maps for every combination of tagged layer variations. Useful for products with multiple colorways, materials, or configurations that share a single Substance Painter project.

## How It Works

Tag layers using a naming convention, and the plugin will iterate through every combination — toggling visibility and exporting textures for each.

### Layer Naming Convention

| Tag | Meaning |
|---|---|
| `S{set}V{var}(value)` | Assigns the layer to a **set** and **variation variable** with a given value. `set` = 1–3, `var` = 1–3. |
| `FMT(template)` | Defines the output folder/file name template. Use `VAR1`, `VAR2`, `VAR3` as placeholders. |

### Example

Given these layers:

```
FMT(shirt_VAR1_VAR2)        ← name template (must be visible)
S1V1(red)   Base Color Red   ← set 1, variable 1, value "red"
S1V1(blue)  Base Color Blue  ← set 1, variable 1, value "blue"
S1V2(cotton) Roughness Cotton ← set 1, variable 2, value "cotton"
S1V2(silk)   Roughness Silk   ← set 1, variable 2, value "silk"
```

The plugin exports all combinations:

- `shirt_red_cotton/`
- `shirt_red_silk/`
- `shirt_blue_cotton/`
- `shirt_blue_silk/`

Each folder contains: `_baseColor.png`, `_normal.png`, `_ambientOcclusion.png`, `_roughness.png`, `_metallic.png`.

### Multiple Sets

You can define independent sets (`S1`, `S2`, `S3`) if different texture sets or groups of layers need separate variation loops. Each set is exported independently.

## Installation

1. Locate your Substance Painter plugins folder:
   - **Windows:** `%USERPROFILE%/Documents/Adobe/Adobe Substance 3D Painter/python/plugins/`
   - **macOS:** `~/Documents/Adobe/Adobe Substance 3D Painter/python/plugins/`
   - **Linux:** `~/.local/share/Adobe/Adobe Substance 3D Painter/python/plugins/`
2. Copy `export_variations.py` into that folder.
3. Restart Substance Painter (or reload plugins via **Python > Reload Plugins**).
4. Access the plugin via **File > Export Variations...**.

A log dock widget will appear showing progress and diagnostics.

## Requirements

- Adobe Substance 3D Painter (2022+ recommended)
- PySide6 (bundled with Substance Painter)

## Limitations

- Exports a fixed set of channels: base color, normal, AO (mixed), roughness, metallic.
- Only processes the **first** texture set that contains a visible `FMT(...)` layer.
- Variation variables must be defined sequentially (V1 before V2 before V3).
- Output names containing quotes or special characters may cause issues with the internal JS bridge.

## License

[MIT](LICENSE)
