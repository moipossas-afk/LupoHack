# FAQ

**Does it replace a scanner/SOC?** No. It is a basic local toolkit.

**Does it analyze all DNS records?** No; V1 queries A/AAAA records.

**Does it confirm malware?** No. Hashes are used for identification/comparison.

**Why does web inspection block localhost?** To reduce SSRF; a local testing environment is not enabled in this version.

**Does it send data?** There is no telemetry; RDAP/web/DNS queries use external infrastructure/the system DNS and reveal the targets to those operators.
