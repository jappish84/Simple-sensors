#
# This Python script monitors the swap usage of a Linux container (LXC) and was created with Google Gemini
#
# **Summary:**
# If the swap usage exceeds a predefined threshold (e.g., 90%), it automatically
# initiates a reboot of the LXC. It's designed to be run periodically via a cron
# job to prevent severe performance degradation caused by excessive swap memory
# consumption, which can occur in resource-constrained environments or due to
# memory leaks.
#
# **Instructions for use:**
# 1.  **Purpose:** Helps mitigate performance issues in LXCs experiencing high swap usage.
# 2.  **Usage:** This script should be run as a cron job at regular intervals (e.g., every 5 minutes).
#     It performs a single check and then exits, avoiding multiple instances.
# 3.  **Getting the script running:**
#     a.  **Save the script:** Save this code as `swap_monitor.py` (e.g., in your home directory: `/home/your_username/swap_monitor.py`).
#     b.  **Make it executable:** Run `chmod +x /home/your_username/swap_monitor.py`
#     c.  **Configure Cron:** Open your crontab with `crontab -e` and add the following line
#         to run the script every 5 minutes, replacing `your_username` with your actual username:
#         `*/5 * * * * /usr/bin/python3 /home/your_username/swap_monitor.py >> /var/log/swap_monitor.log 2>&1`
#     d.  **Tail the logs:** To see the script's output and verify it's running, use:
#         `tail -f /var/log/swap_monitor.log`
# 4.  **Prerequisites:**
#     * If running as a non-root user, requires `sudo` access for `systemctl reboot` configured
#       for that user (preferably NOPASSWD in `/etc/sudoers`).
#     * If running as `root`, `sudo` is not needed for `systemctl reboot`.
#     * The `procps` package (which provides the `free` command) must be installed
#         in the LXC (`sudo apt install procps` on Debian/Ubuntu).
# 5.  **Note:** This is typically a temporary mitigation. The ideal long-term
#     solution is to address the root cause of high swap usage, such as
#     allocating more RAM to the LXC or optimizing the memory consumption of
#     applications running within it (e.g., Frigate).

import subprocess
import time
import sys
from datetime import datetime
current_timestamp = datetime.now()

# --- Configuration ---
SWAP_THRESHOLD_PERCENT = 90  # Reboot if swap usage exceeds this percentage
# CHECK_INTERVAL_SECONDS is no longer used for internal looping,
# as cron handles the execution interval.

# --- Helper Functions ---

def get_swap_usage():
    """
    Retrieves current swap usage from 'free -m' command output.
    Returns (total_swap_mb, used_swap_mb) or (None, None) if parsing fails.
    """
    try:
        # Run 'free -m' command to get memory and swap info in megabytes
        result = subprocess.run(['free', '-m'], capture_output=True, text=True, check=True)
        lines = result.stdout.splitlines()

        total_swap_mb = None
        used_swap_mb = None

        for line in lines:
            # Look for the line starting with 'Swap:'
            if line.startswith('Swap:'):
                # Split the line by spaces and filter out empty strings
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        # Extract total and used swap values
                        total_swap_mb = int(parts[1])
                        used_swap_mb = int(parts[2])
                        return total_swap_mb, used_swap_mb
                    except ValueError:
                        print("Error: Could not parse swap values from 'free -m' output.")
                        return None, None
        print("Error: 'Swap:' line not found in 'free -m' output.")
        return None, None
    except FileNotFoundError:
        print("Error: 'free' command not found. Make sure 'procps' package is installed.")
        return None, None
    except subprocess.CalledProcessError as e:
        print(f"Error running 'free -m': {e}")
        print(f"Stderr: {e.stderr}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred while getting swap usage: {e}")
        return None, None

def reboot_lxc():
    """
    Initiates a reboot of the LXC using systemctl.
    This requires appropriate sudo permissions.
    """
    print(f"Swap usage is at or above {SWAP_THRESHOLD_PERCENT}%. Initiating LXC reboot...")
    try:
        # Use 'sudo systemctl reboot' to reboot the LXC.
        # This command typically requires root privileges.
        subprocess.run(['sudo', 'systemctl', 'reboot'], check=True)
        print("Reboot command sent.")
        # The script will likely terminate here as the system reboots.
        sys.exit(0) # Exit cleanly if reboot command is successful
    except FileNotFoundError:
        print("Error: 'sudo' or 'systemctl' command not found.")
        print("Ensure 'sudo' and 'systemd' are installed and configured.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing reboot command: {e}")
        print(f"Stderr: {e.stderr}")
        print("Please ensure the user running this script has NOPASSWD sudo access for 'systemctl reboot'.")
    except Exception as e:
        print(f"An unexpected error occurred during reboot: {e}")

# --- Main Logic ---

def main():
    print(f "{current_timestamp}"":" "Running swap usage check.")
    print(f"Reboot threshold: {SWAP_THRESHOLD_PERCENT}%")

    total_swap, used_swap = get_swap_usage()

    if total_swap is not None and total_swap > 0:
        swap_percentage = (used_swap / total_swap) * 100
        print(f"Current Swap Usage: {used_swap} MiB / {total_swap} MiB ({swap_percentage:.2f}%)")

        if swap_percentage >= SWAP_THRESHOLD_PERCENT:
            reboot_lxc()
        else:
            print("Swap usage below threshold. No reboot needed.")
    elif total_swap == 0:
        print("No swap space configured or total swap is 0 MiB. No reboots will occur based on swap.")
    else:
        print("Could not retrieve swap usage. Please check logs for errors.")

if __name__ == "__main__":
    main()
