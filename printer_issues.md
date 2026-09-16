# Printer Issues

## Printer Not Found / Offline
Symptoms: Print job stuck in queue, printer shows "offline".

Steps:
1. Confirm the printer is powered on and connected to the same network
   (or USB cable is seated).
2. Restart the print spooler service (Windows: `services.msc` >
   Print Spooler > Restart).
3. Remove and re-add the printer in Settings > Printers & Scanners.
4. Update or reinstall the printer driver from the manufacturer's site.
5. Ping the printer's IP address to confirm it's reachable on the network.

## Print Jobs Stuck in Queue
Symptoms: Documents queue up but never print.

Steps:
1. Cancel all jobs in the print queue.
2. Restart the print spooler service.
3. Clear the spooler folder manually if jobs remain stuck
   (`C:\Windows\System32\spool\PRINTERS` on Windows).
4. Re-send the print job.

## Poor Print Quality
Symptoms: Faded text, streaks, or smudging.

Steps:
1. Run the printer's built-in cleaning/alignment utility.
2. Check ink/toner levels and replace if low.
3. Use manufacturer-recommended paper and check for paper jams affecting
   the rollers.
