from final_project import __version__


def test_version():
    assert isinstance(__version__, str)


def test_cli_runs(capsys):
    from final_project import cli

    cli.main(["--who", "tester"])
    captured = capsys.readouterr()
    assert "Hello, tester" in captured.out
