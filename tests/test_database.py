import unittest
from unittest.mock import MagicMock, patch

from database import DatabaseUnavailable, connect, database_cursor


class DatabaseTests(unittest.TestCase):
    def test_connection_requires_explicit_credentials(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(DatabaseUnavailable):
                connect()

    @patch("database.connect")
    def test_read_closes_cursor_and_connection(self, connect_mock):
        connection = connect_mock.return_value
        with database_cursor() as cursor:
            self.assertIs(cursor, connection.cursor.return_value)
        connection.cursor.assert_called_once_with(dictionary=True, buffered=True)
        cursor.close.assert_called_once_with()
        connection.close.assert_called_once_with()
        connection.commit.assert_not_called()

    @patch("database.connect")
    def test_write_commits_after_success(self, connect_mock):
        connection = connect_mock.return_value
        with database_cursor(write=True):
            connection.commit.assert_not_called()
        connection.commit.assert_called_once_with()
        connection.rollback.assert_not_called()

    def test_write_rolls_back_and_closes_on_failure(self):
        connection = MagicMock()
        with patch("database.connect", return_value=connection):
            with self.assertRaisesRegex(RuntimeError, "write failed"):
                with database_cursor(write=True):
                    raise RuntimeError("write failed")
        connection.rollback.assert_called_once_with()
        connection.commit.assert_not_called()
        connection.cursor.return_value.close.assert_called_once_with()
        connection.close.assert_called_once_with()
