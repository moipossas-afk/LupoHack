# General Installation

## Requirements and support status

The package metadata declares Python 3.11 or later. The recorded validation environment was Python 3.12.3 on Linux aarch64 in the Manus Sandbox. Kali Linux, Windows, macOS, and other Linux distributions were not verified for this release. Platform-specific guides describe commands, not a claim that LupoHack has been tested on that platform.

LupoHack Core uses `dnspython>=2.6,<3` for DNS queries. Nmap, Sherlock, OWASP ZAP, Metasploit Framework, and Git are optional external tools, not Python runtime requirements.

## Install from a source checkout

The canonical source is the public [`moipossas-afk/LupoHack` repository](https://github.com/moipossas-afk/LupoHack), with Git URL `https://github.com/moipossas-afk/LupoHack.git`. On 2026-10-22 its `main` default branch and public read access were confirmed through GitHub. The exact `git clone https://github.com/moipossas-afk/LupoHack.git` command succeeded without credentials. The Linux install commands were checked against the package name and entry point. A source archive or existing local folder can also be used.

### Linux

#### Clone and install from GitHub

The public Git URL was verified for unauthenticated read access on 2026-10-22. If access or repository visibility changes later, obtain authorized access or use a source archive.

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip

git clone https://github.com/moipossas-afk/LupoHack.git
cd LupoHack

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e .

lupohack --help
lupohack diagnostics
lupohack
```

#### Install from an existing local source folder

If the repository is private/inaccessible or the clone command fails, obtain the source archive or an existing local source folder and run the following from the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
lupohack --help
lupohack diagnostics
```

If `python3 -m venv` reports that venv support is missing, install the appropriate `python3-venv` package through your distribution's official package manager, then repeat the command.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
lupohack --help
lupohack diagnostics
```

If activation is blocked, do not change the machine-wide PowerShell execution policy. Use the virtual environment directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\lupohack.exe --help
```

### Development dependencies

The `dev` extra includes the project's test and lint tools. Install it only when developing or validating the source:

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
ruff check .
```

Core installation uses `python -m pip install -e .` and does not install those development tools.

## Optional tools

The external-tool plans are separate from Core. Use `lupohack tools check`, `lupohack tools show nmap`, and `lupohack tools install nmap` to inspect status and an installation plan. The accepted tool identifiers are `nmap`, `sherlock`, `zap`, `metasploit`, and `git`. A detected supported installer can be run only with `--execute` and an exact confirmation. Read [TOOLS.md](TOOLS.md) and the individual guides before installing an external tool. LupoHack does not claim real-binary integration testing for this release.

## Uninstall

From the active Python environment, remove the package with:

```bash
python -m pip uninstall lupohack
```

This does not remove external tools, local configuration, report history, or the virtual environment. Remove only the items you intend to delete. System tools should be uninstalled through the same OS package manager or official installer that installed them.

## Validation

After installation, run:

```bash
lupohack --version
lupohack --help
lupohack diagnostics
lupohack tools check
python -m pytest -q
ruff check .
```

The last two commands require the `dev` extra. Current recorded results and untested areas are listed in [VALIDATION.md](VALIDATION.md).

## Troubleshooting

If `lupohack` is not found after installation, verify that the correct virtual environment is active, or invoke its `bin/lupohack` (Unix-like systems) or `Scripts/lupohack.exe` (Windows) executable directly. If DNS lookups fail, confirm that the system resolver is configured and reachable. If an optional tool is missing, check its installation and `PATH` with `lupohack tools show <name>`; a detected executable does not prove version or integration compatibility. Do not use `sudo` to run the LupoHack application itself merely because an optional-tool installation command may require administrator privileges.

## Further reading

- [Kali Linux](KALI_LINUX.md)
- [Linux](LINUX.md)
- [Windows](WINDOWS.md)
- [Tool Manager](TOOLS.md)
- [Security policy](../SECURITY.md)
