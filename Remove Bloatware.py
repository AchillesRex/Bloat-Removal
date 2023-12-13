import subprocess
import os
import logging
import json

# Setup logging
logging.basicConfig(filename='debloat_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_powershell_command(command):
    """Execute a PowerShell command from Python and log the output."""
    try:
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, check=True)
        logging.info(f"Executed: {command}\nResult: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing: {command}\n{e}")
        return None
    return result.stdout

def create_system_restore_point():
    """Create a system restore point before making changes."""
    logging.info("Creating system restore point.")
    run_powershell_command("Checkpoint-Computer -Description \"DebloatScriptRestorePoint\"")

def check_system_compatibility():
    """Check if the script is running on a compatible version of Windows."""
    logging.info("Checking system compatibility.")
    version = run_powershell_command("(Get-ComputerInfo).WindowsVersion")
    if not version or not version.startswith('10.0'):  # Assuming Windows 11 starts with '10.0'
        logging.error("Incompatible Windows version. Exiting script.")
        exit(1)

def read_user_preferences():
    """Read user preferences from a configuration file."""
    try:
        with open('user_preferences.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error("User preferences file not found. Using default settings.")
    except json.JSONDecodeError:
        logging.error("Error decoding user preferences. Using default settings.")
    return {}

def uninstall_bloatware(user_prefs):
    """Uninstall bloatware applications based on user preferences."""
    apps_to_remove = user_prefs.get("bloatware", [])
    for app in apps_to_remove:
        run_powershell_command(f"Get-AppxPackage *{app}* | Remove-AppxPackage")

def disable_telemetry_and_services(user_prefs):
    """Disable telemetry and services based on user preferences."""
    services_to_disable = user_prefs.get("services", [])
    for service in services_to_disable:
        run_powershell_command(f"Stop-Service {service}")
        run_powershell_command(f"Set-Service {service} -StartupType Disabled")

def apply_registry_tweaks(user_prefs):
    """Apply registry tweaks based on user preferences."""
    tweaks = user_prefs.get("registry_tweaks", {})
    for path, values in tweaks.items():
        for key, value in values.items():
            value_type = values.get("type", "REG_SZ")
            command = f'reg add "{path}" /v {key} /t {value_type} /d {value} /f'
            os.system(command)
            logging.info(f"Applied registry tweak: {command}")

def disable_unnecessary_features(user_prefs):
    """Disable features based on user preferences."""
    features = user_prefs.get("features", [])
    for feature in features:
        run_powershell_command(feature)

def main():
    """Main function to execute all debloating tasks."""
    try:
        logging.info("Starting Windows 11 debloat script.")
        create_system_restore_point()
        check_system_compatibility()
        user_prefs = read_user_preferences()
        uninstall_bloatware(user_prefs)
        disable_telemetry_and_services(user_prefs)
        apply_registry_tweaks(user_prefs)
        disable_unnecessary_features(user_prefs)
        logging.info("Debloat script completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
