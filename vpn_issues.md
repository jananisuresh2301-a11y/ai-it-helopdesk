# VPN Issues

## VPN Won't Connect
Symptoms: Connection attempt times out or fails immediately.

Steps:
1. Confirm internet access works without the VPN.
2. Restart the VPN client application.
3. Check credentials and MFA token haven't expired.
4. Try an alternate VPN gateway/server location if the org offers one.
5. Check for a client software update — outdated clients often fail against
   updated servers.

## VPN Connects but No Access to Internal Resources
Symptoms: VPN shows "connected" but internal sites/shares are unreachable.

Steps:
1. Confirm DNS is resolving internal hostnames (try pinging by IP vs
   hostname).
2. Check split-tunneling configuration.
3. Reconnect — routing tables sometimes fail to apply correctly on connect.
4. Verify the resource itself isn't down for other VPN users.

## Slow Performance Over VPN
Symptoms: Everything works but is very slow.

Steps:
1. Check if split tunneling is disabled, forcing all traffic (including
   non-work traffic) through the VPN.
2. Try a geographically closer VPN gateway.
3. Check local network conditions (Wi-Fi signal, ISP speed) independent of
   VPN.
