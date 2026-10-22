# Sherlock

## Purpose and LupoHack module

Sherlock searches public websites for pages that report a username. LupoHack's `osint.username` adapter validates the supplied username, starts the `sherlock` executable without a shell, applies a timeout/output limit, and reports URLs present in the tool's output. It does not establish identity, ownership, or a relationship between accounts.

## Official installation source

Sherlock's project-maintained installation guide recommends the officially supported PyPI package through pipx:

```bash
pipx install sherlock-project
```

The guide also documents alternative methods and their support status. Follow the [official installation instructions][1] for the current OS-specific prerequisites and pipx setup. LupoHack can display a pipx installation plan if it detects `pipx`; that user-level installation changes the Python application environment and needs exact confirmation in LupoHack.

## Prerequisites and privileges

The `sherlock` executable must be available on `PATH`. The pipx method isolates Sherlock from LupoHack's Python environment and requires package-index/network access. LupoHack does not require administrator privileges for the pipx plan. The official installation page does not specify one universal minimum Python version; do not infer one from LupoHack's own Python requirement.

## Version and LupoHack checks

The official guide documents:

```bash
sherlock --version
```

Check LupoHack's detection and version-probe result with:

```bash
lupohack tools show sherlock
```

This check does not run a username search or prove end-to-end compatibility. LupoHack's adapter was tested with mocks only; a real Sherlock binary was not installed or tested for this release.

## Authorized-by-context integration check

A username search sends requests to public websites and may reveal the queried username to those services. Only use a username you control or are specifically authorized to assess, and follow applicable policy. To run a real search, replace the placeholder in the command below:

```bash
lupohack osint username YOUR_AUTHORIZED_TEST_USERNAME
```

The adapter reports only URLs/text emitted by Sherlock. A reported page can be stale, unavailable, or unrelated to the person you have in mind. Do not treat a match as identity verification.

## Limitations and troubleshooting

If LupoHack reports `MISSING`, confirm that pipx installed the application and that the directory containing `sherlock` is on `PATH`; follow pipx's official path/setup guidance if a new terminal session is needed. If the version check fails, review the executable path and run `sherlock --version` directly. If the LupoHack search times out or returns no matches, public sites may have changed, rate-limited, or blocked requests. LupoHack does not claim that an empty result means no account exists.

## Official sources

[1]: https://sherlockproject.xyz/installation "Sherlock Project installation guide"
[2]: https://github.com/sherlock-project/sherlock "Sherlock Project source repository"
