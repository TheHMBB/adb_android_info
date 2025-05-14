
[English](permission_oprate_en.md) | [简体中文](permission_oprate.md)

# Using ADB Shell to View and Manage Android App Information, Permissions, and App Operations

This comprehensive guide explains how to use the Android Debug Bridge (ADB) `shell` command, in conjunction with tools such as `pm` (Package Manager), `appops` (App Operations), and `dumpsys package`, to retrieve detailed information about apps on an Android device and manage their permissions and App Operations states. These command-line tools offer powerful capabilities for developers, testers, and advanced users to debug, analyze, and control app behavior.

## 1. Prerequisites

Before executing any of the commands in this guide, ensure the following prerequisites are met:

1. **ADB Installed:** You must have the Android SDK Platform-Tools installed on your computer, and the directory containing the ADB binary (typically `platform-tools`) must be added to your system's PATH environment variable. This allows you to run `adb` from any terminal window.
2. **Android Device or Emulator:** Connect an Android device to your computer or start an Android emulator.
3. **Enable USB Debugging:** USB debugging must be enabled in the Developer Options of your Android device. Typically, this requires tapping the "Build number" multiple times under "Settings" > "About phone" to unlock Developer Options.
4. **Authorize the Computer for Debugging:** When the device is first connected with USB debugging enabled, a prompt will appear on the device screen requesting authorization. Grant permission and, if possible, check “Always allow from this computer.”
5. **Verify ADB Connection:** Run `adb devices` from a terminal. If the connection is successful and authorized, the device should appear in the output (e.g., `emulator-5554 device` or `xxxxxxxx device`).

## 2. Finding App Package Names (`adb shell pm list packages`)

To perform operations that target a specific app (like modifying permissions or querying App Ops status), you need the app’s **package name**, such as `com.android.settings` or `com.google.android.youtube`.

The `adb shell pm list packages` command is the most common way to list installed app package names on a device.

**Syntax:**

```bash
adb shell pm list packages [options] [filter]
```

**Common Options:**

* `-f`: Show the path to the APK file.
* `-d`: Show only disabled apps.
* `-e`: Show only enabled apps.
* `-s`: Show only system apps.
* `-3`: Show only third-party (user-installed) apps.
* `-u`: Include uninstalled apps with retained data.
* `[filter]`: Filter package names containing the specified text (case-insensitive).

**Examples:**

* List all app package names:

  ```bash
  adb shell pm list packages
  ```
* List all third-party apps:

  ```bash
  adb shell pm list packages -3
  ```
* List all packages containing "chrome" and show their paths:

  ```bash
  adb shell pm list packages -f chrome
  ```

Once you have the package name, you can use it with the `pm`, `appops`, and `dumpsys package` commands.

## 3. Using `adb shell pm` to Manage Runtime Permissions

The `pm` (Package Manager) tool provides a variety of commands related to app management. Among them, `grant` and `revoke` are used to manage **runtime permissions**, introduced in Android 6.0 (Marshmallow) and later. These permissions are requested by apps at runtime for accessing sensitive features like the camera, location, or contacts.

### 3.1. Runtime Permissions (`grant` / `revoke`)

* **`pm grant <package_name> <permission_name>`**: Grants a specified runtime permission to an app.
* **`pm revoke <package_name> <permission_name>`**: Revokes a specified runtime permission from an app.

**Important Restrictions:**

* You can only grant or revoke permissions that are declared in the app’s `AndroidManifest.xml`.
* On non-rooted devices, `pm grant` mainly simulates user-granted permissions. Force-granting system-level or undeclared permissions usually requires root access.
* `pm revoke` typically works on non-rooted devices for revoking previously granted permissions.

### 3.2. Finding Permission Names

You must know the exact **permission name**, usually starting with `android.permission.` (e.g., `android.permission.READ_EXTERNAL_STORAGE`).

Ways to find permission names:

* **Check Android developer documentation:** This is the most authoritative source.

* **Use `adb shell pm list permissions`:** Lists all known permissions on the device.

  **Syntax:**

  ```bash
  adb shell pm list permissions [options]
  ```

  **Common Options:**

  * `-g`: Group permissions by category.
  * `-d`: Show only dangerous (runtime) permissions.
  * `-u`: Show unknown or undocumented permissions.

  **Example:** List all dangerous permissions by group:

  ```bash
  adb shell pm list permissions -d -g
  ```

* **Use `adb shell dumpsys package <package_name>`:** View all declared permissions of a specific app. Look for the `declared permissions:` section in the output.

  **Example:**

  ```bash
  adb shell dumpsys package com.example.someapp | grep "permission.name="
  ```

### 3.3. `pm grant` and `pm revoke` Examples

**Example 1: Grant camera permission to an app**

```bash
adb shell pm grant com.example.someapp android.permission.CAMERA
```

**Example 2: Revoke read contacts permission**

```bash
adb shell pm revoke com.example.someapp android.permission.READ_CONTACTS
```

**Example 3: Grant read and write external storage permissions**

```bash
adb shell pm grant com.example.someapp android.permission.READ_EXTERNAL_STORAGE
adb shell pm grant com.example.someapp android.permission.WRITE_EXTERNAL_STORAGE
```

Note: For storage access, it's often necessary to grant both read and write permissions if the app requests them.

## 4. Using `adb shell appops` to Manage App Operations

App Operations (App Ops) is a finer-grained permission control mechanism provided by Android. It allows the system or users to control whether certain operations (such as location access, reading the clipboard, or vibrating the device) are permitted, sometimes overriding runtime permissions.

### 4.1. Understanding App Ops States

Each App Op has a name (e.g., `CAMERA`, `READ_CLIPBOARD`, `VIBRATE`) and a state:

* `allow`: Explicitly allows the operation.
* `deny`: Explicitly denies the operation.
* `ignore`: Silently ignores the operation (the app might not receive an error, but the action won't occur).
* `default`: Reverts to the system default behavior, which usually depends on runtime permissions, manifest declarations, and system policies.

### 4.2. Basic `appops` Syntax

```bash
adb shell appops <command> [options] <package_name> [app_op_name] [state]
```

* `<command>`: Action to perform (`get`, `set`, `reset`).
* `[options]`: Optional flags.
* `<package_name>`: The app's package name.
* `[app_op_name]`: Optional App Op name.
* `[state]`: For `set` commands, the new state (`allow`, `deny`, `ignore`, `default`).

### 4.3. Common `appops` Commands

#### 4.3.1. View App Ops State (`get`)

Retrieve the current state of all or a specific App Op for an app.

**Syntax:**

```bash
adb shell appops get <package_name> [app_op_name]
```

**Examples:**

* Get all App Ops states for an app:

  ```bash
  adb shell appops get com.example.someapp
  ```
* Get the state of clipboard access:

  ```bash
  adb shell appops get com.example.someapp READ_CLIPBOARD
  ```

#### 4.3.2. Set App Ops State (`set`)

Change the state of a specific App Op.

**Syntax:**

```bash
adb shell appops set <package_name> <app_op_name> <state>
```

**Examples:**

* Deny location access:

  ```bash
  adb shell appops set com.example.someapp ACCESS_FINE_LOCATION deny
  adb shell appops set com.example.someapp ACCESS_COARSE_LOCATION deny
  ```
* Allow vibrator usage:

  ```bash
  adb shell appops set com.example.someapp VIBRATE allow
  ```
* Reset camera access to default:

  ```bash
  adb shell appops set com.example.someapp CAMERA default
  ```

#### 4.3.3. Reset App Ops (`reset`)

Restore App Ops to their default states.

**Syntax:**

```bash
adb shell appops reset [<package_name>]
```

**Examples:**

* Reset App Ops for a specific app:

  ```bash
  adb shell appops reset com.example.someapp
  ```
* Reset App Ops for all apps (use with caution!):

  ```bash
  adb shell appops reset
  ```

### 4.4. Relationship Between App Ops and Runtime Permissions

This is an important distinction:

* `pm grant`/`revoke` controls whether an app has a certain **runtime permission**.
* `appops set` controls whether an app is **allowed to perform a specific operation**, regardless of permission.

App Ops can override runtime permissions. For example, even if `pm grant` is used to give an app camera permission, if the app’s `CAMERA` App Op is set to `deny`, the app still can’t use the camera.




