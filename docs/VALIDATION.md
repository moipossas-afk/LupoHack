# Validation Record

**Run date:** 2026-10-22
**Project version:** 1.0.0

## Automated checks

- `ruff check .`: passed.
- `python -m pytest -q`: 30 tests passed.
- Tests use local fixtures and mocks for DNS, subprocesses, adapters, configuration, and policy checks; they do not scan public targets.
- A parser check evaluated 77 LupoHack command lines in fenced Markdown examples. All parsed successfully. Parsing verifies command shape, not the safety or runtime outcome of placeholder targets.
- A local-link and language-pattern scan covered all 58 packaged source/document/template/metadata files: zero broken local Markdown links and zero likely Portuguese-language matches.
- A wheel build with pip build isolation completed successfully. It has no license field because the owner has not selected a license; the build does not imply redistribution rights.

## Installation and smoke checks

The Core installation was tested from the extracted publication source in a disposable Python 3.12.3 virtual environment using `python -m pip install --upgrade pip` and `python -m pip install -e '.[dev]'`. Installation of LupoHack 1.0.0 and its declared `dnspython` dependency succeeded. The installed `lupohack --version`, `--help`, and `diagnostics` commands also succeeded. The temporary environment was kept outside the repository tree.

Local checks also completed for `lupohack tools show nmap` and `config set`/`config show` using an isolated temporary configuration directory, which was removed afterward. No optional security tool was installed or launched.

No public DNS, RDAP, HTTP, or Sherlock search was run through LupoHack. No TCP connection or Nmap scan against a real target was run. Tool Manager presence/version probes are not end-to-end integration tests.

## Repository URL check

On 2026-10-22, the authenticated GitHub API confirmed `moipossas-afk/LupoHack` as a public repository with canonical URL `https://github.com/moipossas-afk/LupoHack`, default branch `main`, and administrator access for the connected account. The existing root contained only `README.md` and one initial commit; `main` was not protected and no open pull request existed at inspection time. An unauthenticated `git ls-remote` and the exact unauthenticated command `git clone https://github.com/moipossas-afk/LupoHack.git` both succeeded. The clone returned base commit `0d9c81d3b77a66f472a5f2bd60aeb46d3764dc45`. The README and Linux guide clone command was therefore tested without credentials.

## Environment and compatibility

The recorded execution environment was the Manus Linux aarch64 sandbox with Python 3.12.3. Package metadata declares Python 3.11 or later. Kali Linux, Windows, macOS, and other Linux distributions were not validated. The GitHub Actions workflow is configured for pushes and pull requests on Ubuntu/Windows with Python 3.11/3.12. Its remote run status is reported separately from the local test results above.

## Known limitations

Real-binary tests for Nmap, Sherlock, OWASP ZAP, and Metasploit Framework remain outstanding. Configuration keys `require_scope_confirmation` and `allow_external_targets` are currently accepted but unused by runtime policy. A license and private security-reporting contact remain owner decisions. Review the [internationalization/readiness audit](INTERNATIONALIZATION_AUDIT.md) before public distribution.

## References

[1]: https://github.com/moipossas-afk/LupoHack "Canonical LupoHack repository"
