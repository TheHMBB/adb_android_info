
[English](permission_oprate_en.md) | [简体中文](permission_oprate.md)

# 使用 ADB Shell 查看与管理 Android 应用信息、权限及 App Operations

本文档是一份综合指南，介绍如何使用 Android Debug Bridge (ADB) 的 `shell` 命令，结合 `pm` (Package Manager), `appops` (App Operations), 和 `dumpsys package` 工具，来获取 Android 设备上应用程序的详细信息，并管理它们的权限和 App Operations 状态。这些命令行工具为开发者、测试人员和高级用户提供了强大的功能，用于调试、分析和控制应用的行为。

## 1. 前提条件

在使用本文档中的任何命令之前，你需要满足以下基本条件：

1.  **已安装 ADB 工具：** 你的计算机上需要安装 Android SDK Platform-Tools，并且 ADB 工具所在的目录（通常是 `platform-tools`）已添加到系统的 PATH 环境变量中。这允许你在任何命令行窗口直接运行 `adb` 命令。
2.  **Android 设备或模拟器：** 连接一个 Android 设备到计算机，或者启动一个 Android 模拟器。
3.  **启用 USB 调试：** 在 Android 设备的开发者选项中启用 USB 调试。通常需要在“设置”->“关于手机”中连续点击“版本号”多次来解锁开发者选项。
4.  **授权计算机进行调试：** 当设备首次连接到计算机并启用 USB 调试时，设备屏幕上会弹出授权提示。请允许你的计算机进行调试，通常建议勾选“始终允许使用这台计算机进行调试”。
5.  **验证 ADB 连接：** 在计算机的命令行中输入 `adb devices`。如果设备连接成功并被授权，你应该会在输出中看到设备被列出（例如 `emulator-5554 device` 或 `xxxxxxxx device`）。

## 2. 查找应用包名 (`adb shell pm list packages`)

在执行许多需要指定应用的操作（如修改权限、设置 App Ops 状态或查看详细信息）时，你需要知道应用的**包名** (Package Name)，例如 `com.android.settings` 或 `com.google.android.youtube`。

`adb shell pm list packages` 命令是查找设备上已安装应用包名的最常用方法。

**语法:**

```bash
adb shell pm list packages [options] [filter]
```

**常用选项：**

*   `-f`: 显示应用的 APK 文件路径。
*   `-d`: 仅显示已禁用的应用。
*   `-e`: 仅显示已启用的应用。
*   `-s`: 仅显示系统应用。
*   `-3`: 仅显示第三方应用（用户自行安装的应用）。
*   `-u`: 包含已卸载但仍有数据的应用。
*   `[filter]`: 根据包名包含的文本（不区分大小写）进行过滤。

**示例：**

*   列出设备上所有应用的包名：
    ```bash
    adb shell pm list packages
    ```
*   列出所有第三方应用的包名：
    ```bash
    adb shell pm list packages -3
    ```
*   列出所有包含 "chrome" 的包名及其路径：
    ```bash
    adb shell pm list packages -f chrome
    ```

找到目标应用的包名后，你就可以将其用于后续的 `pm`, `appops` 和 `dumpsys package` 命令。

## 3. 使用 `adb shell pm` 管理运行时权限

`pm` (Package Manager) 工具提供了一系列与应用包管理相关的命令，其中 `grant` 和 `revoke` 用于管理 Android 6.0 (Marshmallow) 及更高版本引入的 **运行时权限** (Runtime Permissions)。运行时权限是应用在运行时向用户请求的敏感权限（如相机、位置、联系人等）。

### 3.1. 运行时权限 (`grant` / `revoke`)

*   **`pm grant <package_name> <permission_name>`**: 授予指定包名应用指定的运行时权限。
*   **`pm revoke <package_name> <permission_name>`**: 撤销指定包名应用指定的运行时权限。

**重要限制：**

*   你只能授予或撤销应用已经在其 `AndroidManifest.xml` 文件中声明过的权限。
*   在非 Root 设备上，`pm grant` 主要用于模拟用户授予权限（即授予已声明但未授予的运行时权限）。强制授予系统权限或未声明的权限通常需要 Root 权限。
*   `pm revoke` 通常在非 Root 设备上也可以工作，用于撤销已授予的权限。

### 3.2. 查找权限名称

要使用 `pm grant` 或 `pm revoke`，你需要知道准确的**权限名称**，它是一个字符串常量，通常以 `android.permission.` 开头（例如 `android.permission.READ_EXTERNAL_STORAGE`）。

获取权限名称的方法：

*   **查阅 Android 开发者文档：** 这是最权威的方式。
*   **使用 `adb shell pm list permissions`：** 列出设备上所有已知的权限。
    **语法:**
    ```bash
    adb shell pm list permissions [options]
    ```
    **常用选项：**
    *   `-g`: 按权限组分组显示。
    *   `-d`: 仅显示危险权限（通常是运行时权限）。
    *   `-u`: 仅显示未知或未记录的权限。
    **示例：** 列出所有危险权限及其分组：
    ```bash
    adb shell pm list permissions -d -g
    ```
*   **使用 `adb shell dumpsys package <package_name>`：** 查看特定应用在其 Manifest 中声明的所有权限。在 `dumpsys package <package_name>` 的输出中查找 `declared permissions:` 部分。
    **示例：** 查看某个应用声明的权限：
    ```bash
    adb shell dumpsys package com.example.someapp | grep "permission.name="
    ```

### 3.3. `pm grant` 和 `pm revoke` 示例

**示例 1：授予应用相机权限**

假设应用包名为 `com.example.someapp`。

```bash
adb shell pm grant com.example.someapp android.permission.CAMERA
```

**示例 2：撤销应用读取联系人权限**

```bash
adb shell pm revoke com.example.someapp android.permission.READ_CONTACTS
```

**示例 3：授予应用读写外部存储权限**

```bash
adb shell pm grant com.example.someapp android.permission.READ_EXTERNAL_STORAGE
adb shell pm grant com.example.someapp android.permission.WRITE_EXTERNAL_STORAGE
```
请注意，对于读写存储权限，通常需要同时授予两个权限（如果应用声明了它们）。

## 4. 使用 `adb shell appops` 管理 App Operations

App Operations (App Ops) 是 Android 提供的一种比运行时权限更细粒度的权限控制机制。它允许系统或用户控制应用对特定操作（如访问位置、读取剪贴板、使用振动器等）的调用是否被允许，有时可以覆盖运行时权限的授权状态。

### 4.1. 理解 App Ops 状态

每个 App Op 都有一个名称（如 `CAMERA`, `READ_CLIPBOARD`, `VIBRATE`）和一个状态：

*   `allow`: 明确允许该操作。
*   `deny`: 明确拒绝该操作。
*   `ignore`: 忽略该操作的请求（应用可能不会收到错误，但操作不会执行）。
*   `default`: 恢复到系统默认行为。默认行为通常取决于运行时权限状态、Manifest 声明以及系统策略。
*   `foreground`: 意味着应用只能在其活动界面可见、正在运行前台服务或以其他方式被系统视为在前台时，才能执行该操作。当应用转入后台时，该操作将被限制或拒绝。

### 4.2. `appops` 基本用法

基本语法为：

```bash
adb shell appops <command> [options] <package_name> [app_op_name] [state]
```

*   `<command>`: 要执行的操作 (`get`, `set`, `reset`)。
*   `[options]`: 可选参数。
*   `<package_name>`: 要操作的应用的包名。
*   `[app_op_name]`: 可选的 App Op 名称。
*   `[state]`: 对于 `set` 命令，要设置的状态 (`allow`, `deny`, `ignore`, `default`)。

### 4.3. 常用 `appops` 命令详解

#### 4.3.1. 查看 App Ops 状态 (`get`)

获取一个应用或特定 App Op 的当前状态。

**语法:**

```bash
adb shell appops get <package_name> [app_op_name]
```

**示例：**

*   查看某应用的所有 App Ops 状态：
    ```bash
    adb shell appops get com.example.someapp
    ```
*   查看某应用读取剪贴板功能的 App Op 状态：
    ```bash
    adb shell appops get com.example.someapp READ_CLIPBOARD
    ```

#### 4.3.2. 设置 App Ops 状态 (`set`)

修改应用的特定 App Op 状态。

**语法:**

```bash
adb shell appops set <package_name> <app_op_name> <state>
```

**示例：**

*   禁止某应用访问位置信息：
    ```bash
    adb shell appops set com.example.someapp ACCESS_FINE_LOCATION deny
    adb shell appops set com.example.someapp ACCESS_COARSE_LOCATION deny
    ```
*   允许某应用使用振动器：
    ```bash
    adb shell appops set com.example.someapp VIBRATE allow
    ```
*   将某应用使用相机功能的 App Op 状态恢复到默认：
    ```bash
    adb shell appops set com.example.someapp CAMERA default
    ```

#### 4.3.3. 重置 App Ops 状态 (`reset`)

将一个应用或所有应用的 App Ops 状态恢复到默认值。

**语法:**

```bash
adb shell appops reset [<package_name>]
```

**示例：**

*   重置特定应用的 App Ops 状态：
    ```bash
    adb shell appops reset com.example.someapp
    ```
*   重置所有应用的 App Ops 状态 (慎用！)：
    ```bash
    adb shell appops reset
    ```

### 4.4. App Ops 与运行时权限的关系

这是一个重要的概念：

*   `pm grant`/`revoke` 修改的是应用是否被授予某个运行时权限的状态。
*   `appops set` 修改的是应用执行某个特定操作时是否被允许的状态。

App Ops 可以在一定程度上覆盖运行时权限。例如，即使你使用 `pm grant` 授予了应用相机权限，但如果该应用的 `CAMERA` App Op 被设置为 `deny`，那么应用仍然无法使用相机。将 App Op 设置为 `default` 通常意味着系统会回退到检查运行时权限的状态来决定是否允许该操作。

因此，要完全控制某个敏感操作，你可能需要同时考虑运行时权限和 App Ops 状态。

## 5. 使用 `adb shell dumpsys package` 查看应用详细信息

`dumpsys package` 命令用于转储 `PackageManagerService`（负责管理设备上所有应用的服务）的内部状态信息。通过这个命令，你可以获取关于特定应用或整个系统应用环境的非常详细的元数据、配置和当前状态。

### 5.1. `dumpsys package` 基本用法

主要有两种形式：

1.  **转储特定应用的信息:**
    ```bash
    adb shell dumpsys package <package_name>
    ```
    这是最常用的形式，输出指定包名的应用的详细信息。

2.  **转储所有应用的信息 (非常冗长):**
    ```bash
    adb shell dumpsys package
    ```
    不指定包名时，会转储所有已安装应用的信息。输出量巨大，通常需要重定向或过滤。

### 5.2. 查看特定应用的详细信息 (`dumpsys package <package_name>`)

**语法:**

```bash
adb shell dumpsys package <package_name>
```

**示例：查看某应用的详细信息**

假设应用包名是 `com.example.someapp`。

```bash
adb shell dumpsys package com.example.someapp
```

输出会非常长，包含的信息包括但不限于：

*   **Package Signatures:** 应用的签名信息。
*   **Permissions:**
    *   `declared permissions`: 应用在 Manifest 中声明的所有权限。
    *   `granted permissions`: 应用已被授予的运行时权限列表。
*   **Activities, Services, Receivers, Providers:** 应用中声明的各类组件及其状态（enabled/disabled）。
*   **User IDs:** 应用在不同用户下的 UID。
*   **Install Path:** 应用 APK 文件的安装路径 (`codePath=`)。
*   **Version Info:** `versionCode`, `versionName`, `targetSdkVersion`, `minSdkVersion` 等。
*   **Install Flags:** 安装时的一些标志。
*   **AppData:** 应用数据目录路径等。

**提示：** 由于输出内容庞大，通常需要结合 `grep` 命令来查找特定信息。

**示例：**

*   查找应用已授予的权限：
    ```bash
    adb shell dumpsys package com.example.someapp | grep "granted=" -A 1
    ```
*   查找应用的安装路径和版本信息：
    ```bash
    adb shell dumpsys package com.example.someapp | grep -E "codePath=|versionName=|versionCode="
    ```
*   查找应用的组件状态（例如 Activity 是否启用）：
    ```bash
    adb shell dumpsys package com.example.someapp | grep -A 5 "Activity Resolver Table" # 或者直接搜索组件名
    ```

### 5.3. 其他 `dumpsys package` 列表命令

`dumpsys package` 也提供了一些用于列出全局信息的子命令：

*   **列出所有系统特性 (`list features`):**
    ```bash
    adb shell dumpsys package list features
    ```
    列出设备支持的所有硬件和软件特性（例如 `android.hardware.camera`, `android.software.webview`）。

*   **列出所有共享库 (`list libraries`):**
    ```bash
    adb shell dumpsys package list libraries
    ```
    列出设备上可用的共享库。

## 6. 注意事项和风险

*   **谨慎操作：** 随意修改系统应用或重要应用的权限或 App Ops 状态可能导致应用崩溃、功能异常甚至系统不稳定。在不确定时，避免修改或使用 `default` 状态。
*   **Root 权限：** 某些更高级或绕过正常流程的操作（例如授予未声明的权限，或修改系统应用的某些状态）可能需要设备具有 Root 权限。
*   **版本差异：** 命令的语法、可用选项以及 `dumpsys package` 的输出格式可能随 Android 版本、设备制造商或 ROM 的不同而变化。
*   **输出冗长：** 不带包名参数的 `dumpsys package` 命令会产生巨大的输出，使用时注意重定向或结合 `grep`。
*   **UI 反映：** `pm grant`/`revoke` 的修改通常会在系统的权限管理 UI 中同步显示。`appops set` 的修改可能不会在所有系统的权限 UI 中直接反映，但会影响实际操作。

## 7. 总结

通过 ADB Shell 结合 `pm`, `appops`, 和 `dumpsys package` 工具，你可以获得对 Android 应用的强大控制和洞察能力：

*   `pm list packages` 帮助你找到目标应用的包名。
*   `pm grant` 和 `pm revoke` 允许你管理应用的运行时权限状态。
*   `appops get`, `set`, 和 `reset` 提供更细粒度的操作控制，可以覆盖或配合运行时权限。
*   `dumpsys package <package_name>` 提供应用的全面详细信息，包括权限、组件、版本和安装路径等。

熟练掌握这些命令对于 Android 开发、测试、安全分析和高级系统管理非常有帮助。在使用这些强大的工具时，请务必理解每个命令的作用及其潜在影响。


