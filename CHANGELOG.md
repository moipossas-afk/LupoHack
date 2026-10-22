# Changelog

## 1.0.0 — Initial release

CLI/menu, diagnostics, DNS A/AAAA, RDAP, TCP connectivity with confirmation, public HTTP(S) inspection, hashes, history, and export.

## LupoHack V1 — Integration expansion

- DNS A/AAAA/MX/NS/TXT/CNAME via `dnspython`.
- Sherlock adapter for username searches with a timeout and limited output.
- Nmap adapter for controlled single-host TCP scanning, authorization, allowlist enforcement, and XML parsing.
- Tool Manager for executable/version status, individual installation plans, and confirmation-gated supported installers.
- Detection/version reporting and confirmed local launch of ZAP and Metasploit, without running scans or exploits.
- Validated persistent JSON configuration and safe read/update commands.
- Offline automated coverage with mocks for processes, adapters, DNS, configuration, and installation decisions.

## V1 professional review update

- Standardized remaining user-facing Portuguese in exports, optional-tool guidance, `.env.example`, and GitHub templates.
- Corrected menu validation, network allowlist consistency, operation summaries, installation wording, and version-check reporting.
- Replaced shell-ambiguous command alternatives and removed non-runnable repository clone placeholders.
- Added separate official-source guides for Nmap, Sherlock, OWASP ZAP, and Metasploit Framework.
- Expanded installation, usage, architecture, module, laboratory, roadmap, and validation documentation.
- Added an internationalization/readiness checklist and recorded owner-dependent publication gates.
- Added the owner-requested Debian/Ubuntu `apt` + `git clone` installation steps to the README and Linux/Kali guides.
- Verified the canonical public repository and completed an unauthenticated `git clone`; aligned source links and installation instructions to the confirmed URL.
