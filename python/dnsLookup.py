#coding=utf-8
#pip install dnspython
import requests
import sys
import socket
import dns
import dns.resolver
from concurrent.futures import ThreadPoolExecutor
import datetime

domains = ["static.zhimg.com","login.cnki.net","piccache.cnki.net","t.cnki.net","bookstore.cnki.net","cstmeeting.chntox.org","hy.csm.org.cn","law.cnki.net","www.acn2023.org","www.amac-cn.net","www.chinacses.org","www.saecce.org.cn","a.cnki.net","baike.cnki.net","baojianshibao.cnki.net","bianke.cnki.net","bnjj.cnki.net","boyue.cnki.net","caj.cnki.net","cajn.cnki.net","cajviewer.cnki.net","cb.cnki.net","cbad.cnki.net","cdmdpj.cnki.net","cfed.cnki.net","check.cnki.net","ches2022.scimeeting.cn","chkd.cnki.net","cidian.cnki.net","cjcr.cnki.net","cnki.com.cn","concept.cnki.net","conf.cnki.net","cpc.cnki.net","cpcedu.cnki.net","crjt.cnki.net","csjs.cnki.net","ctbd.cnki.net","ctwh.cnki.net","cved.cnki.net","cx.cnki.net","cyfz.cnki.net","czit.cnki.net","czyw.cnki.net","dangjian.cnki.net","dangshi.cnki.net","data.cnki.net","dict.cnki.net","dp.cnki.net","dysw.cnki.net","dzjc.cnki.net","dzjgbgs.cnki.net","e.weibo.com","edu.cnki.net","elib.cnki.net","estudy.cnki.net","eval.cnki.net","expert.cnki.net","fast.cnki.net","find.cb.cnki.net","fintech.cnki.net","fybh.cnki.net","gaojiao.cnki.net","gdzk.cnki.net","gj.cnki.net","gjzl.cnki.net","gk.cnki.net","glcx.cnki.net","gongjushu.cnki.net","gpk.cnki.net","graduate.cnki.net","gzjg.cnki.net","help.cnki.net","hq.cnki.net","i.cnki.net","image.cnki.net","ir.cnki.net","itfin.cnki.net","jcjy.cnki.net","jiance.cnki.net","jiangtan.cnki.net","jianjun.cnki.net","jif.cnki.net","jrjg.cnki.net","jtp.cnki.net","jy.cnki.net","k.cnki.net","kj.cnki.net","kjs.cnki.net","km.cnki.net","kms.cnki.net","kns.cnki.net","kt.cnki.net","ky.cnki.net","lawnew.cnki.net","lvyou.cnki.net","m.cnki.net","maker.cnki.net","mall.cnki.net","meitan.cnki.net","method.cnki.net","mp.weixin.qq.com","ms.cnki.net","myhk.cnki.net","navi.cnki.net","oversea.cnki.net","pj.cnki.net","pom.cnki.net","pta.cnki.net","qa.cnki.net","qjsx.cnki.net","quick.cnki.net","qygl.cnki.net","r.cnki.net","sa.cnki.net","saishi.cnki.net","scjg.cnki.net","service.cnki.net","shiyou.cnki.net","shuwu.cnki.net","sk.cnki.net","smpt.cnki.net","ss.knet.cn","sthj.cnki.net","tax.cnki.net","thinker.cnki.net","tsk.cnki.net","tx.cnki.net","ve.cnki.net","vipcard.cnki.net","vsad.cnki.net","wap.cnki.net","wbyx.cnki.net","wjci.cnki.net","wk.cnki.net","wl.cnki.net","wmcys.cnki.net","wuxizazhi.cnki.net","www.cac2022.org.cn","www.chincold-smart.com","www.eubce.com","www.wjx.cn","x.cnki.net","xjpt.cnki.net","xk.cnki.net","xsjy.cnki.net","yd.cnki.net","yjgl.cnki.net","ylpys.cnki.net","yxjc.cnki.net","z.cnki.net","zgxczl.cnki.net","zhengbao.cnki.net","zhifu.cnki.net","zhiku.cnki.net","zk.cnki.net","zl.cnki.net","zngw.cnki.net","zwwh.cnki.net","zxlzta.cnki.net","zy.cnki.net","zyjy.cnki.net"]

def get_ips_by_dns_lookup(domain):
    A_records = []
    AAAA_records = []

    try:
        result = dns.resolver.resolve(domain, 'A')
        for ipv4 in result:
            A_records.append(ipv4.to_text())
    except:
        None

    try:
        result = dns.resolver.resolve(domain, 'AAAA')
        for ipv6 in result:
            AAAA_records.append(ipv6.to_text())
    except:
        None

    return "doamin:{} ipv4:{} ipv6:{}".format(domain, A_records, AAAA_records)

if __name__ == "__main__":
    pool = ThreadPoolExecutor(max_workers=200)
    starttime = datetime.datetime.now()
    futures = [pool.submit(get_ips_by_dns_lookup, domain) for domain in domains]
    for future in futures:
        print(future.result())
    endtime = datetime.datetime.now()
    print((endtime - starttime).seconds)
