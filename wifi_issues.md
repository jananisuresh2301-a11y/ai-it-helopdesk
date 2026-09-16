# Wi-Fi and Network Connectivity Issues

## Intermittent Wi-Fi Disconnects
Symptoms: Connection drops every few minutes, "limited connectivity" warnings,
video calls freezing.

Steps:
1. Move closer to the router to rule out signal strength.
2. Forget the network on the device and reconnect with the password.
3. Update the Wi-Fi adapter driver (Device Manager > Network Adapters on
   Windows; System Report > Network on macOS).
4. Switch the router channel or band (try 5GHz vs 2.4GHz) to avoid
   interference from neighboring networks or cordless phones.
5. Disable Wi-Fi power-saving mode on the adapter.
6. If it persists on one device only, the adapter itself may be failing —
   escalate for hardware replacement.

## No Internet Access but Wi-Fi Connected
Symptoms: Device shows connected to Wi-Fi but pages won't load.

Steps:
1. Restart the router and modem (unplug 30 seconds, plug back in).
2. Run `ipconfig /flushdns` (Windows) or `sudo killall -HUP mDNSResponder`
   (macOS) to clear DNS cache.
3. Try a different DNS server (e.g. 1.1.1.1 or 8.8.8.8).
4. Check if other devices on the same network have internet — isolates
   whether it's device-specific or network-wide.
5. Contact ISP if the outage is network-wide and modem lights show no signal.

## VPN Blocking Local Network Access
Symptoms: Can't reach the internet or local printer only when VPN is on.

Steps:
1. Check if "split tunneling" is enabled in the VPN client.
2. Temporarily disconnect the VPN to confirm it's the cause.
3. Ensure the VPN client is updated to the latest version.
