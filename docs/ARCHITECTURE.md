# Architecture

LupoHack is a layered local Python application. `cli.py` provides the command parser and interactive menu. `modules/` contains DNS/RDAP, network, web, and file services. `integrations/` contains the bounded external-process runner and adapters. `core/` contains validation, result models, exports, and local history. `config.py` manages validated local JSON configuration.

The process runner invokes fixed argument arrays with `shell=False`, a timeout, and an output limit. The Tool Manager uses a fixed executable catalog; free-form user input is not converted into shell commands. Nmap and Sherlock have dedicated adapters. ZAP and Metasploit are limited to local executable detection/version checks and confirmation-gated launches.

Storage is local. LupoHack has no server or telemetry. The only additional Python runtime dependency is `dnspython`; system applications are not included in Python requirements. The Core setup does not install external tools. HTTP inspection validates public destinations and revalidates redirect destinations. It does not pin DNS resolutions, so this is not a guarantee against every DNS-rebinding topology.
