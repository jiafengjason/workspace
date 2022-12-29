#!/usr/bin/env python
# coding=utf-8
 
import time
import gitlab
import collections
import pandas as pd

gl = gitlab.Gitlab('http://192.168.100.70/', private_token='ABxVz3vzTfeKyicoN-Uo', timeout=60, api_version='4')

start_time = '2022-1-1T00:00:00Z'
end_time = '2022-12-29T23:00:00Z'

def get_gitlab():
    """
    gitlab API
    """
    list2 = []
    projects = gl.projects.list(owned=True, all=True)
    num = 0
    for project in projects:
        num += 1
        print("查看了%d个项目" % num)
        for branch in project.branches.list():
            print("branch: %s" % branch)
            commits = project.commits.list(all=True, query_parameters={'since': start_time, 'until': end_time,
                                                                       'ref_name': branch.name})
 
            for commit in commits:
                com = project.commits.get(commit.id)
 
                pro = {}
                try:
                    print(project.path_with_namespace,com.author_name,com.stats["total"])
                    pro["projectName"] = project.path_with_namespace
                    pro["authorName"] = com.author_name
                    pro["branch"] = branch.name
                    pro["additions"] = com.stats["additions"]
                    pro["deletions"] = com.stats["deletions"]
                    pro["commitNum"] = com.stats["total"]
                    list2.append(pro)
                except:
                    print("有错误, 请检查")
 
    return list2

def data():
    """
    数据去重
    key split
    """
 
    ret = {}
 
    for ele in get_gitlab():
        key = ele["projectName"] + ele["authorName"] + ele["branch"]
        if key not in ret:
            ret[key] = ele
            ret[key]["commitTotal"] = 1
        else:
            ret[key]["additions"] += ele["additions"]
            ret[key]["deletions"] += ele["deletions"]
            ret[key]["commitNum"] += ele["commitNum"]
            ret[key]["commitTotal"] += 1
 
    list1 = []
    for key, v in ret.items():
        v["项目名"] = v.pop("projectName")
        v["开发者"] = v.pop("authorName")
        v["分支"] = v.pop("branch")
        v["添加代码行数"] = v.pop("additions")
        v["删除代码行数"] = v.pop("deletions")
        v["提交总行数"] = v.pop("commitNum")
        v["提交次数"] = v["commitTotal"]
        list1.append(v)
    print(list1)
    return list1

def csv(csvName):
    """
    csv
    """
    df = pd.DataFrame(data(), columns=["项目名", "开发者", "分支", "添加代码行数", "删除代码行数", "提交总行数", "提交次数"])
    df.to_csv(csvName, index=False, encoding="utf_8_sig")

if __name__ == "__main__":
    csv("./gitlab.csv")

