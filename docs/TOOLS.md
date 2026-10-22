# Tool Manager and External Tools

The Core application does not require optional system tools. The Tool Manager detects executables on `PATH`, attempts a fixed version command where supported, and displays installation guidance. `AVAILABLE` means an executable was found; inspect `version_check_status` separately. Neither status proves end-to-end compatibility. The project did not run real Sherlock, OWASP ZAP, or Metasploit binaries in its validation environment.

## Commands

```bash
lupohack tools check
lupohack tools launch zap
lupohack tools launch metasploit
lupohack tools setup
lupohack tools setup --full
```

The accepted identifiers for `show` and `install` are `sherlock`, `zap`, `metasploit`, and `git`. Only `zap` and `metasploit` are accepted by `launch`.

The current supported automatic installation method is Sherlock through detected `pipx`. `--execute` is required to request one of those changes, and exact confirmation is required before a subprocess starts. ZAP and Metasploit use official manual installation instructions. No tool is installed in a batch or on first launch.

## External-tool guides

- [Sherlock](tools/sherlock.md): pipx installation, username search, external requests, and result limitations.
- [OWASP ZAP](tools/owasp-zap.md): Java requirements, local GUI launch, and no API/scanning integration.
- [Metasploit Framework](tools/metasploit.md): official install source and confirmation-gated local console launch.

Each remaining guide identifies the upstream official installation source, operating-system caveats, prerequisites/privileges, version and LupoHack checks, known limitations, and troubleshooting steps. Upstream tool availability is not a LupoHack support claim. The current platform-verification field remains `EXPECTED_NOT_VERIFIED`.

## Core and Full Toolkit

Core installation uses `python -m pip install -e .` from the project root. It installs LupoHack and its declared Python runtime dependency, `dnspython`; it does not install system tools.

Full Toolkit is a plan, not a package or batch installer. `lupohack tools setup --full` displays individual plans. Review and request each supported installation separately. LupoHack does not run shell pipelines such as `curl | sh`, elevate privileges itself, or reinstall an already detected executable.
