[English](README_en.md) | [简体中文](README.md)
# ADB 安卓权限查看工具

这是一个使用 Python 和 ADB (Android Debug Bridge) 来分析安卓设备上已安装应用权限的脚本。它可以帮助您了解应用请求了哪些权限、这些权限的用途以及它们的授予状态。

## ✨ 功能特性

*   **交互式查询**: 通过简单的命令行交互选择分析范围和输出格式。
*   **灵活的应用范围选择**:
    *   分析用户安装的应用（智能排除大部分核心系统组件）。
    *   分析所有已安装的应用。
    *   仅分析第三方应用（通过 `adb shell pm list packages -3`）。
    *   分析指定的单个应用（通过输入包名）。
*   **权限范围选择**:
    *   列出应用的所有已请求权限及其状态。
    *   仅查询特定权限在各应用中的状态。
*   **多种输出格式**:
    *   **TXT**: 人类可读的文本格式。
    *   **CSV**: 逗号分隔值，方便导入电子表格进行分析。
    *   **JSON**: 结构化数据，方便程序进一步处理。
*   **人性化显示**:
    *   自动将权限名称映射到中文用途描述（基于内置字典）。
    *   自动将应用包名映射到中文应用名称（基于内置字典）。
*   **控制台输出**: 可选择是否在控制台实时打印分析结果。
*   **进度提示**: 处理多个应用时显示进度条。

## ⚙️ 环境要求

1.  **Python 3.x**: 脚本使用 Python 3 编写。
2.  **ADB (Android Debug Bridge)**:
    *   确保 ADB 已正确安装。
    *   确保 ADB 的路径已添加到系统的环境变量 `PATH` 中，以便脚本可以直接调用 `adb` 命令。
3.  **安卓设备**:
    *   设备已开启“开发者选项”和“USB调试”模式。
    *   当设备通过 USB 连接到计算机时，已授权计算机进行 USB 调试。

## 🚀 使用方法

1.  **克隆或下载脚本**:
    `app_permission_information.py`

2.  **自定义字典 (重要)**:
    脚本内置了两个重要的 Python 字典，强烈建议您根据需要进行更新和补充，以获得更准确和全面的信息：
    *   `permission_descriptions`: 存储权限名称到其中文用途的映射。
        ```python
        permission_descriptions = {
            "android.permission.CAMERA": "允许应用访问摄像头。",
            # ... 更多权限
        }
        ```
    *   `apps_dict`: 存储应用包名到其中文名称的映射。
        ```python
        apps_dict = {
            "com.tencent.mm": "微信",
            # ... 更多应用
        }
        ```
    

3.  **运行脚本**:
    打开命令行终端，导航到脚本所在的目录，然后运行：
    ```bash
    python app_permission_information.py
    ```

4.  **按照提示操作**:
    脚本会依次询问您：
    *   **选择操作**:
        1.  列出所有已授予/已拒绝的权限 (默认)
        2.  仅列出特定权限的状态 (若选择此项，会要求输入权限名)
    *   **选择应用范围**:
        1.  用户应用 (不含常见核心系统组件, 默认)
        2.  所有已安装应用
        3.  仅第三方应用 (用户自行安装的应用)
        4.  选择单个应用 (若选择此项，会要求输入应用包名)
    *   **选择输出格式**:
        1.  TXT (默认)
        2.  CSV
        3.  JSON
    *   **是否在控制台输出信息**:
        1.  是
        2.  否 (默认)

5.  **查看结果**:
    脚本执行完毕后，会在脚本所在的目录下生成报告文件，文件名通常为 `app_permissions_report.txt`、`app_permissions_report.csv` 或 `app_permissions_report.json`。

## 📄 输出格式说明

*   **TXT**:
    ```
    应用包名: com.example.app (示例应用)
    ------------------------------
    权限：
        android.permission.CAMERA: 已授予, 用途：允许应用访问摄像头。
          Flags: USER_SET FIXED GRANTED ...
        android.permission.ACCESS_FINE_LOCATION: 未授予, 用途：允许应用获取精确的地理位置。
          Flags: USER_SET FIXED ...

    ...
    ```
*   **CSV**:
    包含列：`Package Name`, `App Name`, `Permission Name`, `Granted Status`, `Description`, `Raw Flags`
*   **JSON**:
    以应用包名 (和应用名) 为键，值为包含该应用所有相关权限信息的列表。
    ```json
    {
        "com.example.app (示例应用)": {
            "permissions_info": [
                {
                    "permission": "android.permission.CAMERA",
                    "granted_bool": true,
                    "granted_status_text": "已授予",
                    "description": "允许应用访问摄像头。",
                    "raw_flags": "USER_SET FIXED GRANTED ..."
                },
                // ...
            ]
        },
        // ...
    }
    ```

## ⚠️ 注意事项与故障排除

*   **ADB 连接**: 如果脚本提示 "未找到 adb 命令" 或无法获取设备信息，请检查 ADB 是否正确安装、环境变量是否配置、设备是否正确连接并授权。
*   **`dumpsys package` 输出**: 不同 Android 版本或设备制造商的 `dumpsys package` 输出格式可能略有差异。脚本已尝试兼容常见格式，但极端情况下可能需要调整解析逻辑 (`get_permissions_for_package` 函数)。
*   **性能**: 当选择分析“所有已安装应用”时，脚本可能需要较长时间运行，具体取决于设备上安装的应用数量。
*   **字典更新**: 脚本的输出质量高度依赖于 `permission_descriptions` 和 `apps_dict` 字典的完整性和准确性。请定期更新它们。
*   **权限状态解析**: "Granted Status" 的解析主要依赖 `granted=true/false` 标志。对于某些没有此明确标志的权限（如一些安装时固定的权限），脚本会尝试根据 `flags` 推断，但可能不如前者精确。

## [ADB管理权限文档](permission_oprate.md)
---

