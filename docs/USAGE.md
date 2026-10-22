# Usage

Run `lupohack --help` to see the command tree. Running `lupohack` without a subcommand opens the interactive menu. The menu and CLI are both English-language interfaces.

## Common commands

```bash
lupohack --version
lupohack diagnostics
lupohack osint dns example.org
lupohack osint rdap example.org
lupohack osint username YOUR_AUTHORIZED_TEST_USERNAME
lupohack network dns example.org
lupohack network tcp lab.example 443 --authorized
lupohack network nmap lab.example --authorized
lupohack web https://example.org --authorized
lupohack files hash ./sample.bin --algorithm sha256 -o hash.json
lupohack reports list
lupohack config show
lupohack config path
```

`lab.example` and `YOUR_AUTHORIZED_TEST_USERNAME` are placeholders, not authorization to access a real target or search someone else's identity. Replace them only with an in-scope host or username you are authorized to assess. The DNS/RDAP/web/Sherlock commands send queries to external services as described in the README and module guides.

## Scope and confirmations

TCP and Nmap require `--authorized` on the CLI. The interactive menu asks the user to type `YES`. If `allowed_targets` is non-empty, its normalized host entries apply to TCP and Nmap; out-of-scope requests are rejected before a connection or scan starts. Nmap accepts one host, not a CIDR range. Web inspection also requires authorization and blocks non-public destinations and redirects to them.

The configuration keys `require_scope_confirmation` and `allow_external_targets` are accepted for compatibility but are not consulted by the V1 runtime. Confirmation remains mandatory for the applicable operations, and these fields do not grant or remove scope. Do not use them as security controls.

## Optional tools

Use these concrete commands to inspect or plan a tool:

```bash
lupohack tools check
lupohack tools show nmap
lupohack tools install nmap
lupohack tools setup
lupohack tools setup --full
```

The `install` command displays a plan. To request a supported automatic installation, append `--execute` and type the exact confirmation phrase shown by LupoHack. ZAP and Metasploit launch commands are separate:

```bash
lupohack tools launch zap
lupohack tools launch metasploit
```

Launching either application requires its exact `OPEN zap` or `OPEN metasploit` confirmation. ZAP receives no target or scan arguments. Metasploit opens an interactive local console without a target, module, exploit, payload, or command preloaded. These are local launches, not verified real-binary integrations in this release.

## Configuration and reports

Set an allowlist with a JSON array:

```bash
lupohack config set allowed_targets '["lab.example"]'
```

Use `lupohack config set default_timeout_seconds 10` for a validated integer example. `lupohack reports show REPORT_ID` displays an existing local record. `lupohack reports export REPORT_ID ./report.json` exports it; replace `REPORT_ID` with an ID returned by `lupohack reports list`. `lupohack reports clear` asks for confirmation before deleting local history.

For installation or tool troubleshooting, see [INSTALLATION.md](INSTALLATION.md) and [TOOLS.md](TOOLS.md). For the safety boundary, read [SECURITY.md](../SECURITY.md).
