# Signature-Based Intrusion Detection System with Snort

This project configures a signature-based Intrusion Detection System (IDS)
using Snort 2.x on Linux. The IDS monitors network traffic for known malicious
or suspicious patterns and generates alerts when custom Snort signatures match.

## Project Scope

- Implement Snort IDS on a Linux machine or Linux virtual machine.
- Configure the protected network with `HOME_NET`.
- Load custom signatures from `rules/local.rules`.
- Generate test traffic for ICMP ping, SYN scan, Telnet, FTP, and HTTP
  directory traversal attempts.
- Collect Snort alerts as proof of detection.

## Linux Lab Setup

Recommended VM networks:

- `192.168.56.0/24` for VirtualBox host-only labs.
- `10.0.2.0/24` for common NAT VM labs.

These are already configured in `snort.conf`:

```conf
ipvar HOME_NET [192.168.56.0/24,10.0.2.0/24]
ipvar EXTERNAL_NET !$HOME_NET
```

Update `HOME_NET` if your Linux VM uses a different subnet. For single-machine
testing with no separate attacker VM, set both to `any`.

## Setup by OS

### Windows (WSL)

1. Open WSL (Ubuntu). If not installed, run `wsl --install` in PowerShell.
2. Clone the repo and enter the directory.
3. Install Snort:
```bash
sudo apt update && sudo apt install snort -y
```
4. Copy support files:
```bash
sudo cp /etc/snort/*.config ./
sudo cp /etc/snort/*.map ./
sudo cp /etc/snort/threshold.conf ./
```
5. Find your interface name: `ip link show` (usually `eth0`)

### Mac (Lima)

1. Install Lima:
```bash
brew install lima
limactl start --name=snort-lab template:ubuntu-lts
```
2. Enter the Linux VM:
```bash
limactl shell snort-lab
```
3. Clone the repo into the VM and enter the directory.
4. Install Snort:
```bash
sudo apt update && sudo apt install snort -y
```
5. Copy support files:
```bash
sudo cp /etc/snort/*.config ./
sudo cp /etc/snort/*.map ./
sudo cp /etc/snort/threshold.conf ./
```
6. Interface name is `eth0`.

### Linux VM (VirtualBox / UTM)

Install Ubuntu, then follow the same steps as WSL above.

## Validate Configuration

Run this inside Linux after installing Snort:

```bash
sudo snort -T -c snort.conf -i <interface>
```

Replace `<interface>` with the Linux interface name, such as `eth0`, `ens33`,
`enp0s3`, or `wlan0`.

## Run IDS

```bash
sudo snort -A console -q -c snort.conf -i <interface>
```

Or write alerts to files:

```bash
sudo snort -A fast -q -c snort.conf -i <interface> -l /var/log/snort
```

## Test Cases

Generate traffic from another VM when possible:

```bash
ping <victim-ip>
nmap -sS <victim-ip>
telnet <victim-ip> 23
ftp <victim-ip>
curl "http://<victim-ip>/../../../../etc/passwd"
```

Expected custom alert SIDs:

| SID | Detection |
| --- | --- |
| 100001 | ICMP ping |
| 100002 | TCP SYN scan behavior |
| 100003 | Telnet connection attempt |
| 100004 | FTP connection attempt |
| 100005 | HTTP `/etc/passwd` traversal attempt |

## Notes

The repository keeps Snort focused on the custom local signatures for a clean
project demonstration. Stock community/VRT rule includes are commented in
`snort.conf`; enable them only if those rule files are installed in your Linux
Snort environment.
