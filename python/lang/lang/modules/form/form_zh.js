export const form_zh = {
  error_min: "最小授权数为",
  error_max: "最大可授权数为",
  isAany: "协议为{value}时，端口必须为{value}",
  isAaany: "端口为{value}时，协议必须为{value}",
  group: "以字母开头，长度{length}位，包含字母、数字、横杠",
  required: "不能为空",
  min_length: "至少输入{number}个字符",
  select: "请选择",
  max_length: "最多输入{number}个字符",
  username: "以字母或数字开头，长度3~32位，包含字母、数字、下划线",
  password: "以字母、数字或符号（除空格）组成，长度6~32位",
  strong_password: "必须包括字母、数字和符号（除空格），长度8~32位",
  password_repeat: "新密码不能与原密码相同",
  confirm: "两次密码输入不一致，请重新输入",
  illegal: "格式不合法",
  num_illegal: "数值格式不合法",
  int_illegal: "取值只能是整数",
  pInt_illegal: "取值只能是正整数",
  star_illegal: "最多只能输入3个*",
  int1dec1: "取值0-1 限制一位小数 不建议修改",
  max2_dec1: "最多两位整数,可以精确到小数点后一位",
  int_only: "只能输入数字,且可以精确到小数点后两位",
  int_postice_illegal: "取值只能是正整数",
  outOfRange: "应用最大用户数超出了最大用户数",
  please_edit_the_value: "应用最大用户数超过了当前设置的最大用户数",
  onlineuser_not_more_than_usermax: "最大在线用户数超过了最大用户数",
  adminuser_not_more_than_usermax: "最大管理员用户数超过了最大用户数",
  maxInteger: "数值超出了允许的最大整数值范围",
  group_path: "不能包含/或空格",
  service_path: "格式不合法，请以/开头",
  range: "范围：{range}",
  range_int: "范围：{range}整数",
  allowDec2: "允许小数点后两位",
  EnterInt1000: "请输入1000以内的正整数",
  Enterstrin32: "长度在32个字符以内",
  container_max: "安全空间",
  allow_range: "可允许输入范围为0到{number}",
  allow_range_1: "可允许输入范围为1到{number}",
  allow_statuscode_range: "请输入100到505范围内的返回状态码",
  range_illegal: "值不在范围内",
  shared_key: "以字母、数字或特殊符号(_!@#$%^&*)组成，长度8~255位",
  shared_key_repeat: "不能与上次设置的相同",
  shared_key_confirm: "两次密钥输入不一致",
  spa_port: "源地址配置为ANY时，允许访问端口不能为0",
  time_range: "开始时间应早于结束时间",
  time_range_tips: "开始时间应早于结束时间, 请更改",
  strategy_ip_repeat: "不能重复",
  strategy_ip_range: "最多输入10条",
  route_related: "名称与网关地址需填其一",
  ip_zero: "该策略不支持",
  url_prefix: "不用输入http或https",
  alias_illegal: "以字母开头,包含字母、数字（除空格）",
  ip_domain: "格式非法，请输入合法的IP或域名",
  singleRequired: "进程名和服务名至少输入一项",
  singleRequiredReq: "请求速率和请求限制下载带宽至少输入一项",
  repeate: "该地址已存在",
  repeatePort: "该端口已存在",
  greaterZero: "请输入大于零数值",
  noticeGreaterReset: "告警值应大于告警重置值",
  resetSmallerNotice: "告警重置值应小于告警值",
  time_formart: "时间格式不正确",
  max_int: "不得大于{number}",
  max8charter: "只能输入8个字符，字母数字皆可",
  not_allow_space: "不能包含空格",
  port_rules: "多个端口之间必须用-连接",
  full_all_strategy: "请填写所有策略,否则会提示错误!!!",
  Name: "不允许输入特殊字符和空格",
  cpassword: "以字母、数字或符号（除空格）组成，长度6~32位",
  no_zeroIp: "不支持全0ip",
  lua_script: "需符合openresty lua脚本开发规范,以function开头,end结尾",
  char_only: "只支持英文、下划线",
  headerinfo_same: "请求头信息选项不能相同!",
  intRange: "范围为{range}的整数",
  objFilter_tip: "支持数字、字母、下划线等特殊符号",
  upload_tip:"请上传文件",
  incorrect_format:"格式不正确",
  please_enter_number: "请输入数字",
  please_enter_ip: "请填写ip",
  please_enter_ip_type: "请输入ip+掩码格式,例如：{value}",
  lengthTip: '长度在 {min} 到 {max} 个字符',
  input1_100: '请输入1-100正整数',
  input_positive_integerTip: '请输入{min}-{max}正整数',
  inputMax5PositiveInteger: '请输入正整数最大5位数',
  domain_not_duplicated: '域名不能重复',
  enter_voild_domain: '请输入格式合法的域名',
  domain_length_less_100: '域名长度不能大于100',
  please_input_special_ip: '请输入0.0.0.0/0',
  Please_select_upload_file: '请选择上传文件',
  exceed_max999: '超过最大值999',
  multipl_domain_names: '多条域名之间使用英文逗号隔开，示例：{value1},{value2}',
  IPV4_example: 'IPv4示例：{value1},{value2},{value3}',
  IPV6_example: 'IPv6示例：{value1}',
  enter_diy_content: '请输入自定义文本内容',
  timeout_max_30000: '超时时间最大为30000毫秒',
  retries_max_20: '重试次数最大为20次',
  max_monitor_frequency: '监控频率最大为2592000（即30天）',
  max_packets_numb: 'PING包数目最大为100个',
  please_enter_ping_packets: '请先输入PING包数目',
  lost_packets_not_greater_PING: '丢包数目不能大于PING包数目',
  maxLengthTip: '长度在{max}个字符以内',
  validIpHostTip: '请输入格式合法的IP或域名',
}