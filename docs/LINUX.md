# Linux

These commands describe source installation; they are not a platform compatibility claim. The recorded validation environment was Linux aarch64 with Python 3.12.3. Other distributions, including Kali, require their own verification. The public GitHub repository URL was checked with unauthenticated `git ls-remote` on 2026-10-22.

## Install from GitHub on Debian/Ubuntu

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

If repository visibility or access changes and `git clone` fails, use a source archive or existing local checkout and continue below from the project root.

## Install from an existing local source folder

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
lupohack diagnostics
```

Some distributions require their `python3-venv` package first. For development, install the `dev` extra with `python -m pip install -e '.[dev]'`. The toolkit itself does not require `sudo`; optional external-tool installation may require administrator privileges and separate confirmation.
