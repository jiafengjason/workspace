#pip3 install -i https://mirrors.aliyun.com/pypi/simple/ pandas dnspython openpyxl
import dns.resolver
import pandas as pd
from pandas import ExcelWriter
import concurrent.futures

def dns_resolution(dns_server, typ, records):
    ip_list = []
    try:
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [dns_server]
        resolver.timeout = 1
        resolver.lifetime = 1

        answers = resolver.resolve("www.baidu.com", typ)
        for rdata in answers:
            resolved_ip = str(rdata)
            ip_list.append(resolved_ip)
        records[dns_server] = ','.join(ip_list) if ip_list else "NA"
    except Exception:
        records[dns_server] = 'NA'

def check_dns_resolution(excel):
    excel_data = pd.read_excel(excel, sheet_name=None, dtype={"A": str, "AAAA": str}, engine="openpyxl")

    with ExcelWriter('dnsServer_updated.xlsx', engine='openpyxl') as writer:
        for sheet_name, df in excel_data.items():
            print('Sheet:', sheet_name)
            original_columns = df.columns.tolist()

            for column_name in ["A", "AAAA"]:
                records = {}
                dns_servers = df['dns'].dropna().unique()
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                    futures = [executor.submit(dns_resolution, dns_server, column_name, records) for dns_server in dns_servers]
                    concurrent.futures.wait(futures)

                print(records)
                
                for dns_server, resolved_ip in records.items():
                    mask = df['dns'] == dns_server
                    df.loc[mask, column_name] = resolved_ip
                    #if dns_server in df['dns']:
                    #    df.at[dns_server, column_name] = resolved_ip

            df = df[original_columns]
            df.to_excel(writer, sheet_name=sheet_name, index=False)

if __name__ == "__main__":
    check_dns_resolution("dnsServer.xlsx")