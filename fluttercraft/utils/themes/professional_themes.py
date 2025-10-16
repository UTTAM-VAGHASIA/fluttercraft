"""Professional theme definitions with accurate color palettes.

Based on popular VS Code and editor themes.
"""

from .theme import Theme, ThemeType, SemanticColors


# ============================================================================
# DARK THEMES
# ============================================================================

ANSI_DARK = Theme(
    name="ansi_dark",
    type=ThemeType.DARK,
    description="Classic ANSI terminal colors on dark background",
    background="#000000",
    foreground="#FFFFFF",
    accent_blue="#0000FF",
    accent_purple="#FF00FF",
    accent_cyan="#00FFFF",
    accent_green="#00FF00",
    accent_yellow="#FFFF00",
    accent_red="#FF0000",
    gray="#808080",
    comment="#808080",
    diff_added="#00FF00",
    diff_removed="#FF0000",
    gradient_colors=["#00FFFF", "#0000FF", "#FF00FF"],
)

ATOM_ONE_DARK = Theme(
    name="atom_one_dark",
    type=ThemeType.DARK,
    description="Atom's iconic One Dark theme",
    background="#282C34",
    foreground="#ABB2BF",
    accent_blue="#61AFEF",
    accent_purple="#C678DD",
    accent_cyan="#56B6C2",
    accent_green="#98C379",
    accent_yellow="#E5C07B",
    accent_red="#E06C75",
    gray="#5C6370",
    comment="#5C6370",
    diff_added="#98C379",
    diff_removed="#E06C75",
    gradient_colors=["#61AFEF", "#C678DD", "#E06C75"],
)

AYU_DARK = Theme(
    name="ayu_dark",
    type=ThemeType.DARK,
    description="Ayu's elegant dark theme with warm tones",
    background="#0A0E14",
    foreground="#B3B1AD",
    accent_blue="#59C2FF",
    accent_purple="#D2A6FF",
    accent_cyan="#95E6CB",
    accent_green="#AAD94C",
    accent_yellow="#FFB454",
    accent_red="#F07178",
    gray="#4D5566",
    comment="#4D5566",
    diff_added="#AAD94C",
    diff_removed="#F07178",
    gradient_colors=["#59C2FF", "#D2A6FF", "#FFB454"],
)

DEFAULT_DARK = Theme(
    name="default_dark",
    type=ThemeType.DARK,
    description="VS Code default dark theme",
    background="#1E1E1E",
    foreground="#D4D4D4",
    accent_blue="#569CD6",
    accent_purple="#C586C0",
    accent_cyan="#4EC9B0",
    accent_green="#6A9955",
    accent_yellow="#DCDCAA",
    accent_red="#F48771",
    gray="#858585",
    comment="#6A9955",
    diff_added="#4EC9B0",
    diff_removed="#F48771",
    gradient_colors=["#569CD6", "#C586C0", "#4EC9B0"],
)

DRACULA = Theme(
    name="dracula",
    type=ThemeType.DARK,
    description="Dracula's dark theme with vibrant colors",
    background="#282A36",
    foreground="#F8F8F2",
    accent_blue="#8BE9FD",
    accent_purple="#BD93F9",
    accent_cyan="#8BE9FD",
    accent_green="#50FA7B",
    accent_yellow="#F1FA8C",
    accent_red="#FF5555",
    gray="#6272A4",
    comment="#6272A4",
    diff_added="#50FA7B",
    diff_removed="#FF5555",
    gradient_colors=["#8BE9FD", "#BD93F9", "#FF79C6"],
    accent_pink="#FF79C6",
)

GITHUB_DARK = Theme(
    name="github_dark",
    type=ThemeType.DARK,
    description="GitHub's dark theme",
    background="#0D1117",
    foreground="#C9D1D9",
    accent_blue="#58A6FF",
    accent_purple="#BC8CFF",
    accent_cyan="#39C5CF",
    accent_green="#3FB950",
    accent_yellow="#D29922",
    accent_red="#F85149",
    gray="#8B949E",
    comment="#8B949E",
    diff_added="#3FB950",
    diff_removed="#F85149",
    gradient_colors=["#58A6FF", "#BC8CFF", "#F85149"],
)

SHADES_OF_PURPLE = Theme(
    name="shades_of_purple",
    type=ThemeType.DARK,
    description="Shades of Purple - vibrant purple theme",
    background="#2D2B55",
    foreground="#E3DFFF",
    accent_blue="#80FFBB",
    accent_purple="#FAD000",
    accent_cyan="#A599E9",
    accent_green="#3AD900",
    accent_yellow="#FAD000",
    accent_red="#EC3A37",
    gray="#7E7BAC",
    comment="#B362FF",
    diff_added="#3AD900",
    diff_removed="#EC3A37",
    gradient_colors=["#A599E9", "#FAD000", "#FF628C"],
    accent_pink="#FF628C",
    accent_orange="#FF9D00",
)


# ============================================================================
# LIGHT THEMES
# ============================================================================

ANSI_LIGHT = Theme(
    name="ansi_light",
    type=ThemeType.LIGHT,
    description="Classic ANSI terminal colors on light background",
    background="#FFFFFF",
    foreground="#000000",
    accent_blue="#0000FF",
    accent_purple="#FF00FF",
    accent_cyan="#00FFFF",
    accent_green="#008000",
    accent_yellow="#808000",
    accent_red="#FF0000",
    gray="#808080",
    comment="#808080",
    diff_added="#008000",
    diff_removed="#FF0000",
    gradient_colors=["#0000FF", "#FF00FF", "#FF0000"],
)

AYU_LIGHT = Theme(
    name="ayu_light",
    type=ThemeType.LIGHT,
    description="Ayu's clean light theme",
    background="#FAFAFA",
    foreground="#5C6166",
    accent_blue="#399EE6",
    accent_purple="#A37ACC",
    accent_cyan="#4CBF99",
    accent_green="#86B300",
    accent_yellow="#F2AE49",
    accent_red="#F07171",
    gray="#828C99",
    comment="#ABB0B6",
    diff_added="#86B300",
    diff_removed="#F07171",
    gradient_colors=["#399EE6", "#A37ACC", "#F2AE49"],
)

DEFAULT_LIGHT = Theme(
    name="default_light",
    type=ThemeType.LIGHT,
    description="VS Code default light theme",
    background="#FFFFFF",
    foreground="#000000",
    accent_blue="#0000FF",
    accent_purple="#AF00DB",
    accent_cyan="#0070C1",
    accent_green="#008000",
    accent_yellow="#795E26",
    accent_red="#A31515",
    gray="#808080",
    comment="#008000",
    diff_added="#008000",
    diff_removed="#A31515",
    gradient_colors=["#0000FF", "#AF00DB", "#A31515"],
)

GITHUB_LIGHT = Theme(
    name="github_light",
    type=ThemeType.LIGHT,
    description="GitHub's light theme",
    background="#FFFFFF",
    foreground="#24292F",
    accent_blue="#0969DA",
    accent_purple="#8250DF",
    accent_cyan="#1F6FEB",
    accent_green="#1A7F37",
    accent_yellow="#9A6700",
    accent_red="#CF222E",
    gray="#57606A",
    comment="#57606A",
    diff_added="#1A7F37",
    diff_removed="#CF222E",
    gradient_colors=["#0969DA", "#8250DF", "#CF222E"],
)

GOOGLE_CODE_LIGHT = Theme(
    name="google_code_light",
    type=ThemeType.LIGHT,
    description="Google Code's light theme",
    background="#FFFFFF",
    foreground="#000000",
    accent_blue="#0000FF",
    accent_purple="#660E7A",
    accent_cyan="#008080",
    accent_green="#008000",
    accent_yellow="#808000",
    accent_red="#A31515",
    gray="#808080",
    comment="#008000",
    diff_added="#008000",
    diff_removed="#A31515",
    gradient_colors=["#0000FF", "#660E7A", "#A31515"],
)

XCODE_LIGHT = Theme(
    name="xcode_light",
    type=ThemeType.LIGHT,
    description="Xcode's default light theme",
    background="#FFFFFF",
    foreground="#000000",
    accent_blue="#0431FA",
    accent_purple="#9B2393",
    accent_cyan="#23575C",
    accent_green="#177500",
    accent_yellow="#78492A",
    accent_red="#D12F1B",
    gray="#5D6C79",
    comment="#5D6C79",
    diff_added="#177500",
    diff_removed="#D12F1B",
    gradient_colors=["#0431FA", "#9B2393", "#D12F1B"],
)


# ============================================================================
# THEME REGISTRY
# ============================================================================

PROFESSIONAL_THEMES = {
    # Dark themes
    "ansi_dark": ANSI_DARK,
    "atom_one_dark": ATOM_ONE_DARK,
    "ayu_dark": AYU_DARK,
    "default_dark": DEFAULT_DARK,
    "dracula": DRACULA,
    "github_dark": GITHUB_DARK,
    "shades_of_purple": SHADES_OF_PURPLE,
    # Light themes
    "ansi_light": ANSI_LIGHT,
    "ayu_light": AYU_LIGHT,
    "default_light": DEFAULT_LIGHT,
    "github_light": GITHUB_LIGHT,
    "google_code_light": GOOGLE_CODE_LIGHT,
    "xcode_light": XCODE_LIGHT,
}

# Default theme
DEFAULT_THEME = DEFAULT_DARK
