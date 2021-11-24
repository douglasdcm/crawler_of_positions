from src.helper.commands import help_, install, sanity_check
from tests.settings import DATABASE, DB_TYPE
from pytest import mark, fixture
from src.database.db_factory import DbFactory
from tests.resources.fake_driver import FakeDriver

class TestCommands:

    @fixture
    def setup_db(self):
        df = DbFactory("sqlite")
        db = df.get_db()
        db.cria_tabela("positions", "url, description")
        return db

    def test_sanity_check_works(self, setup_db):
        actual = sanity_check(setup_db, FakeDriver())
        expected = "Sanity check finished"
        assert actual == expected

    def test_install_creates_database(self):
        actual = install(DATABASE, DB_TYPE)
        expected = "Installation finished"
        assert actual == expected

    def test_help_is_opened(self):
        actual = help_()
        assert "--initdb" in actual
        assert "--help" in actual
        assert "--sanity-check"
