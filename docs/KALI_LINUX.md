# Kali Linux

Kali-specific commands are provided for convenience; Kali was not tested in the recorded V1 validation. The public GitHub clone URL below was verified for unauthenticated Git read access on 2026-10-22. If repository visibility or access changes and cloning fails, obtain the source archive or an existing checkout and follow the local-source steps.

## Install from the owner-provided GitHub URL

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

## Install from an existing local source folder

From the LupoHack project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
lupohack --help
lupohack diagnostics
```

The toolkit itself does not require `sudo`. Development dependencies are optional and should be installed only for development with `python -m pip install -e '.[dev]'`. Install external tools only when needed, from verified sources, and for an authorized lab scope. See the separate [Metasploit](tools/metasploit.md) guide.
