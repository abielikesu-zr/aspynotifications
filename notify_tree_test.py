import pygtrie


class SubjectTrie:
    def __init__(self) -> None:
        self._trie = pygtrie.Trie()

    def insert_v1(
        self,
        subject: str,
        value: str,
    ) -> None:
        parts = subject.split(".")

        if ">" in parts[:-1]:
            raise ValueError("'>' must be the last token in a subject")

        for level in range(1, len(parts) + 1):
            path = tuple(parts[:level])

            if parts[level - 1] == "*":
                values = self._trie.get(path)

                if values is None:
                    self._trie[path] = [(value, subject)]
                elif (value, subject) not in values:
                    values.append((value, subject))

        leaf = tuple(parts)

        # A '*' leaf was already handled above.
        if parts[-1] == "*":
            return

        values = self._trie.get(leaf)

        if values is None:
            self._trie[leaf] = [value]
        elif value not in values:
            values.append(value)

    def find_matches_v1(self, subject: str) -> list[str]:
        parts = subject.split(".")
        candidates: dict[str, str] = {}
        matches: set[str] = set()

        for level, part in enumerate(parts):
            path = tuple(parts[: level + 1])

            # > at this level is an immediate match.
            greater_path = tuple([*parts[:level], ">"])
            greater_values = self._trie.get(greater_path)

            if greater_values:
                matches.update(greater_values)

            # * at this level adds candidates.
            wildcard_path = tuple([*parts[:level], "*"])
            wildcard_values = self._trie.get(wildcard_path, [])

            for value, candidate_path in wildcard_values:
                candidates[value] = candidate_path

            # Filter existing candidates against the current level.
            for value, candidate_path in list(candidates.items()):
                candidate_parts = candidate_path.split(".")

                if level >= len(candidate_parts):
                    del candidates[value]
                    continue

                candidate_part = candidate_parts[level]

                if candidate_part not in ("*", part):
                    del candidates[value]

            # At the leaf, surviving candidates are matches.
            if level == len(parts) - 1:
                matches.update(candidates.keys())

        # Exact leaf match.
        exact_values = self._trie.get(tuple(parts), [])
        matches.update(exact_values)

        return sorted(matches)

    def insert(
        self,
        subject: str,
        value: str,
    ) -> None:
        parts = subject.split(".")

        if ">" in parts[:-1]:
            raise ValueError("'>' must be the last token in a subject")

        leaf = tuple(parts)
        values = self._trie.get(leaf)

        if values is None:
            self._trie[leaf] = [value]
        elif value not in values:
            values.append(value)

    def find_matches(self, subject: str) -> list[str]:
        parts = subject.split(".")
        matches: set[str] = set()

        # First level: establish the initial candidates.
        part = parts[0]
        candidates: list[tuple[str, ...]] = []

        exact_path = (part,)
        wildcard_path = ("*",)
        greater_path = (">",)

        if self._trie.has_node(exact_path):
            candidates.append(exact_path)

        if self._trie.has_node(wildcard_path):
            candidates.append(wildcard_path)

        if self._trie.has_node(greater_path):
            matches.update(self._trie.get(greater_path, []))

        # Remaining levels: expand each candidate.
        for part in parts[1:]:
            new_candidates: list[tuple[str, ...]] = []

            for candidate in candidates:
                exact_path = candidate + (part,)
                wildcard_path = candidate + ("*",)
                greater_path = candidate + (">",)

                if self._trie.has_node(exact_path):
                    new_candidates.append(exact_path)

                if self._trie.has_node(wildcard_path):
                    new_candidates.append(wildcard_path)

                if self._trie.has_node(greater_path):
                    matches.update(self._trie.get(greater_path, []))

            candidates = new_candidates

            if not candidates:
                break

        # Values on surviving leaf candidates.
        for candidate in candidates:
            values = self._trie.get(candidate, [])

            for value in values:
                if isinstance(value, str):
                    matches.add(value)

        return sorted(matches)

    def get(self, subject: str) -> list[str]:
        return self._trie[tuple(subject.split("."))]  # type: ignore

    def print_tree(self) -> None:
        for key, value in self._trie.items():
            print(f"{'.'.join(key)} -> {value}")


def main() -> None:
    trie = SubjectTrie()

    print("1. Insert node.hr.failed")
    trie.insert(
        "node.hr.failed",
        "policy-1",
    )

    print("\n3. Insert node.*.failed")
    trie.insert(
        "node.*.failed",
        "policy-3",
    )

    print("\n2. Insert node.app.failed")
    trie.insert(
        "node.app.failed",
        "policy-2",
    )

    print("\n4. Insert node.*.failed again with another policy")
    trie.insert(
        "node.*.failed",
        "policy-4",
    )

    print("\n5. Insert node.*")
    trie.insert(
        "node.*",
        "policy-5",
    )

    print("\n6. Insert a completely new branch")
    trie.insert(
        "service.payments.failed",
        "policy-6",
    )

    print("\n7. Insert node.>")
    trie.insert(
        "node.>",
        "policy-7",
    )

    print("\n8. Insert node.hr.>")
    trie.insert(
        "node.hr.>",
        "policy-8",
    )

    print("\n9. Insert node.hr.failed.extra")
    trie.insert(
        "node.hr.failed.extra",
        "policy-9",
    )

    print("\nTree:")
    trie.print_tree()

    print("\nDirect lookups:")
    print("node.hr.failed:", trie.get("node.hr.failed"))
    print("node.app.failed:", trie.get("node.app.failed"))
    print("node.*:", trie.get("node.*"))
    print("node.*.failed:", trie.get("node.*.failed"))
    print("node.>:", trie.get("node.>"))
    print("node.hr.>:", trie.get("node.hr.>"))
    print("node.hr.failed.extra:", trie.get("node.hr.failed.extra"))

    print("\nMatches:")
    print(
        "node.hr.failed:",
        trie.find_matches("node.hr.failed"),
    )
    print(
        "node.app.failed:",
        trie.find_matches("node.app.failed"),
    )
    print(
        "node.hr.failed.extra:",
        trie.find_matches("node.hr.failed.extra"),
    )
    print(
        "node.sales.failed:",
        trie.find_matches("node.sales.failed"),
    )
    print(
        "node.hr.something:",
        trie.find_matches("node.hr.something"),
    )
    print(
        "node.hr.failed.extra.more:",
        trie.find_matches("node.hr.failed.extra.more"),
    )
    print(
        "service.payments.failed:",
        trie.find_matches("service.payments.failed"),
    )
    print(
        "service.other.failed:",
        trie.find_matches("service.other.failed"),
    )


if __name__ == "__main__":
    main()
