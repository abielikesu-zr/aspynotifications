from aspynotifications.services.subject_trie import SubjectTrie


def test_get_subscription_subjects_removes_exact_subject_covered_by_wildcard() -> None:
    trie = SubjectTrie()
    trie.build(
        [
            ("tenant.created", "tenant-policy"),
            ("*.created", "entity-policy"),
        ]
    )

    assert set(trie.get_subjects()) == {"*.created", "tenant.created"}
    assert trie.get_subscription_subjects() == ["*.created"]


def test_get_subscription_subjects_keeps_subjects_not_covered_by_a_wildcard() -> None:
    trie = SubjectTrie()
    trie.build(
        [
            ("*.created", "entity-policy"),
            ("tenant.deleted", "tenant-deleted-policy"),
        ]
    )

    assert trie.get_subscription_subjects() == ["*.created", "tenant.deleted"]


def test_get_subscription_subjects_removes_subject_covered_by_terminal_wildcard() -> None:
    trie = SubjectTrie()
    trie.build(
        [
            ("tenant.>", "tenant-events-policy"),
            ("tenant.created", "tenant-created-policy"),
        ]
    )

    assert trie.get_subscription_subjects() == ["tenant.>"]
