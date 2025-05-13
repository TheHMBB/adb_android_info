# 使用adb获取安卓应用的权限信息
# 本程序最好放在adb工具所在目录下执行
import subprocess
import os
import csv
import json
import re

# 权限用途字典 (确保这个字典是完整的或你能提供的最新版)
permission_descriptions = {
    "android.permission.CAMERA": "允许应用访问摄像头。",
    "android.permission.ACCESS_FINE_LOCATION": "允许应用获取精确的地理位置。",
    "android.permission.ACCESS_COARSE_LOCATION": "允许应用获取粗略的地理位置。",
    "android.permission.RECORD_AUDIO": "允许应用录制音频。",
    "android.permission.READ_CONTACTS": "允许应用读取联系人信息。",
    "android.permission.WRITE_CONTACTS": "允许应用修改联系人信息。",
    "android.permission.GET_ACCOUNTS": "允许应用访问设备上的账户列表。",
    "android.permission.WRITE_EXTERNAL_STORAGE": "允许应用写入外部存储。",
    "android.permission.READ_EXTERNAL_STORAGE": "允许应用读取外部存储。",
    "android.permission.BLUETOOTH": "允许应用访问蓝牙设备。",
    "android.permission.BLUETOOTH_ADMIN": "允许应用配置本地蓝牙设备。",
    "android.permission.INTERNET": "允许应用访问网络。",
    "android.permission.ACCESS_NETWORK_STATE": "允许应用查看网络连接状态。",
    "android.permission.CHANGE_NETWORK_STATE": "允许应用更改网络连接状态。",
    "android.permission.ACCESS_WIFI_STATE": "允许应用查看 Wi-Fi 状态。",
    "android.permission.CHANGE_WIFI_STATE": "允许应用更改 Wi-Fi 状态。",
    "android.permission.SEND_SMS": "允许应用发送短信。",
    "android.permission.RECEIVE_SMS": "允许应用接收短信。",
    "android.permission.READ_SMS": "允许应用读取短信内容。",
    "android.permission.RECEIVE_MMS": "允许应用接收彩信。",
    "android.permission.READ_PHONE_STATE": "允许应用读取设备的电话状态。",
    "android.permission.CALL_PHONE": "允许应用直接拨打电话号码。",
    "android.permission.ANSWER_PHONE_CALLS": "允许应用接听来电（Android 8.0+）。",
    "android.permission.PROCESS_OUTGOING_CALLS": "允许应用在外拨电话时进行监控或重定向（已废弃）。",
    "android.permission.USE_SIP": "允许应用使用 SIP VoIP 服务。",
    "android.permission.SYSTEM_ALERT_WINDOW": "允许应用显示在其他应用上方的悬浮窗。",
    "android.permission.VIBRATE": "允许应用控制振动。",
    "android.permission.FOREGROUND_SERVICE": "允许应用在前台运行服务。",
    "android.permission.REQUEST_INSTALL_PACKAGES": "允许应用请求安装其他应用。",
    "android.permission.WAKE_LOCK": "允许应用防止手机进入休眠状态。",
    "android.permission.WRITE_SETTINGS": "允许应用修改系统设置（需用户手动授权）。",
    "android.permission.RECEIVE_BOOT_COMPLETED": "允许应用在系统启动后自动启动。",
    "android.permission.MANAGE_EXTERNAL_STORAGE": "允许应用访问外部存储中的所有文件（Android 11+ 特殊权限）。",
    "android.permission.READ_CALL_LOG": "允许应用读取通话记录。",
    "android.permission.WRITE_CALL_LOG": "允许应用修改通话记录。",
    "android.permission.USE_FINGERPRINT": "允许应用使用指纹识别（旧 API）。",
    "android.permission.USE_BIOMETRIC": "允许应用使用生物识别硬件（Android 10+）。",
    "android.permission.PACKAGE_USAGE_STATS": "允许应用查看其他应用的使用情况（需手动授权）。",
    "android.permission.ACTIVITY_RECOGNITION": "允许应用获取用户的身体活动信息（如步行、跑步）。",
    "android.permission.BODY_SENSORS": "允许应用访问身体传感器（如心率监测器）。",
    "android.permission.ACCESS_BACKGROUND_LOCATION": "允许应用在后台访问位置信息（Android 10+）。",
    "android.permission.SCHEDULE_EXACT_ALARM": "允许应用安排精确的定时任务（Android 12+）。",
    # --- 网络与连接 ---
    "android.permission.NFC": "允许应用通过近距离无线通讯（NFC）进行操作。",
    "android.permission.CHANGE_WIFI_MULTICAST_STATE": "允许应用进入 Wi-Fi 多播模式。",
    "android.permission.NEARBY_WIFI_DEVICES": "允许应用查找并连接到附近的 Wi-Fi 设备（Android 12+）。", # Android 12新增
    "android.permission.BLUETOOTH_SCAN": "允许应用扫描附近的蓝牙设备（Android 12+）。", # Android 12新增
    "android.permission.BLUETOOTH_ADVERTISE": "允许应用向附近的蓝牙设备广播（Android 12+）。", # Android 12新增
    "android.permission.BLUETOOTH_CONNECT": "允许应用连接到已配对的蓝牙设备（Android 12+）。", # Android 12新增
    "android.permission.UWB_RANGING": "允许应用与附近的超宽带（UWB）设备进行测距（Android 12+）。", # Android 12新增
    # --- 媒体与存储 ---
    "android.permission.READ_MEDIA_IMAGES": "允许应用读取设备上的图片文件（Android 13+）。", # Android 13新增
    "android.permission.READ_MEDIA_VIDEO": "允许应用读取设备上的视频文件（Android 13+）。", # Android 13新增
    "android.permission.READ_MEDIA_AUDIO": "允许应用读取设备上的音频文件（Android 13+）。", # Android 13新增
    "android.permission.ACCESS_MEDIA_LOCATION": "允许应用访问共享存储中媒体文件的地理位置信息（Android 10+）。",
    "android.permission.MANAGE_MEDIA": "允许应用管理媒体文件，如修改或删除（通常需要系统或签名权限）。",
    # --- 日历 ---
    "android.permission.READ_CALENDAR": "允许应用读取用户的日历数据。",
    "android.permission.WRITE_CALENDAR": "允许应用修改或添加用户的日历事件。",
    # --- 账户与凭据 ---
    # "android.permission.GET_ACCOUNTS_PRIVILEGED": "允许应用访问设备上的账户列表，包括特权账户（特权权限）。", # GET_ACCOUNTS 已有，这个是特权版
    "android.permission.READ_SYNC_SETTINGS": "允许应用读取同步设置。",
    "android.permission.WRITE_SYNC_SETTINGS": "允许应用修改同步设置。",
    "android.permission.AUTHENTICATE_ACCOUNTS": "允许应用作为账户验证器（通常用于账户管理应用）。", # 已被 AccountManager API 取代部分功能
    "android.permission.MANAGE_ACCOUNTS": "允许应用管理账户验证器列表（已被 AccountManager API 取代）。", # 已废弃
    "android.permission.USE_CREDENTIALS": "允许应用从账户管理器请求身份验证令牌（已被 AccountManager API 取代）。", # 已废弃
    # --- 设备状态与信息 ---
    "android.permission.READ_PHONE_NUMBERS": "允许应用读取设备的电话号码（Android 11+，需要用户授权）。",
    "android.permission.READ_PRIVILEGED_PHONE_STATE": "允许应用读取特权的电话状态，包括电话号码、IMEI等（特权权限）。",
    "android.permission.BATTERY_STATS": "允许应用收集电池使用统计信息。",
    "android.permission.DUMP": "允许应用检索系统服务的状态转储信息（通常用于调试）。",
    "android.permission.READ_LOGS": "允许应用读取低级别系统日志文件（通常需要系统或签名权限）。",
    # --- 系统与应用交互 ---
    "android.permission.KILL_BACKGROUND_PROCESSES": "允许应用结束其他应用的后台进程。",
    "android.permission.REORDER_TASKS": "允许应用更改任务的 Z 轴顺序。",
    "android.permission.SET_WALLPAPER": "允许应用设置壁纸。",
    "android.permission.SET_WALLPAPER_HINTS": "允许应用设置壁纸提示。",
    "com.android.launcher.permission.INSTALL_SHORTCUT": "允许应用在启动器中添加快捷方式。",
    "com.android.launcher.permission.UNINSTALL_SHORTCUT": "允许应用从启动器中移除快捷方式。",
    "android.permission.EXPAND_STATUS_BAR": "允许应用展开或折叠状态栏。",
    "android.permission.MODIFY_AUDIO_SETTINGS": "允许应用修改全局音频设置，如音量和振铃模式。",
    "android.permission.SET_ALARM": "允许应用设置闹钟。",
    "android.permission.DISABLE_KEYGUARD": "允许应用禁用锁屏（如果非安全锁屏）。", # 在新版中受限
    "android.permission.GET_PACKAGE_SIZE": "允许应用获取任何应用占用的空间大小（已废弃）。",
    "android.permission.CLEAR_APP_CACHE": "允许应用清除其他应用的缓存（需要系统权限）。",
    "android.permission.DELETE_PACKAGES": "允许应用删除其他应用（需要系统权限或用户确认）。",
    "android.permission.INSTALL_LOCATION_PROVIDER": "允许应用向位置管理器安装位置提供程序（需要系统权限）。",
    "android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS": "允许应用请求用户将其添加到电池优化的白名单中。",
    "android.permission.START_ACTIVITIES_FROM_BACKGROUND": "允许应用从后台启动 Activity (Android 10+ 有限制)。",
    # --- 通知 ---
    "android.permission.ACCESS_NOTIFICATION_POLICY": "允许应用访问通知策略，如勿扰模式。",
    "android.permission.BIND_NOTIFICATION_LISTENER_SERVICE": "允许应用绑定到通知监听器服务，以接收通知事件。", # 需要用户在设置中手动开启
    # --- 传感器 (更细致的) ---
    "android.permission.BODY_SENSORS_BACKGROUND": "允许应用在后台访问身体传感器数据（Android 12+）。",
    "android.permission.HIGH_SAMPLING_RATE_SENSORS": "允许应用以高于每秒200次的频率访问传感器数据（Android 12+）。",
    # --- 其他特定权限 ---
    "android.permission.CAMERA_OPEN_CLOSE_LISTENER": "允许应用监听摄像头的打开和关闭事件（Android 13+）。",
    "android.permission.RECORD_BACKGROUND_AUDIO": "允许应用在后台录制音频（Android 10+，需要前台服务）。",
    "android.permission.MANAGE_ONGOING_CALLS": "允许应用管理正在进行的通话（Android 10+，通常用于电话应用）。",
    "android.permission.READ_BASIC_PHONE_STATE_AND_NUMBERS": "允许应用读取基本电话状态和号码（组合权限，Android 12+）。",
    "android.permission.HIDE_OVERLAY_WINDOWS": "允许应用隐藏其他应用绘制的悬浮窗（需要系统权限，Android 12+）。",
    "android.permission.POST_NOTIFICATIONS": "允许应用发送通知（Android 13+，运行时权限）。", # 你已有的列表里是 FOREGROUND_SERVICE，这个是直接发通知的权限
    "android.permission.READ_VOICEMAIL": "允许应用读取语音邮件。",
    "android.permission.WRITE_VOICEMAIL": "允许应用修改或添加语音邮件。",
    "com.android.voicemail.permission.ADD_VOICEMAIL": "允许应用向系统中添加语音邮件。",
    "android.permission.USE_FULL_SCREEN_INTENT": "允许应用使用全屏 Intent，通常用于来电或闹钟等高优先级通知（Android 10+）。",
    "android.permission.REQUEST_COMPANION_RUN_IN_BACKGROUND": "允许配套设备应用在后台运行。",
    "android.permission.REQUEST_COMPANION_USE_DATA_IN_BACKGROUND": "允许配套设备应用在后台使用数据。",
    "android.permission.NFC_TRANSACTION_EVENT": "允许应用接收 NFC 交易事件。",
    "android.permission.NFC_PREFERRED_PAYMENT_INFO": "允许应用读取 NFC 首选支付信息。",
    "android.permission.QUERY_ALL_PACKAGES": "允许应用查询设备上安装的所有应用（Android 11+，受限）。",
    "android.permission.ACCESS_BROADCAST_RADIO": "允许应用访问广播电台（如FM/AM）。",
    "android.permission.ACCESS_CACHE_FILESYSTEM": "允许应用访问缓存文件系统。（系统级）",
    "android.permission.ACCESS_CHECKIN_PROPERTIES": "允许应用访问签入属性（用于设备注册和报告）。（系统级）",
    "android.permission.ACCESS_CONTEXT_HUB": "允许应用访问Context Hub，用于低功耗传感器数据处理。",
    "android.permission.ACCESS_DOWNLOAD_MANAGER": "允许应用访问下载管理器并下载文件。",
    "android.permission.ACCESS_GPU_SERVICE": "允许应用访问GPU服务。（系统级）",
    "android.permission.ACCESS_INSTANT_APPS": "允许应用查询和与即时应用交互。",
    "android.permission.ACCESS_KEYGUARD_SECURE_STORAGE": "允许应用访问与锁屏相关的安全存储。（系统级）",
    "android.permission.ACCESS_LOCATION_EXTRA_COMMANDS": "允许应用向位置提供程序发送额外命令。（系统级）",
    "android.permission.ACCESS_NOTIFICATIONS": "允许应用访问通知信息（功能受限，不如通知监听器）。（系统级）",
    "android.permission.ACCESS_VENDOR_LOG_CONTROL": "允许应用控制对供应商日志的访问。（系统级）",
    "android.permission.ALLOW_PLACE_IN_MULTI_PANE_SETTINGS": "允许应用在多窗格设置中放置UI元素。（系统级）",
    "android.permission.BACKUP": "允许应用执行备份操作。（系统级）",
    "android.permission.BIND_ATTENTION_SERVICE": "允许应用绑定到注意力服务（例如屏幕注视检测）。",
    "android.permission.BIND_CELL_BROADCAST_SERVICE": "允许应用绑定到小区广播服务。",
    "android.permission.BIND_CONNECTION_SERVICE": "允许应用绑定到ConnectionService，用于电话/呼叫管理。",
    "android.permission.BIND_INCALL_SERVICE": "允许应用绑定到InCallService，用于提供通话界面。",
    "android.permission.BIND_JOB_SERVICE": "允许应用绑定到JobService，用于调度后台任务。",
    "android.permission.BIND_NETWORK_RECOMMENDATION_SERVICE": "允许应用绑定到网络推荐服务。",
    "android.permission.BIND_REMOTE_LOCKSCREEN_VALIDATION_SERVICE": "允许应用绑定到远程锁屏验证服务。",
    "android.permission.BIND_ROTATION_RESOLVER_SERVICE": "允许应用绑定到屏幕旋转决策服务。",
    "android.permission.BIND_SETTINGS_SUGGESTIONS_SERVICE": "允许应用绑定到提供设置建议的服务。",
    "android.permission.BLUETOOTH_PRIVILEGED": "允许应用执行特权蓝牙操作。（系统级）",
    "android.permission.BROADCAST_CALLLOG_INFO": "允许应用广播通话记录信息。（系统级）",
    "android.permission.BROADCAST_CLOSE_SYSTEM_DIALOGS": "允许应用广播关闭系统对话框的意图。（系统级）",
    "android.permission.BROADCAST_PHONE_ACCOUNT_REGISTRATION": "允许应用广播电话账户注册事件。（系统级）",
    "android.permission.BROADCAST_STICKY": "允许应用发送粘性广播（已废弃）。",
    "android.permission.CALL_PRIVILEGED": "允许应用拨打特权电话（如紧急呼叫）。（系统级）",
    "android.permission.CAPTURE_AUDIO_OUTPUT": "允许应用捕获设备输出的音频。（系统级）",
    "android.permission.CAPTURE_VIDEO_OUTPUT": "允许应用捕获设备输出的视频。（系统级）",
    "android.permission.CHANGE_APP_IDLE_STATE": "允许应用更改其他应用的空闲状态。（系统级）",
    "android.permission.CHANGE_CONFIGURATION": "允许应用更改设备配置（如区域、字体大小）。（系统级）",
    "android.permission.CLEAR_APP_USER_DATA": "允许应用清除其他应用的用户数据。（系统级）",
    "android.permission.CONFIRM_FULL_BACKUP": "允许应用确认完整的备份/恢复操作。",
    "android.permission.CONFIGURE_DISPLAY_COLOR_MODE": "允许应用配置显示颜色模式。（系统级）",
    "android.permission.CONFIGURE_WIFI_DISPLAY": "允许应用配置Wi-Fi Display（Miracast）。（系统级）",
    "android.permission.CONNECTIVITY_INTERNAL": "允许应用进行内部连接管理操作。（系统级）",
    "android.permission.CONNECTIVITY_USE_RESTRICTED_NETWORKS": "允许应用使用受限网络。（系统级）",
    "android.permission.CONTROL_DISPLAY_COLOR_TRANSFORMS": "允许应用控制显示颜色转换。（系统级）",
    "android.permission.CONTROL_INCALL_EXPERIENCE": "允许应用控制通话中的用户体验。（系统级）",
    "android.permission.CONTROL_UI_TRACING": "允许应用控制UI跟踪（用于调试）。（系统/开发权限）",
    "android.permission.CONTROL_VPN": "允许应用控制VPN连接。（系统级）",
    "android.permission.COPY_PROTECTED_DATA": "允许应用复制受保护的数据。（系统级）",
    "android.permission.CUSTOMIZE_SYSTEM_UI": "允许应用自定义系统UI元素。（系统级）",
    "android.permission.DEVICE_POWER": "允许应用控制设备电源状态。（系统级）",
    "android.permission.ENFORCE_UPDATE_OWNERSHIP": "允许应用强制更新所有权。（系统级）",
    "android.permission.FLASHLIGHT": "允许应用访问手电筒。",
    "android.permission.FORCE_STOP_PACKAGES": "允许应用强制停止其他应用包。（系统级）",
    "android.permission.FOREGROUND_SERVICE_DATA_SYNC": "允许应用在前台运行数据同步服务。",
    "android.permission.FOREGROUND_SERVICE_MEDIA_PROJECTION": "允许应用在前台运行媒体投影服务（屏幕捕获/共享）。",
    "android.permission.FOREGROUND_SERVICE_SYSTEM_EXEMPTED": "允许前台服务免除某些系统限制。（系统级）",
    "android.permission.GET_REMOTE_ID": "允许应用获取远程标识符。",
    "android.permission.GET_TASKS": "允许应用获取当前运行的任务列表（已废弃，功能受限）。",
    "android.permission.HANDLE_CALL_INTENT": "允许应用处理呼叫意图。（系统级）",
    "android.permission.HANDLE_CAR_MODE_CHANGES": "允许应用处理车载模式更改。（系统级）",
    "android.permission.HANDLE_QUERY_PACKAGE_RESTART": "允许应用处理关于包重启的查询。（系统级）",
    "android.permission.HARDWARE_TEST": "允许应用执行硬件测试。（系统级）",
    "android.permission.HIDE_NON_SYSTEM_OVERLAY_WINDOWS": "允许应用隐藏非系统覆盖窗口。（系统级）",
    "android.permission.INJECT_EVENTS": "允许应用注入按键和触摸事件。（系统级，高度敏感）",
    "android.permission.INSTALL_DYNAMIC_SYSTEM": "允许应用安装动态系统更新（DSU）。（系统级）",
    "android.permission.INSTALL_PACKAGES": "允许应用请求安装其他应用包。",
    "android.permission.INTERACT_ACROSS_USERS": "允许应用与当前用户以外的其他用户进行交互。（系统级）",
    "android.permission.INTERACT_ACROSS_USERS_FULL": "允许应用与当前用户以外的其他用户进行完全交互。（系统级）",
    "android.permission.INTERNAL_SYSTEM_WINDOW": "允许应用创建内部系统窗口。（系统级）",
    "android.permission.LAUNCH_MULTI_PANE_SETTINGS_DEEP_LINK": "允许应用启动到多窗格设置的深层链接。（系统级）",
    "android.permission.LIST_ENABLED_CREDENTIAL_PROVIDERS": "允许应用列出已启用的凭据提供程序。（系统级）",
    "android.permission.LOADER_USAGE_STATS": "允许应用访问加载程序使用情况统计信息。（系统级）",
    "android.permission.LOCAL_MAC_ADDRESS": "允许应用访问设备的本地MAC地址。（系统级）",
    "android.permission.LOCATION_HARDWARE": "允许应用直接访问位置硬件（如GPS芯片）。（系统级）",
    "android.permission.LOG_COMPAT_CHANGE": "允许应用记录兼容性更改。（系统级）",
    "android.permission.MAINLINE_NETWORK_STACK": "与通过Mainline更新的网络堆栈相关的权限。（系统级）",
    "android.permission.MANAGE_ACTIVITY_STACKS": "允许应用管理活动堆栈（已废弃，系统专用）。",
    "android.permission.MANAGE_ACTIVITY_TASKS": "允许应用管理活动任务和堆栈。（系统级）",
    "android.permission.MANAGE_APP_HIBERNATION": "允许应用管理应用休眠状态。（系统级）",
    "android.permission.MANAGE_APP_OPS_MODES": "允许应用管理App Ops模式。（系统级）",
    "android.permission.MANAGE_APP_OPS_RESTRICTIONS": "允许应用管理App Ops限制。（系统级）",
    "android.permission.MANAGE_DEBUGGING": "允许应用控制调试功能（如ADB）。（系统级）",
    "android.permission.MANAGE_DEVICE_ADMINS": "允许应用管理设备管理员应用。（系统级）",
    "android.permission.MANAGE_DYNAMIC_SYSTEM": "允许应用管理动态系统更新（DSU）。（系统级）",
    "android.permission.MANAGE_FINGERPRINT": "允许应用管理指纹数据。（系统级，旧API）",
    "android.permission.MANAGE_NETWORK_POLICY": "允许应用管理网络策略（如数据限制）。（系统级）",
    "android.permission.MANAGE_NOTIFICATION_LISTENERS": "允许应用管理通知监听器服务。（系统级）",
    "android.permission.MANAGE_NOTIFICATIONS": "允许应用管理通知（如渠道、勿扰模式）。（系统级）",
    "android.permission.MANAGE_PROFILE_AND_DEVICE_OWNERS": "允许应用管理配置文件和设备所有者。（系统级）",
    "android.permission.MANAGE_ROLE_HOLDERS": "允许应用管理系统角色的持有者。（系统级）",
    "android.permission.MANAGE_SCOPED_ACCESS_DIRECTORY_PERMISSIONS": "允许应用管理作用域访问目录权限。（系统级）",
    "android.permission.MANAGE_USB": "允许应用管理USB连接和设备。（系统级）",
    "android.permission.MANAGE_USER_OEM_UNLOCK_STATE": "允许应用管理用户的OEM解锁状态。（系统级）",
    "android.permission.MANAGE_USERS": "允许应用管理设备上的用户（创建、删除、切换）。（系统级）",
    "android.permission.MANAGE_WIFI_NETWORK_SELECTION": "允许应用管理Wi-Fi网络选择。（系统级）",
    "android.permission.MASTER_CLEAR": "允许应用执行恢复出厂设置。（系统级）",
    "android.permission.MEDIA_CONTENT_CONTROL": "允许应用控制媒体内容的播放。",
    "android.permission.MEDIA_RESOURCE_OVERRIDE_PID": "允许应用覆盖媒体资源管理的PID。（系统级）",
    "android.permission.MODEMSERVICE": "允许应用访问调制解调器服务。（系统级）",
    "android.permission.MODIFY_AUDIO_ROUTING": "允许应用修改音频路由。（系统级）",
    "android.permission.MODIFY_NETWORK_ACCOUNTING": "允许应用修改网络流量统计数据。（系统级）",
    "android.permission.MODIFY_PHONE_STATE": "允许应用修改电话状态（如开关飞行模式，非常强大）。（系统级）",
    "android.permission.MOUNT_UNMOUNT_FILESYSTEMS": "允许应用挂载和卸载文件系统。（系统级）",
    "android.permission.MOVE_PACKAGE": "允许应用在存储位置之间移动应用包。（系统级）",
    "android.permission.NETWORK_SETTINGS": "允许应用访问网络设置。（系统级）",
    "android.permission.OBSERVE_GRANT_REVOKE_PERMISSIONS": "允许应用观察权限授予/撤销事件。（系统级）",
    "android.permission.OEM_UNLOCK_STATE": "允许应用访问OEM解锁状态。（系统级）",
    "android.permission.OVERRIDE_WIFI_CONFIG": "允许应用覆盖Wi-Fi配置。（系统级）",
    "android.permission.PEERS_MAC_ADDRESS": "允许应用访问对等设备的MAC地址（如Wi-Fi Direct）。（系统级）",
    "android.permission.QUERY_ADMIN_POLICY": "允许应用查询设备管理员策略。",
    "android.permission.QUERY_AUDIO_STATE": "允许应用查询音频状态。（系统级）",
    "android.permission.READ_APP_SPECIFIC_LOCALES": "允许应用读取应用特定的区域设置配置。（系统级）",
    "android.permission.READ_BASIC_PHONE_STATE": "允许应用读取基本的电话状态（READ_PHONE_STATE的子集）。",
    "android.permission.READ_BLOCKED_NUMBERS": "允许应用读取已阻止的电话号码列表。",
    "android.permission.READ_CLIPBOARD_IN_BACKGROUND": "允许应用在后台读取剪贴板内容。（系统级，高度敏感）",
    "android.permission.READ_COMPAT_CHANGE_CONFIG": "允许应用读取兼容性更改配置。（系统级）",
    "android.permission.READ_DEVICE_CONFIG": "允许应用读取设备配置值。（系统级）",
    "android.permission.READ_DREAM_STATE": "允许应用读取Daydream（屏幕保护程序）的状态。",
    "android.permission.READ_DREAM_SUPPRESSION": "允许应用读取Daydream抑制状态。（系统级）",
    "android.permission.READ_EFS": "允许应用读取EFS（加密文件系统）分区。（系统级）",
    "android.permission.READ_FRAME_BUFFER": "允许应用直接读取帧缓冲区。（系统级，高度敏感）",
    "android.permission.READ_INSTALLED_SESSION_PATHS": "允许应用读取已安装包会话的路径。（系统级）",
    "android.permission.READ_MEDIA_VISUAL_USER_SELECTED": "允许应用读取用户明确选择的视觉媒体文件（图片和视频，Android 14+）。",
    "android.permission.READ_OEM_UNLOCK_STATE": "允许应用读取OEM解锁状态。（系统级）",
    "android.permission.READ_PRECISE_PHONE_STATE": "允许应用读取精确的电话状态（比READ_PHONE_STATE更敏感）。（系统/特权级）",
    "android.permission.READ_PRINT_SERVICES": "允许应用读取可用的打印服务。",
    "android.permission.READ_PROFILE": "允许应用读取用户个人资料数据。",
    "android.permission.READ_PROJECTION_STATE": "允许应用读取屏幕投影状态。（系统级）",
    "android.permission.READ_SAFETY_CENTER_STATUS": "允许应用读取安全中心的状态。",
    "android.permission.READ_SEARCH_INDEXABLES": "允许应用提供数据以供系统搜索索引。",
    "android.permission.READ_SIMLOCKINFO": "允许应用读取SIM卡锁定信息。（系统/特权级）",
    "android.permission.READ_SYNC_STATS": "允许应用读取同步统计信息。",
    "android.permission.READ_USER_DICTIONARY": "允许应用读取用户自定义词典。",
    "android.permission.REAL_GET_TASKS": "允许应用获取当前运行任务的更详细信息（比GET_TASKS更特权）。（系统级）",
    "android.permission.REBOOT": "允许应用重启设备。（系统级）",
    "android.permission.RECOVERY": "允许应用执行恢复操作。（系统级）",
    "android.permission.REMAP_MODIFIER_KEYS": "允许应用重新映射修饰键。（系统级）",
    "android.permission.REMOVE_TASKS": "允许应用移除任务（已废弃）。（系统级）",
    "android.permission.REQUEST_DELETE_PACKAGES": "允许应用请求删除其他应用包。",
    "android.permission.REQUEST_NETWORK_SCORES": "允许应用请求网络评分（如Wi-Fi质量）。",
    "android.permission.RESTART_WIFI_SUBSYSTEM": "允许应用重启Wi-Fi子系统。（系统级）",
    "android.permission.SEND_SAFETY_CENTER_UPDATE": "允许应用向安全中心发送更新。",
    "android.permission.SEND_SHOW_SUSPENDED_APP_DETAILS": "允许应用发送意图以显示已暂停应用的详细信息。（系统级）",
    "android.permission.SET_KEYBOARD_LAYOUT": "允许应用设置键盘布局。（系统级）",
    "android.permission.SET_MEDIA_KEY_LISTENER": "允许应用设置媒体按键监听器。（系统级）",
    "android.permission.SET_POINTER_SPEED": "允许应用设置指针速度。（系统级）",
    "android.permission.SET_TIME": "允许应用设置系统时间。（系统级）",
    "android.permission.SET_WALLPAPER_COMPONENT": "允许应用设置壁纸组件。（系统级）",
    "android.permission.SHUTDOWN": "允许应用关闭设备。（系统级）",
    "android.permission.START_VIEW_APP_FEATURES": "允许应用启动一个活动以查看应用特定功能或设置。",
    "android.permission.STATUS_BAR": "允许应用控制状态栏（已废弃，使用STATUS_BAR_SERVICE）。（系统级）",
    "android.permission.STATUS_BAR_SERVICE": "允许应用访问和管理状态栏服务。（系统级）",
    "android.permission.STOP_APP_SWITCHES": "允许应用阻止应用切换（例如用于自助服务终端模式）。（系统级）",
    "android.permission.SUBSTITUTE_NOTIFICATION_APP_NAME": "允许应用在通知中替换其名称（例如用于工作资料）。",
    "android.permission.SUGGEST_MANUAL_TIME_AND_ZONE": "允许应用建议手动设置时间和时区。（系统级）",
    "android.permission.TEST_BLACKLISTED_PASSWORD": "允许应用测试密码是否在黑名单中（用于设备管理）。（系统级）",
    "android.permission.TETHER_PRIVILEGED": "允许应用执行特权网络共享操作。（特权级）",
    "android.permission.UNLIMITED_TOASTS": "允许应用显示无速率限制的Toast通知。（系统级）",
    "android.permission.UPDATE_APP_OPS_STATS": "允许应用更新App Ops统计信息。（系统级）",
    "android.permission.UPDATE_DEVICE_STATS": "允许应用更新设备统计信息。（系统级）",
    "android.permission.UPDATE_PACKAGES_WITHOUT_USER_ACTION": "允许应用在没有用户交互的情况下更新包。（系统级）",
    "android.permission.USE_BIOMETRIC_INTERNAL": "允许系统内部使用生物识别硬件。（系统级）",
    "android.permission.USE_COLORIZED_NOTIFICATIONS": "允许应用使用彩色通知。（系统级）",
    "android.permission.USE_ICC_AUTH_WITH_DEVICE_IDENTIFIER": "允许应用使用ICC（SIM卡）身份验证和设备标识符。（系统级）",
    "android.permission.USE_RESERVED_DISK": "允许应用使用保留的磁盘空间。（系统级）",
    "android.permission.USER_ACTIVITY": "允许应用监视用户活动/应用转换（已废弃，系统专用）。",
    "android.permission.WRITE_APN_SETTINGS": "允许应用写入APN（接入点名称）设置。（系统级）",
    "android.permission.WRITE_BLOCKED_NUMBERS": "允许应用写入已阻止的电话号码列表。",
    "android.permission.WRITE_EFS": "允许应用写入EFS（加密文件系统）分区（高度敏感）。（系统级）",
    "android.permission.WRITE_MEDIA_STORAGE": "允许应用写入媒体存储（已废弃，应使用分区存储）。（系统级）",
    "android.permission.WRITE_SECURE_SETTINGS": "允许应用写入安全系统设置。（系统/签名/开发权限）",
    "android.permission.WRITE_USER_DICTIONARY": "允许应用写入用户自定义词典。",
    "android.permission.ZDM_RECOVERY_REBOOT": "ZTE设备管理权限，允许重启到恢复模式。（系统级）", # 重复出现，取一次
    "android.permission.ZTE_AIENGINE_MANAGEMENT": "ZTE AI引擎管理权限。",
    "android.permission.ZTE_AIENGINE_VISITOR": "ZTE AI引擎访客访问权限。",
    "android.permission.ZTE_CALL_FORWARD": "ZTE特定权限，用于呼叫转移功能。",
    "android.permission.ZTE_CONFERENCE_CALL": "ZTE特定权限，用于会议通话功能。",
    "android.permission.ZTE_HEARTYSERVICE_MANAGEMENT": "ZTE HeartyService管理权限。",
    "android.permission.ZTE_HS_INTERFACE": "ZTE HeartyService接口权限。",
    "android.permission.ZTE_MANAGE_NOTIFICATION": "ZTE特定权限，用于管理通知。",
    "android.permission.ZTE_MMS_SEND": "ZTE特定权限，用于发送彩信。",
    "android.permission.ZTE_WRITE_MSG": "ZTE特定权限，用于写入消息。",
    "android.permission.provider.aiProduct": "自定义内容提供程序权限，可能与AI产品相关。",
    "alarmclock.permission.MY_BROADCAST": "闹钟应用自定义权限，用于接收其自身的广播。",
    "com.android.calendar.permission.ACCESS_PROVIDER": "日历应用内容提供程序的访问权限。",
    "com.android.certinstaller.INSTALL_AS_USER": "证书安装程序权限，允许为用户安装证书。",
    "com.android.keychain.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "钥匙串应用内部权限，用于未导出的动态广播接收器。",
    "com.android.phone.permission.ACCESS_LAST_KNOWN_CELL_ID": "电话应用权限，允许访问最后已知的蜂窝ID。",
    "com.android.settings.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "设置应用内部权限，用于未导出的动态广播接收器。",
    "com.android.systemui.permission.MFVKEYGUARD": "SystemUI权限，与中兴MyFlyOS锁屏相关。", # 重复出现，取一次
    "com.android.systemui.permission.fileprovider": "SystemUI的文件提供程序权限。", # 重复出现，取一次
    "com.android.ztescreenshot.permission.SCREENSHOT": "中兴截图应用的截图权限。",
    "com.google.android.googleapps.permission.GOOGLE_AUTH": "Google应用套件权限，用于Google身份验证。",
    "com.google.android.material.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Google Material Design组件库内部权限，用于未导出的动态广播接收器。",
    "com.qti.permission.RECEIVE_ESSENTIAL_RECORDS_LOADED": "高通特定权限，用于接收基本记录已加载的通知。",
    "com.qti.permission.RECEIVE_MSIM_VOICE_CAPABILITY_CHANGED": "高通特定权限，用于接收MSIM语音能力更改的通知。",
    "com.qualcomm.qti.permission.USE_EXT_TELEPHONY_SERVICE": "高通特定权限，允许使用扩展电话服务。",
    "com.wapi.permission.ACCESS_CERTIFICATE": "允许应用访问WAPI（无线局域网鉴别和保密基础结构）证书。",
    "com.zte.emode.permission.ENGINEER_RECEIVER": "中兴工程模式的接收器权限。",
    "com.zte.emode.permission.PHONE_INTERFACE": "中兴工程模式的电话接口访问权限。",
    "com.zte.emode.permission.START_ENTERENCE": "中兴工程模式的启动入口权限。",
    "com.zte.faceverify.permission.START_ACTIVITY": "中兴人脸验证权限，允许启动相关活动。",
    "com.zte.halo.permission.halospeechservice": "中兴Halo功能的语音服务权限。",
    "com.zte.heartyservice.permission.READ_SETTINGS": "中兴HeartyService读取其设置的权限。",
    "com.zte.heartyservice.permission.WRITE_SETTINGS": "中兴HeartyService写入其设置的权限。",
    "com.zte.mfvkeyguard.read": "中兴MyFlyOS锁屏读取权限。",
    "com.zte.mfvkeyguard.write": "中兴MyFlyOS锁屏写入权限。",
    "com.zte.multscr.permission.ACCESS_PROVIDER": "中兴多屏功能的提供程序访问权限。",
    "com.zte.permission.zgesture": "中兴Z手势功能权限。",
    "com.zte.service.powerful.permission.ACCESS_RETRIEVE_SERVICE": "中兴“强大服务”的检索服务访问权限。",
    "com.zte.theme.permission.fileprovider": "中兴主题应用的文件提供程序权限。",
    "com.zte.weather.permission.READ_WEATHER_DATA": "中兴天气应用读取天气数据的权限。", # 重复出现，取一次
    "com.zte.zsound.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "中兴ZSound应用内部权限，用于未导出的动态广播接收器。",
    "android.intent.category.MASTER_CLEAR.permission.C2D_MESSAGE": "非常特定的权限，似乎与接收用于恢复出厂设置的C2D消息相关。",
    "launchermfv.permission.UPDATE_LIMIT_APPS": "中兴MyFlyOS启动器权限，用于更新应用限制。",
    "launchermfv.permission.USE_BACKUP_RESTORE": "中兴MyFlyOS启动器权限，用于使用备份恢复功能。",
    "mfvsettings.permission.FINGERPRINT": "中兴MyFlyOS设置的指纹相关权限。",
    "mipop.permission.BACK_GESTURE": "中兴Mi-Pop悬浮球功能的返回手势权限。",
    "org.zx.AuthComp.permission.GET_USER_INFO": "自定义认证组件获取用户信息的权限。",
    "sensor.service.permission.FLOAT_WINDOW": "传感器服务显示悬浮窗的自定义权限。",
    "setupwizard.permission.SEND_BROADCAST": "设置向导发送广播的权限。",
    "suggest.permission.provider.read": "自定义建议提供程序的读取权限。",
    "systemui.permission.read_pedometer": "SystemUI读取计步器数据的权限。",
    "theme.permission.LOCAL_RESOURCE": "主题应用访问本地资源的权限。",
    "windowreply.permission.RECEIVE_MESSAGE": "窗口回复组件接收消息的自定义权限。",
    "zte.com.cn.filer.permission.START_ACTIVITY": "中兴文件管理器启动活动的权限。",
    "zte.permission.ACCESS_FAST_PAIR_PROVIDER": "中兴访问快速配对提供程序的权限。",
    "zte.permission.ACCESS_POWER_SAVER_OPTIMIZE": "中兴访问省电优化设置的权限。",
    "zte.permission.BIND_DATA_COLLECTION": "中兴绑定到数据收集服务的权限。", # 重复出现，取一次
    "zte.permission.FINGERPRINT": "中兴指纹功能权限。",
    "zte.permission.IGNORE_FAILED_ATTEMPTS": "中兴忽略解锁失败尝试的权限。",
    "zte.permission.LINK_BOOST_RECEIVER": "中兴Link Boost功能的接收器权限。",
    "zte.permission.LINK_BOOST_SENDER": "中兴Link Boost功能的发送器权限。",
    "zte.permission.READ_POWER_SAVER_APPS": "中兴读取省电应用列表的权限。",
    "zte.permission.READ_STRATEGY": "中兴读取策略组件的权限。",
    "zte.permission.WRITE_STRATEGY": "中兴写入策略组件的权限。",
    "cmb.pb.permission.C2D_MESSAGE": "招商银行掌上生活应用接收云端到设备消息（推送通知）的权限。",
    "android.permission.CONTROL_DEVICE_STATE": "允许应用控制设备当前的状态，如是否处于交互模式。（系统级）",
    "search.permission.signature.openweb": "系统搜索应用以签名权限打开网页的权限。",
    "android.permission.READ_INSTALL_SESSIONS": "允许应用读取当前活动的安装会话信息。",
    "android.permission.GET_PROCESS_STATE_AND_OOM_SCORE": "允许应用获取进程状态和内存不足（OOM）得分。（系统级）",
    "android.permission.NOTIFY_PENDING_SYSTEM_UPDATE": "允许应用通知用户有待处理的系统更新。（系统级）",
    "com.yulore.permission.BIND_YULORE_SERVICE": "允许应用绑定到Yulore（电话邦）服务，通常用于号码识别。",
    "android.permission.CHANGE_COMPONENT_ENABLED_STATE": "允许应用更改其他应用组件（如活动、服务）的启用状态。（系统级，谨慎使用）",
    "com.google.android.gms.magictether.permission.DISABLE_SOFT_AP": "Google Play服务权限，允许Magic Tether功能禁用软AP（热点）。",
    "com.smile.gifmaker.permission.KW_SDK_BROADCAST": "快手应用内部KWAI SDK相关的广播权限。",
    "com.google.android.googlequicksearchbox.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Google搜索应用内部使用的、未导出的动态广播接收器权限。",
    "com.google.android.gm.permission.AUTO_SEND": "Gmail应用权限，可能用于自动发送邮件（如预定发送）。",
    "com.google.android.gms.permission.ACTIVITY_RECOGNITION": "Google Play服务权限，允许检测用户活动状态（如步行、驾车）。",
    "android.permission.MANAGE_CAMERA": "允许应用管理摄像头访问，可能包括禁用摄像头。（系统级）",
    "com.android.vending.billing.IN_APP_NOTIFY.permission.C2D_MESSAGE": "Google Play商店应用内购买通知相关的云端到设备消息权限。",
    "com.android.imsserviceentitlement.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "IMS服务授权应用内部使用的、未导出的动态广播接收器权限。",
    "android.permission.BIND_EUICC_SERVICE": "允许应用绑定到eUICC（嵌入式SIM卡）服务，用于管理eSIM。",
    "theme.permission.READ_DOWNLOADED_RESOURCE": "主题应用读取已下载资源的权限。",
    "com.zte.mifavor.miboard.openadsdk.permission.TT_PANGOLIN": "中兴MiFavor画板应用集成穿山甲广告SDK并接收相关消息的权限。",
    "com.android.nfc.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "NFC服务应用内部使用的、未导出的动态广播接收器权限。",
    "com.zte.cn.zteshare.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "中兴ZTE Share应用内部使用的、未导出的动态广播接收器权限。",
    "com.google.android.vending.verifier.ACCESS_VERIFIER": "Google Play商店应用验证程序访问权限。",
    "com.google.android.gms.permission.GROWTH": "Google Play服务权限，可能与用户增长或应用推广相关。",
    "com.google.android.finsky.permission.INSTANT_APP_STATE": "Google Play商店访问即时应用状态的权限。",
    "android.permission.CACHE_CONTENT": "允许应用缓存内容。（系统级）",
    "com.zte.quickrt.provider.READ_PROVIDER": "中兴QuickRT应用的内容提供程序读取权限。",
    "android.permission.NFC_SET_CONTROLLER_ALWAYS_ON": "允许应用设置NFC控制器始终开启。（系统级）",
    "android.permission.REQUEST_UNIQUE_ID_ATTESTATION": "允许应用请求唯一设备ID的证明。（系统级）",
    "android.permission.ACCESS_ADSERVICES_ATTRIBUTION": "允许应用访问广告服务的归因信息 (Android 13+)。",
    "com.google.android.gms.common.internal.SHARED_PREFERENCES_PERMISSION": "Google Play服务内部共享首选项的访问权限。",
    "android.permission.BIND_CARRIER_SERVICES": "允许应用绑定到运营商服务。",
    "android.permission.FOREGROUND_SERVICE_PHONE_CALL": "允许应用在前台运行电话呼叫相关的服务 (Android 12+)。",
    "cn.com.chsi.chsiapp.permission.liantian.RECEIVE": "学信网App“联天”功能接收消息的权限。",
    "zte.permission.PUSH_MESSAGE.a65254e": "中兴设备特定推送消息权限（哈希值可能代表特定服务或应用）。",
    "android.permission.CONFIGURE_DISPLAY_BRIGHTNESS": "允许应用配置屏幕亮度。（系统级）",
    "com.chinamobile.mcloud.permission.MM_MESSAGE": "中国移动和彩云应用内部消息传递权限。",
    "quickcall.permission.dataprovider": "快速呼叫应用的自定义数据提供程序权限。",
    "org.zx.AuthComp.permission.START_VERIFY_CODE": "自定义认证组件启动验证码流程的权限。",
    "quickcall.permission.openaty": "快速呼叫应用打开特定活动（Activity）的权限。",
    "android.permission.WRITE_SOCIAL_STREAM": "允许应用写入社交信息流数据（已废弃）。",
    "android.permission.REQUEST_COMPANION_PROFILE_GLASSES": "允许应用请求与智能眼镜类配套设备关联的配置文件。",
    "com.google.android.gms.permission.APPINDEXING": "Google Play服务权限，用于应用索引，使应用内容可被Google搜索发现。",
    "android.permission.USE_ATTESTATION_VERIFICATION_SERVICE": "允许应用使用证明验证服务。（系统级）",
    "android.permission.MANAGE_TEST_NETWORKS": "允许应用管理测试网络。（系统级）",
    "android.permission.MANAGE_DEVICE_POLICY_DEBUGGING_FEATURES": "允许应用管理设备策略中的调试功能。（系统级）",
    "com.android.ext.adservices.api.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Android广告服务API扩展内部使用的、未导出的动态广播接收器权限。",
    "com.zte.smarthome.AGOO": "中兴智能家居应用使用AGOO推送服务的权限。",
    "com.android.egg.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Android彩蛋应用内部使用的、未导出的动态广播接收器权限。",
    "mfvsettings.permission.SEARCH": "中兴MyFlyOS设置应用的搜索功能权限。",
    "com.android.hotspot2.osulogin.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Hotspot 2.0 OSU登录应用内部使用的、未导出的动态广播接收器权限。",
    "com.android.gallery3d.permission.VIEW_SEARCH": "旧版Android图库应用查看搜索结果的权限。",
    "com.google.android.gms.permission.CONTACTS_SYNC_DELEGATION": "Google Play服务权限，允许代理联系人同步。",
    "com.google.android.xmpp.permission.BROADCAST": "Google XMPP服务广播权限。",
    "android.permission.UPDATE_FONTS": "允许应用更新系统字体。（系统级）",
    "android.permission.GET_APP_OPS_STATS": "允许应用获取App Ops（应用操作）统计信息。（系统级）",
    "android.permission.SIGNAL_REBOOT_READINESS": "允许应用发出重启准备就绪的信号。（系统级）",
    "lf.example.wubi.openadsdk.permission.TT_PANGOLIN": "示例五笔输入法应用集成穿山甲广告SDK的权限。",
    "android.permission.BIND_HOTWORD_DETECTION_SERVICE": "允许应用绑定到热词检测服务（如语音唤醒）。",
    "com.jingdong.app.mall.permission.MIPUSH_RECEIVE": "京东商城应用接收小米推送（MiPush）消息的权限。",
    "android.permission.ACCESS_SHORTCUTS": "允许应用访问启动器快捷方式信息。",
    "com.tencent.mm.wear.message": "微信应用与可穿戴设备（如智能手表）传递消息的权限。",
    "android.permission.UNLIMITED_SHORTCUTS_API_CALLS": "允许应用无限制调用快捷方式API。（系统级）",
    "android.permission.UPDATE_LOCK_TASK_PACKAGES": "允许应用更新锁定任务模式下的应用列表。（系统级）",
    "android.permission.EXECUTE_APP_ACTION": "允许应用执行应用操作（App Actions）。",
    "android.permission.START_TASKS_FROM_RECENTS": "允许应用从最近任务列表启动任务。（系统级）",
    "com.cmcc.cmvideo.permission.PUSH_PROVIDER": "咪咕视频应用作为推送提供程序的权限。",
    "com.android.providers.media.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "媒体提供程序应用内部使用的、未导出的动态广播接收器权限。",
    "com.ss.android.ugc.aweme.permission.READ_ACCOUNT": "抖音应用读取账户信息的权限。",
    "com.ume.browser.openadsdk.permission.TT_PANGOLIN": "UME浏览器应用集成穿山甲广告SDK的权限。",
    "cn.gov.tax.its.push.permission.MESSAGE": "国家税务总局ITS应用推送消息权限。",
    "androidx.constraintlayout.widget.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "AndroidX ConstraintLayout库内部使用的、未导出的动态广播接收器权限。",
    "cmb.pb.permission.FIN_APPLET_RECEIVER": "招商银行掌上生活金融小程序接收器权限。",
    "com.zte.heartyservice.permission.ANTI_VIRUS": "中兴HeartyService反病毒相关权限。",
    "baidu.push.permission.WRITE_PUSHINFOPROVIDER.com.tmri.app.main": "交管12123应用写入百度推送信息的提供程序权限。",
    "com.smile.gifmaker.permission.AGREE_PRIVACY_PERMISSION": "快手应用同意隐私政策的权限（可能是内部标记）。",
    "com.tencent.qzone.permission.notify": "QQ空间应用发送通知的权限。",
    "cn.ecooktwo.permission.C2D_MESSAGE": "网上厨房应用接收云端到设备消息（推送通知）的权限。",
    "com.zte.voicesecretary.permission.importAudio": "中兴语音秘书导入音频的权限。",
    "com.tencent.mm.ext.permission.READ": "微信应用扩展模块的读取权限。",
    "android.permission.PROVIDE_DEFAULT_ENABLED_CREDENTIAL_SERVICE": "允许应用作为默认启用的凭据服务提供者。（系统级）",
    "com.tencent.mm.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "微信应用内部使用的、未导出的动态广播接收器权限。",
    "android.permission.ACCESS_FPS_COUNTER": "允许应用访问FPS（每秒帧数）计数器。（开发/测试权限）",
    "com.icbc.permission.FIN_APPLET_RECEIVER": "工商银行应用金融小程序接收器权限。",
    "zte.permission.Calendar_SCHEDULE_ALERT": "中兴日历日程提醒权限。",
    "android.permission.DOMAIN_VERIFICATION_AGENT": "允许应用作为域名验证代理。（系统级）",
    "com.ume.browser.permission.PUSH_PROVIDER": "UME浏览器应用作为推送提供程序的权限。",
    "launchermfv.permission.Z_RECOVER_SERVICE": "中兴MyFlyOS启动器Z-Recover服务权限。",
    "com.google.android.gms.people.permission.contactssync.BACKUP_SYNC_STATE_UPDATE_BROADCAST": "Google Play服务联系人同步备份状态更新广播权限。",
    "com.android.bluetooth.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "蓝牙应用内部使用的、未导出的动态广播接收器权限。",
    "cn.gov.tax.its.permission.PROCESS_PUSH_MSG": "国家税务总局ITS应用处理推送消息的权限。",
    "android.permission.BIND_CONTROLS": "允许应用绑定到设备控制服务（如智能家居控制）。",
    "android.permission.REQUEST_INCIDENT_REPORT_APPROVAL": "允许应用请求批准事件报告。（系统级）",
    "android.permission.REQUEST_COMPANION_PROFILE_COMPUTER": "允许应用请求与计算机类配套设备关联的配置文件。",
    "com.google.android.projection.gearhead.permission.START_PROJECTED_ACTIVITY": "Android Auto (Gearhead) 启动投射活动的权限。",
    "com.zte.wallet.support.permission.LAUNCH_WECHAT_PAY": "中兴钱包应用启动微信支付的权限。",
    "com.autonavi.minimap.permission.MIPUSH_RECEIVE": "高德地图应用接收小米推送（MiPush）消息的权限。",
    "android.permission.REGISTER_WINDOW_MANAGER_LISTENERS": "允许应用注册窗口管理器监听器。（系统级）",
    "nubia.permission.neostore.downloadmanager": "努比亚应用商店下载管理器权限。",
    "android.permission.REQUEST_COMPANION_SELF_MANAGED": "允许应用请求自我管理的配套设备连接。",
    "android.permission.PACKET_KEEPALIVE_OFFLOAD": "允许应用使用数据包保活卸载功能，以减少网络唤醒。",
    "android.permission.WRITE_SMS": "允许应用写入短信。（已废弃，使用SEND_SMS）",
    "android.permission.ACCESS_ALL_DOWNLOADS": "允许应用访问所有下载内容，包括其他应用的。（系统级，谨慎）",
    "com.tencent.mm.permission.C2D_MESSAGE": "微信应用接收云端到设备消息（推送通知）的权限。",
    "launchermfv.permission.USE_ONLINE_RECEIVER": "中兴MyFlyOS启动器使用在线接收器的权限。",
    "android.permission.CAPTURE_TUNER_AUDIO_INPUT": "允许应用捕获调谐器（如电视、收音机）的音频输入。（系统级）",
    "android.permission.ACCESS_PDB_STATE": "允许应用访问PDB（策略数据库）状态。（系统级）",
    "android.permission.ACCESS_TV_SHARED_FILTER": "允许应用访问电视共享过滤器。（系统级）",
    "android.permission.SET_CLIP_SOURCE": "允许应用设置剪贴板内容的来源。（系统级）",
    "android.permission.SUPPRESS_CLIPBOARD_ACCESS_NOTIFICATION": "允许应用抑制剪贴板访问通知。（系统级）",
    "android.permission.MODIFY_ADSERVICES_STATE": "允许应用修改广告服务状态 (Android 13+)。",
    "com.smile.gifmaker.PERMISSION_UPDATE_SDK_CONFIG": "快手应用更新SDK配置的权限。",
    "com.chinamobile.mcloud.permission.PROCESS_PUSH_MSG": "中国移动和彩云应用处理推送消息的权限。",
    "com.taobao.taobao.push.permission.MESSAGE": "淘宝应用推送消息权限。",
    "android.permission.CAPTURE_VOICE_COMMUNICATION_OUTPUT": "允许应用捕获语音通信的输出音频。（系统级）",
    "com.google.android.permission.BROADCAST_DATA_MESSAGE": "Google应用广播数据消息的权限。",
    "com.google.android.gms.vehicle.permission.SHARED_AUTO_SENSOR_DATA": "Google Play服务车载模式共享汽车传感器数据的权限。",
    "miboard.permission.other.provider": "中兴画板应用其他内容提供程序权限。",
    "android.permission.ADD_ALWAYS_UNLOCKED_DISPLAY": "允许应用添加始终解锁的显示器。（系统级）",
    "com.zte.heartyservice.permission.AUTO_FILL": "中兴HeartyService自动填充相关权限。",
    "com.google.android.apps.gsa.nga.permissions.EDIT_PREFERENCES": "Google App (NGA - Now/Google Assistant) 编辑偏好设置的权限。",
    "com.zte.mfvkeyguard.write.step": "中兴MyFlyOS锁屏写入计步数据的权限。",
    "android.permission.UPDATE_DEVICE_MANAGEMENT_RESOURCES": "允许应用更新设备管理资源。（系统级）",
    "com.cmcc.cmvideo.openadsdk.permission.TT_PANGOLIN": "咪咕视频应用集成穿山甲广告SDK的权限。",
    "com.google.android.gms.permission.GRANT_WALLPAPER_PERMISSIONS": "Google Play服务授予壁纸相关权限的权限。",
    "android.permission.APPROVE_INCIDENT_REPORTS": "允许应用批准事件报告。（系统级）",
    "android.permission.MANAGE_FACTORY_RESET_PROTECTION": "允许应用管理恢复出厂设置保护（FRP）。（系统级）",
    "com.android.healthconnect.controller.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "健康连接控制器应用内部使用的、未导出的动态广播接收器权限。",
    "com.zte.faceverify.permission.PROVIDER": "中兴人脸验证应用的内容提供程序权限。",
    "com.google.android.gms.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Google Play服务内部使用的、未导出的动态广播接收器权限。",
    "android.permission.SEND_SMS_NO_CONFIRMATION": "允许应用在没有用户确认的情况下发送短信。（系统/签名级，高风险）",
    "zte.permission.LAUNCH_POWER_SAVER_ACTIVITY": "中兴设备启动省电模式活动的权限。",
    "android.permission.CREATE_USERS": "允许应用创建新用户。（系统级）",
    "android.permission.ACCESS_TELEPHONY_SIMINFO_DB": "允许应用访问电话SIM卡信息数据库。（系统级）",
    "contactsprovider.permission.WRITE_CALL_PHONE_RECORD": "联系人提供程序写入通话记录的权限。",
    "android.permission.SET_ALWAYS_FINISH": "允许应用设置活动在完成后立即销毁。（开发/测试权限）",
    "com.mi.health.permission.RECEIVER_PROCESS_MESSAGE": "小米健康应用接收和处理消息的权限。",
    "android.permission.SET_UNRESTRICTED_KEEP_CLEAR_AREAS": "允许应用设置不受限制的保持清晰区域。（系统级）",
    "com.qualcomm.qti.qccauthmgr.permission.QCCAUTHMGR": "高通QCC认证管理器权限。",
    "android.permission.MANAGE_CLOUDSEARCH": "允许应用管理云搜索服务。（系统级）",
    "com.qti.permission.RECEIVE_SMS_CALLBACK_MODE": "高通特定权限，用于接收短信回调模式通知。",
    "android.permission.HDMI_CEC": "允许应用访问和控制HDMI-CEC（消费电子控制）。",
    "com.lemon.lv.permission.BEIZI_AD": "剪映（Lemon LV）应用与“贝兹广告”相关的权限。",
    "android.permission.BYPASS_ROLE_QUALIFICATION": "允许应用绕过角色资格检查。（系统级）",
    "com.unionpay.permission.PUSH_PROVIDER": "云闪付（银联）应用作为推送提供程序的权限。",
    "android.ext.services.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Android扩展服务内部使用的、未导出的动态广播接收器权限。",
    "com.greenpoint.android.mc10086.activity.backtrace.warmed_up": "中国移动10086 App内部性能优化（预热）相关的权限。",
    "com.tencent.smartdevice.permission.broadcast": "腾讯智能设备平台广播权限。",
    "android.permission.PERFORM_CDMA_PROVISIONING": "允许应用执行CDMA网络配置。（系统级）",
    "android.permission.SET_DEFAULT_ACCOUNT_FOR_CONTACTS": "允许应用为联系人设置默认账户。（系统级）",
    "com.jingdong.app.mall.permission.PROCESS_PUSH_MSG": "京东商城应用处理推送消息的权限。",
    "cn.nubia.neostore.downloadService": "努比亚应用商店下载服务权限。",
    "cmb.pb.permission.PROCESS_PUSH_MSG": "招商银行掌上生活应用处理推送消息的权限。",
    "com.chinamobile.mcloud.permission.MIPUSH_RECEIVE": "中国移动和彩云应用接收小米推送（MiPush）消息的权限。",
    "com.zte.quickgame.openadsdk.permission.TT_PANGOLIN": "中兴快游戏应用集成穿山甲广告SDK的权限。",
    "tech.lolli.toolbox.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Lolli Toolbox应用内部使用的、未导出的动态广播接收器权限。",
    "com.google.android.gms.carsetup.DRIVING_MODE_MANAGER": "Google Play服务车载设置的驾驶模式管理器权限。",
    "android.permission.ASSOCIATE_COMPANION_DEVICES": "允许应用关联配套设备。",
    "com.xiaomi.mi_connect_service.permission.MI_WEAR_CORE": "小米互联服务与小米穿戴核心功能相关的权限。",
    "android.permission.MANAGE_ACCESSIBILITY": "允许应用管理无障碍服务。（系统级）",
    "com.zte.retrieve.permission.WRITE_SETTINGS": "中兴找回手机功能写入设置的权限。",
    "com.qualcomm.qtil.aptxacu.PERMISSION": "高通aptX音频编解码器配置工具权限。",
    "android.permission.DELETE_STAGED_HEALTH_CONNECT_REMOTE_DATA": "允许应用删除健康连接暂存的远程数据。（系统级）",
    "com.android.vending.p2p.APP_INSTALL_API": "Google Play商店P2P应用安装API权限。",
    "com.android.permissioncontroller.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "权限控制器应用内部使用的、未导出的动态广播接收器权限。",
    "android.permission.MONITOR_INPUT": "允许应用监视输入事件（如按键、触摸）。（系统级，高度敏感）",
    "com.google.android.gms.permission.READ_VALUABLES_IMAGES": "Google Play服务读取贵重物品图片（可能用于Google Pay等）的权限。",
    "android.permission.START_CROSS_PROFILE_ACTIVITIES": "允许应用在不同配置文件（如个人和工作）之间启动活动。",
    "com.tencent.mobileqq.permission.MM_MESSAGE": "QQ应用内部消息传递权限（类似微信的MM_MESSAGE）。",
    "android.permission.TV_INPUT_HARDWARE": "允许应用访问电视输入硬件。（系统级）",
    "android.permission.WRITE_ALLOWLISTED_DEVICE_CONFIG": "允许应用写入白名单中的设备配置项。（系统级）",
    "android.permission.ACCESS_TUNED_INFO": "允许应用访问调谐器信息。（系统级）",
    "com.qualcomm.qti.smq.feedback.providers.write": "高通SMQ反馈提供程序的写入权限。",
    "com.tencent.mm.matrix.permission.PROCESS_SUPERVISOR": "微信Matrix性能监控框架的进程监控权限。",
    "android.permission.REMOTE_AUDIO_PLAYBACK": "允许应用进行远程音频播放。",
    "android.permission.DISPATCH_NFC_MESSAGE": "允许应用分发NFC消息。（系统级）",
    "com.android.gallery3d.permission.VIEW_FAVOURITE": "旧版Android图库应用查看收藏的权限。",
    "zte.com.market.permission.INSTALL_UNINSTALL_RESULT": "中兴应用商店接收安装/卸载结果通知的权限。",
    "com.deepseek.chat.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "DeepSeek Chat应用内部使用的、未导出的动态广播接收器权限。",
    "android.permission.MODIFY_HDR_CONVERSION_MODE": "允许应用修改HDR转换模式。（系统级）",
    "zte.account.permission.Wizard": "中兴账户设置向导权限。",
    "com.qti.permission.BIND_QTI_IMS_SERVICE": "高通特定权限，允许绑定到QTI IMS服务。",
    "android.permission.READ_CARRIER_APP_INFO": "允许应用读取运营商应用信息。",
    "cmb.pb.permission.PUSH_PROVIDER": "招商银行掌上生活应用作为推送提供程序的权限。",
    "android.permission.ADJUST_RUNTIME_PERMISSIONS_POLICY": "允许应用调整运行时权限策略。（系统级）",
    "com.android.vending.billing.ADD_CREDIT_CARD": "Google Play商店添加信用卡的权限（内部使用）。",
    "android.permission.WRITE_VENDOR_CONFIG": "允许应用写入供应商配置。（系统级）",
    "android.permission.ACCESS_VR_MANAGER": "允许应用访问VR管理器服务。",
    "android.permission.BROADCAST_SMS": "允许应用广播收到的短信。（系统级）",
    "android.permission.SET_WALLPAPER_DIM_AMOUNT": "允许应用设置壁纸的暗化程度。（系统级）",
    "com.google.android.gms.permission.PHENOTYPE_OVERRIDE_FLAGS": "Google Play服务Phenotype框架覆盖标志的权限。",

    "com.android.browser.permission.WRITE_HISTORY_BOOKMARKS": "允许应用写入浏览器历史记录和书签。（旧版浏览器）",
    "android.permission.GLOBAL_SEARCH": "允许应用访问全局搜索数据。（系统级）",
    "com.zte.permission.ZONE_CHANGE": "中兴特定权限，可能与时区或地理区域变化相关。",
    "android.permission.READ_ASSISTANT_APP_SEARCH_DATA": "允许应用读取助手应用搜索数据。（系统级）",
    "com.twitter.android.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Twitter应用内部权限，用于动态注册的、不导出的广播接收器。",
    "com.zte.payment.permission.START_PAYMENT": "中兴支付服务权限，允许启动支付流程。",
    "com.google.android.voicesearch.AUDIO_FILE_ACCESS": "Google语音搜索访问音频文件的权限。",
    "com.smile.gifmaker.permission.MIPUSH_RECEIVE": "快手应用接收小米推送（MiPush）消息的权限。",
    "mfvsettings.permission.NAVIGATION": "中兴MyFlyOS设置的导航相关权限。",
    "com.tencent.mm.permission.MM_MESSAGE": "微信内部消息通信权限。",
    "com.xiaomi.fitness.preference.CHANGE": "小米健康应用更改其偏好设置的权限。",
    "com.MobileTicket.permission.PROCESS_PUSH_MSG": "票务类应用（如大麦）处理推送消息的权限。",
    "com.tencent.mm.matrix.strategynotify": "微信性能监控框架（Matrix）的策略通知权限。",
    "com.android.alarm.permission.SET_ALARM": "允许应用设置闹钟。",
    "com.azure.authenticator.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Azure Authenticator应用内部权限，用于动态注册的、不导出的广播接收器。",
    "android.permission.CAPTURE_MEDIA_OUTPUT": "允许应用捕获设备媒体输出（音频和视频）。（系统级）",
    "com.chinamobile.mcloud.permission.PUSH_PROVIDER": "中国移动和彩云推送服务提供商权限。",
    "getui.permission.GetuiService.com.dengziwl.bk": "某个使用个推（Getui）服务的应用（包名 com.dengziwl.bk）的个推服务权限。",
    "cmb.pb.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "招商银行掌上生活应用内部权限，用于动态注册的、不导出的广播接收器。",
    "com.shineyue.sjgjj.permission.PROCESS_PUSH_MSG": "手机公积金类应用处理推送消息的权限。",
    "getui.permission.GetuiService.com.cmcc.cmvideo": "咪咕视频使用个推（Getui）服务的权限。",
    "com.lemon.lv.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "剪映（Lemon LV）应用内部权限，用于动态注册的、不导出的广播接收器。",
    "com.autonavi.minimap.permission.PREFERENCES_COOKIE_SYNC": "高德地图偏好设置和Cookie同步权限。",
    "com.tencent.mm.plugin.permission.READ": "微信插件读取权限。",
    "android.permission.MANAGE_VOICE_KEYPHRASES": "允许应用管理语音唤醒词。（系统级）",
    "android.permission.FOREGROUND_SERVICE_SPECIAL_USE": "允许前台服务用于特殊用途，需声明。（Android 14+）",
    "miboard.permission.signature.writeprovider": "小米画板应用写入其内容提供程序的签名权限。",
    "com.xiaomi.mimobile.permission.PROCESS_PUSH_MSG": "小米移动（全球上网）处理推送消息的权限。",
    "com.tmri.app.main.permission.PROCESS_PUSH_MSG": "交管12123处理推送消息的权限。",
    "com.jd.permissions.MSG_BROADCAST": "京东应用的消息广播权限。",
    "android.permission.ACCESS_BLUETOOTH_SHARE": "允许应用访问蓝牙共享管理器并传输文件。",
    "com.huawei.settings.permission.ELDER_CARE_BROADCAST": "华为设置的关怀模式广播权限。",
    "android.permission.RECEIVE_WAP_PUSH": "允许应用接收WAP PUSH消息。",
    "android.permission.SET_TIME_ZONE": "允许应用设置系统时区。（系统级）",
    "cn.ecooktwo.push.permission.MESSAGE": "网上厨房（ecook）推送消息权限。",
    "android.permission.MANAGE_HOTWORD_DETECTION": "允许应用管理热词检测服务。（系统级）",
    "android.permission.START_FOREGROUND_SERVICES_FROM_BACKGROUND": "允许应用从后台启动前台服务。（受限，Android 12+）",
    "com.tencent.msg.permission.pushnotify": "腾讯系应用（如QQ）的推送通知权限。",
    "android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK": "允许应用在前台运行媒体播放服务。",
    "com.google.android.c2dm.permission.RECEIVE": "允许应用接收Google Cloud Messaging (C2DM/FCM) 推送消息。",
    "com.xunmeng.pinduoduo.permission.JPUSH_MESSAGE": "拼多多接收极光推送（JPush）消息的权限。",
    "com.google.android.gm.email.permission.GET_WIDGET_UPDATE": "Gmail获取其小部件更新的权限。",
    "com.xunmeng.pinduoduo.remote_config": "拼多多远程配置相关权限。",
    "com.smile.gifmaker.permission.PROCESS_PUSH_MSG": "快手处理推送消息的权限。",
    "com.twitter.android.permission.RESTRICTED": "Twitter内部使用的受限权限。",
    "com.android.chrome.permission.C2D_MESSAGE": "Chrome浏览器接收C2DM/FCM推送消息的权限。",
    "android.permission.REQUEST_PASSWORD_COMPLEXITY": "允许应用请求设置密码复杂度级别。（Android 12+）",
    "com.ss.android.ugc.aweme.openadsdk.permission.TT_PANGOLIN": "抖音应用使用穿山甲广告SDK的权限。",
    "alarmclock.permission.ALARM_DB": "闹钟应用访问其数据库的权限。",
    "kidszone.permission.USE_ADAPTER_SERVICE": "儿童空间/模式使用适配器服务的权限。",
    "com.shineyue.sjgjj.permission.JPUSH_MESSAGE": "手机公积金类应用接收极光推送（JPush）消息的权限。",
    "com.kugou.android.lite.permission.ACCESS_KUGOU_SERVICE": "酷狗音乐概念版访问酷狗服务的权限。",
    "com.kugou.android.lite.permission.MIPUSH_RECEIVE": "酷狗音乐概念版接收小米推送（MiPush）消息的权限。",
    "com.android.vending.CHECK_LICENSE": "允许应用检查Google Play商店的许可证。",
    "com.google.android.googlequicksearchbox.permission.FINISH_GEL_ACTIVITY": "Google搜索应用（Google App）结束其GEL（Google Experience Launcher）活动的权限。",
    "com.xunmeng.pinduoduo.permission.lifecycle": "拼多多生命周期管理相关权限。",
    "com.chinamobile.mcloud.permission.FIN_APPLET_RECEIVER": "中国移动和彩云金融小程序接收器权限。",
    "android.permission.QUERY_USERS": "允许应用查询设备上的用户信息。（系统级）",
    "com.smile.gifmaker.refreshToken.ALLOW_RECEIVED": "快手刷新Token允许接收的权限。",
    "web1n.stopapp.permission.switch_apppops": "某个应用（包名web1n.stopapp）切换AppOps设置的权限。",
    "cn.ecooktwo.permission.PUSH_PROVIDER": "网上厨房（ecook）推送服务提供商权限。",
    "com.zte.zbackup.platservice.BIND": "中兴备份服务的平台服务绑定权限。",
    "android.permission.MANAGE_DOCUMENTS": "允许应用管理文档存储，作为文档提供者。（通常用于文件管理器）",
    "com.google.android.providers.settings.permission.WRITE_GSETTINGS": "允许应用写入Google设置提供程序。（系统级）",
    "com.dengziwl.bk.openadsdk.permission.TT_PANGOLIN": "某个应用（包名com.dengziwl.bk）使用穿山甲广告SDK的权限。",
    "com.google.android.finsky.permission.BIND_GET_INSTALL_REFERRER_SERVICE": "允许应用绑定到Google Play商店服务以获取安装来源信息。",
    "cmb.pb.push.permission.MESSAGE": "招商银行掌上生活推送消息权限。",
    "android.permission.CREDENTIAL_MANAGER_QUERY_CANDIDATE_CREDENTIALS": "允许应用查询凭据管理器的候选凭据。（Android 14+）",
    "android.permission.MANAGE_SOUND_TRIGGER": "允许应用管理声音触发器（如热词检测）。（系统级）",
    "com.kugou.android.lite.permission.PUSH_PROVIDER": "酷狗音乐概念版推送服务提供商权限。",
    "com.lemon.lv.permission.PUSH_PROVIDER": "剪映（Lemon LV）推送服务提供商权限。",
    "cmccwm.mobilemusic.permission.MIPUSH_RECEIVE": "咪咕音乐接收小米推送（MiPush）消息的权限。",
    "com.google.android.apps.photos.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Google相册应用内部权限，用于动态注册的、不导出的广播接收器。",
    "com.taobao.taobao.permission.MIPUSH_RECEIVE": "淘宝接收小米推送（MiPush）消息的权限。",
    "miboard.permission.signature.startservice": "小米画板应用启动其服务的签名权限。",
    "launcheradapter.permission.EmailUnReadIntentService": "启动器适配器用于邮件未读数服务的权限。",
    "com.openai.chatgpt.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "OpenAI ChatGPT应用内部权限，用于动态注册的、不导出的广播接收器。",
    "com.jingdong.app.mall.push.permission.MESSAGE": "京东商城推送消息权限。",
    "com.greenpoint.android.mc10086.activity.permission.MIPUSH_RECEIVE": "中国移动App接收小米推送（MiPush）消息的权限。",
    "com.ss.android.ugc.aweme.permission.WRITE_ACCOUNT": "抖音写入账户信息的权限。",
    "android.permission.RESTART_PACKAGES": "允许应用重启其他应用包（已废弃，功能受限）。（系统级）",
    "android.permission.CAPTURE_AUDIO_HOTWORD": "允许应用捕获热词检测时的音频。（系统级）",
    "android.permission.CREDENTIAL_MANAGER_SET_ALLOWED_PROVIDERS": "允许应用设置凭据管理器允许的提供程序。（Android 14+）",
    "android.permission.INTERACT_ACROSS_PROFILES": "允许应用跨用户配置文件进行交互。（系统级）",
    "com.jingdong.app.mall.permission.C2D_MESSAGE": "京东商城接收C2DM/FCM推送消息的权限。",
    "com.icbc.permission.MIPUSH_RECEIVE": "工商银行App接收小米推送（MiPush）消息的权限。",
    "launchermfv.permission.RECENT_CLEAR_BLACKLIST": "中兴MyFlyOS启动器清除最近任务黑名单的权限。",
    "android.permission.SUBSCRIBE_TO_KEYGUARD_LOCKED_STATE": "允许应用订阅锁屏锁定状态变化。（系统级）",
    "android.permission.SUBSCRIBED_FEEDS_WRITE": "允许应用写入已订阅的源数据。",
    "com.gopro.smarty.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "GoPro应用内部权限，用于动态注册的、不导出的广播接收器。",
    "com.google.android.gm.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Gmail应用内部权限，用于动态注册的、不导出的广播接收器。",
    "android.permission.SUBSCRIBED_FEEDS_READ": "允许应用读取已订阅的源数据。",
    "moe.shizuku.manager.permission.MANAGER": "Shizuku Manager管理权限（用于高权限操作）。",
    "ch.protonmail.android.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "ProtonMail应用内部权限，用于动态注册的、不导出的广播接收器。",
    "cmb.pb.permission.HCE_PUSH_MESSAGE": "招商银行掌上生活HCE（主机卡模拟）推送消息权限。",
    "com.zte.userguide.log": "中兴用户指南的日志相关权限。",
    "android.permission.FOREGROUND_SERVICE_CONNECTED_DEVICE": "允许前台服务与已连接设备交互（如蓝牙、USB）。",
    "android.permission.GET_INTENT_SENDER_INTENT": "允许应用获取IntentSender内部的原始Intent。（系统级）",
    "com.tencent.mm.manual.dump": "微信手动dump信息权限（用于调试）。",
    "android.permission.GET_TOP_ACTIVITY_INFO": "允许应用获取顶层活动的信息。（系统级）",
    "android.permission.ACCESS_ADSERVICES_AD_ID": "允许应用访问广告服务的广告ID。（Android 13+）",
    "cn.ecooktwo.permission.MIPUSH_RECEIVE": "网上厨房（ecook）接收小米推送（MiPush）消息的权限。",
    "org.thunderdog.challegram.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Challegram (Telegram X) 应用内部权限，用于动态注册的、不导出的广播接收器。",
    "vfc.hce.broadcast.permission": "虚拟金融卡HCE广播权限（可能与银行卡模拟相关）。",
    "com.mi.health.broadcast.permission.action_login": "小米健康应用登录操作的广播权限。",
    "org.telegram.messenger.permission.MAPS_RECEIVE": "Telegram接收地图相关信息的权限。",
    "com.mfcloudcalculate.networkdisk.openadsdk.permission.TT_PANGOLIN": "和彩云网盘使用穿山甲广告SDK的权限。",
    "com.shineyue.sjgjj.permission.C2D_MESSAGE": "手机公积金类应用接收C2DM/FCM推送消息的权限。",
    "systemui.permission.create_shortcuts": "SystemUI创建快捷方式的权限。",
    "com.google.android.gm.email.permission.READ_ATTACHMENT": "Gmail读取邮件附件的权限。",
    "android.permission.FOREGROUND_SERVICE_CAMERA": "允许前台服务使用摄像头。",
    "com.ss.android.ugc.aweme.permission.MINIAPP_PROCESS_COMMUNICATION": "抖音小程序进程间通信权限。",
    "com.dengziwl.bk.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "某个应用（包名com.dengziwl.bk）内部权限，用于动态注册的、不导出的广播接收器。",
    "com.zte.smarthome.permission.PUSH_PROVIDER": "中兴智能家居推送服务提供商权限。",
    "com.lemon.lv.openadsdk.permission.TT_PANGOLIN": "剪映（Lemon LV）使用穿山甲广告SDK的权限。",
    "com.tencent.msf.permission.account.sync": "腾讯移动同步框架（MSF）的账户同步权限。",
    "com.xiaomi.mimobile.permission.liantian.RECEIVE": "小米移动（全球上网）联通相关接收权限。",
    "getui.permission.GetuiService.com.unionpay": "云闪付使用个推（Getui）服务的权限。",
    "com.autonavi.minimap.permission.ACCESS_DATA_SERVICE": "高德地图访问其数据服务的权限。",
    "android.permission.SET_VOLUME_KEY_LONG_PRESS_LISTENER": "允许应用设置音量键长按监听器。（系统级）",
    "com.ophone.reader.ui.permission.MIPUSH_RECEIVE": "和阅读接收小米推送（MiPush）消息的权限。",
    "com.xiaomi.mimobile.permission.PUSH_PROVIDER": "小米移动（全球上网）推送服务提供商权限。",
    "android.permission.GET_DETAILED_TASKS": "允许应用获取更详细的任务信息（比GET_TASKS更特权）。（系统级）",
    "com.unionpay.permission.VID_CHANGED": "云闪付虚拟卡ID变化通知权限。",
    "com.google.android.googlequicksearchbox.permission.PAUSE_HOTWORD": "Google搜索应用暂停热词检测的权限。",
    "android.permission.FOREGROUND_SERVICE_MICROPHONE": "允许前台服务使用麦克风。",
    "com.tmri.app.main.permission.PUSH_PROVIDER": "交管12123推送服务提供商权限。",
    "com.ophone.reader.ui.permission.PUSH_PROVIDER": "和阅读推送服务提供商权限。",
    "com.ss.android.ugc.aweme.permission.PROCESS_PUSH_MSG": "抖音处理推送消息的权限。",
    "com.zte.smarthome.permission.PROCESS_PUSH_MSG": "中兴智能家居处理推送消息的权限。",
    "com.cmcc.cmvideo.MPUSH": "咪咕视频的MPush（移动推送）权限。",
    "com.tmri.app.main.permission.MIPUSH_RECEIVE": "交管12123接收小米推送（MiPush）消息的权限。",
    "moe.shizuku.privileged.api.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Shizuku特权API内部权限，用于动态注册的、不导出的广播接收器。",
    "cn.ecooktwo.openadsdk.permission.TT_PANGOLIN": "网上厨房（ecook）使用穿山甲广告SDK的权限。",
    "com.lemon.lv.permission.MIPUSH_RECEIVE": "剪映（Lemon LV）接收小米推送（MiPush）消息的权限。",
    "moe.nb4a.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "阅读（Legado）应用内部权限，用于动态注册的、不导出的广播接收器。",
    "cn.gov.tax.its.permission.C2D_MESSAGE": "个人所得税App接收C2DM/FCM推送消息的权限。",
    "zte.permission.PUSH_MESSAGE": "中兴推送消息权限。",
    "com.google.android.googleapps.permission.GOOGLE_AUTH.mail": "Google应用套件针对邮件的Google身份验证权限。",
    "com.taobao.taobao.permission.C2D_MESSAGE": "淘宝接收C2DM/FCM推送消息的权限。",
    "android.permission.DETECT_SCREEN_CAPTURE": "允许应用检测屏幕截图事件。",
    "com.ss.android.ugc.aweme.permission.MIPUSH_RECEIVE": "抖音接收小米推送（MiPush）消息的权限。",
    "com.web1n.permissiondog.andpermission.bridge": "权限狗应用与其AndPermission库桥接的权限。",
    "android.permission.LAUNCH_CAPTURE_CONTENT_ACTIVITY_FOR_NOTE": "允许应用启动捕获内容活动以创建笔记。（系统级，如截屏笔记）",
    "com.redteamobile.virtual.permission.USE_SOFTSIM": "红茶移动虚拟SIM卡使用软SIM卡的权限。",
    "com.aimp.player.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "AIMP播放器应用内部权限，用于动态注册的、不导出的广播接收器。",
    "cn.com.chsi.chsiapp.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "学信网App应用内部权限，用于动态注册的、不导出的广播接收器。",
    "zte.permission.auto.backup": "中兴自动备份权限。",
    "com.mi.health.permission.DEFAULT_READ_DATA": "小米健康应用读取默认数据的权限。",
    "com.ophone.reader.ui.permission.C2D_MESSAGE": "和阅读接收C2DM/FCM推送消息的权限。",
    "launcheradapter.permission.USE_ADAPTER_SERVICE": "启动器适配器使用其服务的权限。",
    "cmccwm.mobilemusic.MPUSH": "咪咕音乐的MPush（移动推送）权限。",
    "android.permission.CONTROL_KEYGUARD": "允许应用控制锁屏。（系统级）",
    "cmccwm.mobilemusic.openadsdk.permission.TT_PANGOLIN": "咪咕音乐使用穿山甲广告SDK的权限。",
    "launchermfv.permission.READ_SETTINGS": "中兴MyFlyOS启动器读取设置的权限。",
    "com.shineyue.sjgjj.permission.PUSH_PROVIDER": "手机公积金类应用推送服务提供商权限。",
    "cmccwm.mobilemusic.permission.C2D_MESSAGE": "咪咕音乐接收C2DM/FCM推送消息的权限。",
    "cmccwm.mobilemusic.push.permission.MESSAGE": "咪咕音乐推送消息权限。",
    "com.eg.android.AlipayGphone.permission.MIPUSH_RECEIVE": "支付宝接收小米推送（MiPush）消息的权限。",
    "miboard.permission.signature.openaty": "小米画板应用打开其活动的签名权限。",
    "com.lemon.lv.permission.C2D_MESSAGE": "剪映（Lemon LV）接收C2DM/FCM推送消息的权限。",
    "com.google.android.apps.now.CURRENT_ACCOUNT_ACCESS": "Google Now（现Google App一部分）访问当前账户的权限。",
    "com.huawei.settings.permission.GET_ELDER_CARE_PACKAGE_NAME": "华为设置获取关怀模式应用包名的权限。",
    "com.MobileTicket.openadsdk.permission.TT_PANGOLIN": "票务类应用（如大麦）使用穿山甲广告SDK的权限。",
    "android.permission.SEND_RESPOND_VIA_MESSAGE": "允许应用通过消息回复来电。",
    "org.telegram.messenger.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Telegram应用内部权限，用于动态注册的、不导出的广播接收器。",
    "launcheradapter.permission.BatchUninstallService": "启动器适配器批量卸载服务的权限。",
    "com.cmcc.cmvideo.permission.MIPUSH_RECEIVE": "咪咕视频接收小米推送（MiPush）消息的权限。",
    "getui.permission.GetuiService.com.xiaomi.mimobile": "小米移动（全球上网）使用个推（Getui）服务的权限。",
    "com.mi.health.permission.MIPUSH_RECEIVE": "小米健康应用接收小米推送（MiPush）消息的权限。",
    "launcheradapter.permission.READ_ADAPTER": "启动器适配器读取其数据的权限。",
    "cn.ecooktwo.permission.PROCESS_PUSH_MSG": "网上厨房（ecook）处理推送消息的权限。",
    "com.kugou.android.lite.openadsdk.permission.TT_PANGOLIN": "酷狗音乐概念版使用穿山甲广告SDK的权限。",
    "com.github.android.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "GitHub应用内部权限，用于动态注册的、不导出的广播接收器。",
    "com.greenpoint.android.mc10086.activity.permission.INCOMING_CALL": "中国移动App来电相关权限。",
    "com.xunmeng.pinduoduo.permission.NOTIFICATION_RECORD": "拼多多通知记录相关权限。",
    "com.zte.smarthome.push.permission.MESSAGE": "中兴智能家居推送消息权限。",
    "android.permission.TRUST_LISTENER": "允许应用成为信任监听器（与Smart Lock等相关）。（系统级）",
    "com.bilibili.app.in.permission.BLKV": "哔哩哔哩应用内部使用的权限（可能与视频或直播相关）。",
    "com.google.android.apps.translate.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Google翻译应用内部权限，用于动态注册的、不导出的广播接收器。",
    "com.google.android.gms.permission.REQUEST_SCREEN_LOCK_COMPLEXITY": "Google Play服务请求屏幕锁定复杂度的权限。",
    "android.permission.PERSISTENT_ACTIVITY": "允许应用创建持久性活动（已废弃）。（系统级）",
    "com.google.android.youtube.permission.C2D_MESSAGE": "YouTube接收C2DM/FCM推送消息的权限。",
    "com.greenpoint.android.mc10086.activity.permission.KEEPALIVE_RECEIVE": "中国移动App保活接收器权限。",
    "com.google.android.youtube.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "YouTube应用内部权限，用于动态注册的、不导出的广播接收器。",
    "launchermfv.permission.WRITE_SETTINGS": "中兴MyFlyOS启动器写入设置的权限。",
    "com.lemon.lv.push.permission.MESSAGE": "剪映（Lemon LV）推送消息权限。",
    "com.ophone.reader.ui.permission.PROCESS_PUSH_MSG": "和阅读处理推送消息的权限。",
    "com.chinamobile.mcloud.permission.MMOAUTH_CALLBACK": "中国移动和彩云OAuth回调权限。",
    "com.greenpoint.android.mc10086.activity.permission.PUSH_PROVIDER": "中国移动App推送服务提供商权限。",
    "com.mi.fitness.permission.CONSOLE_ALARM_RECEIVE": "小米运动（原小米健康）控制台闹钟接收权限。",
    "com.kugou.android.lite.permission.TMF_SHARK": "酷狗音乐概念版使用腾讯TMF Shark组件的权限。",
    "com.google.android.googlequicksearchbox.permission.C2D_MESSAGE": "Google搜索应用接收C2DM/FCM推送消息的权限。",
    "com.google.android.gm.email.permission.ACCESS_PROVIDER": "Gmail访问其内容提供程序的权限。",
    "com.lemon.lv.permission.PROCESS_PUSH_MSG": "剪映（Lemon LV）处理推送消息的权限。",
    "com.unionpay.permission.MIPUSH_RECEIVE": "云闪付接收小米推送（MiPush）消息的权限。",
    "com.android.chrome.permission.READ_WRITE_BOOKMARK_FOLDERS": "Chrome浏览器读写书签文件夹的权限。",
    "com.mi.health.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "小米健康应用内部权限，用于动态注册的、不导出的广播接收器。",
    "com.zte.quickgame.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "中兴快游戏应用内部权限，用于动态注册的、不导出的广播接收器。",
    "com.google.android.finsky.permission.DSE": "Google Play商店动态服务引擎（DSE）相关权限。",
    "com.amap.sdk.protected_provider.ACCESS_DATA": "高德地图SDK访问其受保护内容提供程序数据的权限。",
    "android.permission.SUBSTITUTE_SHARE_TARGET_APP_NAME_AND_ICON": "允许应用在共享目标中替换其名称和图标。（系统级）",
    "cn.gov.tax.its.permission.PUSH_PROVIDER": "个人所得税App推送服务提供商权限。",
    "moe.shizuku.manager.permission.API_V23": "Shizuku Manager API版本23相关权限。",
    "miboard.permission.startmiboard": "小米画板应用启动其主界面的权限。",

    "android.permission.MANAGE_OWN_CALLS": "允许应用作为ConnectionService实现来管理自身的通话（例如，VoIP应用显示系统通话界面）。",
    "com.greenpoint.android.mc10086.activity.permission.C2D_MESSAGE": "中国移动（10086 App）自定义权限，用于接收C2D（Cloud to Device）推送消息。",
    "com.tencent.mm.WAID_PROVIDER_WRITE": "微信（com.tencent.mm）自定义权限，可能用于写入其WAID（WeChat Ad ID）相关的数据提供程序。",
    "com.MobileTicket.permission.PUSH_PROVIDER": "12306（com.MobileTicket）自定义权限，用于其内部推送服务的提供者组件。",
    "mfvsettings.permission.ONEHAND": "中兴MyFavor UI设置的自定义权限，用于单手操作模式功能。",
    "com.tencent.wifisdk.permission.disconnect": "腾讯Wi-Fi SDK相关的自定义权限，允许断开Wi-Fi连接。",
    "com.greenpoint.android.mc10086.activity.push.permission.MESSAGE": "中国移动（10086 App）自定义权限，用于其推送服务接收消息。",
    "com.android.bankabc.permission.MIPUSH_RECEIVE": "中国农业银行（com.android.bankabc）自定义权限，用于接收小米推送（MiPush）消息。",
    "com.google.android.googlequicksearchbox.permission.LENS_SERVICE": "Google搜索应用（QuickSearchBox）的权限，用于访问Google Lens服务。",
    "com.tencent.mm.vfs.broadcast": "微信（com.tencent.mm）自定义权限，与其VFS（虚拟文件系统）相关的广播。",
    "com.azure.authenticator.knox.SUPPORT_PERMISSION": "微软Authenticator应用针对三星Knox环境的自定义支持权限。",
    "com.ss.android.ugc.aweme.permission.C2D_MESSAGE": "抖音（com.ss.android.ugc.aweme）自定义权限，用于接收C2D推送消息。",
    "com.ophone.reader.ui.openadsdk.permission.TT_PANGOLIN": "某OPhone阅读器应用的自定义权限，用于集成穿山甲（TT_PANGOLIN）广告SDK。",
    "com.unionpay.permission.CONTROL_RECEIVE": "云闪付（com.unionpay）或相关银联应用的自定义权限，用于控制接收某些内容或广播。",
    "android.permission.ENTER_CAR_MODE_PRIORITIZED": "允许应用优先进入车载模式。（系统级）",
    "com.ss.android.ugc.aweme.permission.cjpay.multi.process": "抖音（com.ss.android.ugc.aweme）自定义权限，与其支付功能（cjpay）的多进程通信相关。",
    "cmccwm.mobilemusic.permission.PROCESS_PUSH_MSG": "咪咕音乐（cmccwm.mobilemusic）自定义权限，用于处理推送消息。",
    "launchermfv.permission.USE_BACKUP_SERVICE": "中兴MyFavor UI启动器的自定义权限，用于使用备份服务。",
    "com.greenpoint.android.mc10086.activity.permission.RECEIVE_MSG": "中国移动（10086 App）自定义权限，用于接收消息。",
    "com.greenpoint.android.mc10086.activity.permission.PROCESS_PUSH_MSG": "中国移动（10086 App）自定义权限，用于处理推送消息。",
    "com.xunmeng.pinduoduo.push.permission.MESSAGE": "拼多多（com.xunmeng.pinduoduo）自定义权限，用于其推送服务接收消息。",
    "com.zte.smarthome.ACCS": "中兴智能家居（com.zte.smarthome）应用的自定义权限，ACCS可能指Access Control or Communication Service。",
    "cn.gov.tax.its.permission.MIPUSH_RECEIVE": "个人所得税App（cn.gov.tax.its）自定义权限，用于接收小米推送消息。",
    "com.xiaomi.mimobile.permission.MIPUSH_RECEIVE": "小米移动（com.xiaomi.mimobile）或相关小米服务自定义权限，用于接收小米推送消息。",
    "android.permission.INSTALL_PACKAGE_UPDATES": "允许应用安装软件包更新。（系统级，通常授予系统更新程序）",
    "com.xunmeng.pinduoduo.permission.C2D_MESSAGE": "拼多多（com.xunmeng.pinduoduo）自定义权限，用于接收C2D推送消息。",
    "com.zte.permission.cloud": "中兴设备相关的自定义权限，可能用于访问云服务。",
    "com.ss.android.ugc.aweme.permission.LUNA_SESSION_INSTALL_BROADCAST": "抖音（com.ss.android.ugc.aweme）自定义权限，与其LUNA引擎的会话安装广播相关。",
    "com.greenpoint.android.mc10086.activity.com.cmos.sdk.permissions.CUSTOMBROADCAST": "中国移动（10086 App）自定义权限，用于其集成的CMOS SDK发送自定义广播。",
    "com.ophone.reader.ui.MPUSH": "某OPhone阅读器应用的自定义权限，用于其Mpush推送服务。",
    "com.google.android.gms.permission.AD_ID": "允许应用访问广告ID（Advertising ID）。",
    "com.gopro.smarty.feature.softtubes.permission.MESSAGE": "GoPro应用自定义权限，用于其softtubes功能的消息传递。",
    "com.google.android.providers.settings.permission.READ_GSETTINGS": "允许应用读取Gservices设置（已废弃，应使用READ_GSERVICES）。（系统级）",
    "com.unionpay.permission.PROCESS_PUSH_MSG": "云闪付（com.unionpay）或相关银联应用的自定义权限，用于处理推送消息。",
    "com.mfcloudcalculate.networkdisk.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "某云盘应用（mfcloudcalculate.networkdisk）内部权限，用于未导出的动态广播接收器。",
    "com.tencent.photos.permission.DATA": "腾讯相册或类似应用的自定义权限，用于访问其数据。",
    "com.eg.android.AlipayGphone.permission.C2D_MESSAGE": "支付宝（com.eg.android.AlipayGphone）自定义权限，用于接收C2D推送消息。",
    "com.google.android.providers.gsf.permission.READ_GSERVICES": "允许应用读取Google服务框架（GSF）的配置数据。",
    "com.unionpay.push.permission.MESSAGE": "云闪付（com.unionpay）或相关银联应用的自定义权限，用于其推送服务接收消息。",
    "com.unionpay.permission.C2D_MESSAGE": "云闪付（com.unionpay）或相关银联应用的自定义权限，用于接收C2D推送消息。",
    "android.permission.BIND_APPWIDGET": "允许应用告诉AppWidget服务哪个应用可以访问其AppWidget数据。",
    "com.cmcc.cmvideo.push.permission.MESSAGE": "咪咕视频（com.cmcc.cmvideo）自定义权限，用于其推送服务接收消息。",
    "com.cmcc.cmvideo.permission.PROCESS_PUSH_MSG": "咪咕视频（com.cmcc.cmvideo）自定义权限，用于处理推送消息。",
    "com.google.android.gm.permission.BROADCAST_INTERNAL": "Gmail应用（com.google.android.gm）的内部广播权限。",
    "com.tencent.mm.ext.permission.WRITE": "微信（com.tencent.mm）自定义权限，用于其扩展模块的写入操作。",
    "com.tencent.qav.permission.broadcast": "腾讯音视频（QAV）SDK相关的广播权限。",
    "android.permission.FOREGROUND_SERVICE_LOCATION": "允许应用在前台服务中访问位置信息。",
    "com.google.android.gm.permission.READ_GMAIL": "允许应用读取Gmail邮件内容。（高度敏感，通常仅授予Gmail自身）",
    "com.eg.android.AlipayGphone.push.permission.MESSAGE": "支付宝（com.eg.android.AlipayGphone）自定义权限，用于其推送服务接收消息。",
    "com.nexstreaming.app.kinemasterfree.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "KineMaster视频编辑应用内部权限，用于未导出的动态广播接收器。",
    "com.smile.gifmaker.KWAI_LINK_PERMISSION_BROADCAST": "快手（com.smile.gifmaker）自定义权限，用于Kwai Link相关的广播。",
    "com.greenpoint.android.mc10086.activity.andpermission.bridge": "中国移动（10086 App）自定义权限，用于其AndPermission库的桥接功能。",
    "com.MobileTicket.permission.MIPUSH_RECEIVE": "12306（com.MobileTicket）自定义权限，用于接收小米推送消息。",
    "com.cmcc.cmvideo.permission.C2D_MESSAGE": "咪咕视频（com.cmcc.cmvideo）自定义权限，用于接收C2D推送消息。",
    "com.android.browser.permission.READ_HISTORY_BOOKMARKS": "允许应用读取浏览器的历史记录和书签。（不推荐，应使用内容提供程序）",
    "li.songe.gkd.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "GKD（李跳跳）应用内部权限，用于未导出的动态广播接收器。",
    "com.icbc.permission.PROCESS_PUSH_MSG": "中国工商银行（com.icbc）自定义权限，用于处理推送消息。",
    "com.agc.gcam_tools.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "AGC Gcam Tools应用内部权限，用于未导出的动态广播接收器。",
    "android.permission.TRANSMIT_IR": "允许应用使用设备的红外发射器。",
    "com.tencent.qqhead.permission.getheadresp": "腾讯QQ头像相关的自定义权限，用于获取头像响应。",
    "cn.nubia.permission.NUBIA_WIFI_AP_SERVICE": "努比亚（Nubia）设备特定权限，用于其Wi-Fi热点服务。",
    "android.permission.CREDENTIAL_MANAGER_SET_ORIGIN": "允许凭据管理器设置来源信息，通常用于密码填充服务。",
    "android.permission.GET_ACCOUNTS_PRIVILEGED": "允许应用访问账户服务中的账户列表，具有特权。（系统级）",
    "com.google.android.gm.permission.WRITE_GMAIL": "允许应用写入Gmail邮件内容（如修改标签、删除）。（高度敏感，通常仅授予Gmail自身）",
    "com.google.android.gms.permission.AD_ID_NOTIFICATION": "Google Play服务权限，用于与广告ID相关的通知。",
    "com.tencent.mm.backtrace.warmed_up": "微信（com.tencent.mm）自定义权限，可能与其性能监控或错误回溯的预热机制相关。",
    "com.happymax.fcmpushviewer.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "FCM Push Viewer应用内部权限，用于未导出的动态广播接收器。",
    "com.ss.android.ugc.aweme.permission.PUSH_PROVIDER": "抖音（com.ss.android.ugc.aweme）自定义权限，用于其内部推送服务的提供者组件。",
    "com.ophone.reader.ui.push.permission.MESSAGE": "某OPhone阅读器应用的自定义权限，用于其推送服务接收消息。",
    "android.permission.ACCESS_MOCK_LOCATION": "允许应用创建模拟位置信息用于测试。",
    "com.v2ray.ang.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "V2RayNG应用内部权限，用于未导出的动态广播接收器。",
    "android.permission.MOUNT_FORMAT_FILESYSTEMS": "允许应用格式化可移动存储设备。（系统级）",
    "com.jingdong.app.mall.permission.PUSH_PROVIDER": "京东（com.jingdong.app.mall）自定义权限，用于其内部推送服务的提供者组件。",
    "android.permission.START_ANY_ACTIVITY": "允许应用启动任何活动，即使未导出。（系统级，高度敏感）",
    "com.greenpoint.android.mc10086.activity.matrix.permission.PROCESS_SUPERVISOR": "中国移动（10086 App）自定义权限，用于其集成的Matrix性能监控框架的进程监控。",
    "com.zte.mifavor.weather.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "中兴MyFavor天气应用内部权限，用于未导出的动态广播接收器。",
    "android.permission.BIND_ACCESSIBILITY_SERVICE": "必须由AccessibilityService持有，以确保只有系统可以绑定到它。",
    "com.google.android.googleapps.permission.GOOGLE_AUTH.cp": "Google应用套件权限，用于Google身份验证的内容提供程序访问。",
    "cmb.pb.permission.MIPUSH_RECEIVE": "招商银行（cmb.pb）自定义权限，用于接收小米推送消息。",
    "alarmclock.permission.CONTROL_ALARM": "自定义闹钟应用权限，用于控制闹钟（如设置、删除）。",
    "com.tencent.music.data.permission2": "腾讯音乐（如QQ音乐、酷狗）相关的数据权限（可能是第二版或特定类型）。",
    "com.icbc.permission.PUSH_PROVIDER": "中国工商银行（com.icbc）自定义权限，用于其内部推送服务的提供者组件。",
    "com.android.bankabc.vfc.hce.broadcast.vfuchong.100000550000001.permission": "中国农业银行（com.android.bankabc）特定虚拟金融卡（VFC HCE）充值相关的广播权限。",
    "com.smile.gifmaker.frog.game.permission": "快手（com.smile.gifmaker）自定义权限，与其“青蛙游戏”功能相关。",
    "com.shineyue.sjgjj.permission.MIPUSH_RECEIVE": "手机公积金（com.shineyue.sjgjj）自定义权限，用于接收小米推送消息。",
    "com.xiaomi.mimobile.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "小米移动（com.xiaomi.mimobile）应用内部权限，用于未导出的动态广播接收器。",
    "com.android.chrome.TOS_ACKED": "Chrome浏览器权限，表示用户已同意服务条款。",
    "com.android.vending.BILLING": "允许应用通过Google Play进行应用内购买和订阅。",
    "launchermfv.permission.Z_BACKUP_SERVICE": "中兴MyFavor UI启动器的自定义权限，用于其Z备份服务。",
    "moe.nb4a.SERVICE": "NekoBox for Android (moe.nb4a) 应用的服务权限。",
    "com.greenpoint.android.mc10086.activity.permission.receiver": "中国移动（10086 App）自定义权限，用于其内部广播接收器。",
    "com.shineyue.sjgjj.push.permission.MESSAGE": "手机公积金（com.shineyue.sjgjj）自定义权限，用于其推送服务接收消息。",
    "com.zte.smarthome.permission.MIPUSH_RECEIVE": "中兴智能家居（com.zte.smarthome）自定义权限，用于接收小米推送消息。",
    "android.permission.SOUND_TRIGGER_RUN_IN_BATTERY_SAVER": "允许声音触发服务在省电模式下运行。",
    "com.jingdong.app.mall.permission.self_broadcast": "京东（com.jingdong.app.mall）自定义权限，用于其内部的自定义广播。",
    "android.permission.DOWNLOAD_WITHOUT_NOTIFICATION": "允许应用在没有用户通知的情况下下载文件。",
    "com.shineyue.sjgjj.openadsdk.permission.TT_PANGOLIN": "手机公积金（com.shineyue.sjgjj）应用的自定义权限，用于集成穿山甲（TT_PANGOLIN）广告SDK。",
    "android.permission.RUN_USER_INITIATED_JOBS": "允许应用运行用户发起的作业。",
    "com.smile.gifmaker.permission.PUSH_PROVIDER": "快手（com.smile.gifmaker）自定义权限，用于其内部推送服务的提供者组件。",
    "cmccwm.mobilemusic.permission.PUSH_PROVIDER": "咪咕音乐（cmccwm.mobilemusic）自定义权限，用于其内部推送服务的提供者组件。",
    "com.tencent.mm.plugin.permission.WRITE": "微信（com.tencent.mm）自定义权限，用于其插件模块的写入操作。",
    "com.kugou.android.lite.permission.PROCESS_PUSH_MSG": "酷狗音乐极速版（com.kugou.android.lite）自定义权限，用于处理推送消息。",
    "android.permission.FOREGROUND_SERVICE_HEALTH": "允许应用在前台服务中访问与健康相关的数据（例如，用于健身追踪）。",

    "android.permission.REGISTER_CONNECTION_MANAGER": "允许应用注册连接管理器。（系统级）",
    "android.permission.MODIFY_REFRESH_RATE_SWITCHING_TYPE": "允许应用修改刷新率切换类型。（系统级）",
    "android.permission.ENABLE_TEST_HARNESS_MODE": "允许应用启用测试框架模式。（开发/测试权限）",
    "android.permission.NFC_HANDOVER_STATUS": "允许应用接收NFC切换状态更新。",
    "android.permission.BIND_IMS_SERVICE": "允许应用绑定到IMS（IP多媒体子系统）服务，用于VoLTE/VoWiFi等。",
    "com.google.android.gms.permission.CHECKIN_NOW": "Google Play服务权限，允许触发立即签入（与服务器同步）。",
    "com.google.android.gms.DRIVE": "Google Play服务权限，允许访问Google Drive云端硬盘。",
    "android.permission.WAKEUP_SURFACE_FLINGER": "允许应用唤醒SurfaceFlinger（系统图形合成器）。（系统级）",
    "com.google.android.providers.talk.permission.READ_ONLY": "允许只读访问Google Talk（环聊）内容提供程序的数据。",
    "android.permission.MANAGE_WALLPAPER_EFFECTS_GENERATION": "允许应用管理壁纸效果的生成。（系统级）",
    "androidx.appcompat.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "AndroidX AppCompat库内部权限，用于未导出的动态广播接收器。",
    "com.android.adservices.api.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Android广告服务API内部权限，用于未导出的动态广播接收器。",
    "com.android.printservice.recommendation.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Android打印服务推荐功能内部权限，用于未导出的动态广播接收器。",
    "com.android.voicemail.permission.WRITE_VOICEMAIL": "允许应用写入语音邮件。（系统/运营商应用权限）",
    "android.permission.RECEIVE_EMERGENCY_BROADCAST": "允许应用接收紧急广播（如地震、海啸预警）。",
    "contacts.permission.START_ZTE_PHONENUM_MARK_LIST": "中兴联系人特定权限，允许启动电话号码标记列表活动。",
    "com.android.mtp.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Android MTP（媒体传输协议）服务内部权限，用于未导出的动态广播接收器。",
    "android.permission.BIND_VISUAL_VOICEMAIL_SERVICE": "允许应用绑定到可视化语音邮件服务。",
    "android.permission.MANAGE_DEVICE_POLICY_APP_EXEMPTIONS": "允许应用管理设备策略的应用豁免。（设备所有者/配置文件所有者权限）",
    "android.permission.WIFI_UPDATE_USABILITY_STATS_SCORE": "允许应用更新Wi-Fi可用性统计分数。（系统级）",
    "com.ume.browser.permission.PROCESS_PUSH_MSG": "UME浏览器特定权限，用于处理推送消息。",
    "com.zte.heartyservice.permission.TMF_SHARK": "中兴HeartyService特定权限，可能与内部代号为'TMF_SHARK'的功能模块相关。",
    "com.zte.halo.app.permission.barginreceiver": "中兴Halo应用特定权限，用于一个名为'barginreceiver'的广播接收器组件。",
    "android.permission.KILL_UID": "允许应用终止指定UID的进程。（系统级，高风险）",
    "theme.permission.receivechange": "主题应用特定权限，用于接收主题变更通知。",
    "launchermfv.permission.READ_APP_UNREAD_BADGE": "中兴MyFlyOS启动器权限，用于读取应用的未读消息角标数量。",
    "android.permission.PROVIDE_TRUST_AGENT": "允许应用作为信任代理（例如用于Smart Lock智能解锁）。",
    "android.permission.SUGGEST_EXTERNAL_TIME": "允许应用建议外部时间源。（系统级）",
    "android.permission.ALLOW_SLIPPERY_TOUCHES": "允许应用的窗口在其被其他可见窗口部分或完全遮挡时仍能接收触摸事件。",
    "com.google.android.gms.time.permission.SEND_TRUSTED_TIME_SIGNAL": "Google Play服务权限，允许发送可信时间信号。",
    "com.zte.voicesecretary.permission.importservice": "中兴语音秘书特定权限，用于导入服务。",
    "android.permission.MANAGE_CREDENTIAL_MANAGEMENT_APP": "允许应用管理凭据管理应用（如密码管理器、通行密钥）。（系统级）",
    "android.permission.LOCATION_BYPASS": "允许应用绕过位置提供程序限制。（系统/特权级）",
    "nubia.permission.arkbase.USAGE_TIME": "努比亚ArkBase框架特定权限，与使用时长统计相关。",
    "android.permission.BIND_SATELLITE_SERVICE": "允许应用绑定到卫星服务（Android 14+，用于卫星通信）。",
    "android.permission.REBOOT_MODEM": "允许应用重启调制解调器。（系统/特权级）",
    "com.zte.retrieve.permission.READ_SETTINGS": "中兴Retrieve应用特定权限，用于读取其设置。",
    "com.zte.cn.zteshare.permission.BIND_ZTESHARE_SERVICE": "中兴ZTEShare应用特定权限，用于绑定到ZTEShare服务。",
    "android.permission.BIND_GBA_SERVICE": "允许应用绑定到GBA（通用引导架构）服务，用于运营商网络身份验证。",
    "android.permission.MANAGE_BIND_INSTANT_SERVICE": "允许应用管理即时应用服务的绑定。（系统级）",
    "android.contacts.permission.MANAGE_SIM_ACCOUNTS": "Android联系人应用权限，用于管理SIM卡账户。（系统级）",
    "android.permission.MANAGE_MUSIC_RECOGNITION": "允许应用管理音乐识别服务。",
    "com.zte.voiprecorder.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "中兴VoIP录音机内部权限，用于未导出的动态广播接收器。",
    "android.permission.PROVISION_DEMO_DEVICE": "允许应用将设备配置为演示模式。（系统/OEM权限）",
    "android.permission.MANAGE_AUTO_FILL": "允许应用管理自动填充服务。（系统级）",
    "contacts.permission.WRITE_GLOBAL_SUGGESTION": "联系人应用权限，允许写入全局建议（例如用于系统搜索）。（系统级）",
    "com.android.radarpermission.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Android Radar（可能是系统组件）内部权限，用于未导出的动态广播接收器。",
    "com.qti.permission.RECEIVE_PRE_ALERTING_CALL_INFO": "高通特定权限，用于接收预警呼叫信息。",
    "android.permission.SET_SYSTEM_AUDIO_CAPTION": "允许应用设置系统级音频字幕。（系统级）",
    "com.google.android.gms.permission.INTERNAL_BROADCAST": "Google Play服务权限，用于内部广播。",
    "android.permission.RESET_APP_ERRORS": "允许应用重置其他应用的ANR（应用无响应）和崩溃计数。（系统/开发权限）",
    "android.permission.ACCESS_NETWORK_CONDITIONS": "允许应用访问网络状况信息（如拥塞状态）。（系统级）",
    "com.google.android.finsky.permission.INTERNAL_BROADCAST": "Google Play商店（Finsky）权限，用于内部广播。",
    "android.permission.INIT_EXT_SERVICES": "允许应用初始化外部服务。（系统级）",
    "android.permission.ACCESS_PRIVILEGED_AD_ID": "允许特权访问广告ID。（系统级）",
    "com.google.android.gms.trustagent.framework.model.DATA_CHANGE_NOTIFICATION": "Google Play服务信任代理框架权限，用于数据更改通知。",
    "android.permission.SET_ORIENTATION": "允许应用设置屏幕方向（已废弃，应使用Activity的screenOrientation属性）。",
    "com.google.android.gms.magictether.permission.CLIENT_TETHERING_PREFERENCE_CHANGED": "Google Play服务Magic Tether（智能网络共享）权限，用于客户端网络共享偏好更改。",
    "com.google.android.gms.permission.wearable.BUGREPORT_USER_CONSENT": "Google Play服务Wear OS权限，用于用户同意收集错误报告。",
    "com.google.android.gms.permission.SAFETY_NET": "Google Play服务权限，允许使用SafetyNet Attestation API验证设备完整性。",
    "android.permission.ZTE_MANAGE_NETWORK_POLICY": "中兴特定权限，用于管理网络策略。",
    "com.google.android.gms.permission.SEND_ANDROID_PAY_DATA": "Google Play服务权限，允许发送Android Pay（现Google Pay）数据。",
    "android.permission.READ_RUNTIME_PROFILES": "允许应用读取运行时JIT（即时编译）配置文件。（系统/开发权限）",
    "android.permission.MANAGE_APP_PREDICTIONS": "允许应用管理应用预测（例如用于启动器中的应用建议）。（系统级）",
    "android.permission.POWER_SAVER": "允许应用控制省电模式设置。（系统级）",
    "com.airbnb.lottie.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Lottie动画库内部权限，用于未导出的动态广播接收器。",
    "com.android.ondevicepersonalization.services.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Android设备端个性化服务内部权限，用于未导出的动态广播接收器。",
    "android.permission.SET_ACTIVITY_WATCHER": "允许应用监视Activity启动（已废弃，高风险）。（系统级）",
    "android.permission.MANAGE_DEVICE_POLICY_LOCK_TASK": "允许应用通过设备策略管理锁定任务模式（信息亭模式）。（设备所有者权限）",
    "android.permission.MODIFY_DEFAULT_AUDIO_EFFECTS": "允许应用修改默认音频效果。（系统级）",
    "android.permission.RESET_FINGERPRINT_LOCKOUT": "允许应用重置指纹识别锁定状态（例如在多次尝试失败后）。（系统级）",
    "callsetting.permission.PRIVILEGED": "通话设置的特权权限。（应用/OEM特定）",
    "android.permission.FORCE_DEVICE_POLICY_MANAGER_LOGS": "允许应用强制设备策略管理器记录日志。（设备所有者/系统权限）",
    "android.permission.MARK_DEVICE_ORGANIZATION_OWNED": "允许应用将设备标记为组织所有。（设备所有者/配置文件所有者权限）",
    "launchermfv.permission.GS_LAUNCHER_DATA": "中兴MyFlyOS启动器特定权限，与'GS Launcher Data'相关。",
    "android.permission.WIFI_ACCESS_COEX_UNSAFE_CHANNELS": "允许Wi-Fi访问共存不安全信道。（系统级）",
    "androidzte.permission.ZTE_THEME_CHANGE": "中兴特定权限，用于主题更改。（可能是`zte.permission.THEME_CHANGE`或`android.permission.ZTE_THEME_CHANGE`的变体）",
    "android.permission.ACCESS_LOCUS_ID_USAGE_STATS": "允许应用访问LocusId（与上下文感知相关）的使用情况统计。（系统级）",
    "android.permission.USE_CUSTOM_VIRTUAL_MACHINE": "允许应用使用自定义虚拟机（例如用于受保护的执行环境）。（系统级）",
    "android.permission.MAKE_UID_VISIBLE": "允许应用使其UID对其他进程可见。（系统级）",
    "android.permission.MANAGE_SEARCH_UI": "允许应用管理搜索UI组件。（系统级）",
    "contacts.permission.READ_GLOBAL_SUGGESTION": "联系人应用权限，允许读取全局建议。（系统级）",
    "android.permission.MANAGE_HEALTH_PERMISSIONS": "允许应用管理健康相关权限（例如用于Health Connect）。（系统级）",
    "android.permission.TABLET_MODE": "允许应用查询或影响平板模式。（系统级）",
    "android.permission.RECEIVE_DEVICE_CUSTOMIZATION_READY": "允许应用接收设备定制化准备就绪的广播。（系统/OEM权限）",
    "zte.com.cn.filer.permission.SEND_BROADCAST": "中兴文件管理器特定权限，用于发送广播。",
    "com.google.android.gms.trustagent.framework.model.DATA_ACCESS": "Google Play服务信任代理框架权限，用于数据访问。",
    "android.permission.FOREGROUND_SERVICE_FILE_MANAGEMENT": "允许应用运行文件管理类型的前台服务。",
    "com.dts.permission.DTS_EFFECT": "DTS音效控制权限。（音频OEM/应用特定）",
    "android.permission.READ_PEOPLE_DATA": "允许应用读取人物/联系人数据（与Conversations API相关）。",
    "nubia.permission.arkbase.DATA_COLLECTION": "努比亚ArkBase框架特定权限，用于数据收集。",
    "android.permission.SCORE_NETWORKS": "允许应用为网络评分（例如Wi-Fi质量）。（系统级）",
    "android.permission.SEND_DOWNLOAD_COMPLETED_INTENTS": "允许应用发送下载完成的意图。（系统级）",
    "android.permission.SUSPEND_APPS": "允许应用暂停其他应用。（系统/配置文件所有者权限）",
    "com.zte.faceverify.permission.SERVICE": "中兴人脸验证服务的权限。",
    "com.yulore.permission.START_SHOPDETAIL_ACTIVITY": "Yulore（电话邦/号码识别应用）特定权限，允许启动商店详情活动。",
    "contacts.permission.START_DATA_MULTI_SELECTION": "联系人应用权限，允许启动数据多选活动。（系统/OEM特定）",
    "android.permission.MANAGE_BLUETOOTH_WHEN_WIRELESS_CONSENT_REQUIRED": "允许在需要无线同意（如飞行模式）时管理蓝牙。（系统级）",
    "com.google.android.xmpp.permission.XMPP_ENDPOINT_BROADCAST": "Google XMPP服务权限，用于XMPP端点广播。",
    "android.permission.RADIO_SCAN_WITHOUT_LOCATION": "允许应用在没有位置权限的情况下扫描无线电网络（如Wi-Fi、蜂窝网络，有特定条件限制）。",
    "zte.permission.IGNORE_FINGER_VIBRATE": "中兴特定权限，用于忽略手指振动，可能与指纹传感器相关。",
    
    "android.permission.ACCEPT_HANDOVER": "允许应用接受来自其他应用的连接切换（例如，蓝牙切换到Wi-Fi）。（系统级）",
    "android.permission.ACCESS_ADSERVICES_CUSTOM_AUDIENCE": "允许应用访问广告服务的自定义受众数据。（Android 13+）",
    "android.permission.ACCESS_ADSERVICES_MANAGER": "允许应用访问广告服务管理器。（Android 13+）",
    "android.permission.ACCESS_ADSERVICES_TOPICS": "允许应用访问广告服务的主题推断数据。（Android 13+）",
    "android.permission.ACCESS_BROADCAST_RESPONSE_STATS": "允许应用访问广播响应统计信息。（系统级）",
    "android.permission.ACCESS_LOWPAN_STATE": "允许应用访问LoWPAN（低功耗无线个域网）状态。（系统级）",
    "android.permission.ACCESS_MTP": "允许应用作为MTP（媒体传输协议）发起者访问设备。",
    "android.permission.ACCESS_RCS_USER_CAPABILITY_EXCHANGE": "允许应用访问RCS（富通信服务）用户能力交换。",
    "android.permission.ACCESS_SHARED_LIBRARIES": "允许应用访问共享库信息。（系统级）",
    "android.permission.ACCESS_SURFACE_FLINGER": "允许应用直接访问SurfaceFlinger（系统级合成器）。（系统级）",
    "android.permission.ACCESS_TV_DESCRAMBLER": "允许应用访问电视解扰器。",
    "android.permission.ACCESS_TV_TUNER": "允许应用访问电视调谐器硬件。",
    "android.permission.ACCESS_VIBRATOR_STATE": "允许应用访问振动器状态。（系统级）",
    "android.permission.ACCESS_VOICE_INTERACTION_SERVICE": "允许应用访问语音交互服务。",
    "android.permission.ACTIVITY_EMBEDDING": "允许应用在其任务中嵌入其他应用的活动。（Android 12L+）",
    "android.permission.ALLOCATE_AGGRESSIVE": "允许应用请求积极的资源分配（可能影响其他应用）。（系统级）",
    "android.permission.BATTERY_PREDICTION": "允许应用访问电池使用预测数据。（系统级）",
    "android.permission.BIND_DEVICE_ADMIN": "允许应用绑定到设备管理员服务。（系统级）",
    "android.permission.BIND_DIRECTORY_SEARCH": "允许应用绑定到目录搜索服务。",
    "android.permission.BIND_QUICK_ACCESS_WALLET_SERVICE": "允许应用绑定到快速访问钱包服务（例如在锁屏上显示支付卡）。",
    "android.permission.BIND_REMOTEVIEWS": "允许应用绑定到RemoteViews服务，用于创建跨进程UI。",
    "android.permission.BIND_SATELLITE_GATEWAY_SERVICE": "允许应用绑定到卫星网关服务。",
    "android.permission.BIND_TELECOM_CONNECTION_SERVICE": "允许应用绑定到Telecom的ConnectionService，用于电话集成。",
    "android.permission.BIND_TELEPHONY_DATA_SERVICE": "允许应用绑定到电话数据服务。",
    "android.permission.BIND_VISUAL_QUERY_DETECTION_SERVICE": "允许应用绑定到视觉查询检测服务。",
    "android.permission.BLUETOOTH_MAP": "允许应用使用蓝牙MAP（消息访问配置文件）。",
    "android.permission.BROADCAST_OPTION_INTERACTIVE": "允许应用广播交互式选项。（系统级）",
    "android.permission.CHANGE_DEVICE_IDLE_TEMP_WHITELIST": "允许应用临时将应用添加到设备空闲模式的白名单。（系统级）",
    "android.permission.CHANGE_OVERLAY_PACKAGES": "允许应用更改哪些包可以显示悬浮窗。（系统级）",
    "android.permission.CHECK_REMOTE_LOCKSCREEN": "允许应用检查远程锁屏状态。（系统级）",
    "android.permission.CLEAR_FREEZE_PERIOD": "允许应用清除应用的冻结期。（系统级）",
    "android.permission.CONTROL_DEVICE_LIGHTS": "允许应用控制设备上的指示灯（如通知灯）。",
    "android.permission.CONTROL_REMOTE_APP_TRANSITION_ANIMATIONS": "允许应用控制远程应用过渡动画。（系统级）",
    "android.permission.CREATE_VIRTUAL_DEVICE": "允许应用创建虚拟设备。（Android 13+，系统级）",
    "android.permission.DEBUG_VIRTUAL_MACHINE": "允许应用调试虚拟机。（系统级）",
    "android.permission.FORCE_BACK": "允许应用强制执行返回操作。（系统级）",
    "android.permission.FRAME_STATS": "允许应用访问帧统计信息。（系统级）",
    "android.permission.GET_ANY_PROVIDER_TYPE": "允许应用获取任何内容提供程序的类型。（系统级）",
    "android.permission.GET_APP_METADATA": "允许应用获取其他应用的元数据。（系统级）",
    "android.permission.GRANT_RUNTIME_PERMISSIONS": "允许应用授予或撤销其他应用的运行时权限。（系统级）",
    "android.permission.INSTANT_APP_FOREGROUND_SERVICE": "允许即时应用运行前台服务。",
    "android.permission.KEEP_UNINSTALLED_PACKAGES": "允许应用在卸载后保留应用数据。（系统级）",
    "android.permission.KILL_ALL_BACKGROUND_PROCESSES": "允许应用终止所有后台进程。（系统级）",
    "android.permission.LAUNCH_CREDENTIAL_SELECTOR": "允许应用启动凭据选择器。",
    "android.permission.LISTEN_ALWAYS_REPORTED_SIGNAL_STRENGTH": "允许应用监听始终报告的信号强度。（系统级）",
    "android.permission.LOCK_DEVICE": "允许设备管理员应用锁定设备。",
    "android.permission.LOG_FOREGROUND_RESOURCE_USE": "允许应用记录前台资源使用情况。（系统级）",
    "android.permission.MANAGE_APPOPS": "允许应用管理App Ops设置（旧API，新API为MANAGE_APP_OPS_MODES）。（系统级）",
    "android.permission.MANAGE_AUDIO_POLICY": "允许应用管理音频策略。（系统级）",
    "android.permission.MANAGE_COMPANION_DEVICES": "允许应用管理配对的伴侣设备。",
    "android.permission.MANAGE_CONTENT_CAPTURE": "允许应用管理内容捕获服务。（系统级）",
    "android.permission.MANAGE_CONTENT_SUGGESTIONS": "允许应用管理内容建议。（系统级）",
    "android.permission.MANAGE_CRATES": "与Crates（可能是某种存储或容器管理）相关的管理权限。（系统级）",
    "android.permission.MANAGE_DEVICE_LOCK_STATE": "允许应用管理设备锁定状态。（系统级）",
    "android.permission.MANAGE_DEVICE_POLICY_APPS_CONTROL": "允许设备策略控制器管理应用控制策略。",
    "android.permission.MANAGE_DEVICE_POLICY_INSTALL_UNKNOWN_SOURCES": "允许设备策略控制器管理“安装未知来源应用”的设置。",
    "android.permission.MANAGE_DEVICE_POLICY_SAFE_BOOT": "允许设备策略控制器管理安全启动设置。",
    "android.permission.MANAGE_HEALTH_DATA": "允许应用管理健康数据。（Android 14+）",
    "android.permission.MANAGE_LOW_POWER_STANDBY": "允许应用管理低功耗待机模式。（系统级）",
    "android.permission.MANAGE_MEDIA_PROJECTION": "允许应用管理媒体投影会话（屏幕捕获/共享）。",
    "android.permission.MANAGE_ONE_TIME_PERMISSION_SESSIONS": "允许应用管理一次性权限会话。（系统级）",
    "android.permission.MANAGE_ROLLBACKS": "允许应用管理应用回滚。（系统级）",
    "android.permission.MANAGE_SENSOR_PRIVACY": "允许应用管理传感器隐私开关（如摄像头/麦克风总开关）。（系统级）",
    "android.permission.MANAGE_SENSORS": "允许应用管理传感器。（系统级）",
    "android.permission.MANAGE_SMARTSPACE": "允许应用管理Smartspace（例如Google Pixel启动器上的“概览”微件）。（系统级）",
    "android.permission.MANAGE_SUBSCRIPTION_PLANS": "允许应用管理用户的订阅计划。",
    "android.permission.MANAGE_UI_TRANSLATION": "允许应用管理UI翻译服务。（系统级）",
    "android.permission.MANAGE_WIFI_INTERFACES": "允许应用管理Wi-Fi接口。（系统级）",
    "android.permission.MODIFY_AUDIO_SETTINGS_PRIVILEGED": "允许应用执行特权音频设置修改。（系统级）",
    "android.permission.MODIFY_CELL_BROADCASTS": "允许应用修改小区广播设置。（系统级）",
    "android.permission.MODIFY_DAY_NIGHT_MODE": "允许应用修改系统的日间/夜间模式。（系统级）",
    "android.permission.MODIFY_THEME_OVERLAY": "允许应用修改主题叠加层。（系统级）",
    "android.permission.MONITOR_KEYBOARD_BACKLIGHT": "允许应用监控键盘背光状态。（系统级）",
    "android.permission.NET_ADMIN": "允许应用执行网络管理任务（如配置防火墙规则）。（系统级）",
    "android.permission.NET_TUNNELING": "允许应用创建网络隧道。（系统级）",
    "android.permission.NETWORK_FACTORY": "允许应用作为网络工厂，提供网络连接。（系统级）",
    "android.permission.NETWORK_MANAGED_PROVISIONING": "允许应用进行网络管理的配置。",
    "android.permission.NETWORK_STATS_PROVIDER": "允许应用提供网络使用统计数据。（系统级）",
    "android.permission.OBSERVE_APP_USAGE": "允许应用观察其他应用的使用情况。（系统级）",
    "android.permission.OBSERVE_ROLE_HOLDERS": "允许应用观察系统角色的持有者变化。（系统级）",
    "android.permission.OBSERVE_SENSOR_PRIVACY": "允许应用观察传感器隐私开关的状态。（系统级）",
    "android.permission.OVERRIDE_DISPLAY_MODE_REQUESTS": "允许应用覆盖显示模式请求。（系统级）",
    "android.permission.PERFORM_IMS_SINGLE_REGISTRATION": "允许应用执行IMS（IP多媒体子系统）单次注册。（系统级）",
    "android.permission.PROVIDE_REMOTE_CREDENTIALS": "允许应用提供远程凭据。（系统级）",
    "android.permission.PROVIDE_RESOLVER_RANKER_SERVICE": "允许应用提供解析器排序服务。（系统级）",
    "android.permission.QUERY_CLONED_APPS": "允许应用查询已克隆的应用（应用分身）。",
    "android.permission.RADAR_LOG_CONTROL": "与雷达（可能是指Project Soli等技术）日志控制相关的权限。（系统级）",
    "android.permission.READ_CELL_BROADCASTS": "允许应用读取接收到的小区广播消息。",
    "android.permission.READ_LOWPAN_CREDENTIAL": "允许应用读取LoWPAN凭据。（系统级）",
    "android.permission.READ_NEARBY_STREAMING_POLICY": "允许应用读取附近设备流式传输策略。（系统级）",
    "android.permission.READ_NETWORK_USAGE_HISTORY": "允许应用读取网络使用历史记录。",
    "android.permission.READ_PRINT_SERVICE_RECOMMENDATIONS": "允许应用读取打印服务推荐。",
    "android.permission.READ_WIFI_CREDENTIAL": "允许应用读取已保存的Wi-Fi凭据。（系统级）",
    "android.permission.READ_WRITE_SYNC_DISABLED_MODE_CONFIG": "允许应用读写同步禁用模式配置。（系统级）",
    "android.permission.RECEIVE_DATA_ACTIVITY_CHANGE": "允许应用接收数据活动状态变化的通知。",
    "android.permission.RECEIVE_MEDIA_RESOURCE_USAGE": "允许应用接收媒体资源使用情况的通知。（系统级）",
    "android.permission.RECOVER_KEYSTORE": "允许应用恢复密钥库中的密钥。（系统级）",
    "android.permission.REGISTER_CALL_PROVIDER": "允许应用注册为通话提供程序。",
    "android.permission.REGISTER_SIM_SUBSCRIPTION": "允许应用注册SIM卡订阅事件。",
    "android.permission.REGISTER_STATS_PULL_ATOM": "允许应用注册拉取统计原子数据。（系统级）",
    "android.permission.REQUEST_COMPANION_PROFILE_AUTOMOTIVE_PROJECTION": "允许应用请求车载投屏的伴侣设备配置文件。",
    "android.permission.RESTRICTED_VR_ACCESS": "允许应用以受限方式访问VR功能。（系统级）",
    "android.permission.ROTATE_SURFACE_FLINGER": "允许应用旋转SurfaceFlinger的输出。（系统级）",
    "android.permission.SATELLITE_COMMUNICATION": "允许应用进行卫星通信。（Android 14+）",
    "android.permission.SEND_CALL_LOG_CHANGE": "允许应用发送通话记录更改的通知。（系统级）",
    "android.permission.SEND_DEVICE_CUSTOMIZATION_READY": "允许应用发送设备定制化已准备就绪的信号。（系统级）",
    "android.permission.SET_APP_SPECIFIC_LOCALECONFIG": "允许应用设置应用特定的区域配置。（系统级）",
    "android.permission.SET_AUTHENTICATION_DATA": "允许应用设置身份验证数据。（系统级）",
    "android.permission.SET_DEBUG_APP": "允许应用设置调试应用。（系统级）",
    "android.permission.SET_PREFERRED_APPLICATIONS": "允许应用设置首选应用。（系统级）",
    "android.permission.SIGNAL_PERSISTENT_PROCESSES": "允许应用向常驻进程发送信号。（系统级）",
    "android.permission.START_PRINT_SERVICE_CONFIG_ACTIVITY": "允许应用启动打印服务的配置活动。",
    "android.permission.SUGGEST_TELEPHONY_TIME_AND_ZONE": "允许应用建议电话网络提供的时间和时区。（系统级）",
    "android.permission.SYSTEM_APPLICATION_OVERLAY": "允许系统应用显示在其他应用上方的悬浮窗。（系统级）",
    "android.permission.TEST_INPUT_METHOD": "允许应用测试输入法。（系统级）",
    "android.permission.TIS_EXTENSION_INTERFACE": "允许应用访问文本输入服务扩展接口。（系统级）",
    "android.permission.TUNER_RESOURCE_ACCESS": "允许应用访问调谐器资源。",
    "android.permission.TURN_SCREEN_ON": "允许应用在锁屏上方点亮屏幕（已废弃，应使用USE_FULL_SCREEN_INTENT）。",
    "android.permission.UPDATE_CONFIG": "允许应用更新配置。（系统级）",
    "android.permission.UPDATE_LOCK": "允许应用更新锁。（系统级）",
    "android.permission.UPGRADE_RUNTIME_PERMISSIONS": "允许应用升级运行时权限（例如，从文件权限到媒体特定权限）。（系统级）",
    "android.permission.USE_EXACT_ALARM": "允许应用安排精确的闹钟/定时任务（Android 12+的运行时权限，SCHEDULE_EXACT_ALARM的旧名称）。",
    "android.permission.WATCH_APPOPS": "允许应用监视App Ops的更改。（系统级）",
    "android.permission.WHITELIST_AUTO_REVOKE_PERMISSIONS": "允许应用将自身添加到自动撤销未使用权限的白名单中。",
    "android.permission.WHITELIST_RESTRICTED_PERMISSIONS": "允许应用将自身添加到受限权限的白名单中。（系统级）",
    "android.permission.WIFI_UPDATE_COEX_UNSAFE_CHANNELS": "允许应用更新Wi-Fi共存不安全信道信息。（系统级）",
    "android.permission.WRITE_DREAM_STATE": "允许应用写入Daydream（屏幕保护程序）的状态。",
    "android.permission.WRITE_EMBEDDED_SUBSCRIPTIONS": "允许应用写入嵌入式SIM卡（eSIM）的订阅信息。（系统级）",
    "android.permission.health.READ_EXERCISE_ROUTE": "允许应用读取健康数据中的运动路线。（Android 14+）",
    "android.permission.health.READ_HEART_RATE": "允许应用读取健康数据中的心率信息。（Android 14+）",
    "androidx.core.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "AndroidX Core库内部权限，用于未导出的动态广播接收器。",
    "androidx.legacy.coreutils.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "AndroidX Legacy CoreUtils库内部权限，用于未导出的动态广播接收器。",
    "androidx.preference.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "AndroidX Preference库内部权限，用于未导出的动态广播接收器。",
    "cn.nubia.gameassist.permission.GAMEREMINDER": "努比亚游戏助手游戏提醒权限。",
    "cn.zte.gamefloat.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "中兴游戏悬浮窗内部权限。",
    "cn.zte.music.permission.PlaybackService": "中兴音乐应用的播放服务权限。",
    "com.android.apps.tag.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Android Tag应用（NFC）内部权限。",
    "com.android.cellbroadcastreceiver.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "小区广播接收器应用内部权限。",
    "com.android.cellbroadcastreceiver.module.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "小区广播接收器模块内部权限。",
    "com.android.documentsui.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "文件选择器（DocumentsUI）应用内部权限。",
    "com.android.gallery3d.permission.GALLERY_PROVIDER": "图库应用内容提供程序的访问权限。",
    "com.android.gallery3d.permission.GALLERY_SEARCH": "图库应用搜索功能的权限。",
    "com.android.intentresolver.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "意图解析器应用内部权限。",
    "com.android.managedprovisioning.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "设备配置（Managed Provisioning）应用内部权限。",
    "com.android.nearby.halfsheet.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "附近设备半屏显示组件内部权限。",
    "com.android.permission.ALLOWLIST_BLUETOOTH_DEVICE": "允许应用将蓝牙设备添加到白名单。（系统级）",
    "com.android.permission.INSTALL_EXISTING_PACKAGES": "允许应用安装已存在的包（例如，恢复应用）。（系统级）",
    "com.android.permission.USE_INSTALLER_V2": "允许应用使用Installer V2 API。（系统级）",
    "com.android.permission.USE_SYSTEM_DATA_LOADERS": "允许应用使用系统数据加载器。（系统级）",
    "com.android.phone.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "电话应用内部权限。",
    "com.android.printspooler.permission.ACCESS_ALL_PRINT_JOBS": "打印服务后台处理程序权限，允许访问所有打印作业。",
    "com.android.providers.media.module.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "媒体提供程序模块内部权限。",
    "com.android.providers.media.permission.MANAGE_CLOUD_MEDIA_PROVIDERS": "媒体提供程序权限，允许管理云媒体提供程序。",
    "com.android.rkpdapp.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "远程密钥配置应用（RKPDApp）内部权限。",
    "com.android.smspush.WAPPUSH_MANAGER_BIND": "允许应用绑定到WAP Push管理器服务。",
    "com.android.stk.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "SIM卡工具包（STK）应用内部权限。",
    "com.android.systemui.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "SystemUI应用内部权限。",
    "com.android.systemui.accessibility.accessibilitymenu.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "SystemUI无障碍菜单内部权限。",
    "com.android.traceur.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "系统跟踪（Traceur）应用内部权限。",
    "com.android.vending.APP_ERRORS_SERVICE": "Google Play商店错误报告服务权限。",
    "com.android.vending.TOS_ACKED": "Google Play商店服务条款已确认权限。",
    "com.android.vending.billing.BILLING_ACCOUNT_SERVICE": "Google Play商店计费账户服务权限。",
    "com.android.wallpaper.livepicker.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "动态壁纸选择器应用内部权限。",
    "com.android.wifi.dialog.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Wi-Fi对话框应用内部权限。",
    "com.google.android.c2dm.permission.SEND": "允许应用通过Google Cloud Messaging (C2DM) 发送消息给其他应用。（已废弃，被FCM取代）",
    "com.google.android.finsky.permission.PLAY_BILLING_LIBRARY_BROADCAST": "Google Play Billing库广播权限。",
    "com.google.android.gms.auth.authzen.permission.DEVICE_SYNC_FINISHED": "Google Play服务Authzen设备同步完成权限。",
    "com.google.android.gms.auth.authzen.permission.KEY_REGISTRATION_FINISHED": "Google Play服务Authzen密钥注册完成权限。",
    "com.google.android.gms.auth.cryptauth.permission.CABLEV2_SERVER_LINK": "Google Play服务CryptAuth CableV2服务器链接权限。",
    "com.google.android.gms.auth.permission.FACE_UNLOCK": "Google Play服务人脸解锁权限。",
    "com.google.android.gms.auth.permission.GOOGLE_ACCOUNT_CHANGE": "Google Play服务Google账户变更通知权限。",
    "com.google.android.gms.chromesync.permission.METADATA_UPDATED": "Google Play服务Chrome同步元数据更新权限。",
    "com.google.android.gms.cloudsave.BIND_EVENT_BROADCAST": "Google Play服务云存档绑定事件广播权限。",
    "com.google.android.gms.contextmanager.CONTEXT_MANAGER_RESTARTED_BROADCAST": "Google Play服务上下文管理器重启广播权限。",
    "com.google.android.gms.findmydevice.spot.permission.DEVICE_CHANGES": "Google Play服务“查找我的设备”Spot功能设备变更权限。",
    "com.google.android.gms.locationsharingreporter.periodic.STATUS_UPDATE": "Google Play服务位置共享报告器定期状态更新权限。",
    "com.google.android.gms.magictether.permission.CONNECTED_HOST_CHANGED": "Google Play服务Magic Tether已连接主机更改权限。",
    "com.google.android.gms.magictether.permission.SCANNED_DEVICE": "Google Play服务Magic Tether已扫描设备权限。",
    "com.google.android.gms.onetimeinitializer.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Google Play服务一次性初始化器内部权限。",
    "com.google.android.gms.permission.C2D_MESSAGE": "Google Play服务接收C2D（Cloud to Device）消息的权限（FCM）。",
    "com.google.android.gms.permission.NEARBY_START_DISCOVERER": "Google Play服务附近设备开始发现权限。",
    "com.google.android.gms.permission.SHOW_PAYMENT_CARD_DETAILS": "Google Play服务显示支付卡详情权限。",
    "com.google.android.gms.permission.SHOW_TRANSACTION_RECEIPT": "Google Play服务显示交易收据权限。",
    "com.google.android.gms.permission.SHOW_WARM_WELCOME_TAPANDPAY_APP": "Google Play服务显示Tap&Pay应用欢迎界面权限。",
    "com.google.android.gms.presencemanager.permission.PRESENCE_MANAGER_UPDATE_BROADCAST": "Google Play服务在线状态管理器更新广播权限。",
    "com.google.android.gms.smartdevice.permission.NOTIFY_QUICK_START_STATUS": "Google Play服务智能设备快速启动状态通知权限。",
    "com.google.android.gms.trustagent.permission.TRUSTAGENT_STATE": "Google Play服务信任代理状态权限。",
    "com.google.android.googleapps.permission.GOOGLE_AUTH.ALL_SERVICES": "Google应用套件访问所有Google服务的身份验证权限。",
    "com.google.android.googleapps.permission.GOOGLE_AUTH.cl": "Google应用套件特定客户端的身份验证权限。",
    "com.google.android.googleapps.permission.GOOGLE_AUTH.youtube": "Google应用套件YouTube身份验证权限。",
    "com.google.android.gsf.subscribedfeeds.permission.C2D_MESSAGE": "Google服务框架订阅源接收C2D消息权限。",
    "com.google.android.gtalkservice.permission.GTALK_SERVICE": "Google Talk服务权限。",
    "com.google.android.providers.talk.permission.WRITE_ONLY": "Google Talk内容提供程序的只写权限。",
    "com.qti.permission.AUDIO": "高通音频相关权限。",
    "com.qti.phone.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "高通电话应用内部权限。",
    "com.qualcomm.permission.ACCESS_GTPWIFI_CROWDSOURCING_API": "高通访问GTPWi-Fi众包API权限。",
    "com.qualcomm.permission.ACCESS_USER_CONSENT_API": "高通访问用户同意API权限。",
    "com.qualcomm.permission.READPROC": "高通读取/proc文件系统信息的权限。",
    "com.qualcomm.permission.USE_QCRIL_MSG_TUNNEL": "高通使用QCRIL消息通道的权限。",
    "com.qualcomm.permission.wfd.QC_WFD": "高通Wi-Fi Display (Miracast)特定权限。",
    "com.qualcomm.qti.ridemodeaudio.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "高通骑行模式音频内部权限。",
    "com.qualcomm.qtil.aptxals.PERMISSION": "高通aptX Adaptive Low Latency Sound (ALS) 权限。",
    "com.tencent.mocmna.accservice.permission": "腾讯MOC MNA加速服务权限。",
    "com.tencent.tmsecure.permission.ACCESS_SYN_SERVICE": "腾讯手机管家访问同步服务权限。",
    "com.ume.browser.permission.MIPUSH_RECEIVE": "UME浏览器接收小米推送（MiPush）消息的权限。",
    "com.zte.aliveupdate.permission.JPUSH_MESSAGE": "中兴AliveUpdate接收极光推送消息的权限。",
    "com.zte.cloud.permission.getuserinfo": "中兴云服务获取用户信息的权限。",
    "com.zte.cn.doubleapp.permission.ACTIVITY": "中兴应用分身功能的活动权限。",
    "com.zte.halo.app.permission.readsmsover": "中兴Halo应用读取短信权限。",
    "com.zte.mifavor.launcher.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "中兴MiFavor启动器内部权限。",
    "com.zte.quickrt.permission.CARD": "中兴QuickRT卡片相关权限。",
    "com.zte.quickrt.permission.RECEIVE_BROADCAST": "中兴QuickRT接收广播权限。",
    "com.zte.voiceassist.wakeup.bind.wakeup": "中兴语音助手唤醒绑定权限。",
    "com.zte.wallet.support.permission.LAUNCH_MAP": "中兴钱包支持启动地图权限。",
    "com.zte.zdm.permission.BROADCAST": "中兴设备管理（ZDM）广播权限。",
    "huawei.android.permission.HW_SIGNATURE_OR_SYSTEM": "华为设备签名或系统应用权限。",
    "incallui.permission.PRIVILEGED": "通话界面（InCallUI）的特权权限。（系统级）",
    "launchermfv.permission.RECENT_CLEAR": "中兴MyFlyOS启动器清除最近任务权限。",
    "launchermfv.permission.READ_TASK": "中兴MyFlyOS启动器读取任务权限。",
    "launchermfv.permission.SETTING": "中兴MyFlyOS启动器设置相关权限。",
    "launchermfv.permission.SET_SUBSCRIPT": "中兴MyFlyOS启动器设置订阅相关权限。",
    "launchermfv.permission.nubia": "中兴MyFlyOS启动器努比亚特定权限。",
    "mfvsettings.permission.ANNOUNCEMENT": "中兴MyFlyOS设置公告相关权限。",
    "mfvsettings.permission.SHUTDOWN": "中兴MyFlyOS设置关机权限。",
    "miboard.permission.FAVORITE": "MiBoard（可能是小米看板或类似应用）收藏权限。",
    "recorder.permission.START_RECORDER": "录音机应用启动录音权限。",
    "zte.com.market.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "中兴应用市场内部权限。",
    "zte.com.market.openadsdk.permission.TT_PANGOLIN": "中兴应用市场穿山甲广告SDK权限。",
    "zte.com.market.permission.WAKEUP_MESSAGE": "中兴应用市场唤醒消息权限。",
    "zte.permission.PUSH_MESSAGE.b5d866f": "中兴特定推送消息权限（后缀可能是动态生成的）。",
    "zte.permission.PUSH_MESSAGE_3ed90dce": "中兴特定推送消息权限（后缀可能是动态生成的）。",
    "zte.permission.SEND_POWER_SAVER_MODE": "中兴发送省电模式状态权限。",
    "zte.permission.WRITE_POWER_SAVER_APPS": "中兴写入省电应用列表权限。",

    "android.permission.ACCESS_ADSERVICES_STATE": "允许应用访问广告服务的状态。（Android 13+）",
    "android.permission.ACCESS_AMBIENT_CONTEXT_EVENT": "允许应用访问环境上下文事件（如设备是否在口袋里）。",
    "android.permission.ACCESS_AMBIENT_LIGHT_STATS": "允许应用访问环境光传感器统计信息。（系统级）",
    "android.permission.ACCESS_CONTENT_PROVIDERS_EXTERNALLY": "允许应用从外部访问内容提供者。（系统级）",
    "android.permission.ACCESS_DOWNLOAD_MANAGER_ADVANCED": "允许应用对下载管理器进行高级操作。（系统级）",
    "android.permission.ACCESS_IMS_CALL_SERVICE": "允许应用访问IMS（IP多媒体子系统）呼叫服务。",
    "android.permission.ACCESS_MESSAGES_ON_ICC": "允许应用访问ICC（SIM卡）上的消息。（系统级）",
    "android.permission.ACCESS_PRIVILEGED_APP_SET_ID": "允许特权应用访问应用集ID。（系统级）",
    "android.permission.ACCESS_VR_STATE": "允许应用访问VR（虚拟现实）模式状态。",
    "android.permission.ACT_AS_PACKAGE_FOR_ACCESSIBILITY": "允许应用代表另一个包与无障碍服务交互。（系统级）",
    "android.permission.ADD_TRUSTED_DISPLAY": "允许应用添加受信任的显示设备。（系统级）",
    "android.permission.ALLOW_ANY_CODEC_FOR_PLAYBACK": "允许应用在播放时使用任何编解码器，即使不被官方支持。（系统级）",
    "android.permission.AMBIENT_WALLPAPER": "允许应用提供环境光感壁纸。（系统级）",
    "android.permission.ASSOCIATE_INPUT_DEVICE_TO_DISPLAY": "允许应用将输入设备关联到特定显示器。（系统级）",
    "android.permission.BACKGROUND_CAMERA": "允许应用在后台访问摄像头。（Android 11+，受严格限制）",
    "android.permission.BIND_EXPLICIT_HEALTH_CHECK_SERVICE": "允许应用绑定到明确的健康检查服务。",
    "android.permission.BIND_NFC_SERVICE": "允许应用绑定到NFC服务。（系统级）",
    "android.permission.BIND_QUICK_SETTINGS_TILE": "允许应用提供快速设置磁贴。",
    "android.permission.BIND_RESOLVER_RANKER_SERVICE": "允许应用绑定到解析器排序服务。（系统级）",
    "android.permission.BIND_RESUME_ON_REBOOT_SERVICE": "允许应用绑定到重启后恢复服务。",
    "android.permission.BIND_TELEPHONY_NETWORK_SERVICE": "允许应用绑定到电话网络服务。",
    "android.permission.BIND_WALLPAPER": "允许应用绑定到壁纸服务。（系统级）",
    "android.permission.BLUETOOTH_STACK": "允许应用访问完整的蓝牙堆栈。（系统级）",
    "android.permission.BRIGHTNESS_SLIDER_USAGE": "允许应用跟踪亮度滑块的使用情况。（系统级）",
    "android.permission.BROADCAST_WAP_PUSH": "允许应用广播WAP PUSH消息。",
    "android.permission.CALL_AUDIO_INTERCEPTION": "允许应用拦截通话音频。（系统级，高度敏感）",
    "android.permission.CALL_COMPANION_APP": "允许应用调用配套应用。",
    "android.permission.CAPTURE_BLACKOUT_CONTENT": "允许应用捕获被标记为安全或黑屏的内容。（系统级）",
    "android.permission.CAPTURE_SECURE_VIDEO_OUTPUT": "允许应用捕获安全的视频输出。（系统级）",
    "android.permission.CHANGE_ACCESSIBILITY_VOLUME": "允许应用更改无障碍音量。（系统级）",
    "android.permission.CHANGE_LOWPAN_STATE": "允许应用更改LoWPAN（低功耗无线个域网）状态。（系统级）",
    "android.permission.COMPANION_APPROVE_WIFI_CONNECTIONS": "允许配套设备管理器批准Wi-Fi连接。",
    "android.permission.CONFIGURE_INTERACT_ACROSS_PROFILES": "允许应用配置跨配置文件（如工作资料和个人资料）的交互。（系统级）",
    "android.permission.CONTROL_ALWAYS_ON_VPN": "允许应用控制始终开启的VPN。（系统级）",
    "android.permission.CONTROL_DISPLAY_BRIGHTNESS": "允许应用控制显示亮度。（系统级）",
    "android.permission.CONTROL_DISPLAY_SATURATION": "允许应用控制显示饱和度。（系统级）",
    "android.permission.CONTROL_KEYGUARD_SECURE_NOTIFICATIONS": "允许应用控制锁屏安全通知的显示。（系统级）",
    "android.permission.CRYPT_KEEPER": "允许应用访问CryptKeeper服务，用于设备加密。（系统级）",
    "android.permission.DELETE_CACHE_FILES": "允许应用删除缓存文件。（系统级）",
    "android.permission.DISABLE_HIDDEN_API_CHECKS": "允许应用禁用对隐藏API的检查（开发/测试用途）。（系统级）",
    "android.permission.DISPATCH_PROVISIONING_MESSAGE": "允许应用分发设备配置消息。（系统级）",
    "android.permission.FOREGROUND_SERVICE_REMOTE_MESSAGING": "允许应用在前台运行远程消息服务。",
    "android.permission.GET_RUNTIME_PERMISSIONS": "允许应用查询其自身的运行时权限状态。",
    "android.permission.GRANT_RUNTIME_PERMISSIONS_TO_TELEPHONY_DEFAULTS": "允许系统将运行时权限授予默认的电话应用。（系统级）",
    "android.permission.HEALTH_CONNECT_BACKUP_INTER_AGENT": "Health Connect应用内部权限，用于备份代理间通信。",
    "android.permission.INPUT_CONSUMER": "允许应用作为输入消费者，接收但不处理输入事件。（系统级）",
    "android.permission.INSTALL_DPC_PACKAGES": "允许应用安装设备策略控制器（DPC）包。（系统级）",
    "android.permission.INSTALL_GRANT_RUNTIME_PERMISSIONS": "允许安装程序在安装时授予运行时权限。（系统级）",
    "android.permission.INSTALL_LOCATION_TIME_ZONE_PROVIDER_SERVICE": "允许应用安装位置时区提供程序服务。（系统级）",
    "android.permission.INSTALL_TEST_ONLY_PACKAGE": "允许应用安装仅用于测试的包。（开发权限）",
    "android.permission.INTENT_FILTER_VERIFICATION_AGENT": "允许应用作为Intent过滤器验证代理。（系统级）",
    "android.permission.INVOKE_CARRIER_SETUP": "允许应用调用运营商设置流程。（系统级）",
    "android.permission.LAUNCH_DEVICE_MANAGER_SETUP": "允许应用启动设备管理器设置流程。（系统级）",
    "android.permission.MANAGE_APP_TOKENS": "允许应用管理应用令牌。（系统级）",
    "android.permission.MANAGE_BIOMETRIC": "允许应用管理生物识别设置和数据。（系统级）",
    "android.permission.MANAGE_DEFAULT_APPLICATIONS": "允许应用管理默认应用程序（如默认浏览器、短信应用）。（系统级）",
    "android.permission.MANAGE_DEVICE_POLICY_CALLS": "允许应用管理与设备策略相关的呼叫。（系统级）",
    "android.permission.MANAGE_GAME_ACTIVITY": "允许应用管理游戏活动状态。（Android 12+）",
    "android.permission.MANAGE_GAME_MODE": "允许应用管理游戏模式。（Android 12+）",
    "android.permission.MANAGE_ROTATION_RESOLVER": "允许应用管理屏幕旋转决策器。（系统级）",
    "android.permission.MANAGE_SAFETY_CENTER": "允许应用管理安全中心功能。（系统级）",
    "android.permission.MANAGE_SLICE_PERMISSIONS": "允许应用管理Slices的权限。（系统级）",
    "android.permission.MANAGE_SPEECH_RECOGNITION": "允许应用管理语音识别服务。（系统级）",
    "android.permission.MANAGE_SUBSCRIPTION_USER_ASSOCIATION": "允许应用管理订阅与用户的关联。（系统级）",
    "android.permission.MANAGE_TIME_AND_ZONE_DETECTION": "允许应用管理时间和时区自动检测。（系统级）",
    "android.permission.MANAGE_TOAST_RATE_LIMITING": "允许应用管理Toast通知的速率限制。（系统级）",
    "android.permission.MANAGE_VIRTUAL_MACHINE": "允许应用管理虚拟机。（系统级，用于虚拟化框架）",
    "android.permission.MANAGE_WEAK_ESCROW_TOKEN": "允许应用管理弱托管令牌。（系统级）",
    "android.permission.MIGRATE_HEALTH_CONNECT_DATA": "允许应用迁移Health Connect数据。（系统级）",
    "android.permission.MODIFY_ACCESSIBILITY_DATA": "允许应用修改无障碍服务的数据。（系统级）",
    "android.permission.MODIFY_APPWIDGET_BIND_PERMISSIONS": "允许应用修改应用小部件的绑定权限。（系统级）",
    "android.permission.MODIFY_QUIET_MODE": "允许应用修改静默模式（如勿扰模式）。（系统级）",
    "android.permission.MODIFY_SETTINGS_OVERRIDEABLE_BY_RESTORE": "允许应用修改可被恢复操作覆盖的设置。（系统级）",
    "android.permission.MODIFY_TOUCH_MODE_STATE": "允许应用修改触摸模式状态。（系统级）",
    "android.permission.MODIFY_USER_PREFERRED_DISPLAY_MODE": "允许应用修改用户首选的显示模式。（系统级）",
    "android.permission.MONITOR_DEFAULT_SMS_PACKAGE": "允许应用监控默认短信应用的变化。（系统级）",
    "android.permission.MONITOR_DEVICE_CONFIG_ACCESS": "允许应用监控对设备配置的访问。（系统级）",
    "android.permission.NETWORK_BYPASS_PRIVATE_DNS": "允许应用绕过私有DNS设置。（系统级）",
    "android.permission.NETWORK_SCAN": "允许应用执行网络扫描（如Wi-Fi扫描，比ACCESS_WIFI_STATE更强大）。",
    "android.permission.OBSERVE_NETWORK_POLICY": "允许应用观察网络策略的变化。（系统级）",
    "android.permission.OPEN_ACCESSIBILITY_DETAILS_SETTINGS": "允许应用打开特定无障碍服务的详细设置页面。",
    "android.permission.OVERRIDE_COMPAT_CHANGE_CONFIG": "允许应用覆盖兼容性更改配置。（系统级）",
    "android.permission.OVERRIDE_COMPAT_CHANGE_CONFIG_ON_RELEASE_BUILD": "允许应用在发布版本上覆盖兼容性更改配置。（系统级）",
    "android.permission.PACKAGE_VERIFICATION_AGENT": "允许应用作为包验证代理。（系统级）",
    "android.permission.PROCESS_PHONE_ACCOUNT_REGISTRATION": "允许应用处理电话账户注册。（系统级）",
    "android.permission.READ_ACTIVE_EMERGENCY_SESSION": "允许应用读取活动的紧急会话信息。（系统级）",
    "android.permission.READ_GLOBAL_APP_SEARCH_DATA": "允许应用读取全局应用搜索数据。（系统级）",
    "android.permission.READ_INPUT_STATE": "允许应用读取当前输入状态。（系统级）",
    "android.permission.READ_RESTRICTED_STATS": "允许应用读取受限制的统计信息。（系统级）",
    "android.permission.READ_SOCIAL_STREAM": "允许应用读取社交流数据（已废弃）。",
    "android.permission.READ_VENDOR_CONFIG": "允许应用读取供应商特定的配置。（系统级）",
    "android.permission.READ_WALLPAPER_INTERNAL": "允许应用读取内部壁纸数据。（系统级）",
    "android.permission.REGISTER_MEDIA_RESOURCE_OBSERVER": "允许应用注册媒体资源观察者。（系统级）",
    "android.permission.REMOTE_DISPLAY_PROVIDER": "允许应用作为远程显示提供者。（系统级）",
    "android.permission.RENOUNCE_PERMISSIONS": "允许应用放弃其先前授予的权限。（系统级）",
    
    "com.google.android.finsky.permission.ACCESS_INSTANT_APP_NOTIFICATION_ENFORCEMENT": "允许Google Play商店强制执行即时应用的通知策略。",
    "com.google.android.gms.home.matter.BIND_MATTER_COMMISSIONING_SERVICE": "允许绑定到Google Home的Matter智能家居设备配网服务。",
    "com.google.android.onetimeinitializer.permission.ONE_TIME_INITIALIZED": "标记一次性初始化任务已完成的权限（Google服务相关）。",
    "com.google.android.finsky.permission.DEVELOPER_GROUP_ID_INFO": "允许Google Play商店访问开发者组ID信息。",
    "zte.permission.PUSH_MESSAGE_3e4f5a41": "中兴（ZTE）特定推送消息服务的权限（ID: 3e4f5a41）。",
    "com.qualcomm.permission.ACCESS_GTPWIFI_API": "高通（Qualcomm）特定权限，允许访问GTP Wi-Fi API（可能用于数据隧道）。",
    "android.permission.SET_SCREEN_COMPATIBILITY": "允许应用设置屏幕兼容性模式（已废弃）。",
    "suggest.permission.signature": "自定义建议提供程序的签名级别权限，确保只有特定签名的应用可以访问。",
    "launchermfv.permission.DYNAMIC_SHOW_HIDDEN_APPS": "中兴MyFlyOS启动器权限，用于动态显示/隐藏应用。",
    "android.permission.SCHEDULE_PRIORITIZED_ALARM": "允许应用调度高优先级精确闹钟（Android S+，受限）。",
    "androidx.legacy.coreui.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "AndroidX Legacy Core UI库内部权限，用于未导出的动态广播接收器。",
    "com.google.android.gms.permission.CAR_SPEED": "允许Google Play服务访问车辆速度信息（Android Auto相关）。",
    "com.android.vending.INTENT_VENDING_ONLY": "Google Play商店权限，限制某个Intent只能由Play商店处理。",
    "com.google.android.gms.permission.CAR": "允许Google Play服务与车辆集成（Android Auto相关）。",
    "com.google.android.gms.permission.BIOAUTH_CONSENT": "Google Play服务生物识别身份验证的同意权限。",
    "com.google.android.gms.auth.api.phone.permission.SEND": "Google Play服务Auth API权限，用于发送与电话号码验证相关的信息。",
    "androidx.legacy.v4.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "AndroidX Legacy Support v4库内部权限，用于未导出的动态广播接收器。",
    "com.google.android.gms.permission.ACCESS_NEARBY_SHARE_API": "允许Google Play服务访问附近分享（Nearby Share）API。",
    "android.permission.SEND_EMBMS_INTENTS": "允许应用发送与eMBMS（增强型多媒体广播多播服务）相关的意图。",
    "zte.permission.START_GESTURE_GUIDE": "中兴（ZTE）特定权限，用于启动手势引导。",
    "com.android.devicelockcontroller.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "设备锁控制器（Device Lock Controller）内部权限，用于未导出的动态广播接收器。",
    "com.android.voicemail.permission.READ_VOICEMAIL": "允许应用读取语音信箱。",
    "androidx.dynamicanimation.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "AndroidX DynamicAnimation库内部权限，用于未导出的动态广播接收器。",
    "com.google.android.gms.permission.BIND_PAYMENTS_CALLBACK_SERVICE": "允许Google Play服务绑定到支付回调服务（如Google Pay）。",
    "com.yulore.permission.YULORE_BROADCAST_RECEIVER": "号码识别服务（如Yulore）的自定义广播接收器权限。",
    "alarmclock.permission.ENABLE_OR_DISABLE_ALARM": "闹钟应用自定义权限，用于启用或禁用闹钟。",
    "com.android.vending.setup.PLAY_SETUP_SERVICE": "Google Play商店设置服务的权限。",
    "com.qti.qcc.permission.QCCUI": "高通（QTI）特定权限，与QCC（Qualcomm Connected Car）用户界面相关。",
    "android.permission.REQUEST_COMPANION_PROFILE_NEARBY_DEVICE_STREAMING": "允许应用请求配套设备配置文件以进行附近设备流式传输。",
    "com.google.android.apps.now.OPT_IN_WIZARD": "Google Now（或Google助理）选择加入向导的权限。",
    "contacts.permission.START_ADD_TO_BLACKLIST": "联系人应用自定义权限，用于启动添加到黑名单的功能。",
    "com.android.soundpicker.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "声音选择器（Sound Picker）内部权限，用于未导出的动态广播接收器。",
    "com.google.android.gms.permission.GOOGLE_PAY": "允许Google Play服务访问Google Pay功能。",
    "alarmclock.permission.SET_ALARM_DEFAULT_RINGTONE": "闹钟应用自定义权限，用于设置默认闹钟铃声。",
    "com.google.android.gms.matchstick.permission.BROADCAST_LIGHTER_WEB_INFO": "Google Play服务Matchstick（可能与Cast或轻量级Web相关）广播信息的权限。",
    "android.permission.TEST_BIOMETRIC": "允许应用测试生物识别硬件和API。（系统/开发权限）",
    "com.qti.qcc.permission.VENDOR_QCC": "高通（QTI）特定权限，与供应商QCC（Qualcomm Connected Car）功能相关。",
    "com.qualcomm.permission.ACCESS_GTPWWAN_API": "高通（Qualcomm）特定权限，允许访问GTP WWAN API（可能用于移动数据隧道）。",
    "android.permission.SET_GAME_SERVICE": "允许应用设置游戏服务，可能用于游戏模式或优化。（系统级）",
    "zte.permission.PUSH_MESSAGE_23af53b9": "中兴（ZTE）特定推送消息服务的权限（ID: 23af53b9）。",
    "com.zte.halo.app.permission.myprovider": "中兴（ZTE）Halo应用自定义内容提供程序的权限。",
    "com.google.android.gms.auth.proximity.permission.SMS_CONNECT_SETUP_REQUESTED": "Google Play服务Auth邻近功能权限，用于请求SMS连接设置。",
    "com.google.android.gms.permission.ACCESS_MULTIPACKAGE_COMPONENT": "允许Google Play服务访问多包组件。",
    "com.google.android.gms.permission.REPORT_TAP": "允许Google Play服务报告点击事件（可能用于分析或无障碍）。",
    "android.permission.REVOKE_POST_NOTIFICATIONS_WITHOUT_KILL": "允许应用在不终止目标应用的情况下撤销其发送通知的权限。（系统级）",
    "com.google.android.projection.gearhead.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Android Auto (Gearhead) 内部权限，用于未导出的动态广播接收器。",
    "com.zte.permission.FDN_STATUS_CHANGE": "中兴（ZTE）特定权限，用于FDN（固定拨号号码）状态更改通知。",
    "android.permission.START_VIEW_PERMISSION_USAGE": "允许应用启动查看权限使用情况的界面。（系统级）",
    "com.qti.permission.DIAG": "高通（QTI）特定权限，用于访问诊断功能。",
    "android.permission.WRITE_PROFILE": "允许应用写入用户个人资料数据。（系统级）",
    "android.permission.WRITE_GSERVICES": "允许应用写入Google服务框架的配置数据。（系统/签名权限）",
    "com.android.credentialmanager.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "凭据管理器（Credential Manager）内部权限，用于未导出的动态广播接收器。",
    "android.permission.START_ACTIVITY_AS_CALLER": "允许应用以调用者的身份启动活动。（系统级）",
    "com.zte.heartyservice.openadsdk.permission.TT_PANGOLIN": "中兴HeartyService集成穿山甲（Pangolin/TikTok）广告SDK的权限。",
    "android.permission.REQUEST_COMPANION_PROFILE_APP_STREAMING": "允许应用请求配套设备配置文件以进行应用流式传输。",
    "com.zte.beautifyadapter.applytheme": "中兴（ZTE）美化适配器应用主题的权限。",
    "android.permission.REQUEST_NOTIFICATION_ASSISTANT_SERVICE": "允许应用请求成为通知助手服务。",
    "com.google.android.gms.permission.PHENOTYPE_UPDATE_BROADCAST": "Google Play服务Phenotype（配置实验框架）更新广播的权限。",
    "android.permission.RESET_SHORTCUT_MANAGER_THROTTLING": "允许应用重置快捷方式管理器的限流。（系统级）",
    "android.permission.WRITE_DEVICE_CONFIG": "允许应用写入设备配置值。（系统/签名权限）",
    "com.google.android.gms.nearby.exposurenotification.EXPOSURE_CALLBACK": "Google Play服务附近暴露通知（Exposure Notification）回调的权限。",
    "android.permission.REVOKE_RUNTIME_PERMISSIONS": "允许应用撤销其他应用的运行时权限。（系统/签名权限）",
    "android.permission.SYSTEM_CAMERA": "允许应用作为系统相机应用访问摄像头，拥有更高权限。（系统/签名权限）",
    "android.permission.SET_LOW_POWER_STANDBY_PORTS": "允许应用配置在低功耗待机模式下保持活动的网络端口。（系统级）",
    "android.permission.REQUEST_OBSERVE_COMPANION_DEVICE_PRESENCE": "允许应用请求观察配套设备的存在状态。",
    "com.zte.livewallpaper.permission.READ_FILE": "中兴（ZTE）动态壁纸读取文件的权限。",
    "com.google.firebase.auth.api.gms.permission.LAUNCH_FEDERATED_SIGN_IN": "Firebase Auth API权限，用于启动联合身份验证登录流程。",
    "com.android.vending.BIOAUTH_CONSENT": "Google Play商店生物识别身份验证的同意权限（与GMS版本可能略有不同）。",
    "android.permission.TEST_MANAGE_ROLLBACKS": "允许应用测试管理应用回滚功能。（系统/开发权限）",
    "systemui.permission.read_client_provider": "SystemUI自定义权限，允许读取其客户端提供程序的数据。",
    "com.google.android.gms.auth.authzen.permission.GCM_DEVICE_PROXIMITY": "Google Play服务Authzen（双因素认证）设备邻近GCM消息的权限。",
    "com.google.android.gms.learning.permission.LAUNCH_IN_APP_PROXY": "Google Play服务Learning（可能与联合学习相关）启动应用内代理的权限。",
    "does.not.matter.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "占位符/示例包名的内部权限，用于未导出的动态广播接收器。",
    "com.android.permissioncontroller.permission.MANAGE_ROLES_FROM_CONTROLLER": "权限控制器（PermissionController）管理系统角色的权限。",
    "com.android.cellbroadcastservice.FULL_ACCESS_CELL_BROADCAST_HISTORY": "小区广播服务完全访问小区广播历史记录的权限。",
    "android.permission.UWB_PRIVILEGED": "允许应用以特权方式访问UWB（超宽带）硬件。",
    "com.android.simappdialog.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "SIM卡应用对话框（SIM App Dialog）内部权限，用于未导出的动态广播接收器。",
    "android.permission.REQUEST_COMPANION_PROFILE_WATCH": "允许应用请求与手表类配套设备相关的配置文件。",
    "com.google.android.gms.chimera.permission.CONFIG_CHANGE": "Google Play服务Chimera（动态模块加载框架）配置更改的权限。",
    "android.permission.SET_AND_VERIFY_LOCKSCREEN_CREDENTIALS": "允许应用设置并验证锁屏凭据。（系统级）",
    "com.google.android.gms.WRITE_VERIFY_APPS_CONSENT": "允许Google Play服务写入“验证应用”功能的同意状态。",
    "com.qualcomm.permission.IZAT": "高通（Qualcomm）IZat定位服务平台的权限。",
    "com.google.android.gms.dck.permission.DIGITAL_KEY_PRIVILEGED": "Google Play服务数字车钥匙（Digital Car Key）的特权权限。",
    "zte.permission.PUSH_MESSAGE.f1a3f11": "中兴（ZTE）特定推送消息服务的权限（ID: f1a3f11）。", # 格式略有不同，但含义类似
    "com.qualcomm.permission.UIM_REMOTE_CLIENT": "高通（Qualcomm）UIM（用户身份模块）远程客户端的权限。",
    "zte.com.market.permission.READ_DOWNLOADS": "中兴（ZTE）应用商店读取下载内容的权限。",
    "cuuca.sendfiles.Activity.permission.cloudbackup": "特定应用（cuuca.sendfiles）云备份功能的自定义权限。",
    "com.qualcomm.permission.ACCESS_GTPWWAN_CROWDSOURCING_API": "高通（Qualcomm）特定权限，允许访问GTP WWAN众包API。",
    "com.zte.voiceassist.wakeup.permission.wakeup.file": "中兴（ZTE）语音助手唤醒功能访问唤醒文件的权限。",
    "com.google.android.onetimeinitializer.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Google一次性初始化器（OneTimeInitializer）内部权限，用于未导出的动态广播接收器。",
    "com.google.android.gms.permission.BIND_NETWORK_TASK_SERVICE": "允许Google Play服务绑定到网络任务服务。",
    "com.android.vendorlogpermission.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "供应商日志权限管理应用内部权限，用于未导出的动态广播接收器。",
    "com.android.captiveportallogin.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "强制网络门户登录（Captive Portal Login）应用内部权限，用于未导出的动态广播接收器。",
    "androidx.fragment.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "AndroidX Fragment库内部权限，用于未导出的动态广播接收器。",
    "android.permission.TOGGLE_AUTOMOTIVE_PROJECTION": "允许应用切换车载投屏模式（如Android Auto）。（系统级）",
    "android.permission.RETRIEVE_WINDOW_CONTENT": "允许应用检索窗口内容（主要用于无障碍服务或测试）。",
    "com.google.android.gtalkservice.permission.SEND_HEARTBEAT": "Google Talk服务（旧版，现集成于GMS）发送心跳包的权限。",
    "com.zte.heartyservice.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "中兴HeartyService内部权限，用于未导出的动态广播接收器。",
    "com.google.android.gsf.permission.C2D_MESSAGE": "Google服务框架（GSF）接收云端到设备（C2D）消息的权限。",
    "com.google.android.gms.auth.api.signin.permission.REVOCATION_NOTIFICATION": "Google Play服务Auth API登录撤销通知的权限。",
    "android.permission.SET_HARMFUL_APP_WARNINGS": "允许应用设置有害应用警告。（系统级）",
    "systemui.permission.write_client_provider": "SystemUI自定义权限，允许写入其客户端提供程序的数据。",
    "com.android.systemui.permission.SELF": "SystemUI授予自身权限的标记权限。",
    "com.android.companiondevicemanager.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "配套设备管理器（Companion Device Manager）内部权限，用于未导出的动态广播接收器。",
    "android.permission.RECEIVE_STK_COMMANDS": "允许应用接收来自SIM卡工具包（STK）的命令。",
    "com.google.android.finsky.permission.GEARHEAD_SERVICE": "Google Play商店与Android Auto (Gearhead) 服务交互的权限。",
    "com.qualcomm.qti.qdma.permission.QDMA": "高通（QTI）QDMA（Qualcomm Direct Memory Access）功能的权限。",
    "com.zte.mfvkeyguard.read.step": "中兴MyFlyOS锁屏读取计步数据的权限。",
    "com.juphoon.rcs.notify.permission": "卓易讯（Juphoon）RCS（富通信服务）通知的自定义权限。",
    "com.google.android.providers.gsf.permission.WRITE_GSERVICES": "Google服务框架内容提供程序写入GServices配置的权限（与android.permission.WRITE_GSERVICES类似但特定于提供程序）。",
    "zte.permission.PUSH_MESSAGE_449faa87": "中兴（ZTE）特定推送消息服务的权限（ID: 449faa87）。",
    "android.permission.SET_PROCESS_LIMIT": "允许应用设置后台进程限制。（系统/签名权限）",
    "messaging.permission.PRIVILEGED": "授予消息应用特权操作的权限（通常用于系统默认短信应用）。",
    "org.codeaurora.permission.POWER_OFF_ALARM": "CodeAurora（高通相关）特定权限，允许在关机状态下响应闹钟。",
    "android.permission.MANAGE_DEVICE_POLICY_TIME": "允许应用管理设备策略中的时间限制（如家长控制）。（系统级）",
    "com.android.devicelockcontroller.permission.MANAGE_DEVICE_LOCK_SERVICE_FROM_CONTROLLER": "设备锁控制器管理设备锁服务的权限。",
    "com.google.android.googleapps.permission.GOOGLE_AUTH.YouTubeUser": "Google应用套件权限，用于YouTube用户的Google身份验证。",
    "com.qti.permission.RECEIVE_MSIM_VOICE_CAPABILITY": "高通（QTI）特定权限，用于接收MSIM（多SIM卡）语音能力信息。",
    "easymode.permission.provider.call": "简易模式（Easy Mode）内容提供程序关于通话的权限。",
    "com.android.storagemanager.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "存储管理器（Storage Manager）内部权限，用于未导出的动态广播接收器。",
    "mfvkeyguard.permission.START_MFVKEYGUARD": "中兴MyFlyOS锁屏启动自身的权限。",
    "com.google.android.gms.googlehelp.LAUNCH_SUPPORT_SCREENSHARE": "Google Play服务Google帮助启动支持屏幕共享功能的权限。",
    "android.permission.TRIGGER_LOST_MODE": "允许应用触发设备丢失模式。（系统级，通常由设备查找服务使用）",
    "android.permission.STAGE_HEALTH_CONNECT_REMOTE_DATA": "允许应用暂存来自远程源的Health Connect数据，以便后续导入。（系统级）",
    "com.google.android.gms.auth.permission.POST_SIGN_IN_ACCOUNT": "Google Play服务Auth登录后账户操作的权限。",
    "com.google.android.gms.auth.cryptauth.permission.KEY_CHANGE": "Google Play服务CryptAuth（设备间安全通信）密钥更改通知的权限。",
    "android.permission.RETRIEVE_WINDOW_TOKEN": "允许应用检索窗口令牌，用于窗口管理。（系统级）",
    "com.google.android.gms.chromesync.permission.CONTENT_PROVIDER_ACCESS": "Google Play服务Chrome同步功能访问内容提供程序的权限。",
    "android.permission.SET_ANIMATION_SCALE": "允许应用设置动画缩放比例（通常用于开发者选项）。",
    "contactsprovider.permission.READ_CALL_PHONE_RECORD": "联系人提供程序读取通话和电话记录的自定义权限。",
    "com.android.chrome.permission.SHOW_COMPLIANCE_SCREEN": "Chrome浏览器显示合规性界面的权限。",
    "com.zte.retrieve.permission.PUSH": "中兴（ZTE）找回手机（Retrieve）功能的推送权限。",
    "com.google.android.gms.permission.BROADCAST_TO_GOOGLEHELP": "允许Google Play服务向Google帮助应用广播消息。",
    "com.android.shell.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION": "Android Shell内部权限，用于未导出的动态广播接收器。",
    "android.permission.RESET_PASSWORD": "允许应用重置设备锁屏密码（需要设备管理员权限）。",
    "contacts.permission.START_MULTI_SELECTION": "联系人应用自定义权限，用于启动多选模式。",
    "com.zte.permission.CTRL_STORY": "中兴（ZTE）特定权限，可能与“故事”或类似内容聚合功能相关。",
    "com.android.vending.permission.C2D_MESSAGE": "Google Play商店接收云端到设备（C2D）消息的权限。"
}



apps_dict: dict[str, str] = {
    # 社交通讯
    "com.tencent.mm": "微信",
    "com.tencent.mobileqq": "QQ",
    "com.sina.weibo": "微博",
    "com.immomo.momo": "陌陌", # 曾用名，现在可能主要是 "MOMO陌陌"
    "com.smile.gifmaker": "快手", # 快手主App
    "com.ss.android.ugc.aweme": "抖音",
    "com.ss.android.ugc.aweme.lite": "抖音极速版",
    "com.kuaishou.nebula": "快手极速版",
    "com.xingin.xhs": "小红书",
    "tv.danmaku.bili": "哔哩哔哩", # B站
    "com.zhihu.android": "知乎",
    "com.douban.frodo": "豆瓣",
    "com.alibaba.android.rimet": "钉钉",
    "com.tencent.wework": "企业微信",
    "com.ss.android.lark": "飞书",
    "org.telegram.messenger": "Telegram", # 电报 (需特殊网络)
    "com.twitter.android": "Twitter", # 推特 (需特殊网络)
    "com.facebook.katana": "Facebook", # 脸书 (需特殊网络)
    "com.instagram.android": "Instagram", # Ins (需特殊网络)
    "com.whatsapp": "WhatsApp", # (需特殊网络)

    # 电商购物
    "com.taobao.taobao": "淘宝",
    "com.tmall.wireless": "天猫", # 手机天猫
    "com.jingdong.app.mall": "京东",
    "com.xunmeng.pinduoduo": "拼多多",
    "com.suning.mobile.ebuy": "苏宁易购",
    "com.achievo.vipshop": "唯品会",
    "com.mogujie": "蘑菇街",
    "com.taobao.idlefish": "闲鱼",
    "com.dangdang.buy2": "当当",
    "com.amazon.mShop.android.shopping": "亚马逊购物", # 亚马逊中国区可能不同

    # 生活服务 & 出行 & 地图
    "com.sankuai.meituan": "美团",
    "com.dianping.v1": "大众点评",
    "com.wuba": "58同城",
    "com.ganji.android": "赶集网",
    "com.autonavi.minimap": "高德地图",
    "com.baidu.BaiduMap": "百度地图",
    "com.tencent.map": "腾讯地图",
    "com.sdu.didi.psnger": "滴滴出行", # 乘客端
    "com.didapinche.booking": "嘀嗒出行",
    "com.souche.ucar": "神州专车", # 现 神州租车/宝沃汽车
    "ctrip.android.view": "携程旅行",
    "com.Qunar": "去哪儿旅行",
    "com.elong.android.flight": "同程旅行", # 原名艺龙旅行
    "com.taobao.trip": "飞猪旅行", # 原阿里旅行
    "com.mfw.roadbook": "马蜂窝旅游",
    "com.airbnb.android": "Airbnb爱彼迎",
    "com.unionpay.mobile.tsm": "云闪付",
    "com.eg.android.AlipayGphone": "支付宝",

    # 浏览器
    "com.android.chrome": "Chrome浏览器",
    "com.UCMobile": "UC浏览器", # 国内版
    "com.UCMobile.intl": "UC浏览器国际版",
    "com.tencent.mtt": "QQ浏览器",
    "com.baidu.browser.apps": "百度浏览器", # 可能已较少更新
    "com.qihoo.browser": "360浏览器",
    "org.mozilla.firefox": "Firefox浏览器",
    "com.opera.browser": "Opera浏览器",
    "com.microsoft.emmx": "Microsoft Edge",

    # 视频 & 直播
    "com.qiyi.video": "爱奇艺",
    "com.tencent.qqlive": "腾讯视频",
    "com.youku.phone": "优酷视频",
    "com.hunantv.imgo.activity": "芒果TV",
    "com.sohu.sohuvideo": "搜狐视频",
    "com.pplive.androidphone": "PP视频", # 原PPTV
    "com.le.letv": "乐视视频", # 可能已较少更新
    "com.duowan.kiwi": "虎牙直播",
    "air.tv.douyu.android": "斗鱼直播",
    "com.bokecc.live": "CC直播", # 网易CC

    # 音乐 & 音频
    "com.netease.cloudmusic": "网易云音乐",
    "com.tencent.qqmusic": "QQ音乐",
    "com.kugou.android": "酷狗音乐",
    "com.kuwo.player": "酷我音乐",
    "com.baidu.music": "千千音乐", # 原百度音乐
    "fm.xiami.main": "虾米音乐", # 已停止服务，但包名可能仍存在于旧设备
    "com.lizhiinc.荔枝": "荔枝FM", # 包名可能是 com.lizhiinc.LitchiFM
    "com.ximalaya.ting.android": "喜马拉雅",

    # 新闻资讯
    "com.ss.android.article.news": "今日头条",
    "com.tencent.news": "腾讯新闻",
    "com.sina.news": "新浪新闻",
    "com.sohu.newsclient": "搜狐新闻",
    "com.netease.newsreader.activity": "网易新闻",
    "com.ifeng.newsreader": "凤凰新闻",
    "com.baidu.searchbox": "百度App", # 也包含新闻
    "com.uc.infoflow": "UC头条", # UC浏览器内置或独立

    # 工具 & 效率
    "com.baidu.netdisk": "百度网盘",
    "com.tencent.weiyun": "腾讯微云",
    "cn.wps.moffice_eng": "WPS Office", # 或 cn.wps.moffice_cn
    "com.microsoft.office.officehubrow": "Microsoft Office", # 或 Word, Excel, PowerPoint 单独应用
    "com.microsoft.word": "Microsoft Word",
    "com.microsoft.excel": "Microsoft Excel",
    "com.microsoft.powerpoint": "Microsoft PowerPoint",
    "com.adobe.reader": "Adobe Acrobat Reader",
    "com.youdao.dict": "有道词典",
    "com.kingsoft.糍粑": "金山词霸", # 包名可能是 com.kingsoft.ciba
    "com.tencent.qqpimsecure": "腾讯手机管家",
    "com.qihoo.magic": "360手机卫士",
    "com.baidu.system.light": "百度手机卫士", # 可能已较少更新
    "com.sohu.inputmethod.sogou": "搜狗输入法", # 或 sogou.mobile.explorer (搜狗输入法小米版等)
    "com.baidu.input": "百度输入法",
    "com.iflytek.inputmethod": "讯飞输入法",
    "com.tencent.qqpinyin": "QQ输入法",
    "com.google.android.inputmethod.pinyin": "Google拼音输入法",
    "com.meitu.meiyancamera": "美颜相机",
    "com.mt.mtxx.mtxx": "美图秀秀", # 包名可能是 com.meitu.mtxx
    "com.moji.mjweather": "墨迹天气",
    "com.tencent.qqmail": "QQ邮箱",
    "com.netease.mobimail": "网易邮箱大师",
    "com.android.calendar": "系统日历", # 虽然是系统，但常用
    "com.google.android.calendar": "Google日历",
    "com.alipay.android.phone.wealth.financialehlth": "支付宝记账本", # 示例，支付宝内嵌功能包名复杂

    # 游戏 (仅举例几个非常流行的)
    "com.tencent.tmgp.sgame": "王者荣耀",
    "com.tencent.tmgp.pubgmhd": "和平精英", # (原刺激战场)
    "com.miHoYo.Yuanshen": "原神", # 国内安卓渠道包名可能不同，如 com.miHoYo.ys.android.bilibili
    "com.hypergryph.arknights": "明日方舟",
    "com.netease.onmyoji": "阴阳师",

    # 其他
    "com.xueqiu.android": "雪球", # 股票财经
    "com.eastmoney.android.berlin": "东方财富", # 股票财经
    "com.gotokeep.keep": "Keep", # 健身
    "com.chinamworld.main": "中国建设银行",
    "com.icbc": "中国工商银行",
    "com.bankcomm.Bankcomm": "交通银行",
    "com.android.bankabc": "中国农业银行",
    "com.citicbank.mobilebank": "中信银行",
    "com.pingan.paces.ccms": "平安口袋银行",

    "hineyue.sjgjj": "手机公积金 (某个地区或版本)",
    "com.unionpay": "云闪付 (中国银联官方App)",
    "com.cmcc.cmvideo": "咪咕视频 (中国移动旗下)",
    "com.kugou.android.lite": "酷狗音乐概念版或Lite版",
    "com.agc.gcam_tools": "GCam Tools (谷歌相机工具)",
    "com.greenpoint.android.mc10086.activity": "中国移动 (掌上营业厅)",
    "com.zte.manual": "中兴用户手册/说明书",
    "cuuca.sendfiles.Activity": "Cuuca快传 (或类似文件传输工具)",
    "com.agc.gcam84": "GCam 8.4 (谷歌相机移植版)",
    "cn.gov.tax.its": "个人所得税",
    "ch.protonmail.android": "ProtonMail (安全邮箱)",
    "com.google.android.apps.translate": "Google 翻译",
    "com.zte.kidszone": "中兴儿童空间",
    "com.zte.quickgame": "中兴快应用/小游戏中心",
    "moe.shizuku.privileged.api": "Shizuku (提权工具)",
    "com.happymax.fcmpushviewer": "FCM 推送查看器",
    "com.bilibili.app.in": "哔哩哔哩 / B站",
    "com.google.android.youtube": "YouTube / 油管",
    "com.chinamobile.mcloud": "和彩云 (中国移动云盘)",
    "com.zte.userguide": "中兴用户指南",
    "com.v2ray.ang": "V2RayNG (网络代理工具)",
    "com.zte.remotecontroller": "中兴遥控器",
    "com.lemon.lv": "剪映",
    "web1n.stopapp": "StopApp (停止应用工具，可能是字面意思)",
    "li.songe.gkd": "GKD / 李跳跳 (App开屏广告跳过类工具)",
    "com.ophone.reader.ui": "OPhone 阅读 (早期中国移动定制系统阅读器)",
    "com.samsung.agc.gcam84": "三星 GCam 8.4 (三星设备适配的谷歌相机移植版)",
    
    "com.samsung.android.ruler": "三星测距仪",
    "com.gopro.smarty": "GoPro Quik (或GoPro App)",
    "com.mfcloudcalculate.networkdisk": "可能是某个云盘或网络存储应用（名称不明确）",
    "com.google.android.apps.photos": "Google 相册",
    "cn.nubia.game.magicvoice": "努比亚游戏魔音 (努比亚手机内置)",
    "com.shengdoushipp.wbquery": "可能是某个违章查询或类似生活服务应用 (名称不明确)",
    "com.google.android.keep": "Google Keep (Google 记事)",
    "com.redteamobile.roaming": "红茶移动漫游服务 (或类似名称)",
    "com.android.calculator2": "计算器 (通常是原生或类原生安卓系统计算器)",
    "org.thunderdog.challegram": "Challegram (一个非官方Telegram客户端)",
    "com.shineyue.sjgjj": "手机公积金 (或类似名称的公积金查询应用)",
    "com.google.android.gm": "Gmail (Google 邮箱)",
    "com.cnspeedtest.globalspeed": "全球网速管家 (或类似测速应用)",
    "com.mi.health": "小米运动健康 (或小米健康)",
    "com.google.android.googlequicksearchbox": "Google (Google 搜索应用或Google助理的后台包)",
    "lf.example.wubi": "可能是某个五笔输入法示例或小型应用 (名称不明确)",
    "cn.com.chsi.chsiapp": "学信网",
    "com.dengziwl.bk": "可能是某个笔记或备忘录类应用 (名称不明确, “bk”可能指“备忘”或“笔记”)",
    "com.aimp.player": "AIMP (一款音乐播放器)",
    "com.guoyu.strokeorder": "汉字笔顺 (或类似名称的汉字学习应用)",
    "com.zte.cn.compass": "中兴指南针 (中兴手机内置)",
    "com.xiaomi.mimobile": "小米移动 (小米的虚拟运营商服务应用)",
    "com.tmri.app.main": "交管12123",
    "cn.zte.bbs": "中兴社区 (或中兴论坛)",
    "com.zte.smarthome": "中兴智能家居",
    "moe.nb4a": "NekoBox for Android (一款网络代理工具)",
    "com.deepseek.chat": "DeepSeek Chat (或月之暗面Kimi智能助手)",
    "com.MobileTicket": "12306 (中国铁路官方购票应用)",
    "cn.ecooktwo": "网上厨房 (或类似名称的美食菜谱应用)",
    "com.zte.mifavor.variablewidget": "中兴MiFavor可变小部件 (中兴手机系统组件)",
    "com.shamim.cam": "可能是某个第三方相机应用 (名称不明确)",
    "cmb.pb": "招商银行 (招行手机银行)",
    "com.google.android.inputmethod.latin": "Gboard - Google 输入法 (或原生安卓拉丁输入法)",
    "com.azure.authenticator": "Microsoft Authenticator (微软身份验证器)",
    "mark.via.gp": "Via 浏览器 (Google Play 版本)",
    "com.github.android": "GitHub (GitHub 官方安卓应用)",
    "cmccwm.mobilemusic": "咪咕音乐 (中国移动旗下)",
    "com.zte.zmall": "中兴商城",
    "com.openai.chatgpt": "ChatGPT (OpenAI官方应用)",
    "tech.lolli.toolbox": "LSPatch (或搞机助手，一个Xposed模块管理工具)",
    "com.agc.gcam92": "谷歌相机修改版 (AGC移植, 版本9.2)",
    "com.agc.gcam88": "谷歌相机修改版 (AGC移植, 版本8.8)",
    "com.guoyu.gushici": "古诗词 (或类似名称的诗词学习应用)",
    "com.google.android.apps.authenticator2": "Google Authenticator (Google 身份验证器)",
    "com.web1n.permissiondog": "权限狗 (一款权限管理工具)",
    "com.zte.mifavor.weather": "中兴MiFavor天气 (中兴手机内置)",
    "com.mxtech.videoplayer.pro": "MX Player Pro (MX 播放器专业版)",
    "com.nexstreaming.app.kinemasterfree": "KineMaster - 巧影 (视频编辑应用免费版)",
    
    "com.zte.fingerprints": "中兴指纹服务",
    "com.qti.dpmserviceapp": "高通设备策略管理服务",
    "com.zte.linkspeedup": "中兴网络加速",
    "vendor.qti.qesdk.sysservice": "高通QE SDK系统服务", # QE可能指Qualcomm Enhanced
    "com.redteamobile.virtual.softsim": "红茶移动虚拟SIM卡/软SIM服务",
    "zpub.res": "zpub资源包", # "zpub"可能是某个内容提供商或框架的代号
    "com.zte.onemorething": "中兴 One More Thing (特色功能)",
    "com.zte.superwallpaper.planet": "中兴超级壁纸·星球",
    "cn.nubia.filebrowser": "努比亚文件管理器",
    "com.qti.qcc": "高通互联汽车 (QCC)",
    "com.zte.mifavor.quickcall": "中兴MiFavor快速呼叫",
    "com.zte.voiprecorder": "中兴VoIP通话录音",
    "com.zte.zdm": "中兴设备管理 (ZDM)",
    "com.qti.xdivert": "高通X-Divert (通话转移增强)",
    "org.codeaurora.ims": "CAF IMS服务 (VoLTE/VoWiFi核心服务)", # Code Aurora Forum
    "com.zte.zteconfigupdate": "中兴配置更新服务",
    "com.zte.easymode": "中兴简易模式",
    "com.zte.retrieve": "中兴手机找回",
    "com.zte.cloud": "中兴云服务",
    "com.zte.heartrate": "中兴心率监测",
    "cn.nubia.keymapcenter": "努比亚按键映射中心",
    "com.zte.zdmdaemon.install": "中兴设备管理守护进程安装程序",
    "cn.nubia.gamehelpmodule": "努比亚游戏助手模块",
    "com.zte.mifavor.launcher.adapter": "中兴MiFavor启动器适配器",
    "org.zx.AuthComp": "ZX认证组件", # "ZX"可能是开发者或公司缩写
    "com.yulore.framework": "号码慧眼框架 (来电识别)",
    "com.zte.vendor.ifaa": "中兴IFAA服务 (互联网金融身份认证)",
    "com.zte.windowreply": "中兴窗口回复 (快捷回复功能)",
    "com.zte.wlansniffertool": "中兴WLAN嗅探工具",
    "com.westalgo.aftersalecamera": "Westalgo售后相机 (相机算法相关)",
    "com.zte.mifavor.zsearch": "中兴MiFavor Z搜索",
    "com.zte.faceverify": "中兴人脸识别服务",
    "cn.nubia.gif": "努比亚GIF图库/查看器",
    "cn.nubia.arkbase": "努比亚方舟基础服务", # Ark方舟编译器相关
    "vendor.qti.imsrcs": "高通IMS资源",
    "com.sohu.inputmethod.sogou.nubia": "搜狗输入法努比亚版",
    "com.zte.kidszone.adapter": "中兴儿童空间适配器",
    "com.mifavor.callsetting": "MiFavor通话设置",
    "cn.zte.recorder": "中兴录音机",
    "cn.nubia.videoeditor": "努比亚视频编辑器",
    "com.zte.aiengine": "中兴AI引擎",
    "com.zte.livewallpaper": "中兴动态壁纸",
    "cn.nubia.gifmaker": "努比亚GIF制作",
    "com.zte.powersavemode": "中兴省电模式",
    "com.zte.seinputmethod": "中兴安全输入法",
    "com.zte.fastpair": "中兴快速配对服务",
    "cn.nubia.game.networkacceleration": "努比亚游戏网络加速",
    "com.zte.thermald": "中兴温控管理服务",
    "com.tencent.android.location": "腾讯定位服务",
    "zte.com.market": "中兴应用商店",
    "com.zte.quickrt": "中兴QuickRT服务", # RT具体含义需结合上下文
    "com.zte.videoplayer": "中兴视频播放器",
    "cn.nubia.virtualgamehandle": "努比亚虚拟游戏手柄",
    "com.zte.cn.zteshare": "中兴互传/中兴分享",
    "com.qti.snapdragon.qdcm_ff": "高通骁龙显示色彩管理 (QDCM_FF)",
    "com.dts.dtsxultra": "DTS:X Ultra 音效",
    "com.zte.distservice.relayservice": "中兴分布式服务中继服务",
    "com.zte.beautify": "中兴美化/美颜服务",
    "com.zte.neopush": "中兴Neo推送服务",
    "com.zte.timestories": "中兴时光故事 (相册功能)",
    "androidzte": "中兴定制Android系统组件",
    "com.zte.fingerflashpay": "中兴指纹闪付",
    "com.zte.flagreset": "中兴标志重置服务 (系统工具)",
    "com.zte.zgesture": "中兴Z手势",
    "com.zte.aliveupdate": "中兴在线更新/保活更新",
    "com.zte.zsound": "中兴Z音效/音效调节",
    "vendor.qti.data.txpwradmin": "高通数据发射功率管理",
    "vendor.qti.hardware.cacert.server": "高通硬件CA证书服务",
    "zte.com.cn.alarmclock": "中兴闹钟",
    "com.ibimuyu.lockscreen": "比目鱼锁屏",
    "com.zte.wallet": "中兴钱包",
    "com.zte.zdmdaemon": "中兴设备管理守护进程",
    "com.zte.thermalbridge": "中兴温控桥接服务",
    "com.zte.cn.doubleapp": "中兴应用分身",
    "vendor.qti.imsdatachannel": "高通IMS数据通道",
    "com.zte.multscr": "中兴多屏互动",
    "com.zte.intellitext": "中兴智慧识屏/智能文本选择",
    "com.zte.wallet.core": "中兴钱包核心服务",
    "cn.zte.aftersale": "中兴售后服务",
    "com.qti.confuridialer": "高通会议URI拨号器",
    "cn.nubia.gamenotes": "努比亚游戏笔记/截图涂鸦",
    "cn.nubia.nbgame": "努比亚游戏中心/游戏模式",
    "com.zte.mifavor.splitscreengroup": "中兴MiFavor分屏组合",
    "com.zte.floatassist": "中兴悬浮助手",
    "com.zte.distservice.servicemanager": "中兴分布式服务管理器",
    "com.zte.device.state": "中兴设备状态服务",
    "com.zte.mifavor.suggest": "中兴MiFavor智能建议",
    "cn.nubia.paycomponent": "努比亚支付组件",
    "com.tencent.soter.soterserver": "腾讯Soter指纹支付服务",
    "com.fingerprint.sensorservice": "指纹传感器服务", # 可能为通用或特定厂商
    "cn.nubia.healthy": "努比亚健康",
    "com.zte.nps": "中兴网络定位服务 (NPS) 或 用户体验计划",
    "com.quicinc.voice.activation": "高通语音唤醒服务",
    "com.zte.analytics": "中兴数据分析服务",
    "cn.nubia.gamelauncher": "努比亚游戏启动器",
    "cn.nubia.gamepi": "努比亚游戏性能洞察 (GamePI)",
    "com.zte.zbackup.platservice": "中兴Z备份平台服务",
    "com.zte.setupwizard": "中兴设置向导",
    "com.qti.ltebc": "高通LTE广播服务",
    "com.zte.mifavor.miboard": "中兴MiFavor信息板/剪贴板增强",
    "com.ztercs.service": "中兴RCS服务 (富媒体通讯)",
    "com.zte.wallet.support": "中兴钱包支持服务",
    "cn.nubia.gamelab": "努比亚游戏实验室",
    "com.zte.heartyservice.strategy": "中兴灵犀微服务策略引擎", # HeartyService常译为灵犀微服务
    "cn.nubia.photoeditor": "努比亚照片编辑器",
    "com.zte.mifavor.launcher": "中兴MiFavor启动器",
    "com.wapi.wapicertmanage": "WAPI证书管理",
    "cn.nubia.gamehelperline": "努比亚游戏助手辅助线",
    "cn.nubia.touping": "努比亚投屏",
    "com.zte.dbneopush": "中兴数据库Neo推送服务",
    "com.ume.browser": "UME浏览器",
    "com.zte.beautifyadapter": "中兴美化/主题适配器",
    "cn.nubia.diyaod": "努比亚DIY息屏显示",
    "com.zte.dfs": "中兴DFS服务 (动态频率调整或分布式文件系统)",
    "cn.zte.chargeseparation": "中兴充电分离/旁路充电",
    "com.qti.phone": "高通电话服务",
    "com.zte.halo.app": "中兴Halo应用 (灵犀助手相关)",
    "cn.nubia.gameassist": "努比亚游戏助手",
    "com.zte.handservice": "中兴单手操作/手持服务",
    "vendor.qti.iwlan": "高通IWLAN服务 (WiFi通话)",
    "com.zte.burntest.camera": "中兴相机老化测试",
    "zte.com.cn.filer": "中兴文件管理器",
    "cn.zte.gamefloat": "中兴游戏浮窗",
    "com.zte.heartyservice": "中兴灵犀微服务",
    "com.zte.voiceassist.wakeup": "中兴语音助手唤醒服务",
    "com.qti.qualcomm.datastatusnotification": "高通数据状态通知服务",
    "com.ztefingerprint.service": "中兴指纹服务 (另一个包名)",
    "cn.nubia.gpu.drivers": "努比亚GPU驱动程序",
    "cn.nubia.gamehighlights": "努比亚游戏精彩时刻",
    "com.zte.recommend": "中兴智能推荐服务",
    "com.zte.emode": "中兴工程模式",
    "com.zte.mfvkeyguard": "中兴MyFlyOS锁屏",
    "cn.zte.music": "中兴音乐播放器",
    
    "com.android.sdksandbox": "SDK 沙盒",
    "android.ext.services": "Android 扩展服务",
    "com.android.cellbroadcastreceiver": "小区广播接收器",
    "com.android.messaging": "信息", # 或 "短信"
    "com.qualcomm.qtil.btdsda": "高通蓝牙双卡双待代理", # (BT DSDS Agent)
    "com.android.systemui.accessibility.accessibilitymenu": "系统界面无障碍菜单",
    "com.android.vending": "Google Play 商店",
    "com.qualcomm.location": "高通定位服务",
    "com.android.printspooler": "打印后台处理程序",
    "com.qualcomm.qti.telephonyservice": "高通电话服务",
    "com.android.sharedstoragebackup": "共享存储备份",
    "com.android.bluetooth": "蓝牙",
    "com.android.gallery3d": "图库", # (旧版图库，但包名可能沿用)
    "com.android.providers.media": "媒体提供程序", # 或 "媒体存储"
    "com.android.carrierdefaultapp": "运营商默认应用",
    "com.android.captiveportallogin": "强制网络门户登录",
    "com.android.hotspot2.osulogin": "Hotspot 2.0 OSU 登录",
    "com.android.providers.userdictionary": "用户词典提供程序",
    "com.android.systemui": "系统界面",
    "com.android.providers.telephony": "电话服务提供程序",
    "com.android.htmlviewer": "HTML 查看器",
    "com.android.microdroid.empty_payload": "Microdroid 空负载", # (虚拟化相关，非用户应用)
    "com.android.providers.contacts": "联系人提供程序", # 或 "联系人存储"
    "com.android.devicelockcontroller": "设备锁控制器",
    "com.android.companiondevicemanager": "配套设备管理器",
    "com.android.cts.priv.ctsshim": "CTS 私有兼容性测试程序垫片", # (测试工具)
    "com.qualcomm.qti.devicestatisticsservice": "高通设备统计服务",
    "com.android.providers.downloads": "下载管理器提供程序",
    "com.android.mms.service": "彩信服务",
    "com.qualcomm.qti.callfeaturessetting": "高通通话功能设置",
    "com.android.providers.calendar": "日历提供程序", # 或 "日历存储"
    "com.android.rkpdapp": "远程密钥配置应用", # (Remote Key Provisioning)
    "com.android.federatedcompute.services": "联合计算服务",
    "com.qualcomm.qti.ims": "高通 IMS 服务",
    "com.android.camera": "相机",
    "com.android.nearby.halfsheet": "附近分享半屏界面", # (UI组件)
    "com.google.android.gms": "Google Play 服务",
    "com.android.radarpermission": "雷达权限管理", # (可能与Soli雷达相关)
    "com.android.wallpaperbackup": "壁纸备份",
    "android": "Android 系统", # (核心系统)
    "com.android.stk": "SIM 卡工具包",
    "com.qualcomm.qti.xrvd.service": "高通 XR 虚拟显示服务", # (推测, XR Virtual Display)
    "com.android.sdlog": "SD 卡日志", # (系统日志工具)
    "com.android.adservices.api": "广告服务 API",
    "com.android.settings": "设置",
    "com.android.backupconfirm": "备份确认",
    "com.google.android.webview": "Android 系统 WebView",
    "com.android.networkstack.tethering.overlay": "网络堆栈网络共享叠加层",
    "com.google.android.configupdater": "Google 配置更新程序",
    "com.qualcomm.atfwd2": "高通 AT 命令转发服务 2",
    "com.android.wifi.resources.overlay": "WLAN 资源叠加层",
    "com.android.providers.downloads.ui": "下载管理器界面",
    "com.qualcomm.uimremoteclient": "高通 UIM 远程客户端",
    "com.android.permissioncontroller": "权限控制器",
    "com.android.wifi.dialog": "WLAN 对话框",
    "com.android.pacprocessor": "PAC 脚本处理器", # (代理自动配置)
    "com.android.traceur": "系统跟踪 (Traceur)", # (开发者工具)
    "com.android.inputdevices": "输入设备",
    "com.android.nfc": "NFC 服务",
    "com.android.apps.tag": "NFC 标签应用",
    "com.android.ext.adservices.api": "扩展广告服务 API",
    "com.android.proxyhandler": "代理处理程序",
    "com.android.providers.blockednumber": "已屏蔽号码提供程序",
    "com.google.android.projection.gearhead": "Android Auto", # (手机端应用)
    "com.android.certinstaller": "证书安装器",
    "com.android.ons": "ONS 守护程序", # (Operator Name Service)
    "com.android.dynsystem": "动态系统更新", # (DSU)
    "com.android.networkstack": "网络堆栈",
    "com.android.carrierconfig": "运营商配置",
    "com.android.cellbroadcastservice": "小区广播服务",
    "com.android.mtp": "MTP 主机", # (Media Transfer Protocol)
    "com.android.soundpicker": "声音选择器",
    "com.qualcomm.atfwd": "高通 AT 命令转发服务",
    "com.android.health.connect.backuprestore": "健康连接备份与恢复",
    "com.qualcomm.wfd.service": "高通 Wi-Fi Display 服务",
    "com.qualcomm.qti.workloadclassifier": "高通工作负载分类器",
    "com.qualcomm.qtil.aptxui": "高通 aptX UI",
    "com.qualcomm.qti.simcontacts": "高通 SIM 卡联系人",
    "com.android.egg": "Android 彩蛋",
    "com.qualcomm.qti.biometrics.fingerprint.service": "高通指纹服务",
    "com.qualcomm.qti.dynamicddsservice": "高通动态 DDS 服务", # (Default Data Subscription)
    "com.android.settings.intelligence": "设置智能服务",
    "com.android.healthconnect.controller": "健康连接控制器",
    "com.google.android.gsf": "Google 服务框架",
    "com.android.intentresolver": "Intent 解析器", # 或 "打开方式" 界面
    "com.android.wallpapercropper": "壁纸裁剪器",
    "com.android.emergency": "紧急信息服务",
    "com.android.ztescreenshot": "中兴截图", # (OEM特定，此处假设为中兴)
    "com.android.calllogbackup": "通话记录备份",
    "com.android.wallpaper.livepicker": "动态壁纸选择器",
    "com.qualcomm.qti.ridemodeaudio": "高通骑行模式音频",
    "com.android.storagemanager": "存储管理器",
    "com.android.managedprovisioning": "设备管理配置", # (工作资料等)
    "com.android.vendorlogpermission": "供应商日志权限",
    "com.google.android.onetimeinitializer": "Google 一次性初始化程序",
    "com.android.dreams.phototable": "相片屏保",
    "com.qualcomm.qti.lpa": "高通 LPA 服务", # (Local Profile Assistant for eSIM)
    "com.google.android.gms.location.history": "Google 位置记录", # (GMS的一部分)
    "com.qualcomm.qti.cne": "高通连接引擎", # (Connectivity Engine)
    "com.android.providers.settings": "设置提供程序", # 或 "设置存储"
    "com.android.cts.ctsshim": "CTS 兼容性测试程序垫片", # (测试工具)
    "com.android.aftersaleservice": "售后服务", # (通常为厂商定制)
    "com.android.smspush": "WAP 推送服务",
    "com.android.packageinstaller": "软件包安装程序",
    "com.android.modulemetadata": "模块元数据", # (Project Mainline 相关)
    "com.qualcomm.qtil.aptxals": "高通 aptX 自适应低延迟服务", # (推测)
    "com.android.networkstack.overlay": "网络堆栈叠加层",
    "com.android.localtransport": "本地备份传输",
    "com.qualcomm.qti.uceShimService": "高通 UCE 垫片服务", # (User Capability Exchange)
    "com.android.bluetoothmidiservice": "蓝牙 MIDI 服务",
    "com.qualcomm.qtil.aptxacu": "高通 aptX 音频编解码器单元", # (推测)
    "com.android.imsserviceentitlement": "IMS 服务授权",
    "com.android.vpndialogs": "VPN 对话框",
    "com.qualcomm.qcrilmsgtunnel": "高通 QCRIL 消息通道",
    "com.android.ondevicepersonalization.services": "设备端个性化服务",
    "com.android.location.fused": "融合定位服务",
    "com.android.providers.media.module": "媒体提供程序模块", # (Project Mainline 版本)
    "com.android.contacts": "联系人",
    "com.android.se": "安全元素服务", # (Secure Element)
    "com.qualcomm.qti.services.systemhelper": "高通系统助手服务",
    "com.android.externalstorage": "外部存储设备", # (提供程序)
    "com.android.credentialmanager": "凭据管理器",
    "com.android.simappdialog": "SIM 卡应用对话框",
    "com.android.networkstack.tethering": "网络堆栈网络共享",
    "com.android.connectivity.resources.overlay": "连接性资源叠加层",
    "com.google.android.printservice.recommendation": "Google 打印服务推荐",
    "com.android.bips": "内置打印服务",
    "com.android.dialer": "电话", # 或 "拨号器"
    "com.android.keychain": "密钥链",
    "com.android.documentsui": "文件", # 或 "文档界面"
    "com.android.cellbroadcastreceiver.module": "小区广播接收器模块", # (Project Mainline 版本)
    "com.android.mipop": "悬浮球", # (中兴等厂商的悬浮球功能包名可能为此)
    "com.android.phone": "电话服务", # (核心电话功能)
    "com.qualcomm.timeservice": "高通时间服务",
    "com.qualcomm.uimremoteserver": "高通 UIM 远程服务器",
    "com.qualcomm.qti.confdialer": "高通会议拨号器",
    "com.android.server.telecom": "电信服务", # (通话管理框架)
    "com.qualcomm.qti.powersavemode": "高通省电模式",
    "com.android.shell": "Shell", # 或 "Android Shell"
    "com.android.subsys": "子系统管理", # (系统底层服务)
    "com.qualcomm.qti.performancemode": "高通性能模式"
}



def run_adb_command(cmd):
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode != 0:
            # print(f"ADB Command Error: {cmd}\nStderr: {result.stderr.strip()}")
            return ""
        return result.stdout.strip()
    except FileNotFoundError:
        print("错误：未找到 adb 命令。请确保 ADB 已安装并已添加到系统路径中。")
        return ""
    except Exception as e:
        print(f"运行 ADB 命令时发生错误: {e}")
        return ""

def get_all_packages(app_type_filter='user_no_core_system'):
    """
    获取应用包名列表。
    app_type_filter:
        'all': 所有已安装应用
        'third_party': 仅第三方应用 (用户自行安装的应用)
        'user_no_core_system': 用户应用 (不含常见核心系统组件，基于前缀过滤)
    """
    cmd = "adb shell pm list packages"

    if app_type_filter == 'third_party':
        cmd += " -3"

    output = run_adb_command(cmd)
    if not output:
        return []

    packages = [line.replace("package:", "").strip() for line in output.splitlines() if line.strip()]

    if app_type_filter == 'user_no_core_system':
        # 如果是 'user_no_core_system'，应用前缀过滤
        # 确保这是在完整列表或 -3 过滤后的列表上操作
        filtered_packages = []
        system_prefixes = (
            "com.android.", "com.google.android.", "android.",
            "com.qualcomm.", "com.mediatek.", "com.samsung.",
            "com.lge.", "com.motorola.", "com.sony.", "com.oneplus.", "com.oppo.", "com.vivo.", "com.xiaomi.",
            "com.huawei.", "com.honor." # 添加更多常见厂商前缀
        )
        core_system_exact = (
            "android", "system", "org.codeaurora.snapcam" # 举例
        )
        for pkg in packages:
            is_core_system_prefix = any(pkg.startswith(prefix) for prefix in system_prefixes)
            is_exact_core = pkg in core_system_exact
            # 额外排除一些已知是系统核心组件的包（如果它们没有被前缀覆盖）
            # 例如，一些没有明显厂商前缀的系统组件
            is_known_core_component = pkg in [
                "com.android.providers.telephony", # 示例
                # 可以根据需要添加更多
            ]

            if not is_core_system_prefix and not is_exact_core and not is_known_core_component:
                filtered_packages.append(pkg)
        return filtered_packages

    return packages

def get_permissions_for_package(package_name):
    cmd = f'adb shell dumpsys package {package_name}'
    output = run_adb_command(cmd)
    permissions_info = []
    # Regex to capture permission name and the rest of the line containing granted status and flags
    permission_line_regex = re.compile(r"^\s*(?:install|runtime)?\s*([\w\.\-]+):\s*(.*granted=(?:true|false).*?)", re.IGNORECASE)
    # Regex for permissions listed directly under "grantedPermissions:" or similar, without a leading colon
    direct_permission_regex = re.compile(r"^\s*([\w\.\-]+)\s+(granted=(?:true|false).*)", re.IGNORECASE)


    in_permissions_section = False
    # More robust section starters
    permission_section_starters = [
        "requested permissions:", "install permissions:", "runtime permissions:",
        "grantedpermissions:", "install permissions changed:"
    ]
    # Indicators that we've likely left a permission block
    other_section_indicators = [
        "package:", "versioncode", "queries", "activities:", "services:", "receivers:",
        "shared libraries:", "uses-static-libs:", "feature", "dexopt:", "package flags:",
        "data directory:", "code path:", "native library path:", "user id:", "gids:",
        "signatures:", "app links:"
    ]

    for line in output.splitlines():
        line_stripped = line.strip()
        line_lower = line_stripped.lower()

        if any(starter in line_lower for starter in permission_section_starters):
            in_permissions_section = True
            # Handle cases like "grantedPermissions: android.permission.INTERNET granted=true flags=[...]"
            if line_lower.startswith("grantedpermissions:") and len(line_stripped.split()) > 1:
                potential_perm_line = line_stripped.split(":", 1)[1].strip() if ":" in line_stripped else line_stripped
                direct_match = direct_permission_regex.match(potential_perm_line)
                if direct_match:
                    permission_name = direct_match.group(1)
                    full_status_string = direct_match.group(2)
                    permissions_info.append((permission_name, full_status_string))
            continue # Skip the section header line itself

        if in_permissions_section:
            # Check if we've moved to another section
            is_another_section = False
            for indicator in other_section_indicators:
                if line_lower.startswith(indicator):
                    is_another_section = True
                    break
            
            if is_another_section:
                # Further check: if the line still looks like a permission, don't exit section
                # This handles cases where an "other section indicator" might coincidentally be part of a permission flag
                if not (line_lower.startswith("android.permission.") or ".permission." in line_lower or "granted=" in line_lower):
                    in_permissions_section = False
                    continue # Exit this section

            # Try the main regex
            match = permission_line_regex.match(line_stripped)
            if match:
                permission_name = match.group(1)
                full_status_string = match.group(2)
                permissions_info.append((permission_name, full_status_string))
            # Try the direct regex if the main one fails (for lines without a leading colon after permission name)
            elif ":" not in line_stripped and "granted=" in line_stripped :
                direct_match_alt = direct_permission_regex.match(line_stripped)
                if direct_match_alt:
                    permission_name = direct_match_alt.group(1)
                    full_status_string = direct_match_alt.group(2)
                    permissions_info.append((permission_name, full_status_string))
            # Handle multi-line flags (append to the last permission's status string)
            elif permissions_info and "flags=[" in permissions_info[-1][1] and permissions_info[-1][1].count('[') > permissions_info[-1][1].count(']'):
                if line_stripped and not permission_line_regex.match(line_stripped) and not direct_permission_regex.match(line_stripped): # Ensure it's not a new permission
                    last_perm, last_status = permissions_info[-1]
                    permissions_info[-1] = (last_perm, last_status + " " + line_stripped)
    return permissions_info


def get_permission_description(permission_name):
    return permission_descriptions.get(permission_name, "未找到明确定义或用途未知")


def write_to_txt(file_path, content_list):
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in content_list:
            f.write(item)

def write_to_csv(file_path, data_for_csv):
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Package Name', 'App Name', 'Permission Name', 'Granted Status', 'Description', 'Raw Flags'])
        for row in data_for_csv:
            writer.writerow(row)

def write_to_json(file_path, data_for_json):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data_for_json, f, indent=4, ensure_ascii=False)


def main():
    print("选择操作：")
    print("1. 列出所有已授予/已拒绝的权限 (默认)")
    print("2. 仅列出特定权限的状态")
    choice_permissions = input("请选择（1/2）：") or "1"

    specific_permission_filter = None
    if choice_permissions == "2":
        specific_permission_filter = input("请输入要列出的特定权限（例如 android.permission.CAMERA）：").strip()
        if not specific_permission_filter:
            print("未输入特定权限，将列出所有权限。")
            specific_permission_filter = None # Reset if empty

    print("\n选择应用范围：")
    print("1. 用户应用 (不含常见核心系统组件, 默认)")
    print("2. 所有已安装应用")
    print("3. 仅第三方应用 (用户自行安装的应用)")
    print("4. 选择单个应用") # 新增选项
    choice_apps_range = input("请选择（1/2/3/4）：") or "1"

    packages = []
    app_filter_type_for_display = '用户应用 (不含核心系统)' # For display

    if choice_apps_range == "4":
        single_package_name = input("请输入要分析的应用包名：").strip()
        if not single_package_name:
            print("错误：未输入应用包名。程序将退出。")
            return
        packages = [single_package_name]
        app_filter_type_for_display = f"单个应用 ({single_package_name})"
    else:
        app_filter_type_internal = 'user_no_core_system' # Default
        if choice_apps_range == "2":
            app_filter_type_internal = 'all'
            app_filter_type_for_display = '所有已安装应用'
        elif choice_apps_range == "3":
            app_filter_type_internal = 'third_party'
            app_filter_type_for_display = '仅第三方应用'
        # For "1", defaults are already set
        packages = get_all_packages(app_type_filter=app_filter_type_internal)

    if not packages:
        print(f"未能获取任何应用包名 (筛选模式: {app_filter_type_for_display})。请检查 ADB 连接、设备状态或输入的包名。")
        return

    print("\n选择输出格式：")
    print("1. TXT (默认)")
    print("2. CSV")
    print("3. JSON")
    output_format_choice = input("请选择（1/2/3）：") or "1"

    print("\n是否在控制台输出信息？")
    print("1. 是")
    print("2. 否 (默认)")
    console_output_choice = input("请选择（1/2）：") or "2"
    print("-" * 30)

    txt_output_lines = []
    csv_data = []
    json_data_dict = {}
    processed_packages_count = 0

    for i, pkg in enumerate(packages):
        progress = (i + 1) / len(packages)
        bar_length = 30
        filled_length = int(bar_length * progress)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        # 获取应用中文名，如果不在字典中则显示 "未知应用"
        app_name_display = apps_dict.get(pkg, "未知应用")
        print(f'\r正在处理: {pkg[:25]:<25}({app_name_display[:10]:<10}) [{bar}] {i+1}/{len(packages)}', end='')

        permissions_info = get_permissions_for_package(pkg)

        if not permissions_info:
            continue

        current_pkg_txt_lines = []
        pkg_permissions_for_json = [] # Renamed for clarity
        has_relevant_permissions_for_pkg = False

        for permission_name, full_status_string in permissions_info:
            if specific_permission_filter and specific_permission_filter.lower() not in permission_name.lower():
                continue

            has_relevant_permissions_for_pkg = True
            description = get_permission_description(permission_name)

            granted_value_bool = None
            granted_display_text = "状态未知"

            granted_match = re.search(r"granted=(true|false)", full_status_string, re.IGNORECASE)
            if granted_match:
                granted_str = granted_match.group(1).lower()
                granted_value_bool = granted_str == "true"
                granted_display_text = "权限状态：已授予" if granted_value_bool else "权限状态：未授予"
            else: # Fallback if granted=true/false is not found directly
                if "INSTALL_GRANT_FIXED_PERMISSIONS" in full_status_string.upper(): # Example of a fixed permission
                     granted_display_text = "固定授予 (安装时)"
                elif "USER_SET" in full_status_string.upper():
                     granted_display_text = "用户设置" # Could be granted or denied
                elif "USER_FIXED" in full_status_string.upper():
                     granted_display_text = "用户固定" # Could be granted or denied

            raw_flags_value = "无"
            flags_match = re.search(r"flags=\[(.*?)\]", full_status_string, re.DOTALL)
            if flags_match:
                raw_flags_value = " ".join(flags_match.group(1).strip().split()) if flags_match.group(1) else "空"


            if not current_pkg_txt_lines:
                current_pkg_txt_lines.extend([f"应用包名: {pkg} ({app_name_display})\n", "-" * 30 + "\n", "权限：\n"])

            txt_line = f"    {permission_name}: {granted_display_text}, 权限用途：{description}\n      Flags: {raw_flags_value}\n"
            current_pkg_txt_lines.append(txt_line)

            csv_data.append([pkg, app_name_display, permission_name, granted_display_text, description, raw_flags_value])

            pkg_permissions_for_json.append({
                "permission": permission_name,
                "granted_bool": granted_value_bool, # Can be None if not explicitly true/false
                "granted_status_text": granted_display_text,
                "description": description,
                "raw_flags": raw_flags_value,
                # "full_status_string_debug": full_status_string # Uncomment for debugging dumpsys output
            })

        if has_relevant_permissions_for_pkg:
            processed_packages_count += 1
            current_pkg_txt_lines.append("\n")
            txt_output_lines.extend(current_pkg_txt_lines)
            if pkg_permissions_for_json:
                 json_data_dict[f"{pkg} ({app_name_display})"] = {"permissions_info": pkg_permissions_for_json}

    print("\n" + "="*30)
    print(f"处理完成！共扫描 {len(packages)} 个应用，其中 {processed_packages_count} 个应用有相关权限信息。")

    if console_output_choice == "1":
        print("\n--- 控制台输出 ---")
        if txt_output_lines:
            for line in txt_output_lines:
                print(line, end='')
        else:
            print("没有找到符合条件的权限信息在控制台输出。")
        print("--- 控制台输出结束 ---")


    if not txt_output_lines and not csv_data and not json_data_dict: # Check all potential outputs
        print("没有找到符合条件的权限信息可供输出。")
        return

    output_file_base = "app_permissions_report"
    output_file_path = ""

    if output_format_choice == "1":
        output_file_path = f"{output_file_base}.txt"
        if txt_output_lines: write_to_txt(output_file_path, txt_output_lines)
        else: print("没有数据可写入 TXT 文件。"); return
    elif output_format_choice == "2":
        output_file_path = f"{output_file_base}.csv"
        if csv_data: write_to_csv(output_file_path, csv_data)
        else: print("没有数据可写入 CSV 文件。"); return
    elif output_format_choice == "3":
        output_file_path = f"{output_file_base}.json"
        if json_data_dict: write_to_json(output_file_path, json_data_dict)
        else: print("没有数据可写入 JSON 文件。"); return

    if output_file_path and os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 0:
        print(f"\n权限信息已保存到：{os.path.abspath(output_file_path)}")
    elif output_file_path: # File was supposed to be created but might be empty or not exist
        print(f"尝试写入到 {output_file_path}，但可能没有数据或写入失败。")
    elif not output_file_path:
        print("未选择有效的输出格式。")


if __name__ == "__main__":
    main()
