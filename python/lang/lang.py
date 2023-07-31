import configparser
import os
import pandas as pd

def jsonfy(s:str)->object:
    #此函数将不带双引号的json的key标准化
    obj = eval(s, type('js', (dict,), dict(__getitem__=lambda s, n: n))())
    return obj

def json2dict(json, dic, prefix=None):
    newPrefix = ""
    for key,value in json.items():
        if prefix:
            newPrefix = prefix+'.'+key
        else:
            newPrefix = key
        if isinstance(value,dict):
            json2dict(value, dic, newPrefix)
        else:
            dic[newPrefix] = value

def js2dict(js_path):
    dic = {}
    prefixKeys = []
    with open(js_path, 'r') as f:
        js_content = f.read()
        sindex = js_content.find('{')
        eindex = js_content.rfind('}')
        for line in js_content[sindex:eindex+1].splitlines():
            line = line.strip()
            if line.startswith("//"):
                continue
            if line == "},":
                prefixKeys.pop()
                continue
            if ":" in line:
                line = line.strip(",")
                items = line.split(":")
                key = items[0].strip()
                value = items[1].strip().strip("\"").strip("\'").strip()
                if value == "{":
                    prefixKeys.append(key)
                else:
                    if prefixKeys:
                        key = ".".join(prefixKeys)+"."+key
                    dic[key] = value
    return dic

def ini2dict(path):
    dic = {}
    '''
    config = configparser.ConfigParser()
    config.read(js_path)
    for section in config.sections():
        dic[section] = {}
        for option in config.options(section):
            dic[section][option] = config.get(section, option)
    '''
    with open(path, 'r') as f:
        content = f.read()
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("["):
                section = line.strip("[").strip("]")
            if "=" in line:
                items = line.split("=")
                key = items[0].strip()
                value = items[1].strip()
                dic[section+"."+key] = value

    return dic

'''
def gen_sheet(module, js_path, js_name, excel, writer):
    lang = js_name.split(".")[0].split("_")[1]
    dic = js2dict(js_path)
    #print(dic)

    df = pd.DataFrame()
    if os.path.exists(excel):
        excel_file = pd.ExcelFile(excel)
        if module in excel_file.sheet_names:
            df = pd.read_excel(excel, sheet_name=module)
            for index in df.index:
                key = df.loc[index, 'key']
                if key in dic:
                    df.loc[index, lang] = dic[key]
        else:
            df = pd.DataFrame(list(dic.items()), columns=['key', lang])
    else:
        df = pd.DataFrame(list(dic.items()), columns=['key', lang])
    
    # 将修改后的数据写回到 Excel 文件
    df.to_excel(writer, sheet_name=module, index=False)
'''

def gen_sheet(js_path, js_name):
    items = js_name.split(".")
    lang = items[0]
    ext = items[1]
    if "_" in lang:
        lang = lang.split("_")[1]
    if ext=="js":
        dic = js2dict(js_path)
    elif ext=="ini":
        dic = ini2dict(js_path)
    df = pd.DataFrame(list(dic.items()), columns=['key', lang])
    #df.set_index('key', inplace=True)
    #print(df)
    return df

def gen_excel(root, excel='lang.xlsx'):
    writer = pd.ExcelWriter(excel)
    for module in os.listdir(root):
        module_path = os.path.join(root, module)
        if os.path.isdir(module_path):
            merged_df = pd.DataFrame()
            for js_name in os.listdir(module_path):
                js_path = os.path.join(module_path, js_name)
                if os.path.isfile(js_path):
                    print(js_path)
                    #gen_sheet(module, js_path, js_name, excel, writer)
                    df = gen_sheet(js_path, js_name)
                    if merged_df.empty:
                        merged_df = df
                    else:
                        merged_df = merged_df.merge(df, on='key', how='outer')
            merged_df.to_excel(writer, sheet_name=module, index=False)
        #break
    writer.save()

def parseDic(dic):
    newDic = {}
    for keys, value in dic.items():
        keyList = keys.split(".")
        count = len(keyList)
        temp = newDic
        for i in range(count):
            key = keyList[i]
            if i == count-1:
                temp[key] = value
            else:
                if key not in temp:
                    temp[key] = {}
                temp = temp[key]
    return newDic

def gen_js_content(f, dic, indent):
    for key,value in dic.items():
        if isinstance(value,dict):
            line = "%s%s: {\n" % (indent*" ", key)
            f.write(line)
            gen_js_content(f, value, indent+4)
            line = "%s},\n" % (indent*" ")
            f.write(line)
        else:
            line = "%s%s: \'%s\',\n" % (indent*" ", key, value)
            f.write(line)

def gen_ini_content(f, dic):
    for key,value in dic.items():
        if isinstance(value,dict):
            line = "[%s]\n" % (key)
            f.write(line)
            gen_ini_content(f, value)
        else:
            line = "%s=%s\n" % (key, value)
            f.write(line)

def gen_js(excel, fmt):
    # 读取 Excel 文件
    excel_data = pd.read_excel(excel, sheet_name=None)

    root = excel.split(".")[0]+"_i18n"
    for sheet_name, df in excel_data.items():
        print('Sheet:', sheet_name)
        module = os.path.join(root, sheet_name)
        if not os.path.exists(module):
            os.makedirs(module)
        df.set_index('key', inplace=True)
        for column_name in df.columns:
            # 将 DataFrame 转化为字典对象
            records = df[column_name].fillna('').to_dict()
            #print(records)
            dic = parseDic(records)
            #print(dic)
            #jsFile = "%s_%s.js" % (sheet_name, column_name)
            jsFile = os.path.join(module, column_name+".js")
            with open(jsFile, "w", encoding="utf-8") as f:
                if fmt == "client":
                    f.write("module.exports = {\n")
                elif fmt == "server":
                    f.write("export const %s_%s = {\n" % (sheet_name, column_name))
                gen_js_content(f, dic, 4)
                f.write("}\n")
                #json.dump(records, f, indent=4, ensure_ascii=False)

def gen_ini(excel):
    # 读取 Excel 文件
    excel_data = pd.read_excel(excel, sheet_name=None)

    root = excel.split(".")[0]+"_ini"
    for sheet_name, df in excel_data.items():
        print('Sheet:', sheet_name)
        module = os.path.join(root, sheet_name)
        if not os.path.exists(module):
            os.makedirs(module)
        df.set_index('key', inplace=True)
        for column_name in df.columns:
            # 将 DataFrame 转化为字典对象
            records = df[column_name].fillna('').to_dict()
            #print(records)
            dic = parseDic(records)
            iniFile = os.path.join(module, column_name+".ini")
            with open(iniFile, "w", encoding="utf-8") as f:
                gen_ini_content(f, dic)

if __name__ == '__main__':
    #gen_excel("lang/modules", 'lang.xlsx')
    #gen_js("lang.xlsx", "server")
    #gen_excel("ues", 'ues.xlsx')
    #gen_js('ues.xlsx', "client")
    #gen_excel("uebm", 'uebm.xlsx')
    gen_ini('uebm.xlsx')