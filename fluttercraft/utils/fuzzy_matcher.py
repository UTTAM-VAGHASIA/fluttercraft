"""Fuzzy matching utilities for FlutterCraft command completions.

This module provides fast fuzzy string matching using rapidfuzz for
intelligent command completion suggestions.
"""

from typing import List, Tuple
from rapidfuzz import fuzz, process


class FuzzyMatcher:
    """Fast fuzzy matcher for command completions using rapidfuzz.

    Provides intelligent fuzzy matching with scoring for command suggestions.
    Optimized for completion performance (< 50ms for 100 commands).

    Attributes:
        min_score (int): Minimum match score threshold (0-100)
        max_results (int): Maximum number of results to return
    """

    def __init__(self, min_score: int = 60, max_results: int = 10):
        """Initialize FuzzyMatcher.

        Args:
            min_score: Minimum score threshold for matches (0-100, default: 60)
            max_results: Maximum number of results to return (default: 10)
        """
        self.min_score = min_score
        self.max_results = max_results

    def match(self, query: str, targets: List[str]) -> List[Tuple[str, int]]:
        """Fuzzy match query against list of targets.

        Uses WRatio scorer for best results with partial matches.
        Returns matches sorted by score (highest first).

        Args:
            query: Search query string
            targets: List of target strings to match against

        Returns:
            List of tuples (target, score) sorted by score descending.
            Empty list if no matches above min_score.

        Examples:
            >>> matcher = FuzzyMatcher()
            >>> matcher.match("fvmr", ["fvm releases", "fvm remove", "flutter run"])
            [("fvm releases", 95), ("fvm remove", 85)]
        """
        if not query or not targets:
            return []

        # Use process.extract for efficient batch matching
        # WRatio scorer: Handles partial matches well (e.g., "fvmr" → "fvm releases")
        results = process.extract(
            query,
            targets,
            scorer=fuzz.WRatio,
            limit=self.max_results,
            score_cutoff=self.min_score,
        )

        # Convert to list of tuples (target, score)
        return [(match[0], match[1]) for match in results]

    def match_with_meta(self, query: str, targets: dict) -> List[Tuple[str, int, str]]:
        """Fuzzy match with metadata preservation.

        Args:
            query: Search query string
            targets: Dict of {target: metadata} pairs

        Returns:
            List of tuples (target, score, metadata) sorted by score descending

        Examples:
            >>> matcher = FuzzyMatcher()
            >>> targets = {"fvm releases": "List Flutter versions", "fvm remove": "Remove version"}
            >>> matcher.match_with_meta("fvmr", targets)
            [("fvm releases", 95, "List Flutter versions"), ("fvm remove", 85, "Remove version")]
        """
        if not query or not targets:
            return []

        target_list = list(targets.keys())
        matches = self.match(query, target_list)

        # Add metadata to results
        return [(target, score, targets[target]) for target, score in matches]

    def highlight_match(self, query: str, target: str) -> str:
        """Generate highlighted version of target with matched characters.

        Uses simple character-by-character matching for highlighting.

        Args:
            query: Original search query
            target: Target string that matched

        Returns:
            Target string with matched characters in markup (for display)

        Examples:
            >>> matcher = FuzzyMatcher()
            >>> matcher.highlight_match("fvmr", "fvm releases")
            "[bold]f[/bold][bold]v[/bold][bold]m[/bold] [bold]r[/bold]eleases"
        """
        if not query or not target:
            return target

        query_lower = query.lower()
        target_lower = target.lower()
        result = []
        query_idx = 0

        for char in target:
            if query_idx < len(query_lower) and char.lower() == query_lower[query_idx]:
                # Matched character - make it bold
                result.append(f"[bold]{char}[/bold]")
                query_idx += 1
            else:
                # Non-matched character
                result.append(char)

        return "".join(result)
