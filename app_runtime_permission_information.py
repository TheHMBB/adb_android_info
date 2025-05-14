# 使用adb获取安卓应用的App Ops（应用操作）状态
# 本程序最好放在adb工具所在目录下执行
import subprocess
import os
import csv
import json
import re
import sys

# App Ops 用途字典 (可以根据需要补充和完善)
# 注意：这些是 App Op 名称，与传统的权限名称略有不同，但通常相关。
appop_descriptions = {
    # 从 android.permission. 中转换并筛选常见的运行时操作
    "CAMERA": "控制应用是否可以使用摄像头。",
    "ACCESS_FINE_LOCATION": "控制应用是否可以获取精确的地理位置信息。",
    "ACCESS_COARSE_LOCATION": "控制应用是否可以获取大致的地理位置信息。",
    "RECORD_AUDIO": "控制应用是否可以使用麦克风录音。",
    "READ_CONTACTS": "控制应用是否可以读取联系人。",
    "WRITE_CONTACTS": "控制应用是否可以写入联系人。",
    "GET_ACCOUNTS": "控制应用是否可以访问设备上的账户列表。",
    "WRITE_EXTERNAL_STORAGE": "控制应用是否可以写入外部存储（如SD卡）上的文件。",
    "READ_EXTERNAL_STORAGE": "控制应用是否可以读取外部存储（如SD卡）上的文件。",
    # BLUETOOTH 相关的 App Ops 通常是更细粒度的
    "BLUETOOTH_SCAN": "控制应用是否可以扫描附近的蓝牙设备。", # 对应 android.permission.BLUETOOTH_SCAN
    "BLUETOOTH_ADVERTISE": "控制应用是否可以进行蓝牙广播。", # 对应 android.permission.BLUETOOTH_ADVERTISE
    "BLUETOOTH_CONNECT": "控制应用是否可以连接已配对的蓝牙设备。", # 对应 android.permission.BLUETOOTH_CONNECT
    # INTERNET, NETWORK_STATE, WIFI_STATE 等通常没有用户可控的 App Op
    "SEND_SMS": "控制应用是否可以发送短信。",
    "RECEIVE_SMS": "控制应用是否可以接收短信。",
    "READ_SMS": "控制应用是否可以读取短信。",
    "RECEIVE_MMS": "控制应用是否可以接收彩信。",
    "READ_PHONE_STATE": "控制应用是否可以访问设备电话状态。", # 对应 android.permission.READ_PHONE_STATE
    "CALL_PHONE": "控制应用是否可以直接拨打电话。",
    "ANSWER_PHONE_CALLS": "控制应用是否可以接听电话。", # 对应 android.permission.ANSWER_PHONE_CALLS
    "PROCESS_OUTGOING_CALLS": "控制应用是否可以处理拨出电话。", # 对应 android.permission.PROCESS_OUTGOING_CALLS
    "USE_SIP": "控制应用是否可以使用SIP协议进行网络电话。",
    "SYSTEM_ALERT_WINDOW": "控制应用是否可以在其他应用上方显示悬浮窗。",
    # VIBRATE 通常没有用户可控的 App Op
    # FOREGROUND_SERVICE 是权限，不是 App Op
    "REQUEST_INSTALL_PACKAGES": "控制应用是否可以请求安装其他应用。",
    # WAKE_LOCK 是权限，但有对应的 App Op
    "WAKE_LOCK": "控制应用是否可以阻止设备进入休眠状态。",
    "WRITE_SETTINGS": "控制应用是否可以修改系统设置。",
    # RECEIVE_BOOT_COMPLETED 是广播接收权限，不是 App Op
    # MANAGE_EXTERNAL_STORAGE 是特殊访问权限，通常没有对应的 App Op
    "READ_CALL_LOG": "控制应用是否可以读取通话记录。",
    "WRITE_CALL_LOG": "控制应用是否可以写入通话记录。",
    "USE_FINGERPRINT": "控制应用是否可以使用指纹识别（旧 API）。", # 对应 android.permission.USE_FINGERPRINT
    "USE_BIOMETRIC": "控制应用是否可以使用生物识别硬件。", # 对应 android.permission.USE_BIOMETRIC
    "GET_USAGE_STATS": "控制应用是否可以查看其他应用的使用情况。", # 对应 android.permission.PACKAGE_USAGE_STATS
    "ACTIVITY_RECOGNITION": "控制应用是否可以获取用户的身体活动信息。", # 对应 android.permission.ACTIVITY_RECOGNITION
    "BODY_SENSORS": "控制应用是否可以使用身体传感器（如心率监测）。",
    "ACCESS_FINE_LOCATION_BACKGROUND": "控制应用是否可以在后台获取精确位置。", # 对应 android.permission.ACCESS_BACKGROUND_LOCATION 的一部分
    "ACCESS_COARSE_LOCATION_BACKGROUND": "控制应用是否可以在后台获取大致位置。", # 对应 android.permission.ACCESS_BACKGROUND_LOCATION 的一部分
    "SCHEDULE_EXACT_ALARM": "控制应用是否可以安排精确的定时任务。", # 对应 android.permission.SCHEDULE_EXACT_ALARM / USE_EXACT_ALARM
    # NFC 权限通常没有对应的 App Op
    "NEARBY_WIFI_DEVICES": "控制应用是否可以发现附近的Wi-Fi设备。", # Android 12+ App Op
    "UWB_RANGING": "控制应用是否可以与附近的超宽带（UWB）设备进行测距。", # Android 12+ App Op
    "READ_MEDIA_IMAGES": "控制应用是否可以读取设备上的图片文件。", # Android 13+ App Op
    "READ_MEDIA_VIDEO": "控制应用是否可以读取设备上的视频文件。", # Android 13+ App Op
    "READ_MEDIA_AUDIO": "控制应用是否可以读取设备上的音频文件。", # Android 13+ App Op
    "ACCESS_MEDIA_LOCATION": "控制应用是否可以访问共享存储中媒体文件的地理位置信息。", # Android 10+ App Op
    "READ_CALENDAR": "控制应用是否可以读取日历信息。",
    "WRITE_CALENDAR": "控制应用是否可以写入日历信息。",
    # Sync settings 权限通常没有对应的 App Op
    # Account/Credential 管理权限通常没有对应的 App Op
    "READ_PHONE_NUMBERS": "控制应用是否可以读取设备的电话号码。", # 对应 android.permission.READ_PHONE_NUMBERS
    # Privileged/System info 权限通常没有对应的 App Op
    # System/App Interaction 权限很多没有对应的 App Op
    "SET_ALARM": "控制应用是否可以设置闹钟。", # 对应 android.permission.SET_ALARM
    # DISABLE_KEYGUARD 通常没有对应的 App Op
    "REQUEST_IGNORE_BATTERY_OPTIMIZATIONS": "控制应用是否可以请求忽略电池优化。", # 对应 android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS
    "START_ACTIVITIES_FROM_BACKGROUND": "控制应用是否可以从后台启动 Activity。", # 对应 android.permission.START_ACTIVITIES_FROM_BACKGROUND (Android 10+ 受限)
    "ACCESS_NOTIFICATION_POLICY": "控制应用是否可以修改通知策略（如勿扰模式）。", # 对应 android.permission.ACCESS_NOTIFICATION_POLICY
    "BIND_NOTIFICATION_LISTENER_SERVICE": "控制应用是否可以绑定到通知监听器服务。", # 对应 android.permission.BIND_NOTIFICATION_LISTENER_SERVICE (需要用户手动开启)
    "BODY_SENSORS_BACKGROUND": "控制应用是否可以在后台访问身体传感器数据。", # Android 12+ App Op
    "HIGH_SAMPLING_RATE_SENSORS": "控制应用是否可以以高频率访问传感器数据。", # Android 12+ App Op
    "CAMERA_OPEN_CLOSE_LISTENER": "控制应用是否可以监听摄像头的打开和关闭事件。", # Android 13+ App Op
    "RECORD_BACKGROUND_AUDIO": "控制应用是否可以在后台录制音频。", # Android 10+ App Op
    "MANAGE_ONGOING_CALLS": "控制应用是否可以管理正在进行的通话。", # Android 10+ App Op
    "READ_BASIC_PHONE_STATE_AND_NUMBERS": "控制应用是否可以读取基本电话状态和号码。", # Android 12+ App Op
    "USE_FULL_SCREEN_INTENT": "控制应用是否可以使用全屏 Intent。", # Android 10+ App Op
    "READ_VOICEMAIL": "控制应用是否可以读取语音邮件。", # 对应 android.permission.READ_VOICEMAIL
    "WRITE_VOICEMAIL": "控制应用是否可以修改或添加语音邮件。", # 对应 android.permission.WRITE_VOICEMAIL
    "ADD_VOICEMAIL": "控制应用是否可以添加语音邮件。", # 对应 com.android.voicemail.permission.ADD_VOICEMAIL (通常由系统或运营商应用持有)
    # QUERY_ALL_PACKAGES 是特殊访问权限，通常没有对应的 App Op
    "POST_NOTIFICATIONS": "控制应用是否可以发送通知。", # Android 13+ App Op
    "READ_CLIPBOARD": "控制应用是否可以读取剪贴板内容。", # Android 10+ App Op
    "WRITE_CLIPBOARD": "控制应用是否可以写入剪贴板内容。",
    "ACCESS_MOCK_LOCATION": "控制应用是否可以创建模拟位置信息。", # 对应 android.permission.ACCESS_MOCK_LOCATION
    "TRANSMIT_IR": "控制应用是否可以使用设备的红外发射器。", # 对应 android.permission.TRANSMIT_IR
    "MANAGE_OWN_CALLS": "控制应用是否可以管理自身的通话（如VoIP）。", # 对应 android.permission.MANAGE_OWN_CALLS
    "ACCEPT_HANDOVER": "控制应用是否可以接受连接切换。", # 对应 android.permission.ACCEPT_HANDOVER
    "ACCESS_NOTIFICATIONS": "控制应用是否可以访问通知信息。", # 对应 android.permission.ACCESS_NOTIFICATIONS
    "ACT_AS_PACKAGE_FOR_ACCESSIBILITY": "控制应用是否可以代表另一个包与无障碍服务交互。", # 系统级 App Op
    "BACKGROUND_CAMERA": "控制应用是否可以在后台访问摄像头。", # Android 11+ App Op
    "BIND_ACCESSIBILITY_SERVICE": "控制应用是否可以绑定到无障碍服务。", # 需要用户手动开启
    "MANAGE_APP_OPS_MODES": "控制应用是否可以管理App Ops模式。", # 系统级 App Op
    "MANAGE_SENSOR_PRIVACY": "控制应用是否可以管理传感器隐私开关。", # 系统级 App Op
    "OBSERVE_SENSOR_PRIVACY": "控制应用是否可以观察传感器隐私开关的状态。", # 系统级 App Op
    "READ_CELL_BROADCASTS": "控制应用是否可以读取接收到的小区广播消息。", # 对应 android.permission.READ_CELL_BROADCASTS
    "RECEIVE_EMERGENCY_BROADCAST": "控制应用是否可以接收紧急广播。", # 对应 android.permission.RECEIVE_EMERGENCY_BROADCAST
    "PROVIDE_TRUST_AGENT": "控制应用是否可以作为信任代理（如Smart Lock）。", # 对应 android.permission.PROVIDE_TRUST_AGENT
    "MANAGE_AUTO_FILL": "控制应用是否可以管理自动填充服务。", # 对应 android.permission.MANAGE_AUTO_FILL
    "SET_SYSTEM_AUDIO_CAPTION": "控制应用是否可以设置系统级音频字幕。", # 系统级 App Op
    "TOGGLE_AUTOMOTIVE_PROJECTION": "控制应用是否可以切换车载投屏模式（如Android Auto）。", # 系统级 App Op
    "RETRIEVE_WINDOW_CONTENT": "控制应用是否可以检索窗口内容（主要用于无障碍服务或测试）。", # 对应 android.permission.RETRIEVE_WINDOW_CONTENT
    "SET_HARMFUL_APP_WARNINGS": "控制应用是否可以设置有害应用警告。", # 系统级 App Op
    "RECEIVE_STK_COMMANDS": "控制应用是否可以接收来自SIM卡工具包（STK）的命令。", # 对应 android.permission.RECEIVE_STK_COMMANDS
    "MANAGE_DEVICE_POLICY_TIME": "控制应用是否可以管理设备策略中的时间限制。", # 系统级 App Op
    "TRIGGER_LOST_MODE": "控制应用是否可以触发设备丢失模式。", # 系统级 App Op
    "SET_ANIMATION_SCALE": "控制应用是否可以设置动画缩放比例。", # 对应 android.permission.SET_ANIMATION_SCALE (开发者选项)
    "READ_RUNTIME_PROFILES": "控制应用是否可以读取运行时JIT配置文件。", # 系统/开发 App Op
    "SET_ACTIVITY_WATCHER": "控制应用是否可以监视Activity启动（已废弃）。", # 系统级 App Op
    "MODIFY_DEFAULT_AUDIO_EFFECTS": "控制应用是否可以修改默认音频效果。", # 系统级 App Op
    "RESET_FINGERPRINT_LOCKOUT": "控制应用是否可以重置指纹识别锁定状态。", # 系统级 App Op
    "MANAGE_APP_PREDICTIONS": "控制应用是否可以管理应用预测。", # 系统级 App Op
    "POWER_SAVER": "控制应用是否可以控制省电模式设置。", # 系统级 App Op
    "SET_PROCESS_LIMIT": "控制应用是否可以设置后台进程限制。", # 系统/签名 App Op
    "MANAGE_DEVICE_POLICY_LOCK_TASK": "控制应用是否可以管理锁定任务模式。", # 设备所有者权限
    "MANAGE_HEALTH_PERMISSIONS": "控制应用是否可以管理健康相关权限（Health Connect）。", # 系统级 App Op
    "MANAGE_SEARCH_UI": "控制应用是否可以管理搜索UI组件。", # 系统级 App Op
    "SCORE_NETWORKS": "控制应用是否可以为网络评分（Wi-Fi质量）。", # 系统级 App Op
    "SUSPEND_APPS": "控制应用是否可以暂停其他应用。", # 系统/配置文件所有者 App Op
    "RADIO_SCAN_WITHOUT_LOCATION": "控制应用是否可以在没有位置权限的情况下扫描无线电网络。", # 对应 android.permission.RADIO_SCAN_WITHOUT_LOCATION
    "READ_PEOPLE_DATA": "控制应用是否可以读取人物/联系人数据（Conversations API）。", # 对应 android.permission.READ_PEOPLE_DATA
    "MANAGE_BLUETOOTH_WHEN_WIRELESS_CONSENT_REQUIRED": "控制应用是否在需要无线同意时管理蓝牙。", # 系统级 App Op
    "ACCEPT_HANDOVER": "控制应用是否可以接受来自其他应用的连接切换。", # 对应 android.permission.ACCEPT_HANDOVER
    "ACCESS_ADSERVICES_ATTRIBUTION": "控制应用是否可以访问广告服务的归因信息。", # Android 13+ App Op
    "ACCESS_ADSERVICES_CUSTOM_AUDIENCE": "控制应用是否可以访问广告服务的自定义受众数据。", # Android 13+ App Op
    "ACCESS_ADSERVICES_MANAGER": "控制应用是否可以访问广告服务管理器。", # Android 13+ App Op
    "ACCESS_ADSERVICES_TOPICS": "控制应用是否可以访问广告服务的主题推断数据。", # Android 13+ App Op
    "ACCESS_BROADCAST_RESPONSE_STATS": "控制应用是否可以访问广播响应统计信息。", # 系统级 App Op
    "ACCESS_LOWPAN_STATE": "控制应用是否可以访问LoWPAN状态。", # 系统级 App Op
    "ACCESS_MTP": "控制应用是否作为MTP发起者访问设备。", # 对应 android.permission.ACCESS_MTP
    "ACCESS_RCS_USER_CAPABILITY_EXCHANGE": "控制应用是否访问RCS用户能力交换。", # 对应 android.permission.ACCESS_RCS_USER_CAPABILITY_EXCHANGE
    "ACCESS_SHARED_LIBRARIES": "控制应用是否访问共享库信息。", # 系统级 App Op
    "ACCESS_SURFACE_FLINGER": "控制应用是否直接访问SurfaceFlinger。", # 系统级 App Op
    "ACCESS_TV_DESCRAMBLER": "控制应用是否访问电视解扰器。", # 对应 android.permission.ACCESS_TV_DESCRAMBLER
    "ACCESS_TV_TUNER": "控制应用是否访问电视调谐器硬件。", # 对应 android.permission.ACCESS_TV_TUNER
    "ACCESS_VIBRATOR_STATE": "控制应用是否访问振动器状态。", # 系统级 App Op
    "ACCESS_VOICE_INTERACTION_SERVICE": "控制应用是否访问语音交互服务。", # 对应 android.permission.ACCESS_VOICE_INTERACTION_SERVICE
    "ACTIVITY_EMBEDDING": "控制应用是否在其任务中嵌入其他应用的活动。", # Android 12L+ App Op
    "ALLOCATE_AGGRESSIVE": "控制应用是否请求积极资源分配。", # 系统级 App Op
    "BATTERY_PREDICTION": "控制应用是否访问电池使用预测数据。", # 系统级 App Op
    "BIND_DEVICE_ADMIN": "控制应用是否绑定到设备管理员服务。", # 系统级 App Op
    "BIND_DIRECTORY_SEARCH": "控制应用是否绑定到目录搜索服务。", # 对应 android.permission.BIND_DIRECTORY_SEARCH
    "BIND_QUICK_ACCESS_WALLET_SERVICE": "控制应用是否绑定到快速访问钱包服务。", # 对应 android.permission.BIND_QUICK_ACCESS_WALLET_SERVICE
    "BIND_REMOTEVIEWS": "控制应用是否绑定到RemoteViews服务。", # 对应 android.permission.BIND_REMOTEVIEWS
    "BIND_SATELLITE_GATEWAY_SERVICE": "控制应用是否绑定到卫星网关服务。", # 对应 android.permission.BIND_SATELLITE_GATEWAY_SERVICE
    "BIND_TELECOM_CONNECTION_SERVICE": "控制应用是否绑定到Telecom的ConnectionService。", # 对应 android.permission.BIND_TELECOM_CONNECTION_SERVICE
    "BIND_TELEPHONY_DATA_SERVICE": "控制应用是否绑定到电话数据服务。", # 对应 android.permission.BIND_TELEPHONY_DATA_SERVICE
    "BIND_VISUAL_QUERY_DETECTION_SERVICE": "控制应用是否绑定到视觉查询检测服务。", # 对应 android.permission.BIND_VISUAL_QUERY_DETECTION_SERVICE
    "BLUETOOTH_MAP": "控制应用是否使用蓝牙MAP（消息访问配置文件）。", # 对应 android.permission.BLUETOOTH_MAP
    "BROADCAST_OPTION_INTERACTIVE": "控制应用是否广播交互式选项。", # 系统级 App Op
    "CHANGE_DEVICE_IDLE_TEMP_WHITELIST": "控制应用是否临时将应用添加到设备空闲模式白名单。", # 系统级 App Op
    "CHANGE_OVERLAY_PACKAGES": "控制应用是否更改哪些包可以显示悬浮窗。", # 系统级 App Op
    "CHECK_REMOTE_LOCKSCREEN": "控制应用是否检查远程锁屏状态。", # 系统级 App Op
    "CLEAR_FREEZE_PERIOD": "控制应用是否清除应用的冻结期。", # 系统级 App Op
    "CONTROL_DEVICE_LIGHTS": "控制应用是否控制设备指示灯。", # 对应 android.permission.CONTROL_DEVICE_LIGHTS
    "CONTROL_REMOTE_APP_TRANSITION_ANIMATIONS": "控制应用是否控制远程应用过渡动画。", # 系统级 App Op
    "CREATE_VIRTUAL_DEVICE": "控制应用是否创建虚拟设备。", # Android 13+ 系统级 App Op
    "DEBUG_VIRTUAL_MACHINE": "控制应用是否调试虚拟机。", # 系统级 App Op
    "FORCE_BACK": "控制应用是否强制执行返回操作。", # 系统级 App Op
    "FRAME_STATS": "控制应用是否访问帧统计信息。", # 系统级 App Op
    "GET_ANY_PROVIDER_TYPE": "控制应用是否获取任何内容提供程序的类型。", # 系统级 App Op
    "GET_APP_METADATA": "控制应用是否获取其他应用的元数据。", # 系统级 App Op
    "GRANT_RUNTIME_PERMISSIONS": "控制应用是否授予或撤销其他应用的运行时权限。", # 系统级 App Op
    "INSTANT_APP_FOREGROUND_SERVICE": "控制即时应用是否运行前台服务。", # 对应 android.permission.INSTANT_APP_FOREGROUND_SERVICE
    "KEEP_UNINSTALLED_PACKAGES": "控制应用是否在卸载后保留应用数据。", # 系统级 App Op
    "KILL_ALL_BACKGROUND_PROCESSES": "控制应用是否终止所有后台进程。", # 系统级 App Op
    "LAUNCH_CREDENTIAL_SELECTOR": "控制应用是否启动凭据选择器。", # 对应 android.permission.LAUNCH_CREDENTIAL_SELECTOR
    "LISTEN_ALWAYS_REPORTED_SIGNAL_STRENGTH": "控制应用是否监听始终报告的信号强度。", # 系统级 App Op
    "LOCK_DEVICE": "控制设备管理员应用是否锁定设备。", # 对应 android.permission.LOCK_DEVICE
    "LOG_FOREGROUND_RESOURCE_USE": "控制应用是否记录前台资源使用情况。", # 系统级 App Op
    "MANAGE_APPOPS": "控制应用是否管理App Ops设置（旧）。", # 系统级 App Op
    "MANAGE_AUDIO_POLICY": "控制应用是否管理音频策略。", # 系统级 App Op
    "MANAGE_COMPANION_DEVICES": "控制应用是否管理配对的伴侣设备。", # 对应 android.permission.MANAGE_COMPANION_DEVICES
    "MANAGE_CONTENT_CAPTURE": "控制应用是否管理内容捕获服务。", # 系统级 App Op
    "MANAGE_CONTENT_SUGGESTIONS": "控制应用是否管理内容建议。", # 系统级 App Op
    "MANAGE_CRATES": "控制应用是否管理Crates（存储/容器）。", # 系统级 App Op
    "MANAGE_DEVICE_LOCK_STATE": "控制应用是否管理设备锁定状态。", # 系统级 App Op
    "MANAGE_DEVICE_POLICY_APPS_CONTROL": "控制设备策略控制器是否管理应用控制策略。", # 对应 android.permission.MANAGE_DEVICE_POLICY_APPS_CONTROL
    "MANAGE_DEVICE_POLICY_INSTALL_UNKNOWN_SOURCES": "控制设备策略控制器是否管理安装未知来源设置。", # 对应 android.permission.MANAGE_DEVICE_POLICY_INSTALL_UNKNOWN_SOURCES
    "MANAGE_DEVICE_POLICY_SAFE_BOOT": "控制设备策略控制器是否管理安全启动设置。", # 对应 android.permission.MANAGE_DEVICE_POLICY_SAFE_BOOT
    "MANAGE_HEALTH_DATA": "控制应用是否管理健康数据。", # Android 14+ App Op
    "MANAGE_LOW_POWER_STANDBY": "控制应用是否管理低功耗待机模式。", # 系统级 App Op
    "MANAGE_MEDIA_PROJECTION": "控制应用是否管理媒体投影会话。", # 对应 android.permission.MANAGE_MEDIA_PROJECTION
    "MANAGE_ONE_TIME_PERMISSION_SESSIONS": "控制应用是否管理一次性权限会话。", # 系统级 App Op
    "MANAGE_ROLLBACKS": "控制应用是否管理应用回滚。", # 系统级 App Op
    "MANAGE_SENSORS": "控制应用是否管理传感器。", # 系统级 App Op
    "MANAGE_SMARTSPACE": "控制应用是否管理Smartspace（如概览）。", # 系统级 App Op
    "MANAGE_SUBSCRIPTION_PLANS": "控制应用是否管理用户的订阅计划。", # 对应 android.permission.MANAGE_SUBSCRIPTION_PLANS
    "MANAGE_UI_TRANSLATION": "控制应用是否管理UI翻译服务。", # 系统级 App Op
    "MANAGE_WIFI_INTERFACES": "控制应用是否管理Wi-Fi接口。", # 系统级 App Op
    "MODIFY_AUDIO_SETTINGS_PRIVILEGED": "控制应用是否执行特权音频设置修改。", # 系统级 App Op
    "MODIFY_CELL_BROADCASTS": "控制应用是否修改小区广播设置。", # 系统级 App Op
    "MODIFY_DAY_NIGHT_MODE": "控制应用是否修改系统的日间/夜间模式。", # 系统级 App Op
    "MODIFY_THEME_OVERLAY": "控制应用是否修改主题叠加层。", # 系统级 App Op
    "MONITOR_KEYBOARD_BACKLIGHT": "控制应用是否监控键盘背光状态。", # 系统级 App Op
    "NET_ADMIN": "控制应用是否执行网络管理任务。", # 系统级 App Op
    "NET_TUNNELING": "控制应用是否创建网络隧道。", # 系统级 App Op
    "NETWORK_FACTORY": "控制应用是否作为网络工厂。", # 系统级 App Op
    "NETWORK_MANAGED_PROVISIONING": "控制应用是否进行网络管理的配置。", # 对应 android.permission.NETWORK_MANAGED_PROVISIONING
    "NETWORK_STATS_PROVIDER": "控制应用是否提供网络使用统计数据。", # 系统级 App Op
    "OBSERVE_APP_USAGE": "控制应用是否观察其他应用使用情况。", # 系统级 App Op
    "OBSERVE_ROLE_HOLDERS": "控制应用是否观察系统角色持有者变化。", # 系统级 App Op
    "OPEN_ACCESSIBILITY_DETAILS_SETTINGS": "控制应用是否打开特定无障碍服务的详细设置。", # 对应 android.permission.OPEN_ACCESSIBILITY_DETAILS_SETTINGS
    "OVERRIDE_COMPAT_CHANGE_CONFIG": "控制应用是否覆盖兼容性更改配置。", # 系统级 App Op
    "OVERRIDE_COMPAT_CHANGE_CONFIG_ON_RELEASE_BUILD": "控制应用是否在发布版本覆盖兼容性更改配置。", # 系统级 App Op
    "PACKAGE_VERIFICATION_AGENT": "控制应用是否作为包验证代理。", # 系统级 App Op
    "PROCESS_PHONE_ACCOUNT_REGISTRATION": "控制应用是否处理电话账户注册。", # 系统级 App Op
    "READ_ACTIVE_EMERGENCY_SESSION": "控制应用是否读取活动的紧急会话信息。", # 系统级 App Op
    "READ_GLOBAL_APP_SEARCH_DATA": "控制应用是否读取全局应用搜索数据。", # 系统级 App Op
    "READ_INPUT_STATE": "控制应用是否读取当前输入状态。", # 系统级 App Op
    "READ_RESTRICTED_STATS": "控制应用是否读取受限制统计信息。", # 系统级 App Op
    "READ_SOCIAL_STREAM": "控制应用是否读取社交流数据（已废弃）。", # 对应 android.permission.READ_SOCIAL_STREAM
    "READ_VENDOR_CONFIG": "控制应用是否读取供应商配置。", # 系统级 App Op
    "READ_WALLPAPER_INTERNAL": "控制应用是否读取内部壁纸数据。", # 系统级 App Op
    "REGISTER_MEDIA_RESOURCE_OBSERVER": "控制应用是否注册媒体资源观察者。", # 系统级 App Op
    "REMOTE_DISPLAY_PROVIDER": "控制应用是否作为远程显示提供者。", # 系统级 App Op
    "RENOUNCE_PERMISSIONS": "控制应用是否放弃其先前授予的权限。", # 系统级 App Op
    "REQUEST_COMPANION_PROFILE_AUTOMOTIVE_PROJECTION": "控制应用是否请求车载投屏伴侣设备配置文件。", # 对应 android.permission.REQUEST_COMPANION_PROFILE_AUTOMOTIVE_PROJECTION
    "RESTRICTED_VR_ACCESS": "控制应用是否以受限方式访问VR功能。", # 系统级 App Op
    "ROTATE_SURFACE_FLINGER": "控制应用是否旋转SurfaceFlinger输出。", # 系统级 App Op
    "SATELLITE_COMMUNICATION": "控制应用是否进行卫星通信。", # Android 14+ App Op
    "SEND_CALL_LOG_CHANGE": "控制应用是否发送通话记录更改通知。", # 系统级 App Op
    "SEND_DEVICE_CUSTOMIZATION_READY": "控制应用是否发送设备定制化准备就绪信号。", # 系统级 App Op
    "SET_APP_SPECIFIC_LOCALECONFIG": "控制应用是否设置应用特定的区域配置。", # 系统级 App Op
    "SET_AUTHENTICATION_DATA": "控制应用是否设置身份验证数据。", # 系统级 App Op
    "SET_DEBUG_APP": "控制应用是否设置调试应用。", # 系统级 App Op
    "SET_PREFERRED_APPLICATIONS": "控制应用是否设置首选应用。", # 系统级 App Op
    "SIGNAL_PERSISTENT_PROCESSES": "控制应用是否向常驻进程发送信号。", # 系统级 App Op
    "START_PRINT_SERVICE_CONFIG_ACTIVITY": "控制应用是否启动打印服务配置活动。", # 对应 android.permission.START_PRINT_SERVICE_CONFIG_ACTIVITY
    "SUGGEST_TELEPHONY_TIME_AND_ZONE": "控制应用是否建议电话网络提供的时间和时区。", # 系统级 App Op
    "SYSTEM_APPLICATION_OVERLAY": "控制系统应用是否显示在其他应用上方的悬浮窗。", # 系统级 App Op
    "TEST_INPUT_METHOD": "控制应用是否测试输入法。", # 系统级 App Op
    "TIS_EXTENSION_INTERFACE": "控制应用是否访问文本输入服务扩展接口。", # 系统级 App Op
    "TUNER_RESOURCE_ACCESS": "控制应用是否访问调谐器资源。", # 对应 android.permission.TUNER_RESOURCE_ACCESS
    "TURN_SCREEN_ON": "控制应用是否在锁屏上方点亮屏幕（已废弃）。", # 对应 android.permission.TURN_SCREEN_ON
    "UPDATE_CONFIG": "控制应用是否更新配置。", # 系统级 App Op
    "UPDATE_LOCK": "控制应用是否更新锁。", # 系统级 App Op
    "UPGRADE_RUNTIME_PERMISSIONS": "控制应用是否升级运行时权限。", # 系统级 App Op
    "USE_EXACT_ALARM": "控制应用是否安排精确的闹钟/定时任务。", # Android 12+ App Op (旧名称)
    "WATCH_APPOPS": "控制应用是否监视App Ops更改。", # 系统级 App Op
    "WHITELIST_AUTO_REVOKE_PERMISSIONS": "控制应用是否将自身添加到自动撤销未使用权限白名单。", # 对应 android.permission.WHITELIST_AUTO_REVOKE_PERMISSIONS
    "WHITELIST_RESTRICTED_PERMISSIONS": "控制应用是否将自身添加到受限权限白名单。", # 系统级 App Op
    "WIFI_UPDATE_COEX_UNSAFE_CHANNELS": "控制应用是否更新Wi-Fi共存不安全信道信息。", # 系统级 App Op
    "WRITE_DREAM_STATE": "控制应用是否写入Daydream状态。", # 系统级 App Op
    "WRITE_EMBEDDED_SUBSCRIPTIONS": "控制应用是否写入嵌入式SIM卡订阅信息。", # 系统级 App Op
    "READ_EXERCISE_ROUTE": "控制应用是否读取健康数据中的运动路线。", # Android 14+ App Op
    "READ_HEART_RATE": "控制应用是否读取健康数据中的心率信息。", # Android 14+ App Op
    "ACCESS_ADSERVICES_STATE": "控制应用是否访问广告服务状态。", # Android 13+ App Op
    "ACCESS_AMBIENT_CONTEXT_EVENT": "控制应用是否访问环境上下文事件。", # 对应 android.permission.ACCESS_AMBIENT_CONTEXT_EVENT
    "ACCESS_AMBIENT_LIGHT_STATS": "控制应用是否访问环境光传感器统计信息。", # 系统级 App Op
    "ACCESS_CONTENT_PROVIDERS_EXTERNALLY": "控制应用是否从外部访问内容提供者。", # 系统级 App Op
    "ACCESS_DOWNLOAD_MANAGER_ADVANCED": "控制应用是否对下载管理器进行高级操作。", # 系统级 App Op
    "ACCESS_IMS_CALL_SERVICE": "控制应用是否访问IMS呼叫服务。", # 对应 android.permission.ACCESS_IMS_CALL_SERVICE
    "ACCESS_MESSAGES_ON_ICC": "控制应用是否访问ICC（SIM卡）上的消息。", # 系统级 App Op
    "ACCESS_PRIVILEGED_APP_SET_ID": "控制特权应用是否访问应用集ID。", # 系统级 App Op
    "ACCESS_VR_STATE": "控制应用是否访问VR模式状态。", # 对应 android.permission.ACCESS_VR_STATE
    "ADD_TRUSTED_DISPLAY": "控制应用是否添加受信任的显示设备。", # 系统级 App Op
    "ALLOW_ANY_CODEC_FOR_PLAYBACK": "控制应用是否在播放时使用任何编解码器。", # 系统级 App Op
    "AMBIENT_WALLPAPER": "控制应用是否提供环境光感壁纸。", # 系统级 App Op
    "ASSOCIATE_INPUT_DEVICE_TO_DISPLAY": "控制应用是否将输入设备关联到特定显示器。", # 系统级 App Op
    "BIND_EXPLICIT_HEALTH_CHECK_SERVICE": "控制应用是否绑定到明确健康检查服务。", # 对应 android.permission.BIND_EXPLICIT_HEALTH_CHECK_SERVICE
    "BIND_NFC_SERVICE": "控制应用是否绑定到NFC服务。", # 系统级 App Op
    "BIND_QUICK_SETTINGS_TILE": "控制应用是否提供快速设置磁贴。", # 对应 android.permission.BIND_QUICK_SETTINGS_TILE
    "BIND_RESOLVER_RANKER_SERVICE": "控制应用是否绑定到解析器排序服务。", # 系统级 App Op
    "BIND_RESUME_ON_REBOOT_SERVICE": "控制应用是否绑定到重启后恢复服务。", # 对应 android.permission.BIND_RESUME_ON_REBOOT_SERVICE
    "BIND_TELEPHONY_NETWORK_SERVICE": "控制应用是否绑定到电话网络服务。", # 对应 android.permission.BIND_TELEPHONY_NETWORK_SERVICE
    "BIND_WALLPAPER": "控制应用是否绑定到壁纸服务。", # 系统级 App Op
    "BLUETOOTH_STACK": "控制应用是否访问完整的蓝牙堆栈。", # 系统级 App Op
    "BRIGHTNESS_SLIDER_USAGE": "控制应用是否跟踪亮度滑块使用情况。", # 系统级 App Op
    "BROADCAST_WAP_PUSH": "控制应用是否广播WAP PUSH消息。", # 对应 android.permission.BROADCAST_WAP_PUSH
    "CALL_AUDIO_INTERCEPTION": "控制应用是否拦截通话音频。", # 系统级 App Op
    "CALL_COMPANION_APP": "控制应用是否调用配套应用。", # 对应 android.permission.CALL_COMPANION_APP
    "CAPTURE_BLACKOUT_CONTENT": "控制应用是否捕获被标记为安全或黑屏的内容。", # 系统级 App Op
    "CAPTURE_SECURE_VIDEO_OUTPUT": "控制应用是否捕获安全的视频输出。", # 系统级 App Op
    "CHANGE_ACCESSIBILITY_VOLUME": "控制应用是否更改无障碍音量。", # 系统级 App Op
    "CHANGE_LOWPAN_STATE": "控制应用是否更改LoWPAN状态。", # 系统级 App Op
    "COMPANION_APPROVE_WIFI_CONNECTIONS": "控制配套设备管理器是否批准Wi-Fi连接。", # 对应 android.permission.COMPANION_APPROVE_WIFI_CONNECTIONS
    "CONFIGURE_INTERACT_ACROSS_PROFILES": "控制应用是否配置跨配置文件交互。", # 系统级 App Op
    "CONTROL_ALWAYS_ON_VPN": "控制应用是否控制始终开启的VPN。", # 系统级 App Op
    "CONTROL_DISPLAY_BRIGHTNESS": "控制应用是否控制显示亮度。", # 系统级 App Op
    "CONTROL_DISPLAY_SATURATION": "控制应用是否控制显示饱和度。", # 系统级 App Op
    "CONTROL_KEYGUARD_SECURE_NOTIFICATIONS": "控制应用是否控制锁屏安全通知显示。", # 系统级 App Op
    "CRYPT_KEEPER": "控制应用是否访问CryptKeeper服务。", # 系统级 App Op
    "DELETE_CACHE_FILES": "控制应用是否删除缓存文件。", # 系统级 App Op
    "DISABLE_HIDDEN_API_CHECKS": "控制应用是否禁用隐藏API检查（开发）。", # 系统级 App Op
    "DISPATCH_PROVISIONING_MESSAGE": "控制应用是否分发设备配置消息。", # 系统级 App Op
    "FOREGROUND_SERVICE_REMOTE_MESSAGING": "控制应用是否在前台运行远程消息服务。", # 对应 android.permission.FOREGROUND_SERVICE_REMOTE_MESSAGING
    "GET_RUNTIME_PERMISSIONS": "控制应用是否查询自身运行时权限状态。", # 对应 android.permission.GET_RUNTIME_PERMISSIONS
    "GRANT_RUNTIME_PERMISSIONS_TO_TELEPHONY_DEFAULTS": "控制系统是否将运行时权限授予默认电话应用。", # 系统级 App Op
    "HEALTH_CONNECT_BACKUP_INTER_AGENT": "控制Health Connect应用内部备份代理间通信。", # 对应 android.permission.HEALTH_CONNECT_BACKUP_INTER_AGENT
    "INPUT_CONSUMER": "控制应用是否作为输入消费者。", # 系统级 App Op
    "INSTALL_DPC_PACKAGES": "控制应用是否安装DPC包。", # 系统级 App Op
    "INSTALL_GRANT_RUNTIME_PERMISSIONS": "控制安装程序是否在安装时授予运行时权限。", # 系统级 App Op
    "INSTALL_LOCATION_TIME_ZONE_PROVIDER_SERVICE": "控制应用是否安装位置时区提供程序服务。", # 系统级 App Op
    "INSTALL_TEST_ONLY_PACKAGE": "控制应用是否安装测试包。", # 开发权限
    "INTENT_FILTER_VERIFICATION_AGENT": "控制应用是否作为Intent过滤器验证代理。", # 系统级 App Op
    "INVOKE_CARRIER_SETUP": "控制应用是否调用运营商设置流程。", # 系统级 App Op
    "LAUNCH_DEVICE_MANAGER_SETUP": "控制应用是否启动设备管理器设置流程。", # 系统级 App Op
    "MANAGE_APP_TOKENS": "控制应用是否管理应用令牌。", # 系统级 App Op
    "MANAGE_BIOMETRIC": "控制应用是否管理生物识别设置和数据。", # 系统级 App Op
    "MANAGE_DEFAULT_APPLICATIONS": "控制应用是否管理默认应用程序。", # 系统级 App Op
    "MANAGE_DEVICE_POLICY_CALLS": "控制应用是否管理与设备策略相关的呼叫。", # 系统级 App Op
    "MANAGE_GAME_ACTIVITY": "控制应用是否管理游戏活动状态。", # Android 12+ App Op
    "MANAGE_GAME_MODE": "控制应用是否管理游戏模式。", # Android 12+ App Op
    "MANAGE_ROTATION_RESOLVER": "控制应用是否管理屏幕旋转决策器。", # 系统级 App Op
    "MANAGE_SAFETY_CENTER": "控制应用是否管理安全中心功能。", # 系统级 App Op
    "MANAGE_SLICE_PERMISSIONS": "控制应用是否管理Slices权限。", # 系统级 App Op
    "MANAGE_SPEECH_RECOGNITION": "控制应用是否管理语音识别服务。", # 系统级 App Op
    "MANAGE_SUBSCRIPTION_USER_ASSOCIATION": "控制应用是否管理订阅与用户关联。", # 系统级 App Op
    "MANAGE_TIME_AND_ZONE_DETECTION": "控制应用是否管理时间和时区自动检测。", # 系统级 App Op
    "MANAGE_TOAST_RATE_LIMITING": "控制应用是否管理Toast通知速率限制。", # 系统级 App Op
    "MANAGE_VIRTUAL_MACHINE": "控制应用是否管理虚拟机。", # 系统级 App Op
    "MANAGE_WEAK_ESCROW_TOKEN": "控制应用是否管理弱托管令牌。", # 系统级 App Op
    "MIGRATE_HEALTH_CONNECT_DATA": "控制应用是否迁移Health Connect数据。", # 系统级 App Op
    "MODIFY_ACCESSIBILITY_DATA": "控制应用是否修改无障碍服务数据。", # 系统级 App Op
    "MODIFY_APPWIDGET_BIND_PERMISSIONS": "控制应用是否修改应用小部件绑定权限。", # 系统级 App Op
    "MODIFY_QUIET_MODE": "控制应用是否修改静默模式（勿扰）。", # 系统级 App Op
    "MODIFY_SETTINGS_OVERRIDEABLE_BY_RESTORE": "控制应用是否修改可被恢复覆盖的设置。", # 系统级 App Op
    "MODIFY_TOUCH_MODE_STATE": "控制应用是否修改触摸模式状态。", # 系统级 App Op
    "MODIFY_USER_PREFERRED_DISPLAY_MODE": "控制应用是否修改用户首选显示模式。", # 系统级 App Op
    "MONITOR_DEFAULT_SMS_PACKAGE": "控制应用是否监控默认短信应用变化。", # 系统级 App Op
    "MONITOR_DEVICE_CONFIG_ACCESS": "控制应用是否监控对设备配置的访问。", # 系统级 App Op
    "NETWORK_BYPASS_PRIVATE_DNS": "控制应用是否绕过私有DNS设置。", # 系统级 App Op
    "NETWORK_SCAN": "控制应用是否执行网络扫描（如Wi-Fi）。", # 对应 android.permission.NETWORK_SCAN
    "OBSERVE_NETWORK_POLICY": "控制应用是否观察网络策略变化。", # 系统级 App Op
    "OBSERVE_ROLE_HOLDERS": "控制应用是否观察系统角色持有者变化。", # 系统级 App Op
    "OVERRIDE_DISPLAY_MODE_REQUESTS": "控制应用是否覆盖显示模式请求。", # 系统级 App Op
    "PERFORM_IMS_SINGLE_REGISTRATION": "控制应用是否执行IMS单次注册。", # 系统级 App Op
    "PROVIDE_REMOTE_CREDENTIALS": "控制应用是否提供远程凭据。", # 系统级 App Op
    "PROVIDE_RESOLVER_RANKER_SERVICE": "控制应用是否提供解析器排序服务。", # 系统级 App Op
    "QUERY_CLONED_APPS": "控制应用是否查询已克隆的应用。", # 对应 android.permission.QUERY_CLONED_APPS
    "RADAR_LOG_CONTROL": "控制应用是否控制雷达日志。", # 系统级 App Op
    "READ_LOWPAN_CREDENTIAL": "控制应用是否读取LoWPAN凭据。", # 系统级 App Op
    "READ_NEARBY_STREAMING_POLICY": "控制应用是否读取附近设备流式传输策略。", # 系统级 App Op
    "READ_NETWORK_USAGE_HISTORY": "控制应用是否读取网络使用历史记录。", # 对应 android.permission.READ_NETWORK_USAGE_HISTORY
    "READ_PRINT_SERVICE_RECOMMENDATIONS": "控制应用是否读取打印服务推荐。", # 对应 android.permission.READ_PRINT_SERVICE_RECOMMENDATIONS
    "READ_WIFI_CREDENTIAL": "控制应用是否读取已保存的Wi-Fi凭据。", # 系统级 App Op
    "READ_WRITE_SYNC_DISABLED_MODE_CONFIG": "控制应用是否读写同步禁用模式配置。", # 系统级 App Op
    "RECEIVE_DATA_ACTIVITY_CHANGE": "控制应用是否接收数据活动状态变化通知。", # 对应 android.permission.RECEIVE_DATA_ACTIVITY_CHANGE
    "RECEIVE_MEDIA_RESOURCE_USAGE": "控制应用是否接收媒体资源使用情况通知。", # 系统级 App Op
    "RECOVER_KEYSTORE": "控制应用是否恢复密钥库中的密钥。", # 系统级 App Op
    "REGISTER_CALL_PROVIDER": "控制应用是否注册为通话提供程序。", # 对应 android.permission.REGISTER_CALL_PROVIDER
    "REGISTER_SIM_SUBSCRIPTION": "控制应用是否注册SIM卡订阅事件。", # 对应 android.permission.REGISTER_SIM_SUBSCRIPTION
    "REGISTER_STATS_PULL_ATOM": "控制应用是否注册拉取统计原子数据。", # 系统级 App Op
    "REQUEST_COMPANION_PROFILE_AUTOMOTIVE_PROJECTION": "控制应用是否请求车载投屏伴侣设备配置文件。", # 对应 android.permission.REQUEST_COMPANION_PROFILE_AUTOMOTIVE_PROJECTION
    "RESTRICTED_VR_ACCESS": "控制应用是否以受限方式访问VR功能。", # 系统级 App Op
    "ROTATE_SURFACE_FLINGER": "控制应用是否旋转SurfaceFlinger输出。", # 系统级 App Op
    "SATELLITE_COMMUNICATION": "控制应用是否进行卫星通信。", # Android 14+ App Op
    "SEND_CALL_LOG_CHANGE": "控制应用是否发送通话记录更改通知。", # 系统级 App Op
    "SEND_DEVICE_CUSTOMIZATION_READY": "控制应用是否发送设备定制化准备就绪信号。", # 系统级 App Op
    "SET_APP_SPECIFIC_LOCALECONFIG": "控制应用是否设置应用特定的区域配置。", # 系统级 App Op
    "SET_AUTHENTICATION_DATA": "控制应用是否设置身份验证数据。", # 系统级 App Op
    "SET_DEBUG_APP": "控制应用是否设置调试应用。", # 系统级 App Op
    "SET_PREFERRED_APPLICATIONS": "控制应用是否设置首选应用。", # 系统级 App Op
    "SIGNAL_PERSISTENT_PROCESSES": "控制应用是否向常驻进程发送信号。", # 系统级 App Op
    "START_PRINT_SERVICE_CONFIG_ACTIVITY": "控制应用是否启动打印服务配置活动。", # 对应 android.permission.START_PRINT_SERVICE_CONFIG_ACTIVITY
    "SUGGEST_TELEPHONY_TIME_AND_ZONE": "控制应用是否建议电话网络提供的时间和时区。", # 系统级 App Op
    "SYSTEM_APPLICATION_OVERLAY": "控制系统应用是否显示在其他应用上方的悬浮窗。", # 系统级 App Op
    "TEST_INPUT_METHOD": "控制应用是否测试输入法。", # 系统级 App Op
    "TIS_EXTENSION_INTERFACE": "控制应用是否访问文本输入服务扩展接口。", # 系统级 App Op
    "TUNER_RESOURCE_ACCESS": "控制应用是否访问调谐器资源。", # 对应 android.permission.TUNER_RESOURCE_ACCESS
    "TURN_SCREEN_ON": "控制应用是否在锁屏上方点亮屏幕（已废弃）。", # 对应 android.permission.TURN_SCREEN_ON
    "UPDATE_CONFIG": "控制应用是否更新配置。", # 系统级 App Op
    "UPDATE_LOCK": "控制应用是否更新锁。", # 系统级 App Op
    "UPGRADE_RUNTIME_PERMISSIONS": "控制应用是否升级运行时权限。", # 系统级 App Op
    "USE_EXACT_ALARM": "控制应用是否安排精确的闹钟/定时任务。", # Android 12+ App Op (旧名称)
    "WATCH_APPOPS": "控制应用是否监视App Ops更改。", # 系统级 App Op
    "WHITELIST_AUTO_REVOKE_PERMISSIONS": "控制应用是否将自身添加到自动撤销未使用权限白名单。", # 对应 android.permission.WHITELIST_AUTO_REVOKE_PERMISSIONS
    "WHITELIST_RESTRICTED_PERMISSIONS": "控制应用是否将自身添加到受限权限白名单。", # 系统级 App Op
    "WIFI_UPDATE_COEX_UNSAFE_CHANNELS": "控制应用是否更新Wi-Fi共存不安全信道信息。", # 系统级 App Op
    "WRITE_DREAM_STATE": "控制应用是否写入Daydream状态。", # 系统级 App Op
    "WRITE_EMBEDDED_SUBSCRIPTIONS": "控制应用是否写入嵌入式SIM卡订阅信息。", # 系统级 App Op
    "READ_EXERCISE_ROUTE": "控制应用是否读取健康数据中的运动路线。", # Android 14+ App Op
    "READ_HEART_RATE": "控制应用是否读取健康数据中的心率信息。", # Android 14+ App Op
    # 添加一些常见但可能没有直接对应权限的 App Ops
    "RUN_IN_BACKGROUND": "控制应用是否可以在后台运行。",
    "TOAST_WINDOW": "控制应用是否可以显示Toast通知。",
    "PICTURE_IN_PICTURE": "控制应用是否可以使用画中画模式。", # 对应 android.permission.PICTURE_IN_PICTURE
    "NEARBY_DEVICES": "控制应用是否可以发现附近的设备（包括Wi-Fi Aware, UWB, Bluetooth等）。", # Android 12+ App Op，涵盖多个权限
    "READ_BASIC_PHONE_STATE": "控制应用是否可以读取基本的电话状态（READ_PHONE_STATE的子集）。", # 对应 android.permission.READ_BASIC_PHONE_STATE
    "READ_CALL_READ_ONLY": "控制应用是否只读访问通话记录。", # Android 10+ App Op
    "ACCESS_CLIPBOARD": "控制应用是否访问剪贴板。", # Android 10+ App Op (READ_CLIPBOARD 和 WRITE_CLIPBOARD 可能合并或相关)
    "MANAGE_NOTIFICATIONS": "控制应用是否管理通知（如渠道、勿扰模式）。", # 系统级 App Op
    # 其他一些可能出现在 appops get 输出中的 App Ops (根据经验补充)
    "MUTE_MICROPHONE": "控制应用是否可以静音麦克风。",
    "WIFI_SCAN": "控制应用是否可以扫描Wi-Fi网络。", # 对应 android.permission.SCAN_WIFI 或 ACCESS_WIFI_STATE 的一部分
    "CHANGE_WIFI_STATE": "控制应用是否可以更改Wi-Fi状态。", # 有对应的权限，也可能出现在 App Ops 中
    "CHANGE_BLUETOOTH_STATE": "控制应用是否可以更改蓝牙状态。", # 有对应的权限，也可能出现在 App Ops 中
    "ACTIVATE_VPN": "控制应用是否可以激活VPN。",
    "ESTABLISH_VPN": "控制应用是否可以建立VPN连接。", # 对应 android.permission.BIND_VPN_SERVICE
    "SYSTEM_ALERT_WINDOW": "控制应用是否可以在其他应用上方显示悬浮窗。", # 对应 android.permission.SYSTEM_ALERT_WINDOW
    "WRITE_SMS": "控制应用是否可以写入短信。", # 对应 android.permission.WRITE_SMS (已废弃，但 App Op 可能存在)
    "READ_CELL_BROADCASTS": "控制应用是否可以读取小区广播。", # 对应 android.permission.READ_CELL_BROADCASTS
    "REQUEST_DELETE_PACKAGES": "控制应用是否可以请求删除其他应用。", # 对应 android.permission.REQUEST_DELETE_PACKAGES
    "READ_PHONE_STATE_FROM_DATA": "控制应用是否可以从数据中读取电话状态。", # 可能与 READ_PHONE_STATE 相关
    "READ_ICC_SMS": "控制应用是否可以读取SIM卡上的短信。", # 可能与 READ_SMS 相关
    "RECEIVE_WAP_PUSH": "控制应用是否可以接收WAP PUSH消息。", # 对应 android.permission.RECEIVE_WAP_PUSH

    "READ_MEDIA_VISUAL_USER_SELECTED": "控制应用是否可以读取用户明确选择的视觉媒体文件（图片和视频，Android 14+）。",
    "WRITE_MEDIA_IMAGES": "控制应用是否可以写入共享存储中的图片文件（Android 13+）。",
    "TAKE_AUDIO_FOCUS": "控制应用是否可以请求音频焦点，从而控制设备音频输出（例如在播放音频时暂停其他应用的播放）。",
    "NO_ISOLATED_STORAGE": "控制应用是否可以绕过分区存储（Scoped Storage）限制，使用旧版存储模型访问外部存储。（通常与 LEGACY_STORAGE 相关，允许更广泛的文件访问）",
    "MANAGE_EXTERNAL_STORAGE": "控制应用是否可以拥有对外部存储中所有文件的广泛访问权限（即“所有文件访问”特殊权限，Android 11+）。",
    "LEGACY_STORAGE": "控制应用是否允许使用旧版存储模式（即不强制执行分区存储）。（通常用于应用兼容性）",
    "PROJECT_MEDIA": "控制应用是否可以进行媒体投影（屏幕或音频捕获）。",
    "COARSE_LOCATION": "控制应用是否可以访问粗略的地理位置信息（例如基于基站或 Wi-Fi）。",
    "WRITE_MEDIA_VIDEO": "控制应用是否可以写入共享存储中的视频文件（Android 13+）。",
    "ACCESS_RESTRICTED_SETTINGS": "控制应用是否可以引导用户进入特定系统设置页面以授予受限权限（如无障碍服务、通知监听器等）。",
    "FINE_LOCATION": "控制应用是否可以访问精确的地理位置信息（例如基于 GPS）。",
    "WRITE_MEDIA_AUDIO": "控制应用是否可以写入共享存储中的音频文件（Android 13+）。",
    
    "MOCK_LOCATION": "允许应用创建模拟位置数据，用于测试或覆盖真实位置。",
    "NEIGHBORING_CELLS": "允许应用访问设备蜂窝网络信息，包括附近的基站。",
    "AUDIO_MEDIA_VOLUME": "允许应用控制媒体播放音量。",
    "READ_DEVICE_IDENTIFIERS": "允许应用读取设备的持久性标识符，如 IMEI 或 MEID。",
    "USE_ICC_AUTH_WITH_DEVICE_IDENTIFIER": "允许应用结合设备标识符使用 SIM 卡 (ICC) 认证机制。",
    "ZTE_WRITE_MSG": "中兴设备特定：允许应用编写消息（很可能是短信/彩信）。",
    "ZTE_CALL_FORWARD": "中兴设备特定：允许应用管理呼叫转移设置。",
    "POST_NOTIFICATION": "允许应用在状态栏发布通知。",
    "AUDIO_ALARM_VOLUME": "允许应用控制闹钟音量。",
    "MONITOR_HIGH_POWER_LOCATION": "允许应用使用高精度方法（如 GPS）持续监控设备位置。",
    "ACCESS_ACCESSIBILITY": "允许应用访问辅助功能服务，可能与其它应用的界面进行交互。",
    "VIBRATE": "允许应用控制设备的振动器。",
    "MONITOR_LOCATION": "允许应用使用较低电量方法持续监控设备位置。",
    "ZTE_MMS_SEND": "中兴设备特定：允许应用发送彩信。",
    "MANAGE_MEDIA": "允许应用管理媒体文件（例如，修改、删除）。",
    "ZTE_CONFERENCE_CALL": "中兴设备特定：允许应用管理电话会议。",
    "START_FOREGROUND": "允许应用启动前台服务（在后台运行并带有持久通知）。",
    "GPS": "允许应用访问设备的 GPS 接收器以获取位置数据。",
    "ESTABLISH_VPN_SERVICE": "允许应用建立和管理 VPN（虚拟专用网络）连接。",
    
    "android.permission.AUDIO_VOICE_VOLUME": "控制语音通话音量",
    "android.permission.MANAGE_IPSEC_TUNNELS": "管理 IPsec 隧道",
    "android.permission.AUDIO_RING_VOLUME": "控制铃声音量",
    
    "PHONE_CALL_MICROPHONE": "控制通话期间麦克风的使用 (App Op)",
    "PHONE_CALL_CAMERA": "控制通话期间相机的使用 (如视频通话) (App Op)",
    "AUDIO_RING_VOLUME": "控制铃声音量的调整 (App Op)",
    "AUDIO_BLUETOOTH_VOLUME": "控制蓝牙音频音量的调整 (App Op)",
    "MANAGE_IPSEC_TUNNELS": "管理 IPsec 隧道 (通常是系统/签名权限)",
    "AUDIO_NOTIFICATION_VOLUME": "控制通知音量的调整 (App Op)",
    "ACTIVITY_RECOGNITION_SOURCE": "控制从特定源获取活动识别数据 (App Op)",
    "AUDIO_VOICE_VOLUME": "控制语音通话音量的调整 (App Op)",
    "READ_WRITE_HEALTH_DATA": "读取/写入健康数据 (App Op)",
    "SYSTEM_EXEMPT_FROM_DISMISSIBLE_NOTIFICATIONS": "允许发送不可清除的通知 (通常是系统/签名权限)",
    "FINE_LOCATION_SOURCE": "控制从特定源获取精确位置数据 (App Op)"
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
    """运行ADB命令并返回输出"""
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode != 0:
            # print(f"ADB Command Error: {cmd}\nStderr: {result.stderr.strip()}") # Debugging line
            # 如果 appops get 针对某个包失败，可能是包名无效或权限问题，返回空列表即可
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
    elif app_type_filter == 'system': # 添加一个系统应用选项，尽管主函数里没用，但函数支持
         cmd += " -s"

    output = run_adb_command(cmd)
    if not output:
        return []

    packages = [line.replace("package:", "").strip() for line in output.splitlines() if line.strip()]

    # 注意：“user_no_core_system”过滤器的精度低于“-3”，但可能会排除
    # 一些“-3”不会排除的系统组件。如有需要，请保留它以保持相似性。
    # 对于 appops，关注“-3”（第三方）可能更符合用户隐私方面的考虑。

    if app_type_filter == 'user_no_core_system':
        filtered_packages = []
        # 此列表仅供参考，可能需要根据设备/Android 版本进行调整
        system_prefixes = (
            "com.android.", "com.google.android.", "android.",
            "com.qualcomm.", "com.mediatek.", "com.samsung.",
            "com.lge.", "com.motorola.", "com.sony.", "com.oneplus.", "com.oppo.", "com.vivo.", "com.xiaomi.",
            "com.huawei.", "com.honor.", "com.cyanogenmod.", "com.lineageos." # Add more common prefixes
        )
        # Exact package names for known core system components
        core_system_exact = (
            "android", "system", "com.google.android.gms", "com.android.vending", # GMS and Play Store often considered system
            "com.android.systemui", "com.android.providers.media",
            "com.android.providers.telephony", "com.android.providers.settings",
            "com.android.shell", "com.android.inputmethod.latin", # Default keyboard
            "com.android.bluetooth", "com.android.settings", "com.android.phone",
            "com.android.server.telecom", "com.android.packageinstaller",
            "com.android.launcher", # Default launcher
            # Add more as needed for specific devices/versions
        )
        for pkg in packages:
            is_core_system_prefix = any(pkg.startswith(prefix) for prefix in system_prefixes)
            is_exact_core = pkg in core_system_exact

            # 启发式检查：排除经常在 /system 或 /product 中找到的软件包
            # 这种方法并不完美，但有助于过滤。需要使用“adb shell pm path <pkg>”，但速度较慢。# 或者检查 dumpsys 中的标志，但我们避免使用 dumpsys 来获取主要信息。
            # 为了简单和快速，这里主要依赖前缀/精确名称会更好。
            # 更稳健的方法可能是将 -3 与排除列表结合使用。
            # 在本版本中，我们继续使用前缀/精确列表。

            if not is_core_system_prefix and not is_exact_core:
                filtered_packages.append(pkg)
        return filtered_packages

    # 如果不是“user_no_core_system”，则直接从 adb 返回列表
    return packages


def get_app_ops_for_package(package_name):
    """
    使用 adb shell appops get 获取应用的 App Ops 状态。
    返回一个列表，每个元素是 (app_op_name, state, raw_info_string)
    """
    cmd = f'adb shell appops get {package_name}'
    output = run_adb_command(cmd)
    app_ops_info = []

    if not output:
        # print(f"Warning: No app ops output for package {package_name}") # Debugging line
        return []

    # 用于捕获应用操作名称、状态和行其余内容的正则表达式
    # 示例行：
    # CAMERA：允许；时间=1 小时 3 分 15 秒 987 毫秒前
    # READ_EXTERNAL_STORAGE：拒绝；时间=1 天前
    # ACCESS_FINE_LOCATION：默认；时间=5 小时前
    # RUN_ANY_IN_BACKGROUND：允许；uid=10123；pkg=com.example.app；时间=12 小时前
    # VIBRATE：允许；dur=0 毫秒；时间=1 秒 345 毫秒前
    # 处理间距和其他信息中的潜在变化
    app_op_line_regex = re.compile(r"^\s*([\w\.\_]+):\s*([\w]+)(.*)", re.IGNORECASE)

    # 跳过第一行（UID模式）
    lines = output.splitlines()
    if lines:
        lines = lines[1:] # 跳过标题

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        match = app_op_line_regex.match(line_stripped)
        if match:
            app_op_name = match.group(1).strip()
            state = match.group(2).strip()
            raw_info_string = match.group(3).strip() # 该行的其余部分（时间、持续时间等）
            app_ops_info.append((app_op_name, state, raw_info_string))
        # else:
            # print(f"警告：无法解析程序包 {package_name} 的应用程序操作行：“{line_stripped}”") # 调试未解析的行

    return app_ops_info


def get_appop_description(appop_name):
    """获取 App Op 的描述"""
    return appop_descriptions.get(appop_name.upper(), "未找到明确定义或用途未知") # 使用 upper() 进行不区分大小写的查找
    


def write_to_txt(file_path, content_list):
    """将内容列表写入 TXT 文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in content_list:
            f.write(item)

def write_to_csv(file_path, data_for_csv):
    """将数据写入 CSV 文件"""
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # 更新了 App Ops 数据的标头
        writer.writerow(['Package Name', 'App Name', 'App Op Name', 'State', 'Description', 'Raw Info'])
        for row in data_for_csv:
            writer.writerow(row)

def write_to_json(file_path, data_for_json):
    """将数据写入 JSON 文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data_for_json, f, indent=4, ensure_ascii=False)


def main():
    print("选择操作：")
    print("1. 列出所有 App Ops 状态 (默认)")
    print("2. 仅列出特定 App Op 的状态")
    choice_appops = input("请选择（1/2）：") or "1"

    specific_app_op_filter = None
    if choice_appops == "2":
        # App Op 名称通常为大写，请进行相应提示
        specific_app_op_filter = input("请输入要列出的特定 App Op (例如 CAMERA, ACCESS_FINE_LOCATION)：").strip().upper()
        if not specific_app_op_filter:
            print("未输入特定 App Op，将列出所有 App Ops。")
            specific_app_op_filter = None # 如果为空则重置

    print("\n选择应用范围：")
    print("1. 用户应用 (不含常见核心系统组件, 默认)")
    print("2. 所有已安装应用")
    print("3. 仅第三方应用 (用户自行安装的应用)")
    print("4. 选择单个应用")
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
        # 对于“1”，默认值已设置
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
    processed_packages_count = 0 # 统计包含任何相关应用程序操作信息的软件包

    for i, pkg in enumerate(packages):
        progress = (i + 1) / len(packages)
        bar_length = 30
        filled_length = int(bar_length * progress)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        # 获取应用中文名，如果不在字典中则显示 "未知应用"
        app_name_display = apps_dict.get(pkg, "未知应用")
        # Display shorter package name if it's too long
        display_pkg = pkg if len(pkg) <= 25 else pkg[:22] + "..."
        
        progress_line = f'正在处理: {display_pkg:<25} [{bar}] {i+1}/{len(packages)}'

        # 使用 '\r' 回车 + 清空行 + 写入进度信息
        sys.stdout.write('\r' + ' ' * 100 + '\r')  # 清除整行
        sys.stdout.write(progress_line)
        sys.stdout.flush()

        app_ops_info = get_app_ops_for_package(pkg)

        if not app_ops_info:
            # 此软件包可能没有通过 `appops get` 列出的任何应用程序操作，或者命令失败。
            # 如果没有任何信息，请不要将其添加到 processed_pa​​ckages_count。
            continue

        current_pkg_txt_lines = []
        pkg_app_ops_for_json = []
        has_relevant_app_ops_for_pkg = False # 如果此软件包有符合过滤器的应用程序操作，则进行标记

        for app_op_name, state, raw_info_string in app_ops_info:
            # 应用特定的 App Op 过滤器（不区分大小写，根据大写过滤器进行检查）
            if specific_app_op_filter and specific_app_op_filter not in app_op_name.upper():
                continue

            has_relevant_app_ops_for_pkg = True
            description = get_appop_description(app_op_name)

            # 准备输出格式的数据
            if not current_pkg_txt_lines:
                current_pkg_txt_lines.extend([f"应用包名: {pkg} ({app_name_display})\n", "-" * 30 + "\n", "App Ops 状态：\n"])

            txt_line = f"    {app_op_name}: 状态={state}, 用途：{description}\n      附加信息: {raw_info_string if raw_info_string else '无'}\n"
            current_pkg_txt_lines.append(txt_line)

            csv_data.append([pkg, app_name_display, app_op_name, state, description, raw_info_string])

            pkg_app_ops_for_json.append({
                "app_op": app_op_name,
                "state": state,
                "description": description,
                "raw_info": raw_info_string,
            })

        if has_relevant_app_ops_for_pkg:
            processed_packages_count += 1
            current_pkg_txt_lines.append("\n")
            txt_output_lines.extend(current_pkg_txt_lines)
            if pkg_app_ops_for_json:
                 json_data_dict[f"{pkg} ({app_name_display})"] = {"app_ops_info": pkg_app_ops_for_json}

    # 清除进度线
    print('\r' + ' ' * 80, end='') # 打印空格以清除行
    print("\n" + "="*30)
    print(f"处理完成！共扫描 {len(packages)} 个应用，其中 {processed_packages_count} 个应用有相关 App Ops 信息。")

    if console_output_choice == "1":
        print("\n--- 控制台输出 ---")
        if txt_output_lines:
            # 如果需要，可以连接多行以获得更清晰的控制台输出，或者逐行打印
            for line in txt_output_lines:
                 print(line, end='')
        else:
            print("没有找到符合条件的 App Ops 信息在控制台输出。")
        print("--- 控制台输出结束 ---")


    # 根据生成的列表/字典确定是否有要写入的数据
    has_output_data = bool(txt_output_lines) or bool(csv_data) or bool(json_data_dict)

    if not has_output_data:
        print("没有找到符合条件的 App Ops 信息可供输出到文件。")
        return

    output_file_base = "app_appops_report"
    output_file_path = ""

    try:
        if output_format_choice == "1":
            output_file_path = f"{output_file_base}.txt"
            if txt_output_lines:
                 write_to_txt(output_file_path, txt_output_lines)
            else:
                 print("没有数据可写入 TXT 文件。") 
                 output_file_path = "" # 阻止成功消息
        elif output_format_choice == "2":
            output_file_path = f"{output_file_base}.csv"
            if csv_data:
                 write_to_csv(output_file_path, csv_data)
            else:
                 print("没有数据可写入 CSV 文件。") 
                 output_file_path = "" # 阻止成功消息
        elif output_format_choice == "3":
            output_file_path = f"{output_file_base}.json"
            if json_data_dict:
                 write_to_json(output_file_path, json_data_dict)
            else:
                 print("没有数据可写入 JSON 文件。") 
                 output_file_path = "" # 阻止成功消息
        else:
             print("未选择有效的输出格式。")
             return # 如果未选择有效格式则退出

        # 检查文件是否确实创建并且包含内容
        if output_file_path and os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 0:
            print(f"\nApp Ops 信息已保存到：{os.path.abspath(output_file_path)}")
        elif output_file_path: # 文件是预期的，但可能是空的或失败的
             print(f"\n尝试写入到 {os.path.abspath(output_file_path)}，但可能没有数据或写入失败。")

    except IOError as e:
        print(f"\n写入文件时发生错误: {e}")
    except Exception as e:
        print(f"\n发生未知错误: {e}")


if __name__ == "__main__":
    main()

