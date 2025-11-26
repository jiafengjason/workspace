# -*- coding: utf-8 -*-
import os
import re
import pandas as pd
import sys

# 关键词列表（可根据实际需求扩展）
DANGEROUS_KEYWORDS = ['SQLI', 'XSS', 'RCE', 'LFI', 'RFI', 'SESSION', 'PHISHING', 'COMMAND', 'INJECTION', 'TRAVERSAL']

# 更均衡的权重分配
BLOCK_WEIGHT = 0.17
SEVERITY_WEIGHT = 0.17
PHASE_WEIGHT = 0.16
MSG_WEIGHT = 0.16
ACCURACY_WEIGHT = 0.17
MATURITY_WEIGHT = 0.17

# 默认值
DEFAULT_SEVERITY = 7
DEFAULT_PHASE = 3
DEFAULT_BLOCK = 0
DEFAULT_ACCURACY = 1
DEFAULT_MATURITY = 1

# 判定函数
def judge_confidence(score):
    if score < 0.3:
        return '正常（放行）'
    elif score < 0.6:
        return '可疑（记录）'
    elif score < 0.9:
        return '高危（告警）'
    else:
        return '攻击（封禁）'

# 解析SecRule字段
def parse_secrule_block(block):
    # 提取SecRule参数字符串（双引号或单引号包裹）
    def extract_param_string(block):
        match = re.search(r'SecRule.*?([\'"])(.+)\1\s*$', block, re.DOTALL)
        if match:
            return match.group(2)
        return ''
    param_str = extract_param_string(block)
    # severity
    def extract_severity(param_str):
        match = re.search(r"severity\s*:\s*['\"]?([A-Za-z]+)['\"]?", param_str, re.IGNORECASE)
        if match:
            sev_str = match.group(1).upper()
            if sev_str in SEVERITY_MAP:
                return SEVERITY_MAP[sev_str]
        match = re.search(r"severity\s*:\s*['\"]?([0-7])['\"]?", param_str)
        if match:
            return int(match.group(1))
        return DEFAULT_SEVERITY
    severity = extract_severity(param_str)
    # 其余字段照常提取
    # id
    id_match = re.search(r'id\s*:\s*([0-9]+)', block)
    rule_id = id_match.group(1) if id_match else ''
    # phase
    phase_match = re.search(r'phase\s*:\s*([0-9]+)', block)
    phase = int(phase_match.group(1)) if phase_match else DEFAULT_PHASE
    # block/deny
    block_flag = 1 if re.search(r'\b(deny|block)\b', block, re.IGNORECASE) else DEFAULT_BLOCK
    # msg - 优化提取正则表达式
    msg_match = re.search(r"msg\s*:\s*(['\"])(.*?)\1", block, re.IGNORECASE | re.DOTALL)
    if not msg_match:
        # 处理未加引号或包含特殊字符的情况
        msg_match = re.search(r"msg\s*:\s*([^,;]+?)(?=\s*[;,]|$)", block, re.IGNORECASE | re.DOTALL)
    msg = msg_match.group(2).strip() if (msg_match and len(msg_match.groups()) > 1) else (msg_match.group(1).strip() if msg_match else '')
    # accuracy
    accuracy_match = re.search(r"accuracy\s*:\s*['\"]?([0-9]+)['\"]?", block)
    accuracy = int(accuracy_match.group(1)) if accuracy_match else DEFAULT_ACCURACY
    # maturity
    maturity_match = re.search(r"maturity\s*:\s*['\"]?([0-9]+)['\"]?", block)
    maturity = int(maturity_match.group(1)) if maturity_match else DEFAULT_MATURITY
    # msg关键词 - 优化匹配逻辑
    msg_weight = 0
    # 为不同关键词设置权重
    KEYWORD_WEIGHTS = {
        'SQLI': 0.3, 'XSS': 0.3, 'RCE': 0.3, 
        'LFI': 0.2, 'RFI': 0.2, 'SESSION': 0.2, 
        'PHISHING': 0.2, 'COMMAND': 0.25, 
        'INJECTION': 0.25, 'TRAVERSAL': 0.2
    }
    # 匹配关键词并计算权重
    for kw, weight in KEYWORD_WEIGHTS.items():
        if re.search(r'\b' + re.escape(kw.lower()) + r'\b', msg.lower()):
            msg_weight += weight
    # 限制最大权重为1
    msg_weight = min(msg_weight, 1.0)
    return {
        'id': rule_id,
        'phase': phase,
        'severity': severity,
        'block': block_flag,
        'msg': msg,
        'accuracy': accuracy,
        'maturity': maturity,
        'msg_weight': msg_weight
    }

# 置信度计算
def calc_confidence(rule):
    # block归一化
    block_score = rule['block'] * BLOCK_WEIGHT
    # severity归一化
    severity_score = ((7 - rule['severity']) / 7) * SEVERITY_WEIGHT
    # phase归一化
    if rule['phase'] == 1 or rule['phase'] == 2:
        phase_normalized = 1.0  # 请求阶段最重要
    elif rule['phase'] == 3 or rule['phase'] == 4:
        phase_normalized = 0.5  # 响应阶段次重要
    else:  # phase 5
        phase_normalized = 0.2  # 日志阶段重要性最低
    phase_score = phase_normalized * PHASE_WEIGHT
    # msg关键词
    msg_score = rule['msg_weight'] * MSG_WEIGHT
    # accuracy归一化
    accuracy_score = ((int(rule['accuracy']) - 1) / 8) * ACCURACY_WEIGHT
    # maturity归一化
    maturity_score = ((int(rule['maturity']) - 1) / 8) * MATURITY_WEIGHT
    # 总分
    score = block_score + severity_score + phase_score + msg_score + accuracy_score + maturity_score
    score = min(max(score, 0), 1)  # 保证在0-1之间
    
    nonlinear_score = 4 * score * (1 - score)
    return round(score, 3), round(nonlinear_score, 3)

SEVERITY_MAP = {
    'EMERGENCY': 0,
    'ALERT': 1,
    'CRITICAL': 2,
    'ERROR': 3,
    'WARNING': 4,
    'NOTICE': 5,
    'INFO': 6,
    'DEBUG': 7
}

SEVERITY_LEVELS = [
    'EMERGENCY',  # 0
    'ALERT',      # 1
    'CRITICAL',   # 2
    'ERROR',      # 3
    'WARNING',    # 4
    'NOTICE',     # 5
    'INFO',       # 6
    'DEBUG'       # 7
]

def extract_severity(text):
    # 先查字符串等级
    match = re.search(r"severity\s*:\s*['\"]?([A-Za-z]+)['\"]?", text, re.IGNORECASE)
    if match:
        sev_str = match.group(1).upper()
        if sev_str in SEVERITY_MAP:
            return SEVERITY_MAP[sev_str]
    # 再查数字
    match = re.search(r"severity\s*:\s*['\"]?([0-7])['\"]?", text)
    if match:
        return int(match.group(1))
    return DEFAULT_SEVERITY

def extract_param_string(block):
    # 提取SecRule参数字符串（双引号或单引号包裹）
    match = re.search(r'SecRule.*?([\'\"])(.+)\\1\\s*$', block, re.DOTALL)
    if match:
        return match.group(2)
    return ''

def extract_severity(param_str):
    # 先查字符串等级
    match = re.search(r"severity\\s*:\\s*['\\\"]?([A-Za-z]+)['\\\"]?", param_str, re.IGNORECASE)
    if match:
        sev_str = match.group(1).upper()
        if sev_str in SEVERITY_MAP:
            return SEVERITY_MAP[sev_str]
    # 再查数字
    match = re.search(r"severity\\s*:\\s*['\\\"]?([0-7])['\\\"]?", param_str)
    if match:
        return int(match.group(1))
    return DEFAULT_SEVERITY

# 在parse_secrule_block中
# param_str = extract_param_string(block)
# severity = extract_severity(param_str)

def extract_secrule_blocks(text):
    # 支持多行SecRule，按SecRule开头分割
    blocks = []
    current = []
    for line in text.splitlines():
        if line.strip().startswith('SecRule'):
            if current:
                blocks.append('\n'.join(current))
                current = []
        if line.strip() or current:
            current.append(line.rstrip())
    if current:
        blocks.append('\n'.join(current))
    return blocks

if __name__ == '__main__':
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

    if len(sys.argv) > 1:
        RULES_DIR = sys.argv[1]
    else:
        RULES_DIR = input("请输入规则目录的完整路径: ").strip()

    if not os.path.exists(RULES_DIR):
        print(f"错误：目录 '{RULES_DIR}' 不存在！")
        sys.exit(1)

    OUTPUT_FILE = os.path.join(SCRIPT_DIR, 'confidence.xlsx')

    rules = []
    for filename in os.listdir(RULES_DIR):
        if filename.endswith('.conf'):
            filepath = os.path.join(RULES_DIR, filename)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                secrule_blocks = extract_secrule_blocks(content)
                for block in secrule_blocks:
                    if block.strip().startswith('SecRule'):
                        rule = parse_secrule_block(block)
                        if rule['id']:
                            linear_conf, nonlinear_conf = calc_confidence(rule)
                            result = rule.copy()
                            result['confidence'] = nonlinear_conf
                            result['result'] = judge_confidence(nonlinear_conf)
                            # 移除severity_raw、severity_normalized、severity_level输出
                            # result['severity_raw'] = severity
                            # result['severity_normalized'] = round((7 - severity) / 7, 3)
                            # result['severity_level'] = SEVERITY_LEVELS[severity]
                            rules.append(result)
    df = pd.DataFrame(rules)
    df.to_excel(OUTPUT_FILE, index=False)
    print(f'处理完成，结果已保存到 {OUTPUT_FILE}')