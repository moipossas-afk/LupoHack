# Windows PowerShell

These commands describe a local source checkout; they are not evidence of verified Windows compatibility. Native Windows testing was not performed for this release.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
.\.venv\Scripts\lupohack.exe diagnostics
```

If activation is blocked, do not change the machine-wide execution policy. Use the virtual environment directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\lupohack.exe diagnostics
```

For development, install `python -m pip install -e ".[dev]"` from the activated environment. Optional external-tool integration varies by launcher and `PATH`; LupoHack compatibility must be verified separately from the upstream tool's installation support.
