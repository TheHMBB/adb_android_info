[English](README_en.md) | [简体中文](README.md)
# ADB Android Permission Viewer

This is a Python script that uses ADB (Android Debug Bridge) to analyze the permissions of installed applications on an Android device. It helps you understand which permissions applications request, their purpose, and their grant status.

## ✨ Features

*   **Interactive Query**: Select analysis scope and output format through simple command-line interactions.
*   **Flexible Application Scope Selection**:
    *   Analyze user-installed apps (intelligently excludes most core system components).
    *   Analyze all installed apps.
    *   Analyze third-party apps only (via `adb shell pm list packages -3`).
    *   Analyze a specific single app (by entering its package name).
*   **Permission Scope Selection**:
    *   List all requested permissions for an app and their status.
    *   Query the status of a specific permission across various apps.
*   **Multiple Output Formats**:
    *   **TXT**: Human-readable text format.
    *   **CSV**: Comma-Separated Values, easy to import into spreadsheets for analysis.
    *   **JSON**: Structured data, convenient for further programmatic processing.
*   **User-Friendly Display**:
    *   Automatically maps permission names to their descriptions (based on a built-in dictionary).
    *   Automatically maps app package names to their common names (based on a built-in dictionary).
*   **Console Output**: Option to print analysis results directly to the console.
*   **Progress Indicator**: Displays a progress bar when processing multiple applications.

## ⚙️ Requirements

1.  **Python 3.x**: The script is written in Python 3.
2.  **ADB (Android Debug Bridge)**:
    *   Ensure ADB is correctly installed.
    *   Ensure ADB's path is added to your system's `PATH` environment variable so the script can call `adb` commands directly.
3.  **Android Device**:
    *   The device must have "Developer options" and "USB debugging" enabled.
    *   When the device is connected to the computer via USB, USB debugging must be authorized for that computer.

## 🚀 How to Use

1.  **Clone or Download the Script**:
    `app_permission_information.py` 

2.  **Customize Dictionaries (Important)**:
    The script includes two important Python dictionaries. It is highly recommended to update and supplement them as needed for more accurate and comprehensive information:
    *   `permission_descriptions`: Maps permission names to their (currently Chinese) descriptions.
        ```python
        permission_descriptions = {
            "android.permission.CAMERA": "允许应用访问摄像头。", // "Allows the app to access the camera."
            # ... more permissions
        }
        ```
    *   `apps_dict`: Maps application package names to their common (currently Chinese) names.
        ```python
        apps_dict = {
            "com.tencent.mm": "微信", // "WeChat"
            # ... more apps
        }
        ```
    

3.  **Run the Script**:
    Open a command-line terminal, navigate to the directory where the script is saved, and run:
    ```bash
    python app_permission_information.py
    ```

4.  **Follow the Prompts**:
    The script will ask you sequentially:
    *   **Select operation**:
        1.  List all granted/denied permissions (Default)
        2.  List status of a specific permission only (If selected, you'll be asked for the permission name)
    *   **Select application scope**:
        1.  User apps (excluding common core system components, Default)
        2.  All installed apps
        3.  Third-party apps only (user-installed)
        4.  Select a single app (If selected, you'll be asked for the package name)
    *   **Select output format**:
        1.  TXT (Default)
        2.  CSV
        3.  JSON
    *   **Output information to console?**:
        1.  Yes
        2.  No (Default)

5.  **View Results**:
    After the script finishes, it will generate a report file in the same directory as the script. The filename will typically be `app_permissions_report.txt`, `app_permissions_report.csv`, or `app_permissions_report.json`.

## 📄 Output Format Description

*   **TXT**:
    ```
    Application Package: com.example.app (Sample App)
    ------------------------------
    Permissions:
        android.permission.CAMERA: Granted, Purpose: Allows the app to access the camera.
          Flags: USER_SET FIXED GRANTED ...
        android.permission.ACCESS_FINE_LOCATION: Not Granted, Purpose: Allows the app to get precise location.
          Flags: USER_SET FIXED ...

    ...
    ```
    *(Note: The "Purpose" will be in Chinese unless you translate the `permission_descriptions` dictionary in the script.)*

*   **CSV**:
    Includes columns: `Package Name`, `App Name`, `Permission Name`, `Granted Status`, `Description`, `Raw Flags`
    *(Note: "App Name" and "Description" will be in Chinese unless dictionaries are translated.)*

*   **JSON**:
    Keyed by application package name (and app name), with values containing a list of all relevant permission information for that app.
    ```json
    {
        "com.example.app (Sample App)": {
            "permissions_info": [
                {
                    "permission": "android.permission.CAMERA",
                    "granted_bool": true,
                    "granted_status_text": "Granted", // Or "已授予" if not translated
                    "description": "Allows the app to access the camera.", // Or Chinese equivalent
                    "raw_flags": "USER_SET FIXED GRANTED ..."
                },
                // ...
            ]
        },
        // ...
    }
    ```
    *(Note: String values like `granted_status_text` and `description` will reflect the language of the dictionaries in the script.)*

## ⚠️ Notes & Troubleshooting

*   **ADB Connection**: If the script reports "adb command not found" or cannot retrieve device information, check if ADB is correctly installed, if the `PATH` environment variable is configured, and if the device is properly connected and authorized.
*   **`dumpsys package` Output**: The output format of `dumpsys package` might vary slightly across different Android versions or device manufacturers. The script attempts to be compatible with common formats, but in extreme cases, parsing logic (in the `get_permissions_for_package` function) might need adjustments.
*   **Performance**: When "All installed apps" is selected, the script might take a considerable amount of time to run, depending on the number of apps installed on the device.
*   **Dictionary Updates**: The quality of the script's output heavily depends on the completeness and accuracy of the `permission_descriptions` and `apps_dict` dictionaries. Update them periodically. For English output, these dictionaries need to be translated.
*   **Permission Status Parsing**: The "Granted Status" parsing primarily relies on the `granted=true/false` flag. For some permissions without this explicit flag (like some install-time fixed permissions), the script attempts to infer status from `flags`, but this might be less precise.

## [ADB management permission document](permission_oprate.md)
---
