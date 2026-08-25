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

    def get_subscription_subjects(self) -> list[str]:
        """Return subjects after removing those covered by a broader pattern.

        Policy matching retains every subject in the trie.  Worker subscriptions,
        however, must not contain both a broad pattern and one of its subsets:
        subscribing to ``*.created`` already receives ``tenant.created``.
        """
        subjects = self.get_subjects()

        return [
            subject
            for subject in subjects
            if not any(
                broader_subject != subject
                and self._subject_covers(broader_subject, subject)
                for broader_subject in subjects
            )
        ]

    @staticmethod
    def _subject_covers(broader_subject: str, narrower_subject: str) -> bool:
        """Whether every event matching ``narrower_subject`` matches the broader one."""
        broader_tokens = broader_subject.split(".")
        narrower_tokens = narrower_subject.split(".")

        for index, broader_token in enumerate(broader_tokens):
            if broader_token == ">":
                return index < len(narrower_tokens)

            if index >= len(narrower_tokens):
                return False

            narrower_token = narrower_tokens[index]
            if broader_token not in ("*", narrower_token):
                return False

        return len(broader_tokens) == len(narrower_tokens)

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
