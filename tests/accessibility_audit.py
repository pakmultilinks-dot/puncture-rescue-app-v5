#!/usr/bin/env python3
"""Check the restrained v5 UI palette against WCAG AA for normal text."""


def luminance(color):
    channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(foreground, background):
    light, dark = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


PAIRS = [
    ("primary button text / vermilion", "#FFFEFB", "#B94430"),
    ("main text / warm paper", "#252723", "#F6F4EF"),
    ("main text / soft white", "#252723", "#FFFEFB"),
    ("secondary text / warm paper", "#62675F", "#F6F4EF"),
    ("secondary text / soft white", "#62675F", "#FFFEFB"),
    ("placeholder / soft white", "#676C63", "#FFFEFB"),
    ("request copy / preview tint", "#62675F", "#EFE8E2"),
    ("request eyebrow / preview tint", "#252723", "#EFE8E2"),
    ("accent label / warm paper", "#B94430", "#F6F4EF"),
    ("alert text / warm paper", "#8B3325", "#F6F4EF"),
]


def main():
    failed = []
    values = []
    for label, foreground, background in PAIRS:
        value = contrast(foreground, background)
        values.append(value)
        print(f"{'PASS' if value >= 4.5 else 'FAIL'}  {value:.2f}:1  {label}")
        if value < 4.5:
            failed.append(label)
    print(f"Minimum audited contrast: {min(values):.2f}:1 (WCAG AA normal-text threshold: 4.50:1)")
    if failed:
        raise SystemExit(f"Contrast failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
