import pytest
from prompt_mgr.search import SearchIndex


@pytest.fixture
def search_db(tmp_path):
    db_path = tmp_path / "test_search.db"
    return str(db_path)


def test_search_index_and_query(search_db):
    idx = SearchIndex(search_db)
    idx.index_prompt(
        path="prompt1.yaml",
        name="Python Expert",
        content="You are an expert in Python",
        tags=["python", "expert"],
        description="A prompt for python",
    )

    # Search by name
    results = idx.search("Python")
    assert len(results) == 1
    assert results[0]["name"] == "Python Expert"

    # Search by tag
    results = idx.search("expert")
    assert len(results) == 1

    # Search by description
    results = idx.search("prompt")
    assert len(results) == 1


def test_search_remove(search_db):
    idx = SearchIndex(search_db)
    idx.index_prompt("p1.yaml", "N1", "C1", ["T1"], "D1")

    assert len(idx.search("N1")) == 1
    idx.remove_prompt("p1.yaml")
    assert len(idx.search("N1")) == 0


def test_search_treats_user_punctuation_as_plain_text(search_db):
    idx = SearchIndex(search_db)
    idx.index_prompt("sql.yaml", "SQL helper", "optimize query", ["database"], "SQL")
    assert idx.search('SQL: "helper"')
    assert idx.search("---") == []
