# Authorized Laboratory

Use a deliberately isolated analysis environment and a deliberately vulnerable target VM on a host-only or internal network. Do not bridge the lab to the public Internet. Use snapshots and synthetic data. Isolate management interfaces, restrict traffic to the lab range, record the authorized targets, and revert snapshots after each exercise.

LupoHack V1 does not run exploits, payloads, persistence, or post-exploitation. The Tool Manager can open the local Metasploit interactive console only after an explicit confirmation; it does not supply a target, module, exploit, payload, or command. It can also open the local ZAP GUI after confirmation, but it does not connect to the ZAP API or start a scan. The real-binary launches have not been tested in this release.

Install and operate external tools only from their official sources and under the laboratory policy. Keep the tool's own actions within the authorized lab. See the separate [Nmap](tools/nmap.md), [OWASP ZAP](tools/owasp-zap.md), and [Metasploit](tools/metasploit.md) guides.
