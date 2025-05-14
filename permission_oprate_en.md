
[English](permission_oprate_en.md) | [简体中文](permission_oprate.md)

# Viewing and Managing Android App Information, Permissions, and App Operations using ADB Shell

This document is a comprehensive guide on how to use the `shell` command of Android Debug Bridge (ADB), combined with the `pm` (Package Manager), `appops` (App Operations), and `dumpsys package` tools, to obtain detailed information about applications on an Android device and manage their permissions and App Operations states. These command-line tools provide powerful capabilities for developers, testers, and advanced users to debug, analyze, and control app behavior.

## 1. Prerequisites

Before using any commands in this document, you need to meet the following basic conditions:

1.  **ADB Tools Installed:** You need to have the Android SDK Platform-Tools installed on your computer, and the directory containing the ADB tools (usually `platform-tools`) added to your system's PATH environment variable. This allows you to run the `adb` command directly from any command-line window.
2.  **Android Device or Emulator:** Connect an Android device to your computer or start an Android emulator.
3.  **USB Debugging Enabled:** Enable USB debugging in the Developer Options on your Android device. This usually requires tapping the "Build number" multiple times in "Settings" -> "About phone" to unlock Developer Options.
4.  **Authorize Computer for Debugging:** When the device is first connected to your computer with USB debugging enabled, a dialog box will appear on the device screen asking for authorization. Please allow your computer to debug, and it's generally recommended to check "Always allow from this computer".
5.  **Verify ADB Connection:** Open a command-line window on your computer and type `adb devices`. If the device is connected successfully and authorized, you should see your device listed in the output (e.g., `emulator-5554 device` or `xxxxxxxx device`).

## 2. Finding App Package Names (`adb shell pm list packages`)

When performing many operations that require specifying an application (such as modifying permissions, setting App Ops states, or viewing detailed information), you need to know the app's **Package Name**, for example, `com.android.settings` or `com.google.android.youtube`.

The `adb shell pm list packages` command is the most common way to find the package names of installed apps on the device.

**Syntax:**

```bash
adb shell pm list packages [options] [filter]
```

**Common Options:**

*   `-f`: Show the path to the APK file for each package.
*   `-d`: Filter to only show disabled packages.
*   `-e`: Filter to only show enabled packages.
*   `-s`: Filter to only show system packages.
*   `-3`: Filter to only show third-party packages (apps installed by the user).
*   `-u`: Include uninstalled packages that still have data.
*   `[filter]`: Filter the list by package names containing the text in the filter (case-insensitive).

**Examples:**

*   List package names for all apps on the device:
    ```bash
    adb shell pm list packages
    ```
*   List package names for all third-party apps:
    ```bash
    adb shell pm list packages -3
    ```
*   List package names and paths for all packages containing "chrome":
    ```bash
    adb shell pm list packages -f chrome
    ```

Once you have found the target app's package name, you can use it in subsequent `pm`, `appops`, and `dumpsys package` commands.

## 3. Using `adb shell pm` to Manage Runtime Permissions

The `pm` (Package Manager) tool provides a series of commands related to application package management. Among these, `grant` and `revoke` are used to manage **Runtime Permissions**, introduced in Android 6.0 (Marshmallow) and later. Runtime permissions are sensitive permissions (like camera, location, contacts, etc.) that apps must request from the user at runtime.

### 3.1. Runtime Permissions (`grant` / `revoke`)

*   **`pm grant <package_name> <permission_name>`**: Grants the specified runtime permission to the application with the given package name.
*   **`pm revoke <package_name> <permission_name>`**: Revokes the specified runtime permission from the application with the given package name.

**Important Limitations:**

*   You can only grant or revoke permissions that the app has already declared in its `AndroidManifest.xml` file.
*   On non-rooted devices, `pm grant` is primarily used to simulate a user granting permission (i.e., granting a declared but not yet granted runtime permission). Forcing the granting of system permissions or undeclared permissions usually requires Root access.
*   `pm revoke` typically works on non-rooted devices as well, to revoke permissions previously granted by the user or system.

The permission status modified using `pm grant`/`pm revoke` will be reflected in the system's "Settings" -> "Apps" -> [App Name] -> "Permissions" screen.

### 3.2. Finding Permission Names

To use `pm grant` or `pm revoke`, you need to know the exact **Permission Name**, which is a string constant, usually starting with `android.permission.` (e.g., `android.permission.READ_EXTERNAL_STORAGE`).

Methods to obtain permission names:

*   **Consult Android Developer Documentation:** This is the most authoritative source.
*   **Using `adb shell pm list permissions`:** Lists all known permissions on the device.
    **Syntax:**
    ```bash
    adb shell pm list permissions [options]
    ```
    **Common Options:**
    *   `-g`: Group permissions by permission group.
    *   `-d`: Only list dangerous permissions (usually runtime permissions).
    *   `-u`: Only list unknown or undocumented permissions.
    **Example:** List all dangerous permissions and their groups:
    ```bash
    adb shell pm list permissions -d -g
    ```
*   **Using `adb shell dumpsys package <package_name>`:** View all permissions declared by a specific app in its Manifest. Look for the `declared permissions:` section in the output of `dumpsys package <package_name>`.
    **Example:** View permissions declared by an app:
    ```bash
    adb shell dumpsys package com.example.someapp | grep "permission.name="
    ```

### 3.3. `pm grant` and `pm revoke` Examples

**Example 1: Grant camera permission to an app**

Assume the app's package name is `com.example.someapp`.

```bash
adb shell pm grant com.example.someapp android.permission.CAMERA
```

After execution, if you view the app's permission settings screen, the camera permission should appear as granted.

**Example 2: Revoke read contacts permission from an app**

```bash
adb shell pm revoke com.example.someapp android.permission.READ_CONTACTS
```

**Example 3: Grant read and write external storage permissions to an app**

```bash
adb shell pm grant com.example.someapp android.permission.READ_EXTERNAL_STORAGE
adb shell pm grant com.example.someapp android.permission.WRITE_EXTERNAL_STORAGE
```
Note that for storage permissions, you often need to grant both permissions simultaneously if the app declares them.

## 4. Using `adb shell appops` to Manage App Operations

App Operations (App Ops) is a more fine-grained permission control mechanism provided by Android than runtime permissions. It allows the system or the user to control whether an app's calls to specific operations (such as accessing location, reading clipboard, using the vibrator, etc.) are allowed, and can sometimes override the authorization state of runtime permissions.

### 4.1. Understanding App Ops States

Each App Op has a name (like `CAMERA`, `READ_CLIPBOARD`, `VIBRATE`) and a state:

*   `allow`: The operation is explicitly allowed.
*   `deny`: The operation is explicitly denied.
*   `ignore`: The request for the operation is ignored (the app may not receive an error, but the operation won't execute).
*   `default`: Reverts to the system's default behavior. The default behavior usually depends on the runtime permission status, Manifest declarations, and system policies.

### 4.2. `appops` Basic Usage

The basic syntax is:

```bash
adb shell appops <command> [options] <package_name> [app_op_name] [state]
```

*   `<command>`: The operation to perform (`get`, `set`, `reset`).
*   `[options]`: Optional parameters.
*   `<package_name>`: The package name of the app to operate on.
*   `[app_op_name]`: Optional App Op name.
*   `[state]`: For the `set` command, the state to set (`allow`, `deny`, `ignore`, `default`).

### 4.3. Common `appops` Command Details

#### 4.3.1. Viewing App Ops State (`get`)

Gets the current state of an app's App Ops or a specific App Op.

**Syntax:**

```bash
adb shell appops get <package_name> [app_op_name]
```

**Examples:**

*   View the state of all App Ops for an app:
    ```bash
    adb shell appops get com.example.someapp
    ```
*   View the App Op state for an app's clipboard reading function:
    ```bash
    adb shell appops get com.example.someapp READ_CLIPBOARD
    ```

#### 4.3.2. Setting App Ops State (`set`)

Modifies the state of a specific App Op for an app.

**Syntax:**

```bash
adb shell appops set <package_name> <app_op_name> <state>
```

**Examples:**

*   Deny an app access to location information:
    ```bash
    adb shell appops set com.example.someapp ACCESS_FINE_LOCATION deny
    adb shell appops set com.example.someapp ACCESS_COARSE_LOCATION deny
    ```
*   Allow an app to use the vibrator:
    ```bash
    adb shell appops set com.example.someapp VIBRATE allow
    ```
*   Revert the App Op state for an app's camera function to default:
    ```bash
    adb shell appops set com.example.someapp CAMERA default
    ```

#### 4.3.3. Resetting App Ops State (`reset`)

Resets the App Ops states for an app or all apps to their default values.

**Syntax:**

```bash
adb shell appops reset [<package_name>]
```

**Examples:**

*   Reset App Ops states for a specific app:
    ```bash
    adb shell appops reset com.example.someapp
    ```
*   Reset App Ops states for all apps (Use with caution!):
    ```bash
    adb shell appops reset
    ```

### 4.4. Relationship between App Ops and Runtime Permissions

This is an important concept:

*   `pm grant`/`revoke` modifies whether an app is granted a specific runtime permission.
*   `appops set` modifies whether an app is allowed to perform a specific operation when it calls the corresponding API.

App Ops can, to some extent, override runtime permissions. For example, even if you use `pm grant` to give an app camera permission, if the app's `CAMERA` App Op is set to `deny`, the app may still not be able to use the camera. Setting an App Op to `default` typically means the system will fall back to checking the runtime permission status to decide whether to allow the operation.

Therefore, to fully control a sensitive operation, you may need to consider both runtime permissions and App Ops states.

## 5. Using `adb shell dumpsys package` to View App Details

The `dumpsys package` command is used to dump the internal state information of the `PackageManagerService`, which is responsible for managing all applications on the device. Through this command, you can obtain very detailed metadata, configuration, and current status information about a specific application or the entire system's app environment.

### 5.1. `dumpsys package` Basic Usage

There are two main forms:

1.  **Dumping information for a specific app:**
    ```bash
    adb shell dumpsys package <package_name>
    ```
    This is the most commonly used form, outputting detailed information for the specified package name.

2.  **Dumping information for all apps (very verbose):**
    ```bash
    adb shell dumpsys package
    ```
    If no package name is specified, it will attempt to dump information for all installed apps. The output volume is very large and usually needs to be redirected to a file or filtered with other tools.

### 5.2. Viewing Specific App Details (`dumpsys package <package_name>`)

**Syntax:**

```bash
adb shell dumpsys package <package_name>
```

**Example: View detailed information for an app**

Assume the app's package name is `com.example.someapp`.

```bash
adb shell dumpsys package com.example.someapp
```

The output will be very long and includes information such as, but not limited to:

*   **Package Signatures:** Information about the app's signature.
*   **Permissions:**
    *   `declared permissions`: All permissions declared by the app in its Manifest.
    *   `granted permissions`: A list of runtime permissions that have been granted to the app.
*   **Activities, Services, Receivers, Providers:** The various components declared in the app and their status (enabled/disabled).
*   **User IDs:** The app's UID under different users.
*   **Install Path:** The installation path of the app's APK file (`codePath=`).
*   **Version Info:** `versionCode`, `versionName`, `targetSdkVersion`, `minSdkVersion`, etc.
*   **Install Flags:** Some flags related to the installation.
*   **AppData:** Path to the app's data directory, etc.

**Tip:** Due to the large amount of output, it's often necessary to combine this command with `grep` to find specific information.

**Examples:**

*   Find the permissions granted to an app:
    ```bash
    adb shell dumpsys package com.example.someapp | grep "granted=" -A 1
    ```
*   Find the app's installation path and version information:
    ```bash
    adb shell dumpsys package com.example.someapp | grep -E "codePath=|versionName=|versionCode="
    ```
*   Find the status of an app's components (e.g., if an Activity is enabled):
    ```bash
    adb shell dumpsys package com.example.someapp | grep -A 5 "Activity Resolver Table" # Or grep for specific component name
    ```

### 5.3. Other `dumpsys package` List Commands

`dumpsys package` also provides some subcommands for listing global information:

*   **List all system features (`list features`):**
    ```bash
    adb shell dumpsys package list features
    ```
    Lists all hardware and software features supported by the device (e.g., `android.hardware.camera`, `android.software.webview`).

*   **List all shared libraries (`list libraries`):**
    ```bash
    adb shell dumpsys package list libraries
    ```
    Lists shared libraries available on the device.

## 6. Notes and Risks

*   **Use Caution:** Arbitrarily modifying the permissions or App Ops states of system apps or important apps can lead to app crashes, functional abnormalities, or even system instability. When unsure, avoid modifying or use the `default` state.
*   **Root Permissions:** Certain more advanced operations or operations that bypass normal procedures (such as granting undeclared permissions or modifying certain states of system apps) may require the device to have Root permissions.
*   **Version Differences:** The command syntax, available options, and the output format of `dumpsys package` may vary depending on the Android version, device manufacturer, or ROM.
*   **Verbose Output:** The `dumpsys package` command without a package name parameter produces a very large output. Be mindful of redirecting or combining it with `grep` when using it.
*   **UI Reflection:** Modifications made with `pm grant`/`revoke` are usually reflected synchronously in the system's permission management UI. Modifications made with `appops set` may not be directly reflected in all system permission UIs but will affect actual operation.

## 7. Summary

By using ADB Shell in combination with the `pm`, `appops`, and `dumpsys package` tools, you gain powerful control and insight into Android applications:

*   `pm list packages` helps you find the target app's package name.
*   `pm grant` and `pm revoke` allow you to manage the app's runtime permission status.
*   `appops get`, `set`, and `reset` provide more fine-grained operational control, which can override or work in conjunction with runtime permissions.
*   `dumpsys package <package_name>` provides comprehensive detailed information about an app, including permissions, components, version, and installation path.

Mastering these commands is very helpful for Android development, testing, security analysis, and advanced system administration. When using these powerful tools, always understand the purpose of each command and its potential impact.
