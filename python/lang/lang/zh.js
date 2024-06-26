/*
 * @Author:  liff liff@enlink.cn
 * @Date: 2022-05-20 09:34:23
 * @LastEditors: liutao 2193565156@qq.com
 * @LastEditTime: 2023-06-29 15:48:09
 * @FilePath: \ensbrain-web-admin\src\i18n\lang\zh.js
 * @Description: 
 * 
 * Copyright (c) 2017-2023 . Jiangsu Enlink Network Technology Co.,Ltd., All Rights Reserved. 
 */

import { login_zh } from './modules/login/login_zh';
import { home_zh } from './modules/home/home_zh';
import { log_zh } from './modules/log/log_zh';
import { admin_zh } from './modules/administrator/administrator_zh';
import { message_zh } from './modules/message/message_zh';
import { form_error_zh } from './modules/form_error/form_error_zh';
import { system_zh } from './modules/system/system_zh';
import { users_zh } from './modules/users/users_zh';
import { gateway_zh } from './modules/gateway/gateway_zh';
import { operation_zh } from './modules/operationalConf/operationalConf_zh';
import { approve_zh } from './modules/approve/approve_zh';
import { form_zh } from './modules/form/form_zh';
import { creditLev_zh } from './modules/creditLev/creditLev_zh';
import { network_zh } from './modules/network/network_zh';
import { release_zh } from './modules/release/release_zh';
import { policy_zh } from './modules/secure_policy/secure_policy_zh'
import { strategy_zh } from './modules/strategy/strategy_zh';
import { trust_auth_zh } from './modules/trust_auth/trust_auth_zh';
import { app_zh } from './modules/app/app_zh';
import { privacy_zh } from './modules/privacy/privacy_zh';
import { configs_zh } from './modules/configs/configs_zh';
import { linkage_zh } from './modules/linkage/linkage_zh';
import { alarm_zh } from './modules/alarm/alarm_zh';
import { space_zh } from './modules/space/space_zh';
import { operationTip_zh } from './modules/operation/operation_zh';
import { device_zh } from '@/i18n/lang/modules/device/device_zh';
import { tagMng_zh } from '@/i18n/lang/modules/tagMng/tagMng_zh';
import { notice_zh } from './modules/notice/notice_zh';
import { loginDiy_zh } from './modules/loginDiy/loginDiy_zh';
import { deviceRegistration_zh } from './modules/deviceRegistration/deviceRegistration_zh';
import { messageMng_zh } from '@/i18n/lang/modules/messageCenter/message_zh';
import { packageMng_zh } from '@/i18n/lang/modules/packageMng/packageMng_zh';
import { distributeMng_zh } from '@/i18n/lang/modules/distributeMng/distributeMng_zh';
import { userManage_zh } from './modules/userManage/userManage_zh';
import { appMng_zh } from '@/i18n/lang/modules/appMng/app_zh';
import { operateMng_zh } from '@/i18n/lang/modules/operateMng/operate_zh';
import { routeName_zh } from '@/i18n/lang/modules/routeName/routeName_zh';

export default {
    unknown:'未知',
    me: '我',
    i18nTip: '部分国际化重新登录后生效',
    language_set: '语言设置',
    data_preparation: '数据准备中...',
    application_publish: '应用发布',
    retryCount:'重试次数（次）',
    retrInterval:'重试间隔（秒）',
    detectionNum:'探测次数（次）',
    detectionInterval:'探测间隔（秒）',
    switch_theme: '主题切换',
    managementCustom: '管理端自定义',
    number: '{number}',
    all: '所有',
    totals: '总数',
    final_value: '最后值',
    average_value: '平均值',
    maximum_value: '最大值',
    minimum_value: '最小值',
    mins: '{value}分钟',
    hour: '{value}小时',
    one_day: '一天',
    monday: '周一',
    Tuesday: '周二',
    wednesday: '周三',
    thursday: '周四',
    friday: '周五',
    saturday: '周六',
    sunday: '周日',
    service_threads_numb: '服务线程数',
    message_cumulative: 'MQ消息累积数',
    Redis_response_time: 'Redis响应时间',
    interface_response_time: '接口响应时间',
    interface_success_rate: '接口成功率',
    tripartite_interface_success_rate: '三方接口成功率',
    service_monitor_index: '服务监控指标',
    import_application: '导入应用',
    health_check: '健康度检查',
    total_monitor: '全部监控',
    Monitor_object_type: '监控对象类型',
    Own_group: '所属分组',
    ipc: '专利',    
    next_level: '下一级',    
    add_access_policy: '新增访问策略',    
    clear_up: '清空',    
    department: '个部门',    
    personnel: '个人员',    
    characters: '个角色',    
    tags: '个标签',    
    devices: '个设备',    
    device_groups: '个设备组',    
    set_custom_column: '设置自定义列',    
    enter_keyword_filter: '可输入关键词过滤',    
    select_group_first: '请先选择组织架构',    
    phone_email_example: '例如"13811111111,test@qq.com,15811111111"',    
    multiple_entries: '支持多个输入逗号隔开',    
    app_search_tip: '应用名称、应用url、标签',    
    monitor_frequency: '监控频率',    
    advanced_set: '高级设置',    
    http_request_header: 'HTTP请求头',    
    request_content: '请求内容',    
    PING_packet_number: 'PING包数目',    
    lost_packets_numb_up: '丢包数目上限',    
    send_content_tip: '发送的内容格式为: key1=value1;key2=value2。或者一段JSONObject',    
    request_header_tip: '请求头信息格式：key1:value1 回车换行 key2:value2',    
    cookie_tip: 'cookie格式：key1:value1;key2:value2',    
    timeOut: '超时时间（毫秒）',    
    custom_minutes: '自定义(分钟)',    
    task_type: '任务类型',    
    probe_point: '探测点',    
    select_detection_point: '选择检测点',    
    dial_test: '拨测检验',    
    add_condition_group: '添加条件组',    
    availability_condition: '可用条件',    
    assertion_definition: '断言定义',    
    monitor_tip: '设置探测点上拨测响应结果是否异常的判断条件，满足所有条件的探测点为可用探测点',    
    Monitor_object: '监控对象',    
    select_server: '请选择服务器',    
    enter_task_name: '请输入任务名称',    
    monitoring_task: '监控任务',    
    delete_monitoring_task: '删除监控任务',    
    sure_delete_monitoring_task: '是否要删除该监控任务？',    
    support_equipment: '配套设备',    
    tool: '工具',
    create_task: '创建任务',
    task: '任务',
    add_task: '新增任务',
    edit_task: '编辑任务',
    sure_disable_task: '确认禁用该任务吗？',
    sure_enable_task: '确认启用该任务吗？',
    change_key_tip: '秘钥修改影响应用对接，请确认',
    system_monitoring: '系统监控',
    system_icon: '系统图标',
    exporting: '正在导出',
    background_continue: '后台继续',
    historical_record: '历史记录',
    download_fail: '下载失败',
    deriving: '导出中',
    importing: '导入中',
    export_complete: '导出完成',
    import_complete: '导入完成',
    service_monitoring: '服务监控',
    process_monitoring: '进程监控',
    Network_information: '网卡信息',
    business_service: '业务服务',
    gsnw_netware: '网关服务',
    data_services: '数据服务',
    basic_service: '基础服务',
    system_service: '系统服务',
    alarm_management: '告警管理',
    elimination_reason: '消除理由',
    delete_alarm_conf: '删除告警配置',
    is_delete_alarm_conf: '是否要删除该告警配置？',
    operation_stop_detect: '该操作将停止对监控对象进行检测',
    operation_start_detect: '该操作将开始对监控对象进行检测',
    no_license_tip: '您还可以分别对组织机构下不同组织进行授权配置。',
    have_license_tip: '点击“+”按钮可分别对组织机构下不同组织进行授权配置。',
    traffic_range_color: '策略执行的流量范围,红色代表阻止,绿色代表放行,蓝色代表隧道',
    exceed_user_warning: '用户数超过阈值预警',
    exceed_user_manage: '用户数超限处理',
    allow_login: '允许用户登录',
    disabled_login: '禁止用户登录',
    alarm_reason: '消除理由',
    remind: '提醒',
    ealth_check: '健康度检查',
    auth_config: '认证配置',
    equipment_tag: '设备标签',
    RSA: '国际密码标准（RSA）',
    SM2: '中国商业密码标准（SM2加密）',
    CA_issue_certificate: 'CA签发证书',
    collor_cert_update: '控制器证书修改',
    del_national_secret_cert: '删除国密证书',
    del_business_secret_cert: '删除商密证书',
    policy_classification: '策略分类',
    add_certificate: '+添加证书',
    subject_name: '主题名',
    flow_mirroring: '流量镜像',
    usb_device: 'USB存储设备',
    printer: '打印机',
    terminal_watermark_strategy: '终端水印策略',
    peripheral_control_policy: '外设管控策略',
    uninstallation_control_policy: '卸载管控策略',
    add_specific_conditions: '新增具体条件',
    disabled:'已禁用',
    have_been_enabled:'已禁用',
    terminal_name:'终端名称',
    image_server_IP: '镜像服务器IP',
    enter_image_server: '请输入镜像服务器',
    terminal_control: '终端管控',
    peripheral_control: '外设管控',
    terminal_watermark: '终端水印',
    unloading_control: '卸载管控',
    number_effective_objects: '生效对象数',
    SSO_verification: 'SSO校验',
    SSO_Single_point: 'SSO单点配置',
    get_ticket_class: '获取票据实现类',
    get_ticket_URL: '获取票据URL',
    interface_parameter: '接口参数',
    capture_packet: '抓包',
    new_subgroup: '新建子组',
    packet_capture_log: '抓包日志',
    group_not_renamed: '根组不可重命名',
    group_not_del: '根组不可删除',
    network_management: '网络管理',
    dns_configuration: 'DNS配置',
    add_upstream_DNS_server: '添加上游DNS服务器',
    add_resolution_address: '添加解析地址',
    del_resolution_address: '删除解析地址',
    edit_resolution_address: '编辑解析地址',
    add_DNS_server: '新增DNS服务器',
    edit_DNS_server: '编辑DNS服务器',
    del_DNS_server: '删除DNS服务器',
    lock_cause: '锁定原因',
    lock_type: '锁定类型',
    unlock_ip: '解锁IP',
    update_time: '更新时间',
    time_selector: '时间选择器',
    locking_duration: '锁定时长',
    dns_query: 'DNS查询',
    NAT_policy: 'NAT策略',
    policy_name_and_category: '策略名称、分类',
    organizationalAndUser: '组织模型、用户模型',
    system_strategy: '系统策略',
    watermarkName: '张三(zhangsan)',
    certificate_management: '证书管理',
    subject_issuer: '主题、签发者',
    delete_certificate: '删除证书',
    group_not_app: '应用组下暂无应用',
    enable_group_allApp: '确定启用该组下所有应用吗?',
    disable_group_allApp: '确定禁用该组下所有应用吗?',
    edit_appGroup_success: '更新应用组成功',
    add_appGroup_success: '新增应用组成功',
    institutional_framework: '组织机构',
    move_group_success: '移动至分组成功',
    instruction_add_success: '指令新增成功',
    disable_app: '禁用应用',
    enable_app: '启用应用',
    pleaseSelectMoveApp: '请选择要移动的应用',
    batch_enable: '批量启用',
    batch_disable: '批量禁用',
    sure_enable_select_app: '确定启用选中的应用吗？',
    sure_disable_select_app: '确定禁用选中的应用吗？',
    add_app_tag: '新增应用标签',
    waterMarlTip: '显式水印：肉眼可见水印（透明度5%以上），人眼可以较明显的看到水印内容。',
    waterMarlTip1: '隐式水印：肉眼不可见水印（透明度2%），可以通过调整图片对比度查看水印内容。用于事后审计，不影响员工正常办公。',
    IP_whitelist_policy_tip: 'IP白名单策略一旦开启,只允许白名单内访问。如果您同时使用IPv4、IPv6,请将它们加入此白名单',
    IP_whitelist_policy_tip1: 'IP地址范围可以是单个IP地址、IP地址段:',
    IP_whitelist_policy_tip2: '1、单个IP地址：例如192.168.10.10',
    IP_whitelist_policy_tip3: '2、IP地址段：例如192.168.52.0-192.168.52.24或者192.168.52.0/24',
    IP_whitelist_policy_tip4: 'IPv6地址范围支持以下格式：',
    IP_whitelist_policy_tip5: '1、单个IP地址：例如2001::123',
    IP_whitelist_policy_tip6: '2、IPv6前缀：例如2001::123/64',
    IP_whitelist_policy_tip7: '注：IPv6暂不支持range形式',
    enter_ip_and_IP_segment: '请输入IP、IP段',
    enter_IPv6_with_mask: '请输入IPv6格式可加掩码',
    both_account_tip: '针对同一账号，设定时间内密码连续输错达到设定次数，则执行相应动作',
    level1: '级别一',  
    level2: '级别二',  
    level3: '级别三',  
    level4: '级别四',  
    level5: '级别五',  
    associated_domain: '关联域名',  
    del_app: '删除应用',
    push_channel: '推送通道',
    fault_location: '故障定位',
    info_and_above: 'info及以上',
    warn_and_above: 'warn及以上',
    independent_choice: '自主选择',
    already_associated_domain: '已关联的域名',
    manually_delete_alarm: '手动删除告警',
    alarm_methods: '告警处理手段',
    operation_tip: '该操作可能会影响系统服务',
    restarting_tip: '正在重启请稍等...',
    refresh_cycle: '刷新周期',
    process_name: '进程名称',
    memory_usage: '内存使用',
    open_file_count: '打开文件数',
    nic_name: '网卡名称',
    IPV4_gateway: 'IPv4默认网关',
    IPV6_gateway: 'IPv6默认网关',
    Default_Gateway: '默认网关',
    route_config: '路由配置',
    edit_nic: '编辑网卡信息',
    iP_configuration: 'IP 配置',
    health: '健康',
    fault: '故障',
    restart: '重启',
    toolName: '工具名称',
    level: '级',
    pieces: '个',
    length_err_100:'长度不可超过100个字符',
    weightValue: '权重值',
    belongOrganization: '所属组织',
    organizationName: '组织名称',
    manageOrg: '管理组织',
    catalogues: '学科',
    subject: '学科',
    department: '院系',
    priority: '优先级',
    main: '主体',
    more: '更多',
    details: '详情',
    soundLight: '声光报警',
    plain: '正序',
    reverse: '倒序',
    china: '中国',
    population: '人数',
    greater: '大于',
    lt: '小于',
    equal_to: '等于',
    less_than_or_equal: '小于等于',
    greater_or_equal: '大于等于',
    not_equal: '不等于',
    person: '人',
    progress: '进度',
    domain: '域名',
    cache_update: '缓存更新',
    correlation_time: '关联时间',
    add_ass_domin: '新增关联域名',
    activeCommunity: '活跃社群',
    abnormalCommunity: '异常社群',
    activeEntity: '活跃实体',
    abnormalEntity: '异常实体',
    ip: 'IP',
    account: '账户',
    to_activate: '待激活',
    activate: '激活',
    active: '活跃',
    block: '锁定',
    unlocked: '已解锁',
    unloaded: '已卸载',
    fileType: '文件类型',
    yes: '是',
    no: '否',
    lock: '锁定',
    what: '吗',
    demand: '要',
    bit: '位',
    most: '最多',
    terminalAddress:"终端地址",
    accessApp:"访问应用",
    integer: '正整数',
    positive: '正数',
    be: '为',
    must: '必须',
    benull: '为空',
    cannot: '不能',
    params: '参数',
    threshold: '阈值',
    units: '单位',
    strategys: '策略',
    low: '低',
    middle: '中',
    high: '高',
    grade: '等级',
    alarm: '告警',
    systemRunTime: '运行时长',
    days: '天',
    months: '月',
    month: '个月',
    years: '年',
    lately: '最近',
    guidemap: '导览图',
    scorefilter: '综合筛选',
    countfilter: '出现次数筛选',
    rcountfilter: '度中心性筛选',
    unfilter: '不筛选',
    norm: '准则',
    filtrate: '筛选',
    layer: '层数',
    query: '查询',
    outbound: '出向',
    inbound: '入向',
    bothway: '双向',
    direction: '方向',
    relevance: '关联',
    ceiling: '上限',
    node: '节点',
    sw: '开关',
    highlight: '高亮',
    dynamic: '动态',
    effect: '效果',
    on: '开启',
    off: '关闭',
    force: '力导图',
    annular: '环形',
    layout: '布局',
    normal: '正常',
    abnormal: '异常',
    start: '开始',
    end: '结束',
    date: '日期',
    append: '添加',
    agg: '聚合',
    aggregation: '聚合',
    available: '可用的',
    base: '基本',
    bucket: '维度',
    buckets: '维度',
    button: '按钮',
    bottom: '底部',
    cancels: '取 消',
    chart: '图表',
    chinese: '中文',
    close: '关闭',
    collapse: '折叠',
    color: '颜色',
    config: '配置',
    configuration: '配置',
    custom: '自定义',
    data: '数据',
    delete: '删除',
    rechristen: '重命名',
    description: '描述',
    format: '格式',
    formatting: '格式化',
    func: '函数',
    disable: '禁用',
    enable: '启用',
    english: '英文',
    empty: '空',
    press: '按',
    esc: 'Esc',
    expand: '展开',
    from: '从',
    please: '请',
    filed: '字段',
    hide: '隐藏',
    label: '标签',
    language: '语言',
    left: '左侧',
    load: '加载',
    loading: '加载中',
    logins: '登录',
    logout: '登出',
    manage: '管理',
    management: '管理',
    metric: '指标',
    metrics: '指标',
    module: '模块',
    move: '移动',
    moveTo: '移动至',
    names: '名称',
    adminRoleLevel: '层级',
    roleLevel: '管理员角色层级',
    new: '新建',
    none: '无',
    ok: '确 定',
    script: '脚本',
    option: '选项',
    panel: '面板',
    panels: '面板',
    group: '分组',
    password: '密码',
    remove: '移除',
    reset: '重置',
    again: '重新',
    change: '更换',
    result: '结果',
    return: '返回',
    right: '右侧',
    run: '运行',
    save: '保存',
    select: '选择',
    selected: '已选择',
    setting: '设置',
    settings: '设置',
    show: '显示',
    source: '源',
    switch: '切换',
    switchLanguage: '切换语言',
    system: '系统',
    to: '至',
    top: '顶部',
    user: '用户',
    users: '用户',
    username: '用户名',
    server: '服务器',
    error: '错误',
    success: '成功',
    failed: '失败',
    batch: '批量',
    authorization_code: "授权码",
    period_of_validity: "有效期",
    basic: '基础',
    information: '信息',
    info: '消息',
    table: '表格',
    pie: '饼图',
    line: '折线图',
    area: '面积图',
    bar: '柱状图',
    heatmap: '日期热力图',
    map: '地图',
    markdown: '注释',
    stylesheet: '样式',
    week: '星期',
    day: '天',
    daily: '天',
    hours: '小时',
    hourly: '小时',
    minutes: '分钟',
    minute: '分钟',
    seconds: '秒',
    second: '秒',
    range: '范围',
    command_control: '指令管控',
    enter_rules: '请填写流量规则',
    hide_app_in_portal: '门户隐藏该应用',
    enabled_app_not_show: '开启后该应用不在门户列表页面展示',
    allow_self: '允许自助申请',
    not_auth_warning: '访问未授权应用告警提示',
    Auth_password: '认证密码',
    refresh: '刷新',
    auto: '自动',
    filter: '过滤',
    exit: '退出',
    default: '默认',
    instance: '实例',
    fullscreen: '全屏',
    warning: '警告',
    other: '其它',
    incomplete: '不完整',
    theresno: '没有',
    datasource: '数据源',
    isnot: '是否',
    prompt: '提示',
    visual: '可视化',
    list: '列表',
    input: '输入',
    keyword: '关键字',
    existing: '已存在',
    existings: '已有',
    noExisting: '不存在',
    timestamp: '时间戳',
    alias: '别名',
    originalTable: '原始表格',
    or: '或',
    the: '的',
    this: '此',
    interval: '间隔',

    sortord: '排序方式',
    records: '记录',
    num: '数',
    sortOfDesc: '降序',
    sortOfAsc: '升序',
    legend: '图例',
    evaluate: '评估',
    FilterType: '筛选类型',
    AuditConfiguration: '审计配置',
    auditStrategie: '审计策略',
    mode: "方式",
    allSee:"全员可见",
    term: '检索词',
    terminalAddress:"终端地址",
    count: '次数',
    liveness: '活跃度',
    listTerms: '检索词列表',
    downloadfilelist: '下载文件列表',
    subjectList: '关注学科列表',
    usingTerminalTypes: '使用终端类型',
    filename: '文件名称',
    downloadcount: '下载次数',
    immediate_auth: '立即认证',
    auth_by_phone: '通过"短信验证"',
    auth_by_email: '通过"邮箱验证"',
    please_input_binded_phone: '请输入绑定手机',
    please_input_binded_email: '请输入绑定邮箱',
    auth_success_tip: '二次认证成功，等待跳转...',
    resetPass_success_tip: '账号密码修改成功，请重新登录',
    login_direct: '直接登录',
    jigsaw_slide_tip: '向右拖动滑块填充拼图',
    input_code: '输入验证码',
    click_to_get: '点击获取',
    resend_seconds: '秒后重发',
    backto_reset_type: '返回重置方式',
    auth_code_ple: "请输入验证码",
    nextStep: '下一步',
    jigsaw_tip: "请完成安全验证",
    jigsaw_success_tip: "验证成功",
    guide: {
        modelTitle: '你还没有可供展示的模块',
        clicks: '你可以点击',
        modelSubTitle: {
            t2: '添加或显示模块',
            t3: '或者点击顶部下拉菜单中的可视化配置'
        },
        panelTitle: '没有可展示的面板',
        panelSubTitle: {
            t3: '或者切换顶部模块查看相关面板'
        },
        chartTitle: '没有可展示的图表',
        chartSubTitle: {
            t1: '导航上的',
            t2: '为该面板添加图表',
            t3: '创建可用图表'
        }
    },
    helpCenter: '帮助中心',
    pleaseInput: '请输入',
    account: '账号',
    Remember: '记住',
    forgetPassword: '忘记密码',
    submit: '提交',
    loading: '拼命加载中',
    accountOrPassError: '账号或密码错误',
    loginError: '登录出错',
    loginAgain: '请重新登录',
    manageAccount: '管理您的账号',
    onlineTime: '当前在线',
    lastLoginTime: '上次登录',
    userInfos: '用户信息',
    headPortrait: '头像',
    name: '姓名',
    bind: '绑定',
    unbind: '解绑',
    current_alarm: '当前告警',
    alarm_time: '告警时间',
    alarm_rule: '告警规则',
    history_alarm: '历史告警',
    config_type: '配置类型',
    email: '邮箱',
    originPassword: '原密码',
    newPassword: '新密码',
    confirmPassword: '确认密码',
    verificationCode: '验证码',
    get: '获取',
    newAndOldPassword: '新密码不能与原密码相同!',
    passwordNotSame: '两次输入密码不一致!',
    InvalidFormat: '格式不合法',
    updateSuccess: '密码修改成功',
    modify_successfully: '修改成功',
    enterToSearch: '输入账号进行搜索',
    pleaseSelect: '请选择',
    userInfo: {
        updateName: "修改姓名",
        updatePassword: "修改密码",
        updateAccount: "修改账号",
        bindPhone: "绑定手机",
        unbindPhone: "解绑手机",
        bindEmail: "绑定邮箱",
        unbindEmail: "解绑邮箱",
    },
    log: log_zh,
    analysis: {
        trackType: '轨迹类型',
        AccessPath: '访问轨迹',
        warningRecord: '告警记录',
        loginBehavior: '登录行为',
        downloadBehavior: '下载行为',
        timeOfDuration: '持续时间',
        locationMap: '用户到访位置图'
    },
    beforeOrAfterSpaces: '请勿输入前导或后导空格',
    welcomeTips: '欢迎使用易安联数据可视化产品',
    scriptRegExp: 'script必须是至少两位字符并且由英文或数字开头的条件语句',
    inputSourceTips: '您可以在您输入的前缀后面加*进行过滤，不允许使用空格和特殊字符 , /, ?, ", &lt;, &gt;, |！。',
    souceFullNameTips: '--- 请输入字段全名,时间可以用星号*代替（例如：res-nh-filebeat-2018-10-23，输入：res-nh-filebeat-*）',
    chartDeleteTips: '面板保存前，您仍可以通过【取消】操作，恢复暂时被删除的图表, 确定删除？',
    panelCancelTips: '此操作会将数据恢复到上次保存后的状态，确定取消吗？',

    slogan: "云应用访问安全领导者",
    app_name: "安枢统一控制中心",
    copy_right: "Copyright© 2005-2021 江苏易安联网络技术有限公司 苏ICP备14042977号",
    instructions: "说明",
    password_length: "密码长度{number}~32位",
    password_rules: "密码以字母、数字或符号（除空格）组成",
    password_rules_strict: "密码必须包括字母、数字和符号（除空格）",
    password_same: "密码不能跟上次设置的密码相同",
    i18n: true,
    enlink: "江苏易安联",
    please_input: "请输入",
    please_input_unitTime: "请输入单位时间",
    please_input_threshold: "请输入阈值",
    confirm: "确定",
    next: "下一步",
    chinese: "简体中文",
    english: "English",
    add: "新增",
    edit: "编辑",
    modification: "修改",
    auto_play: "自动播放",
    update: "更新",
    finish: "完成",
    add_push: "添加",
    sso_config: "SSO配置",
    config: "配置",
    synchronization: "同步",
    system_config: "引用系统配置",
    freeze: "冻结",
    delete_import: "删除导入数据",
    cancel: "取消",
    off_line: "下线",
    on_line: "上线",
    auth: "授权",
    authByLevel: "分级授权",
    import_account: "导入账号",
    export_account: "导出账号",
    import_device: '导入设备',
    export_device: '导出设备',
    export_app: "导出应用",
    import_web: "web应用导入",
    import_app: "应用导入",
    app_derivation: "应用导出",
    delock: "解锁",
    on: "启动",
    off: "停止",
    sort: "排序",
    addApp:'新增应用',
    search: "搜索",
    search_tips: "请输入关键字搜索",
    app_name: "统一控制中心",
    reset: "重置密码",
    resetPassword: "重置密码",
    emoji_error: "不支持emoji表情符号",
    hasName_error: "不得包含账号的完整字符串",
    keyboard_error: "避免键盘排序密码",
    protocol_url: "格式不合法(须包换协议http、https、ftp)",
    to_zh: "切换到中文",
    to_en: "切换到英文",
    export_records: "导出记录",
    finish_condition: "完成情况",
    permissions: "权限",
    more_group: "更多组",
    import_success: "导入成功",
    import_fail: "导入失败",
    opt_complete: "操作完成，导入结果请查看导入状态",
    export: "导出",
    import: "导入",
    import_type: "{type}导入",
    export_type: "{type}导出",
    unread: "未读",
    read: "已读",
    no_data: "已经没有更多数据了",
    yes: "是",
    no: "否",
    platform: "平台",
    equipment: "设备",
    phoneNum: "手机号",
    lose_efficacy: "失效",
    create: "创建",
    create_at: "创建时间",
    client_id: "客户端ID",
    client_key: "客户端密钥",
    refresh_success: "刷新成功",
    update_at: "修改时间",
    check_details: "查看详情",
    fault_tolerance: "容错次数",
    fault_tolerance_period: "时段累计容错次数",
    input_fault_tolerance: "请输入容错次数",
    input_fault_period: "请输入累计时段",
    add_success: "新增成功",
    basic_config: "基础配置",
    basic_attribute: "基础属性",
    advanced_config: "高级配置",
    add_copy_success: "复制-新增成功",
    enable_success: "启用成功",
    disable_success: "禁用成功",
    open_success: "开启成功",
    close_success: "关闭成功",
    update_success: "更新成功",
    copy_success: "复制成功",
    test_success: "账号测试成功",
    successful_test: "测试成功",
    test_error: "账号测试有误,请重试",
    testname_password_none: "测试名称和密码不能为空!",
    group: "组",
    user_group: "用户组",
    user_group_choose: "请选择用户组",
    app_group: "应用分组",
    user_group_choose_tips: "请选择用户组到右侧后再操作",
    user_group_config_tips: "一次只能配置一个用户组",
    del_tip: "删除后，不可恢复，确认删除吗",
    strategy_del_tip: "删除后【数据】和【策略】都会被删除,确认删除吗",
    drag_file: "将文件拖到此处，或",
    click_upload: "点击上传",
    upload_logo: "上传图标",
    upload_type: "只能上传{type1}或{type2}格式的文件",
    upload_type3: "只能上传{type1}、{type2}或{type3}格式的文件",
    upload_type2: "只能上传{type}格式的文件",
    download_tel: "模板下载",
    upload_serve: "上传到服务器",
    max_file: "文件格式必须少于{number}MB!",
    upload_success: "上传成功！",
    waitUpload: "请等待上传成功",
    upload_failed: "上传失败，请稍后重试！",
    item: "项",
    download_check_later: "正在下载，请稍后查看...",
    search_name: "请输入姓名或账号搜索",
    unable_recover: "后无法恢复，确定继续?",
    start: "开始",
    end: "结束",
    strategy_enable_status: "策略启用状态",
    chain_strategy: "策略链",
    static_strategy_chain: "静态策略链",
    access_security_policy: "访问安全策略",
    perform_action: "执行动作",
    allow_access: "允许访问",
    block_access: "禁止访问",
    time: "时间",
    network_strategy: "内网策略",
    terminal_strategy: "终端策略",
    terminal_config: "终端配置",
    config_item: "配置项",
    port: "端口",
    not_this_port: "非此端口",
    not_this_host: "非此host",
    is_save_cap: "是否保存Cap格式",
    userName: "用户名",
    del_tips: "请勾选需要删除的数据！",
    opration_tips: "请勾选需要{desc}的数据！",
    opration_tips_enable: "请勾选需要启用的数据！",
    opration_tips_disabled: "请勾选需要禁用的数据！",
    user_opration_tips: "用户已处于{desc}状态！",
    app_opration_tips: "应用已处于{desc}状态！",
    app_disable_tips: "应用已处于禁用状态！",
    app_enable_tips: "应用已处于启用状态！",
    choose_send_tips: "请勾选需要发送的数据！",
    del_confirm_tips: "确定删除所选数据吗?",
    del_confirm: "确定删除该条数据吗?",
    del_success: "删除成功",
    app_choose_tips: "该应用已经被选择了！",
    app_no_dis: "当前未分配应用，请先选择！",
    app_dis_success: "应用分配成功！",
    app: "应用",
    edit_dis: "编辑分配",
    icon: "图标",
    edit_app:'编辑应用',
    diy_icon: "自定义图标",
    choose_icon: "图标选择",
    state: "状态",
    input_des_tips: "请输入描述信息",
    app_dis: "应用分配",
    app_add_tips: "请输入应用名称并选择添加……",
    app_add_tip: "请输入应用名称",
    data_loading: "数据加载中",
    choosed: "已选择",
    address: "地址",
    confirm_del: "确定删除吗",
    mores: "更多操作",
    search_name_tip: "请输入名称搜索",
    input_name_tips: "请输入名称",
    route: "路由",
    agreement: "协议",
    choose_agre: "请选择协议",
    network: "目的网段",
    source_add: "源地址",
    gateway_add: "网关地址",
    role: "角色",
    roleName: "角色名称",
    choose_role_operation: "请选择角色到右侧后再操作",
    increase: "增加",
    operations: "操作",
    refresh_key: "刷新密钥",
    allocate_time: "分配时间",
    allocate_user_group: "分配用户组",
    confirm_del_tip: "确认删除吗",
    add_role: "增加角色",
    instructions: "说明",
    password_length: "密码长度{number}~32位",
    password_rules: "密码以字母、数字或符号（除空格）组成",
    password_rules_strict: "密码必须包括字母、数字和符号（除空格）",
    password_same: "密码不能跟上次设置的密码相同",
    resets: "重置",
    read_only_tip: "仅支持查看，无法操作",
    read_only: "只读",
    edit_success: "编辑成功",
    clear_cache_success: "清除缓存成功",
    edit_failure: "编辑失败",
    config_effect: "配置将在30秒内生效",
    effective_scope: "生效范围",
    interface: "接口",
    apps_name: "应用分组名称",
    mac: "MAC 地址",
    enable_state: "启用状态",
    pullback: "收起",
    edit_interface: "编辑接口",
    edit_interface_tip: "请输入接口名称",
    input_ip_tip: "请输入IP",
    ip_illegal: "IP不合法，请输入有效IP",
    mac_input_tip: "请输入MAC地址",
    all_read: "全部读取",
    batct_read: "批量读取",
    add_app_btn: "添加应用",
    add_app_group_btn: "添加应用分组",
    sort_app_btn: "应用排序",
    sort_app_group_btn: "分组排序",
    task_list: "任务列表",
    progress_total: "进行中{doingTotal}个",
    total: "共 { total } 条",
    no_permission: "您无此功能操作权限",
    download: "下载",
    view: "查看",
    execution: "执行中",
    ready_perform: "准备执行",
    execute_success: "执行成功",
    execute_failed: "执行失败",
    search_usergroup_tips: "请输入用户组名搜索",
    search_group_tips: "请输入应用分组名搜索",
    tips: "提示：",
    logout: "退出",
    log_off: "注销",
    offline: "离线",
    online: "在线",
    test: "测试",
    test_required: "测试账号必填项",
    connection: "连接中",
    ip: "IP(IP/掩码)",
    success: "成功",
    fail: "失败",
    opt_success: "操作成功",
    sync_success: "同步成功",
    opt_error: "操作失败,请重试",
    pbl_success: "发布成功",
    pbl_error: "发布失败,请重试",
    upload: "上传",
    send: "发送",
    temporary: "临时",
    sendAll: "全部发送",
    choose_file: "请选择文件",
    user: "用户",
    choose_user: "请选择用户",
    choose_tip: "请选择",
    type: "类型",
    copy: "复制",
    copyLicense: "复制本行License",
    title: "标题",
    content: "内容",
    ready: "读",
    write: "写",
    input_rate: "输入速率",
    output_rate: "输出速率",
    choose: "选择",
    synchronous: "同步中",
    times: "次数",
    web_app: "Web应用",
    is: "正在{msg}模块，请稍候...",
    nat: "nat",
    alertLevel: "告警等级",
    high: "高",
    middle: "中",
    low: "低",
    select_alertlevel: "请选择告警等级",
    isNat: "是否NAT",
    vpn: "虚拟IP",
    auto_allocation: "自动分配",
    vpn_tips: "请输入虚拟IP",
    IPV4: "IPv4",
    IPV6: "IPv6",
    bestSizeforicon: "图标最佳尺寸为256*256px",
    appMaxNum: "最大应用数",
    add_alarmConf: "新增告警配置",
    edit_alarmConf: "编辑告警配置",
    userMaxNum: "最大用户数",
    max_conf: "最大支持配置",
    onlineUserMaxNum: "最大在线用户数",
    adminMaxNum: "最大管理员数",
    batchAdd: "批量新增",
    maxRangeTip: "最大在线用户数、最大管理员数以及应用最大用户数不能超过最大用户数",
    moreThanMaxUser: "最大用户数超过可配置数",
    moreThanOnlineMaxUser: "最大在线用户数超过可配置数",
    moreThanAdminMaxUser: "最大管理员数超过可配置数",
    lessThanMinUser: "最小用户数小于已存在数",
    lessThanOnlineMinUser: "最小在线用户数小于已存在数",
    lessThanAdminMinUser: "最小管理员数小于已存在数",
    onlineUserMaxNumMoreThanMaxUser: "最大在线用户数超过了最大用户数",
    AdminUserMaxNumMoreThanMaxUser: "最大管理员数超过了最大用户数",
    AppMaxNumMoreThanMaxUser: "应用最大数超过了最大用户数",
    morePhoneAndEmall: "支持手机号和邮箱的消息接收方式，多个临时接收人以逗号隔开",
    diyMessageRecipient: "自定义的消息接收人（如不在系统用户中的三方运维人员）。",
    admin: "管理员",
    account: "账号",
    SMS_unsent_details: "短信未发送详情",
    email_unsent_details: "邮箱未发送详情",
    load_more_datas: "加载更多",
    detail_page: "详情页",
    database: "数据库",
    app_group_tree: "应用分组树",
    web_proxy: "Web应用",
    forward_proxy: "Web应用",
    reverse_proxy: "反向代理",
    terminal_app: "运维终端",
    network_layer: "隧道应用",
    app_config: "应用配置",
    clear_alarm: "消除告警",
    backEnd_server_URL: "后端服务器URL",
    associated_domain_probing: "关联域名探测",
    Domain_detection: "域名探测",
    enter_domainOrIP_condition: "请输入域名或ip(域名仅支持SSH、Telnet)",
    mini_program: "小程序",
    data_center: "数据中心",
    unity: "合一",
    China: "中国",
    American: "美国",
    France: "法国",
    England: "英国",
    Korea: "韩国",
    Japan: "日本",
    German: "德国",
    Singapore: "新加坡",
    Canada: "加拿大",
    Italy: "意大利",
    defaultIcon: "默",
    monitoring: "监控",
    regExp: "正则表达式",
    directive: "指令",
    addDirective: "新增指令",
    directiveStratigy: "指令策略",
    screenRecording: "录屏",
    source: "来源",
    RemoteUnloading: "远程卸载",
    unloadCode: "卸载码",
    remote_connect: "远程连接",
    connect_protocol: "连接协议",
    turn_on_time: "接入时间",
    playback: "回放",
    link: "连接",
    approverRole: "审批角色",
    disconnect: "断开",
    access_time: "接入时长",
    delete_all_tips: "请选择需要删除的数据",
    disconnect_success: "断开成功",
    enable_ldap: "确定启用该认证吗?",
    disable_ldap: "确定禁用该认证吗?",
    unfinished: "未完成",
    organization: "组织架构",
    monitoring_management: "监控管理",
    organization_group: "部门/分组",
    alls: "全部",
    phone: "手机",
    select_date: "选择日期",
    file_size_limit: "文件大小必须少于{size}",
    file_size: '文件大小',
    cancel_del: '已取消删除',
    back_up_page: "返回上一页",
    serve: "服务",
    rely: "依赖",
    resource: "资源",
    control: "控制",
    safetySpace: "安全空间",
    structure: "组织架构",
    credit: "信用等级",
    maxselect: "依赖资源最多选择{number}个",
    browser: "浏览器",
    gateways: "网关",
    file: "文件",
    legal: "合法的",
    appGroup: "应用组",
    IKnow: "我知道了",
    channelPath: "所属路径",
    verify: "校验",
    sub_account: "子账户",
    auth_fit: "认证适配",
    assignment: "赋值",
    decision: "决策",
    subpolicy: "执行子策略",
    discharged: "放行",
    stop: "阻止",
    forbid: "禁止",
    allot: "分配",
    key: "键",
    bits: "位数",
    value: "值",
    again_auth: "重新认证",
    second_auth: "二次认证",
    network_card: '网卡',
    last_time: '最近一次',
    device_name: '设备名',
    feature_code: '设备特征码',
    operate_system: '操作系统',
    client: '客户端',
    client_type: '客户端版本',
    all_time_high:'历史高点',
    registered_equipments:'注册设备',
    publish_all:'发布总数',
    app_upLimit:'应用上限',
    enable_account:'启用数量',
    disposal_account:'处置次数',
    strategy_account:'策略总数',
    online_gateway:'在线网关',
    offline_gateway:'离线网关',
    online_users: '在线用户',
    all_time_high_users: '历史高点用户',
    online_equipments: '在线设备',
    publish_app: '发布应用',
    system_server: '系统服务器',
    controller: '控制器',
    appGateway: '应用网关',
    accessApp:"访问应用",
    stand: '台',
    resource_pool: '资源池',
    onlineUsers_remark: '处于登录状态的账号为一个在线用户',
    allTimeHigh_remark: '从系统运行至今，同时在线的最多用户数',
    onlineEquipments_remark: '处于登录状态的设备为一个在线设备',
    daily_active_users: '日活跃用户',
    daily_online_equipments: '日在线设备',
    numbers: '数量',
    length_err:'长度不可超过120个字符',
    app_vivisted_rank: '应用访问量排名',
    real_time_flow: '实时流量',
    real_time_online_user: '实时在线用户',
    in_recent_sevendays: '最近7天',
    in_recent_15days: '最近15天',
    in_recent_30days: '最近30天',
    application_group:'应用组',
    sync:'同步',
    sync_success:'同步成功',
    secondModuleName: '二级模块名',
    deviceIp: '设备IP',
    device: '设备',
    org:'组织',
    upstream_addr: '上游地址',
    useragent: '用户代理信息',
    setAdmin: '设置管理员',
    setAdminSuccess: '设置管理员成功',
    preview: "预览",
    sendTime: '发送时间',
    authorization_code_type: '授权码类型',
    authorization_code_validity: '授权码有效期',
    send_mode: '发送方式',
    effective_user: '生效用户',
    noMoreThan: '最大不超过{value}个中文字符',
    rootGroup: '根',
    login: login_zh,
    home: home_zh,
    form_error: form_error_zh,
    system: system_zh,
    users: users_zh,
    gateway: gateway_zh,
    approve: approve_zh,
    release: release_zh,
    form: form_zh,
    network: network_zh,
    creditLev: creditLev_zh,
    admin: admin_zh,
    message: message_zh,
    operation: operation_zh,
    secure_policy: policy_zh,
    strategy: strategy_zh,
    trust_auth: trust_auth_zh,
    apps: app_zh,
    privacy: privacy_zh,
    configs: configs_zh,
    linkage: linkage_zh,
    alarms: alarm_zh,
    space: space_zh,
    operationTip: operationTip_zh,
    deviceMng: device_zh,
    tagMng: tagMng_zh,
    notice: notice_zh,
    messageMng: messageMng_zh,
    loginDiy: loginDiy_zh,
    deviceRegistration: deviceRegistration_zh,
    packageMng: packageMng_zh,
    distributeMng: distributeMng_zh,
    userManage: userManage_zh,
    appMng: appMng_zh,
    operateMng: operateMng_zh,
    routeName: routeName_zh,
};