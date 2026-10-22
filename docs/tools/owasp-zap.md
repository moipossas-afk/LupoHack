# OWASP ZAP

## Purpose and LupoHack module

OWASP ZAP is an external web-security application. In LupoHack V1 it belongs to the `web_security`/lab tool catalog and is limited to executable detection, a version probe where the detected launcher supports it, and confirmation-gated local launch. LupoHack does not connect to the ZAP API, send targets to ZAP, spider sites, or start passive or active scans.

## Official installation source and prerequisites

Use the [official ZAP download page][1] to select an installer, package, or operating-system repository. The official page states that Windows and Linux installations require Java 17 or later; the macOS installer includes Java 17. Check the current official page and release checksums before installing. The ZAP project warns that some releases may be unsigned, so verify the source and checksum rather than bypassing an operating-system warning automatically.[1]

LupoHack does not install ZAP. Installing an application may require administrator approval depending on the package and installation location. The LupoHack launch adapter does not elevate privileges.

## Version and LupoHack checks

The official command-line documentation states that `-version` reports the ZAP version. On Windows, use `zap.bat` for command-line options; `zap.exe` does not process them. On macOS the documented launcher is the app's `zap.sh`; on Linux use the installed `zap.sh`.[2]

```bash
lupohack tools show zap
```

LupoHack searches for `zaproxy`, `zap.sh`, `zap.bat`, or `ZAP.exe`. If it finds `ZAP.exe`, it reports detection but does not pass the version flag to the GUI executable. This is not an API or scan integration test. Real ZAP binaries and GUI launch were not tested for this release.

## Launch check

After installing ZAP from the official source and confirming it is on `PATH`, this command asks for the exact `OPEN zap` confirmation and then attempts to open the local application:

```bash
lupohack tools launch zap
```

It supplies no URL, target, scan command, or API argument. Do not interpret a successful GUI launch as a successful security scan.

## Limitations and troubleshooting

If ZAP is not detected, check the installation directory and `PATH`, then run `lupohack tools check` and `lupohack tools show zap`. On Windows, expose the documented `zap.bat` launcher if you need command-line version detection; a detected `ZAP.exe` alone cannot be version-checked by this LupoHack adapter. For a Java startup failure, compare the installed Java runtime with the current ZAP download requirements. For installation integrity, use the official release checksums. LupoHack V1 has no ZAP API, target management, scan, or ZAP-specific results parser.

## Official sources

[1]: https://www.zaproxy.org/download/ "OWASP ZAP official downloads and requirements"
[2]: https://www.zaproxy.org/docs/desktop/cmdline/ "OWASP ZAP command-line documentation"
[3]: https://www.zaproxy.org/getting-started/ "OWASP ZAP getting started guide"
