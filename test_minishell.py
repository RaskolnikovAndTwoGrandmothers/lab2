import os
import sys
import shutil
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from minishell import MiniShell

@pytest.fixture
def temp_dir():
    test_dir = tempfile.mkdtemp()
    original_dir = os.getcwd()
    os.chdir(test_dir)
    
    with open("test.txt", 'w') as f:
        f.write("Hello")
    
    os.makedirs("dir")
    with open("dir/inner.txt", 'w') as f:
        f.write("Inner")
    
    yield test_dir
    
    os.chdir(original_dir)
    shutil.rmtree(test_dir)
    
    if os.path.exists('shell.log'):
        os.remove('shell.log')

@pytest.fixture
def shell(temp_dir):
    s = MiniShell()
    s.current_dir = temp_dir
    return s

def test_ls_basic(shell, capsys):
    shell.ls()
    out = capsys.readouterr().out
    assert "test.txt" in out
    assert "dir" in out

def test_ls_detailed(shell, capsys):
    shell.ls(detailed=True)
    out = capsys.readouterr().out
    assert "test.txt" in out

def test_cd_valid(shell):
    shell.cd("dir")
    assert shell.current_dir.endswith("dir")

def test_cd_parent(shell):
    original = shell.current_dir
    shell.cd("dir")
    shell.cd("..")
    assert shell.current_dir == original

def test_cd_invalid(shell, capsys):
    original = shell.current_dir
    shell.cd("bad")
    assert shell.current_dir == original
    assert "Error" in capsys.readouterr().out

def test_cat_file(shell, capsys):
    shell.cat("test.txt")
    assert "Hello" in capsys.readouterr().out

def test_cat_nonexistent(shell, capsys):
    shell.cat("bad.txt")
    assert "Error" in capsys.readouterr().out

def test_cp_file(shell):
    shell.cp("test.txt", "copy.txt")
    assert os.path.exists("copy.txt")

def test_cp_dir(shell):
    shell.cp("dir", "dir_copy", recursive=True)
    assert os.path.exists("dir_copy/inner.txt")

def test_mv_file(shell):
    shell.mv("test.txt", "new.txt")
    assert not os.path.exists("test.txt")
    assert os.path.exists("new.txt")

def test_rm_file(shell):
    shell.rm("test.txt")
    assert not os.path.exists("test.txt")

def test_rm_dir_no_r(shell, capsys):
    shell.rm("dir")
    assert "Error" in capsys.readouterr().out
    assert os.path.exists("dir")

def test_rm_dir_with_r(shell):
    with open('input.txt', 'w') as f:
        f.write('y\n')
    with open('input.txt', 'r') as f:
        import builtins
        original_input = builtins.input
        builtins.input = lambda _: 'y'
        shell.rm("dir", recursive=True)
        builtins.input = original_input
    os.remove('input.txt')
    assert not os.path.exists("dir")

def test_logging(shell):
    shell.log_command("cmd")
    assert os.path.exists("shell.log")
    with open("shell.log", 'r') as f:
        assert "cmd" in f.read()

def test_integration(shell):
    shell.cp("test.txt", "copy.txt")
    assert os.path.exists("copy.txt")
    
    shell.mv("copy.txt", "moved.txt")
    assert not os.path.exists("copy.txt")
    assert os.path.exists("moved.txt")
    
    shell.cd("dir")
    assert shell.current_dir.endswith("dir")
    
    shell.cd("..")
    
    with open('input.txt', 'w') as f:
        f.write('y\n')
    with open('input.txt', 'r') as f:
        import builtins
        original_input = builtins.input
        builtins.input = lambda _: 'y'
        shell.rm("moved.txt")
        builtins.input = original_input
    os.remove('input.txt')
    assert not os.path.exists("moved.txt")

def test_main_loop_exit(monkeypatch, capsys):
    shell = MiniShell()
    inputs = ["exit"]
    monkeypatch.setattr('builtins.input', lambda _: inputs.pop(0))
    shell.run()
    assert "Goodbye" in capsys.readouterr().out

def test_main_loop_ls(monkeypatch, capsys):
    shell = MiniShell()
    inputs = ["ls", "exit"]
    monkeypatch.setattr('builtins.input', lambda _: inputs.pop(0))
    
    with patch.object(shell, 'ls') as mock_ls:
        shell.run()
        mock_ls.assert_called_once_with(None, False)

def test_main_loop_cd(monkeypatch):
    shell = MiniShell()
    inputs = ["cd dir", "exit"]
    monkeypatch.setattr('builtins.input', lambda _: inputs.pop(0))
    
    with patch.object(shell, 'cd') as mock_cd:
        shell.run()
        mock_cd.assert_called_once_with('dir')

def test_main_loop_invalid(monkeypatch, capsys):
    shell = MiniShell()
    inputs = ["badcmd", "exit"]
    monkeypatch.setattr('builtins.input', lambda _: inputs.pop(0))
    shell.run()
    assert "Unknown" in capsys.readouterr().out

def test_empty_input(monkeypatch):
    shell = MiniShell()
    inputs = ["", "exit"]
    monkeypatch.setattr('builtins.input', lambda _: inputs.pop(0))
    shell.run()

def test_keyboard_interrupt(monkeypatch, capsys):
    shell = MiniShell()
    call_count = 0
    def mock_input(prompt):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise KeyboardInterrupt
        return "exit"
    monkeypatch.setattr('builtins.input', mock_input)
    shell.run()
    assert "Goodbye" in capsys.readouterr().out

def test_cd_to_file(shell, capsys):
    original = shell.current_dir
    shell.cd("test.txt")
    assert shell.current_dir == original
    assert "Error" in capsys.readouterr().out

def test_cd_home(shell):
    shell.cd("~")
    assert shell.current_dir == os.path.expanduser("~")

from unittest.mock import patch

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
