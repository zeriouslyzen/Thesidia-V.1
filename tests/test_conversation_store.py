import tempfile
import unittest
from pathlib import Path
import sys

# Ensure repo root is on sys.path so `webapp.*` imports work when running directly.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TestSQLiteConversationStore(unittest.TestCase):
    def test_upsert_list_get(self):
        from webapp.conversations.storage import SQLiteConversationStore, ConversationMessage

        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "conversations.sqlite3"
            store = SQLiteConversationStore(db_path=db_path)

            store.upsert_conversation(
                conversation_id="c1",
                user_id="u1",
                session_id="s1",
                title="hello",
                preview="preview",
                messages=[
                    ConversationMessage(role="user", content="hi", ts_ms=1),
                    ConversationMessage(role="thesidia", content="yo", ts_ms=2),
                ],
            )

            lst = store.list_conversations(user_id="u1", session_id="s1", limit=10)
            self.assertEqual(len(lst), 1)
            self.assertEqual(lst[0]["id"], "c1")

            conv = store.get_conversation("c1", user_id="u1", session_id="s1")
            self.assertIsNotNone(conv)
            self.assertEqual(conv["id"], "c1")
            self.assertEqual(len(conv["messages"]), 2)

            # Scope check: wrong user should not see it
            conv2 = store.get_conversation("c1", user_id="u2", session_id="s1")
            self.assertIsNone(conv2)


if __name__ == "__main__":
    unittest.main()


