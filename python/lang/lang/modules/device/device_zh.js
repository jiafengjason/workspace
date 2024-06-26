/*
 * @Author:  liff liff@enlink.cn
 * @Date: 2023-04-04 09:35:33
 * @LastEditors: liff liff@enlink.cn
 * @LastEditTime: 2023-06-27 11:51:41
 * @FilePath: \ensbrain-web-admin\src\i18n\lang\modules\device\device_zh.js
 * @Description: 
 * 
 * Copyright (c) 2017-2023 . Jiangsu Enlink Network Technology Co.,Ltd., All Rights Reserved. 
 */
export const device_zh = {
  base: {
    terminalManagement: '终端管理',
    tagMng: '标签管理',
    importExport: '导入/导出',
    to: '至',
    close: '关闭',
    registered: '已注册',
    unregistered: '已注销',
    uninstalled: '已卸载',
    logout: '登出',
    moveTo: '移动至',
  },
  register: {
    unlock: '解锁',
    platformCount: '平台类型总数',
    osCount: '系统版本总数',
    clientCount: '客户端版本总数',
    statisticalAnalysis: '统计分析',
    platformDistribution: '平台类型分布',
    systemDistribution: '系统版本分布',
    clientDistribution: '客户端版本分布',
    importDevice: '导入设备',
    exportDevice: '导出设备',
    deleteExplainTip: '一旦删除，该设备将处于注销状态，可在"已注销设备"查看，被注销的设备无法接入企业网络，无法访问资源，用户需要重新注册才能获得访问权限。',
    deleteDevice: '删除设备',
    deleteTip: '你确定要删除该设备吗？',
    noData: '暂无数据',
    searchTip: '使用人、登录ip、设备名称',
    searchTipUnregisteredTip: '登录ip、设备名称、操作系统、客户端版本',
    notActiveForbiddenTip: '待激活设备不能进行此操作！',
    lockForbiddenTip: '已锁定设备不能进行此操作！',
    unlockForbiddenTip: '已解锁设备不能进行此操作！',
    selectDataTip: '请选择至少一条数据！',
    lockDeviceTip: '该操作将锁定选中的所有设备，请谨慎操作！',
    unlockDeviceTip: '该操作将解锁选中的所有设备，请谨慎操作！',
    offlineForbiddenTip: '不在线设备不能进行此操作！',
    logoutTip: '所有使用选中设备的用户将强制登出，请谨慎操作！',
    noLabelTip: '选中项没有关联标签！',
    tableUnlockTip: '该操作将解锁操作的设备，请谨慎操作！',
    tableLockTip: '该操作将锁定操作的设备，请谨慎操作！',
    tableLogoutTip: '该设备的用户将强制登出，请谨慎操作！',
    loseEfficacy: '失效',
    copyTip: '卸载码已复制到粘贴板',
    cannotCopyTip: '当前卸载码不支持复制黏贴',
    unknown: '未知人',
    macDevice: '的Mac',
    computerDevice: '的电脑',
    androidDevice: '的安卓手机',
    iphoneDevice: '的iPhone',
    ipadDevice: '的iPad',
    phoneDevice: '的手机',
    safe: '安全',
    lowRisk: '低风险',
    mediumRisk: '中风险',
    highRisk: '高风险',
    importDevices: '设备导入',
    exportDevices: '设备导出',
    exportDeviceTip: '请选择要导出的信息',
    historyRecords: '历史记录',
    codeContent: '设备{name}的卸载码如下',
    editDevices: '编辑设备',
    MaximumNumberOfBoundUsers:'最大绑定用户数',
    MaximumNumberOfBoundUsersTip:"一台设备默认绑定用户数为1人，超出范围的用户无法登录该设备，管理员可手动更改最大绑定用户数。",
    editMaxSuccess:"编辑最大绑定用户数成功!",
    maxUserRule:"最大绑定用户数不能为空",
    unloadSure:"确定要卸载该设备吗？",
    unloadTip:"（注：卸载后，可在'已卸载'查看该设备）",
    SilentlyUninstall:"静默卸载",
    AuthorizationUninstall:"授权卸载",
    noEmployeeSureUnload:"（无需员工确认，后台自动强制卸载）",
    employeeSureUnload:"（需要员工确认，允许后才可卸载）",
    moveDevice: '移动设备',
    moveDevicesSuccess: '移动成功！',
    linkDevices: '关联设备',
    deviceStatus:"设备状态",
    lockOperationTip: '该操作将锁定选中组下所有设备，请谨慎操作！',
    unlockOperationTip: '该操作将解锁选中组下所有设备，请谨慎操作！',
    logoutOperationTip: '所有使用选中组下设备的用户将强制登出，请谨慎操作！',
    deleteOperationTip: '该操作将删除选中组下所有设备，请谨慎操作！',
    lockOperationSuccess: '锁定成功！',
    unlockOperationSuccess: '解锁成功！',
    logoutOperationSuccess: '登出成功！',
    deleteOperationSuccess: '删除成功！',
    batchLock: '批量锁定设备',
    batchUnLock: '批量解锁设备',
    batchOffline: '批量登出设备',
    unLock: '解锁设备',
    lock: '锁定设备',
    offline: '登出设备',
    chartNum: '台',
    eventCountNum: '{number} 件',
    softwareCountNum: '{number} 个',
  },
  table: {
    lastLoginIP: '最近登录IP',
    cancelTime: '注销时间',
    device: '设备',
    deviceGroupName: '组织架构',
    registerUser: '使用人',
    userList: '绑定用户',
    deviceScore: '风险等级',
    deviceIp: '登录位置',
    lastLoginTime: '最近登录时间',
    securityEvent: '安全事件',
    macAddress: 'MAC 地址',
    softwareNum: '软件数量',
    systemInfo: '操作系统',
    terminalVersion: '客户端版本',
    tagList: '标签',
    ownDevice: "的设备",
  },
  netcellDevice:'网元设备',
  ctrlPool:'控制器池',
  findGateway:'网关发现',
  gatewayDetail:'网关详情',
  registerType:'注册类型',
  gatewayAuth:'网关授权',
  ctrlList:'控制器列表',
  deleteCtrlPool:'删除控制器池',
  deleteCtrl:'删除控制器',
  deleteCtrlConfirm:'确认删除该控制器？',
  deleteCtrlPoolConfirm:'删除控制器池将删除当前控制器池下所有控制器，请谨慎操作！',
  masterSlave:'主备',
  cluster:'集群',
  singleHost:'单机',
  editController:'编辑控制器',
  editControllerPool:'编辑控制器池',
  addController:'新增控制器',
  addControllerPool:'新增控制器池',
  controllerName:'控制器名称',
  adminPort:'管理端监听端口',
  clientPort:'客户端监听端口',
  portConfig:'出口配置',
  addPortConfig:'新增出口配置',
  editPortConfig:'编辑出口配置',
  accessGatewayPool:'接入网关池',
  adminInPort:'管理端入口',
  clientInPort:'客户端入口',
  deleteConfirm:'删除操作不可恢复, 是否继续?',
  accessGatewayPoolIdDuplicate:'接入网关池id重复',
  accessGatewayPoolDuplicate:'接入网关池重复',
  outConfigNotEmpty:'出口配置不得为空',
  servicePort:'服务端口',
  startCommand:'启动命令',
  stopCommand:'停止命令',
  useKillCommand:'若为空，将使用系统Kill命令清除服务',
  controllerAddress:'控制器地址',
  gatewaySyncAddress:'网关同步设备特征码以及授权码的地址',
  internetDomain:'公网域名',
  ipSegment:'IP段',
  pleaseInputIpSegment:'请输入IP段',
  gatewayAuthTips:'无人为授权关系的网关所有用户皆可使用，一旦网关与角色绑定，只有拥有该角色的用户方可使用这些网关。',
  inputPositiveInteger:'请输入1-100正整数',
  formatError:'格式错误',
  subIPMaxInput:'子IP地址最大输入条数为',
  item:'条',
  notEmpty:'不能为空',
  notMoreThan32Chars:'不能超过32个字符',
  onlyInput8Chars:'只能输入8个字符,字母数字皆可',
  userAuthControlTips:'解决应用权限管控问题，对于授权的应用进行代理转发，非授权应用进行拦截，该模式由于URL子链较难穷举可能有兼容性问题',
  appAccessedTips:'解决应用访问连通性问题，所有代理到网关的web业务流量直接进行代理转发',
  gateway_tunnel_strategys_tips:'未开启时，网关放行所有流量；开启后，白名单列表（授权的应用）中的应用放行，黑名单列表（未授权的应用）中的应用拦截，其他应用执行默认动作（阻止/放行）',
  gatewayPoolAuthTips:'无人为授权关系的网关池所有用户皆可使用，一旦网关池与角色绑定，只有拥有该角色的用户方可使用这些网关池。',
  VirIpType:'虚IP选择',
  gatewayState:'网关状态',
  publish_secret_certificate:'发布商密证书',
  publish_national_secret_certificate:'发布国密证书',
  last_login_ip:'最近一次登录IP地址',
  current_used_license:'当前网关使用证书',
  main_name:'主体名',
  serial_number:'序列号',
  license_type:'证书类型',
  expire_date:'截止日期',
  sure_to_offline_space:'确定下线空间吗？',
  sure_to_enable_space:'确定启用空间吗？',
  sure_to_offline_gateway:'确定下线该网关吗？',
  sure_to_online_gateway:'确定上线该网关吗？',
  notice_gateway_online:'已通知网关上线，请稍后查看其状态',
  config_start_command:'请配置启动命令',
  notice_gateway:'已通知网关，请稍后查看其状态',
  offline_gateway:'下线网关',
  online_gateway:'上线网关',
  del_gateway:'删除网关',
  delGatewayPool: '删除网关池',
  baseDetail: {
    title: '基础信息',
    device_information: '设备信息',
    device_IP: '设备 IP',
    computing_group: '计算机组',
    is_enable_remote_desktop: '是否启用远程桌面',
    location_equipment: '设备所在地',
    final_blocking_time: '最后阻断时间',
    poweron_state: '开机状态',
    turn_on: '开机',
    shut_down: '关机',
    CPU_model: 'CPU 型号',
    hard_disk: '硬盘',
    motherboard: '主板',
    device_MAC_address: '设备MAC地址',
    multiple_operating_systems: '是否多操作系统',
    system_serial_number: '系统序列号',
    virtual_machine_or_not: '是否虚拟机',
    shared_information: '共享信息',
    Hardware_change_info: '硬件变更信息',
    system_install_record: '操作系统安装记录',
    system_users_acconut_info: '当前操作系统用户账号信息',
    registerUser: '注册人',
    registerTime: '注册时间',
    registerMethod: '注册方式',
    firstLoginTime: '首次登录时间',
    validTime: '有效期',
    perpetual: '永久有效',
    idleTime: '闲置时长',
    deviceName: '设备名称',
    terminalVersion: '客户端版本',
    featureCode: '硬件特征码',
    manuFacturer: '制造商',
    deviceModel: '型号',
    serialNumber: '序列号',
    osType: '平台类型',
    systemInfo: '系统版本',
    u: '未',
    networkInfo: '网络信息',
    adapterName: '网卡名称',
    macAddr: 'MAC地址',
    ipv4Addr: 'IPv4地址',
    ipv6Addr: 'IPv6地址',
    defaultGateway: '默认网关',
    enableState: '开启状态',
    upgradeRecord: '升级记录',
    nameAndAccount: '姓名&账号',
    deviceScore: '设备评分',
    deviceGroup: '设备组',
    loginTime: '登录时间',
    loginMethod: '登录方式',
    deviceDetail: '设备详情',
    softwareList: '软件列表',
    serviceList: '服务列表',
    safeEvent: '安全事件',
    usingHistory: '最近使用记录',
    subordinate_group: '隶属组',
    device_type: '设备类型',
    occurrence_time: '发生时间',
    original_configuration: '原配置',
    new_configuration: '新配置',
    logonDomain: '登录域',
    oldVersion: '旧版本',
    afterUpdateVersion: '升级后版本',
    forceUpdate: '是否强制升级',
    updateSuccess: '是否升级成功',
    upgradeTime: '升级时间',
    deviceUUID: '设备UUID',
    deviceGroupPath: '所属设备组',
    deviceMAC: '设备 MAC',
    installedSoftware: '安装的软件',
  },
  safeEvent: {
    riskNum: '{number}个风险',
    searchPlaceholder: '请输入检测对象',
    reportingTime: '上报时间',
    classification: '检测分类',
    entity: '检测对象',
    rule: '规则',
    dangerLevel: '危险等级',
    baseline: '安全基线',
    all: '全部',
    application: '应用检测',
    service: '服务检测',
    port: '端口检测',
    process: '进程检测',
    firewall: '防火墙检测',
    outerDevice: '外设检测',
  },
  serviceList: {
    searchPlaceholder: '请输入服务名称',
    name: '服务名称',
    type: '服务类型',
    description: '描述',
    serviceStatus: '状态',
    fileSystemDriver: '文件系统驱动',
    kernelDriver: '内核级驱动',
    ownProcess: '单独进程服务',
    shareProcess: '共享进程服务',
    interactiveProcess: '交互式服务',
    unknown: '未知',
    running: '服务正在运行',
    stopped: '服务未运行',
    paused: '服务已暂停',
    continuePending: '服务即将继续',
    pausePending: '服务即将暂停',
    startPending: '服务正在启动',
    stopPending: '服务正在停止',
    isStopped: '服务已停止',
    sleep: '服务休眠中',
    zomb: '服务部分已销毁',
    Agents: '代理进程',
    Daemons: '守护进程',
    notRunning: '未运行',
  },
  softwareList: {
    searchPlaceholder: '请输入软件名称',
    installDate: '安装时间',
    name: '软件名称',
    publisher: '发布者',
    version: '版本号',
    processDetail: '进程详情',
    productName: '产品名称',
    process: '进程',
    md5: '哈希值',
    signIssuer: '签名',
    engine_version: '引擎版本',
    virus_library_version: '病毒库版本',
    appSoftware: '应用软件',
    antivirus: '杀毒软件',
  },
  usingHistory: {
    username: '姓名',
    userAccount: '账号',
    createTime: '时间',
    accessMode: '接入方式',
    area: '地区',
    operation: '操作',
  },
  authServer:'认证服务器',
  emailServer:'邮箱服务器',
  messageServer:'短信服务器',
  robotsServer:'机器人服务器',
  otherServer:'其他服务器',
  addNewServer:'添加新服务器',
  third_scan_code:'三方扫码登录配置',
  sim_card_auth:'SIM卡认证',
  feishu_scan:'飞书扫码登录',
  testing:'测试中',
  cas_server:'CAS认证服务器',
  oauth_server:'OAuth认证服务器',
  devicePort:'设备端口',
  public_account_type:'公众号类型',
  wechat_public_account:'微信公众号',
  wechat_scan_tips:'请使用微信扫码关注公司微信公众号后，再扫码右侧验证码',
  auth_code_scan_tips:'请关注公司微信公众号后，再扫码上方授权码',
  callback_domain:'回调域名',
  gen_auth_code:'生成授权码',
  robots_address:'机器人地址',
  secret_key:'加密秘钥',
  delete_server:'删除服务器',
  add_server:'新增服务器',
  local_auth:'本地认证',
  wechat_robots:'企业微信机器人',
  dingding_robots:'钉钉机器人',
  feishu_robots:'飞书机器人',
  wechat:'微信',
  enterpriseWeChat:'企业微信',
  retryCount:'重试次数',
  retryCycle:'重试周期',
  scan_success:'扫码绑定成功！',
  no_permission:'您当前无权限!',
  config_auth_server:'配置认证服务器',
  add_auth_server:'新增认证服务器',
  edit_auth_server:'编辑认证服务器',
  edit_server:'修改服务器',
  opt_complete:'操作完成',
  del_data_tips:'删除导入数据后无法恢复，确定继续?',
  del_confirm:'确定删除该数据吗?',
  server_cas:'CAS服务器',
  server_oauth:'OAuth服务器',
  new_auth_server:'添加认证服务器',
  org_arch:'所属组织架构',
  server_type:'服务器类型',
  server_address:'服务器地址',
  import_state:'导入状态',
  server_sort_tips:'优先级用来控制登录方式顺序,优先级从小到大排列',
  is_disable_cas:'是否要禁用CAS?',
  canceled:'已取消',
  is_disable_oauth:'是否要禁用OAUTH?',
  please_input_test_account:'请输入测试账号',
  contact_secret:'通讯录secret',
  data_sync:'数据同步',
  local_data_to_prevail:'以本地数据为准',
  other_party_data_to_prevail:'以对方数据为准',
  connect_config:'连接配置',
  authName:'认证名称',
  please_input_auth_name:'请输入认证名称',
  please_input_server_address:'请输入服务器地址',
  database_type:'数据库类型',
  database_port:'数据库端口',
  please_input_database_port:'请输入数据库端口',
  database_account:'数据库管理账号',
  please_input_database_account:'请输入数据库管理账号',
  database_password:'数据库管理密码',
  please_input_database_password:'请输入数据管理密码',
  database_name:'数据库名称',
  please_input_database_name:'请输入数据库名称',
  database_tablename:'数据库表名',
  please_input_database_tablename:'请输入数据库表名',
  database_account_field:'账号字段名',
  please_input_account_field:'请输入账号字段名',
  password_field:'密码字段名',
  please_input_database_password_field:'请输入密码字段名',
  encrypt:'加密方式',
  name_field:'姓名字段名',
  please_input_name_field:'请输入姓名字段名',
  phone_field:'手机号字段名',
  please_input_phone_field:'请输入手机号字段名',
  email_field:'邮箱字段名',
  please_input_email_field:'请输入邮箱字段名',
  description_field:'描述字段名',
  please_input_description_field:'请输入描述字段名',
  test_account:'测试账号',
  please_input_test_account:'请输入测试账号',
  test_password:'测试密码',
  please_input_test_password:'请输入密码',
  condition_query:'条件查询',
  condition_query_tips:'满足查询条件的用户方可登录系统。',
  field_name:'字段名',
  select_condition:'选择条件',
  ldap_right:'LDAP权限',
  read_and_write:'读写',
  read_and_write_and_del:'全部(读、写、删)',
  user_mode_setting:'用户模式设置',
  group_mode_setting:'组模式设置',
  member_mode_setting:'成员模式设置',
  radius_server:'RADIUS服务器',
  please_input_radius_server:'请输入RADIUS服务器',
  port:'端口',
  please_input_port:'请输入端口',
  shared_secret:'预共享秘钥',
  please_input_shared_secret:'请输入预共享秘钥',
  authAlgorithm:'认证算法',
  test_user:'测试用户名',
  please_input_test_user:'请输入测试用户名',
  rest_auth_config:'Restful认证配置',
  attr_config:'属性配置',
  key:'键名',
  attr:'属性',
  upload: {
    tip: '导入后未匹配成功的设备会关联至“默认组”，当该设备处于“默认组”时，系统会根据该设备的第一个使用人所在的组织架构为设备分组，仅生效一次。',
    fileName: '设备模板',
    isExporting: '正在导出',
    failedRecord: '设备导入失败记录',
  },
  associatedDevices: {
    Third_Party_QR_Code_Login: '三方扫码登录',
    syncStrategy: '同步策略',
    rootGroupId: '根部门id',
    other: '其他',
    inputRootId: '请输入根部门id',
    userFieldMap: '用户组织字段映射',
    userDataMap: '用户数据字段映射',
    fieldName: '字段名称',
    fieldDefine: '字段定义',
    keyField: '关键字段',
    keyFieldTip: '关键字段用以确认用户数据的唯一性，请慎重勾选',
    inputFieldName: '请输入字段名称',
    inputFieldDefine: '请输入字段定义',
    qrResultUrl: '获取扫码结果URL',
    qrGenerateUrl: '生成二维码URL',
    inputQrGenerateUrl: '请输入生成二维码URL',
    inputQrResultUrl: '请输入获取扫码结果URL'
  },
  DB:{
    syncCon: '数据同步配置',
    syncOrNot: '是否同步',
    enterPlugName: '请输入插件名称',
    plugName: '插件名称',
    enterTableName: '请输入组织表名称',
    tableName: '组织表名称',
    enterUserName: '请输入用户表名称',
    UserTableName: '用户表名称',
    clickToUpload: '点击上传',
    onlyxlsFiles: '只能上传xls文件',
    templateDownFail: '模板下载失败',
  },
  deviceLog: {
    deleteLog: '删除日志',
    deleteLogTip: '确定删除选中的日志？',
    reportLog: '上报日志',
    viewLog: '查看日志',
    reportSuccess: '上报成功！',
    logList: '日志列表',
  },
}
