# Nmap

## Purpose and LupoHack module

Nmap provides controlled TCP service discovery for one explicitly authorized host. The adapter is used by the `network` module. LupoHack invokes TCP connect (`-sT`), timing template `-T2`, the top 20 ports, XML output, and a bounded timeout. It does not run vulnerability scripts, CIDR scans, stealth options, or exploits.

## Official installation sources

Use the operating system's trusted package manager or the [official Nmap download page][1]. The official Linux guide documents distribution packages and notes that package versions can differ from upstream releases.[2] LupoHack's guided Linux installer currently supports detected Debian-family (`apt-get`), Fedora-family (`dnf`), and Arch (`pacman`) environments. It requests exact confirmation before running a package-manager command. Installation can require administrator privileges and network access.

For Windows, use the official self-installer from Nmap's download page and follow its prompts, including any Npcap component required by the selected features.[3] Nmap publishes platform-specific instructions. LupoHack's Windows/macOS integration has not been tested, and LupoHack does not install Nmap on those platforms.

## Prerequisites and privileges

Nmap must be on `PATH`. The LupoHack invocation uses `-sT` and does not request raw-packet scan modes or elevate privileges. Package installation is separate and may require administrator access. Network policy, endpoint protection, and local firewall rules can affect results.

## Version and LupoHack checks

Check the executable version with:

```bash
nmap --version
```

Check what LupoHack can detect with:

```bash
lupohack tools show nmap
```

The latter reports PATH detection and the outcome of its version probe. It does not perform a scan or prove that the adapter has been tested with a real Nmap binary. Real-binary integration was not tested for this release.

## Authorized integration test

Only after confirming ownership or written authorization, configure the exact host in `allowed_targets` when an allowlist is in use, then run the command against that single lab host:

```bash
lupohack network nmap YOUR_AUTHORIZED_LAB_HOST --authorized
```

Replace the placeholder before running the command. Do not use a public target as a test. LupoHack requires the `--authorized` confirmation flag and enforces `allowed_targets` when it is non-empty. An open port is not, by itself, a vulnerability.

## Limitations and troubleshooting

A `MISSING` result usually means Nmap is not installed or its executable directory is not on `PATH`. An `AVAILABLE` result with a failed version check means the executable was found, but LupoHack could not verify its version; the Tool Manager will not reinstall it automatically. If a target is rejected, review the normalized host in `allowed_targets`. If a scan times out or returns no parsed hosts, check the lab route, firewall, target availability, and the recorded Nmap error before retrying.

## Official sources

[1]: https://nmap.org/download "Nmap official download page"
[2]: https://nmap.org/book/inst-linux.html "Nmap Linux installation guide"
[3]: https://nmap.org/book/inst-windows.html "Nmap Windows installation guide"
