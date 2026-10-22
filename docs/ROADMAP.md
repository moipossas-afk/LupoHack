# Roadmap

## Implemented in V1

- Local validated JSON configuration, reports, and history.
- DNS lookups for A, AAAA, MX, NS, TXT, and CNAME; RDAP lookup.
- Defensive HTTP(S) header inspection with non-public destination and redirect blocking.
- Local file hashing and metadata inspection.
- Sherlock adapter with input validation and bounded process execution.
- Confirmation-gated local launch of OWASP ZAP and Metasploit Framework; no automated scans or exploitation.

Implementation is not the same as production verification. Optional external-tool adapters were tested with mocks only; the external binaries were not available in the recorded validation environment.

## Outstanding engineering work

1. Decide whether `require_scope_confirmation` and `allow_external_targets` should be implemented or removed; V1 accepts these configuration keys but does not consult them at runtime.
2. Continue centralizing and documenting scope policy across TCP, web, and public-information lookups.
3. Evaluate stronger SSRF protections, including resolution pinning and redirect/DNS-rebinding edge cases.
4. Add real-binary integration tests in isolated lab environments, with no public targets.
5. Run CI and native verification across the project's intended Linux, Windows, and macOS environments before claiming compatibility.
6. Configure a private security-reporting contact before public publication.

Do not implement automated exploitation, stealth, credential collection, or a cloud service as part of the defensive V1 scope.
