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
lupohack network tls lab.example --authorized
lupohack tools inventory --status available
lupohack web https://example.org --authorized
lupohack files hash ./sample.bin --algorithm sha256 -o hash.json
lupohack reports list
lupohack config show
lupohack config path
```

`lab.example` and `YOUR_AUTHORIZED_TEST_USERNAME` are placeholders, not authorization to access a real target or search someone else's identity. Replace them only with an in-scope host or username you are authorized to assess. The DNS/RDAP/web/Sherlock commands send queries to external services as described in the README and module guides.

## Scope and confirmations

TCP and TLS require `--authorized` on the CLI. The interactive menu asks the user to type `YES`. If `allowed_targets` is non-empty, its normalized host entries apply to TCP and TLS; out-of-scope requests are rejected before a connection starts. TLS inspection performs one handshake with the default certificate and hostname checks, not a port scan or cryptographic audit. Web inspection also requires authorization and blocks non-public destinations and redirects to them.

The configuration keys `require_scope_confirmation` and `allow_external_targets` are accepted for compatibility but are not consulted by the V1 runtime. Confirmation remains mandatory for the applicable operations, and these fields do not grant or remove scope. Do not use them as security controls.

## Optional tools

Use these concrete commands to inspect or plan a tool:

```bash
lupohack tools check
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

## Interactive menu navigation

The main menu groups only implemented features into Reconnaissance, Network diagnostics, Web security, Files & forensics, Tools & environment, Reports & history, and Settings & help. Within a submenu, `B` returns to the category list, `0` returns to the main menu, `H` prints contextual help, and `Q` exits. Tool inventory pagination uses `N` and `P` when multiple pages exist. The banner is ASCII-only and uses color only for an interactive terminal that has not set `NO_COLOR`.

`lupohack tools inventory` checks whether the four optional catalog executables occur on `PATH`; it does not run them. Use `--query`, `--category`, `--status`, `--page`, and `--page-size` for search, filtering, and pagination. The presence result is intentionally distinct from the more active `lupohack tools check` version probes.

For installation or tool troubleshooting, see [INSTALLATION.md](INSTALLATION.md) and [TOOLS.md](TOOLS.md). For the safety boundary, read [SECURITY.md](../SECURITY.md).
