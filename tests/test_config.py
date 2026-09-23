import os
import stat

from app import config


def test_dotenv_quotes_comments_and_environment_precedence(tmp_path, monkeypatch):
    monkeypatch.setattr(os, "environ", dict(os.environ))
    for key in ("TANDAU_TEST_QUOTED", "TANDAU_TEST_SINGLE", "TANDAU_TEST_PLAIN", "TANDAU_TEST_OVERRIDE"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("TANDAU_TEST_OVERRIDE", "environment")
    env_file = tmp_path / ".env"
    env_file.write_text(
        'TANDAU_TEST_QUOTED="key # with spaces" # outside comment\n'
        "TANDAU_TEST_SINGLE='off'\n"
        'TANDAU_TEST_PLAIN=off # comment\n'
        'TANDAU_TEST_OVERRIDE=file\n',
        encoding="utf-8",
    )
    config._load_dotenv(env_file)
    assert os.environ["TANDAU_TEST_QUOTED"] == "key # with spaces"
    assert os.environ["TANDAU_TEST_SINGLE"] == "off"
    assert os.environ["TANDAU_TEST_PLAIN"] == "off"
    assert os.environ["TANDAU_TEST_OVERRIDE"] == "environment"


def test_secret_is_persistent_and_private(tmp_path, monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    directory = tmp_path / "var"
    first = config._secret_key(directory)
    assert len(first) >= 48
    assert config._secret_key(directory) == first
    assert (directory / "secret_key").read_text(encoding="utf-8") == first
    if os.name == "posix":
        assert stat.S_IMODE((directory / "secret_key").stat().st_mode) == 0o600


def test_secret_environment_override_does_not_create_file(tmp_path, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "configured-secret")
    directory = tmp_path / "var"
    assert config._secret_key(directory) == "configured-secret"
    assert not directory.exists()


def test_default_settings_work_from_another_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SECRET_KEY", "configured-secret")
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    monkeypatch.delenv("LLM_MODE", raising=False)
    settings = config.get_settings()
    assert settings.database_path == config.BASE_DIR / "var" / "tandau.db"
    assert settings.data_path.is_file()
    assert settings.llm_mode == "off"
