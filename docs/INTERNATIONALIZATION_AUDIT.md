# Internationalization and V1 Readiness Audit

**Review date:** 2026-10-22
**Verdict:** LupoHack V1 source is ready for repository review, but it is **not ready for a formal v1.0.0 release** until the owner resolves the release gates below.

## Scope reviewed

The review covered the README and root project guidance, package metadata and dependency declarations, CLI/menu text and behavior, core validation/results/export code, service modules, external-tool adapters, automated tests, documentation, GitHub templates/workflow, example environment file, and the PRD startup mockup. The final publication review checked all 58 package files; it excluded the virtual environment, caches, build output, and ZIP artifacts.

This review did not install external tools, scan a real network target, or perform public DNS, RDAP, web, or username searches. External tool adapters were assessed from code and offline tests; their real binaries were not available for end-to-end testing.

## Work completed

The public-facing project text is now in international English, including the README, installation and usage guides, module and architecture notes, tool guidance, roadmap, changelog, `.env.example`, and GitHub templates. A repository scan found no likely Portuguese-language remnants and no broken local Markdown links in the reviewed text/code. The README now states the platform, testing, licensing, and security-contact limitations rather than implying a completed public release.

Command examples were compared with the real parser: all 77 documented LupoHack command lines parsed successfully. Shell-ambiguous alternatives and placeholder clone URLs were removed or clearly identified. Separate official-source guides were added for [Nmap](tools/nmap.md), [Sherlock](tools/sherlock.md), [OWASP ZAP](tools/owasp-zap.md), and [Metasploit Framework](tools/metasploit.md); they distinguish upstream installation availability from LupoHack compatibility and document privileges, version checks, limitations, and troubleshooting.

Several correctness issues were fixed without removing existing CLI subcommands: operation summaries now reflect failure/cancellation/partial status; invalid interactive tool/setup choices are rejected; Core setup no longer claims every optional tool is absent; the configured `allowed_targets` list now applies consistently to TCP and Nmap; and tool detection distinguishes finding an executable from successfully verifying its version. The ZAP desktop `ZAP.exe` path is not given a command-line version flag it does not support. TXT export labels and remaining user-visible messages were translated.

The PRD artwork remains explicitly identified as a conceptual mockup, not a live CLI screenshot. Its startup command was corrected to `lupohack`; all other visual content was preserved.

The placeholder license string was removed from package metadata rather than publishing an invented license. The resulting wheel builds successfully with no license field, pending an owner decision.

The canonical GitHub destination is [moipossas-afk/LupoHack][1]. Its public visibility, `main` default branch, and unauthenticated Git read access were confirmed on 2026-10-22. The existing repository had one initial commit and only a README in its root; `main` was not protected. The exact supplied `git clone` command was tested without credentials against the canonical URL. An earlier unauthenticated browser request was inconclusive; the authenticated repository API and direct anonymous clone now confirm the destination.

## Outstanding release gates

### Owner decisions required before public release

1. **Choose a license and add the corresponding license file and package metadata.** None is selected; this audit does not grant permission to redistribute the code or PRD artwork.
2. **Configure a monitored private security-reporting contact.** No contact address or private reporting channel exists in this release.
3. **Decide the behavior of `require_scope_confirmation` and `allow_external_targets`.** V1 currently accepts these configuration keys but does not consult them at runtime. Confirmation remains mandatory where implemented, and `allowed_targets` applies to TCP/Nmap, but the two fields themselves are not policy controls. The owner should implement or remove them before users rely on configuration as a security boundary.

### Verification work still required

- Run CI on the chosen repository and test every platform the project intends to support. Python package metadata declares Python 3.11+; recorded execution was Linux aarch64 with Python 3.12.3. Kali Linux, Windows, macOS, and other Linux distributions were not verified.
- Test optional integrations with actual Nmap, Sherlock, ZAP, and Metasploit binaries inside isolated, authorized environments. The current integration tests use mocks. The upstream tools' supported platforms do not establish LupoHack compatibility.
- Add cross-platform tests for launchers, subprocess handling, package managers, paths, and report storage before making native compatibility claims.
- Continue hardening the HTTP destination boundary. Current checks reject non-public addresses and revalidate redirects, but they do not pin DNS resolutions and do not guarantee protection against every DNS-rebinding topology.
- Review `allowed_targets` scope across all modules. In V1 it applies to TCP/Nmap; web has its own non-public-address block and explicit authorization, while public OSINT requests are not controlled by that list.

## Recorded validation

The final local review recorded 30 passing offline tests, clean Ruff checks, 77 parser-valid LupoHack command lines in Markdown, CLI/help/diagnostics/Tool Manager/configuration smoke checks, and a successful wheel build. No authorized-target scan or public-information query was run. Exact commands and environment are recorded in [VALIDATION.md](VALIDATION.md).

## Release recommendation

The repository source is available for review. Do not describe the project as cross-platform verified, fully integrated with the external tools, licensed for redistribution, or ready to receive public security reports until the outstanding gates have been resolved.

## References

[1]: https://github.com/moipossas-afk/LupoHack "Canonical LupoHack repository"
