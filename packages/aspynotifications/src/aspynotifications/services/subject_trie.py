from collections.abc import Iterable

import pygtrie  # type: ignore[import-untyped]


class SubjectTrie:
    def __init__(self) -> None:
        self._trie = pygtrie.Trie()
        self._valid = False

    def valid(self) -> bool:
        """Whether the trie has been successfully built."""
        return self._valid

    def insert(self, subject: str, value: str) -> None:
        parts = subject.split(".")
        if ">" in parts[:-1]:
            raise ValueError("'>' must be the last token in a subject")

        leaf = tuple(parts)
        values = self._trie.get(leaf)
        if values is None:
            self._trie[leaf] = [value]
        elif value not in values:
            values.append(value)

    def reset(self) -> None:
        """Invalidate and clear the trie."""
        self._trie = pygtrie.Trie()
        self._valid = False

    def get_subjects(self) -> list[str]:
        if not self._valid:
            raise RuntimeError("SubjectTrie has not been built")

        return [".".join(key) for key, _ in self._trie.items()]

    def build(self, pairs: Iterable[tuple[str, str]]) -> None:
        """Rebuild the trie from a list of (subject_pattern, id) pairs."""
        self.reset()

        for subject, value in pairs:
            self.insert(subject, value)

        self._valid = True

    def find_matches(self, subject: str) -> list[str]:
        if not self._valid:
            raise RuntimeError("SubjectTrie has not been built")

        parts = subject.split(".")
        if not parts:
            return []

        matches: set[str] = set()
        candidates: list[tuple[str, ...]] = []

        # First token
        part = parts[0]
        for token in (part, "*", ">"):
            path: tuple[str, ...] = (token,)

            if self._trie.has_node(path):
                if token == ">":
                    matches.update(self._trie.get(path, []))
                else:
                    candidates.append(path)

        # Remaining tokens
        for part in parts[1:]:
            new_candidates: list[tuple[str, ...]] = []
            for candidate in candidates:
                for next_token in (part, "*", ">"):
                    path = candidate + (next_token,)
                    if self._trie.has_node(path):
                        if next_token == ">":
                            matches.update(self._trie.get(path, []))
                        else:
                            new_candidates.append(path)
            candidates = new_candidates
            if not candidates:
                break

        # Collect values from surviving full-length paths
        for candidate in candidates:
            values = self._trie.get(candidate, [])
            matches.update(v for v in values if isinstance(v, str))

        return sorted(matches)

    def get(self, subject: str) -> list[str]:
        if not self._valid:
            raise RuntimeError("SubjectTrie has not been built")
        return self._trie.get(tuple(subject.split(".")), [])

    def print_tree(self) -> None:
        if not self._valid:
            raise RuntimeError("SubjectTrie has not been built")

        for key, value in self._trie.items():
            print(f"{'.'.join(key)} -> {value}")
