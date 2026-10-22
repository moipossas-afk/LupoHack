# Troubleshooting

- `lupohack` not found: activate the venv or invoke the executable inside `.venv`.
- `No module named lupohack`: install it with `python -m pip install -e .` from the project root.
- RDAP/web request fails: check DNS, connectivity, and service limits; do not disable TLS validation.
- Web reports a blocked destination: the host resolves to a non-public IP; there is no bypass.
- File permission error: choose a file you can read; the program does not elevate privileges.
- No TCP response: a firewall, filtering, or routing issue can produce the same result; this does not prove that the host is offline.
