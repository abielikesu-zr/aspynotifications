from aspynotifications.services.subject_trie import SubjectTrie


def main() -> None:
    policies = [
        ("node.hr.failed", "policy-1"),
        ("node.*.failed", "policy-3"),
        ("node.app.failed", "policy-2"),
        ("node.*.failed", "policy-4"),
        ("node.*", "policy-5"),
        ("service.payments.failed", "policy-6"),
        ("node.>", "policy-7"),
        ("node.hr.>", "policy-8"),
        ("node.hr.failed.extra", "policy-9"),
    ]

    trie = SubjectTrie()
    trie.build(policies)

    print("Tree:")
    trie.print_tree()

    print("\nMatches:")
    test_subjects = [
        "node.hr.failed",
        "node.app.failed",
        "node.hr.failed.extra",
        "node.sales.failed",
        "node.hr.something",
        "node.hr.failed.extra.more",
        "service.payments.failed",
        "service.other.failed",
    ]

    for subject in test_subjects:
        print(f"{subject}: {trie.find_matches(subject)}")


if __name__ == "__main__":
    main()
