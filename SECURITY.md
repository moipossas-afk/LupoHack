# Security Policy

Use LupoHack only on systems, domains, files, and networks for which you have explicit authorization. The user is responsible for complying with the law and the agreed scope.

V1 performs public-information queries and limited diagnostics, including one explicitly authorized TCP or TLS connection; it does not exploit vulnerabilities, scan ports, or perform a cryptographic audit. TCP and TLS enforce `allowed_targets` when that list is non-empty. To report a flaw in LupoHack itself, do not publish sensitive details publicly. A monitored private security-reporting contact has not been configured for this release, so the project owner must designate and publish one before inviting external security reports.

SSRF protection blocks addresses that are not globally routable and revalidates redirects. This is a conservative safeguard, not a guarantee against all DNS topologies or conditions.
