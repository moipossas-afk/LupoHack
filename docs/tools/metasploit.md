# Metasploit Framework

## Purpose and LupoHack module

Metasploit Framework is an external tool for authorized laboratory work. In LupoHack V1 it is listed under the `lab` integration. LupoHack can detect `msfconsole`, attempt a version check, and open its local interactive console only after the exact `OPEN metasploit` confirmation. It does not supply a target, module, exploit, payload, script, or command.

## Official installation source and prerequisites

Use Rapid7's [official installation guide][1] and its current system-requirements page. Rapid7 states that its installer includes required dependencies and that installation requires administrator privileges. Official installers are described for Linux, Windows, and macOS, but that upstream availability is not proof of LupoHack integration support on those platforms. LupoHack does not install Metasploit. The official documentation also describes nightly installers and first-launch database setup.[2]

Install and use Metasploit only in an intentionally isolated lab. Do not disable antivirus, endpoint protection, or firewalls merely to make an installation proceed; resolve warnings through your organization's security process and official vendor guidance.

## Version and LupoHack checks

The LupoHack Tool Manager checks whether `msfconsole` is on `PATH` and attempts its configured `--version` command:

```bash
lupohack tools show metasploit
```

This is executable/version detection, not an end-to-end test. A real Metasploit binary was not installed or tested for this release. Cross-platform LupoHack integration is unverified.

## Confirmation-gated local launch

After you have reviewed your lab boundaries, run:

```bash
lupohack tools launch metasploit
```

LupoHack asks for the exact `OPEN metasploit` phrase, then starts the local console without adding arguments. The first Metasploit startup may prompt for database initialization. Any actions entered into the console are outside LupoHack's control and must remain within the authorized lab.

## Limitations and troubleshooting

If the tool is reported as `MISSING`, verify the official installation and that `msfconsole` is available on `PATH`. If the version probe fails, run the vendor-provided console command in a terminal and compare the reported error; do not assume that a detected executable is compatible. If first launch asks about database setup, follow the official guide for your isolated environment. LupoHack does not initialize, reset, or manage the Metasploit database.

## Official sources

[1]: https://docs.rapid7.com/metasploit/installing-the-metasploit-framework/ "Rapid7 Metasploit Framework installation guide"
[2]: https://rapid7.github.io/metasploit-framework/docs/using-metasploit/getting-started/nightly-installers.html "Rapid7 Metasploit Framework nightly installers"
