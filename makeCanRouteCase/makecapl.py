# -*- coding: UTF-8 -*-
import codecs
import csv
import re

from ETH_MTBF.eth_mtbf import getRootPath

filepath = getRootPath() + "/makeCanRouteCase/"
def get_row_data(case_id):
    '''
    :param case_id: 用例id
    :return: 返回该id这行所有数据
    '''
    case_data = None
    with codecs.open(filepath+'/orl_file/router.csv',mode="r", encoding='gbk') as f:
        for row in csv.DictReader(f, skipinitialspace=True):
            if case_id in str(row.get("No.")):
                case_data = row
    f.close()
    return case_data

def get_pr_router_signal(case_id):
    teststep = str(get_row_data(case_id)["TestSteps"]).split("\n")
    pr_router_signame = []
    for j in range(len(teststep)):
        if "=" in teststep[j] and "DLC=" not in teststep[j] :
            pr_router_signame.append(teststep[j].split("=")[0])
    print("路由前的信号")
    print(pr_router_signame)
    return pr_router_signame

def get_router_message_id(case_id):
    #获取报文的路由前后ID
    Summary = str(get_row_data(case_id)["Summary"])
    ids = re.search("CAN信号路由_(.*?)->(.*)",Summary)
    pr_router_id = ids.group(1)
    be_router_id = ids.group(2)
    print("路由前的ID："+pr_router_id)
    print("路由后的ID："+be_router_id)
    return pr_router_id,be_router_id

def get_router_message_name(case_id):
    # 获取报文的路由前后报文的名称
    teststep = str(get_row_data(case_id)["TestSteps"])
    pr_router_message = re.search("发送报文名称：(.*?)，报文ID",teststep).group(1)
    Expectedresults = str(get_row_data(case_id)["Expectedresults"])
    be_router_message = re.search("报文名称：(.*?)，报文ID", Expectedresults).group(1)
    print("路由前的报文名称："+pr_router_message)
    print("路由后的报文名称："+be_router_message)
    return pr_router_message,be_router_message

def make_eviments(case_id,channel):
    filepath_ev = getRootPath() + "/makeCanRouteCase/out_file/" + "eviment.txt"
    pre_signal = get_pr_router_signal(case_id)
    #制作上部分
    with open(filepath_ev, "w", encoding="utf-8") as f:
        be_router_message =get_router_message_name(case_id)[0]
        f.write(f'  <namespace name="{channel}" comment="" interface="">\n')
        f.write(f'      <namespace name="{be_router_message}" comment="" interface="">\n')
        #环境指定到值
        for i in range(len(pre_signal)):
            f.write(f'        <variable anlyzLocal="2" readOnly="false" valueSequence="false" unit="" name="E_{pre_signal[i]}" comment="" bitcount="32" isSigned="true" encoding="65001" type="float" />\n')
        #制作下部分
        f.write(f'      </namespace>\n')
        f.write(f'   </namespace>\n')
        f.write(f'</systemvariables>\n')
    f.close()

def make_send_signal(case_id,channel):
    #编写发送端
    pre_signal = get_pr_router_signal(case_id)
    pr_router_id = get_router_message_id(case_id)[0]
    pr_router_message_name = get_router_message_name(case_id)[0]
    #写发送信号端---申请对象
    filepath_tx = getRootPath() + "/makeCanRouteCase/out_file/" + "tx.txt"
    with open(filepath_tx, "w", encoding="utf-8") as f:
        f.write(f"    message {channel}::{pr_router_message_name} m_{pr_router_message_name};//{pr_router_id}\n")
        f.close()
    # 写发送信号端-
    print(len(pre_signal))
    print(pre_signal)
    print(filepath_tx)
    with open(filepath_tx, "a", encoding="utf-8") as f:
        for i in range(len(pre_signal)):
            f.write(f"//{pr_router_id}\n")
            f.write(f"on sysvar_update {channel}::{pr_router_message_name}::E_{pre_signal[i]}")
            f.write("{\n")
            f.write(f"		m_{pr_router_message_name}.{pre_signal[i]}.phys\t=\t@this;\n")
            f.write(f"		output(m_{pr_router_message_name});\n")
            f.write("}\n")
        f.close()

def make_be_router_signal(case_id):
    teststep = str(get_row_data(case_id)["Expectedresults"]).split("\n")
    be_router_signame = []
    for j in range(len(teststep)):
        if "=" in teststep[j] and "DLC=" not in teststep[j] :
            be_router_signame.append(teststep[j].split("=")[0])
    print(be_router_signame)
    return be_router_signame

def get_be_router_message_cyctime(case_id):
    Expectedresults = str(get_row_data(case_id)["Expectedresults"])
    cyctime = re.search("周期为(.*?)ms", Expectedresults).group(1)
    print("路由后的周期："+cyctime)
    return cyctime
#
def make_capl(case_id,pr_channel,be_channel):
    filepath_result = getRootPath() + "/makeCanRouteCase/out_file/" + "result.txt"
    be_router_message_name = get_router_message_name(case_id)[-1]
    pr_router_message_name = get_router_message_name(case_id)[0]
    #申请变量
    with open(filepath_result, "w", encoding="utf-8") as f:
        f.write(f"\t\t//{get_router_message_id(case_id)[-1]}\n")
        f.write(f'\t\tint act_dirs_{str(be_router_message_name).lower()};\n')
        f.write(f'\t\tint act_dlc_{str(be_router_message_name).lower()};\n')
        f.write(f'\t\tint act_id_{str(be_router_message_name).lower()};\n')
        f.write("\n")
        f.close()
    #制作接收端
    with open(filepath_result, "a", encoding="utf-8") as f:
        f.write(f'on message {be_channel}::{be_router_message_name}')
        f.write("{\n")
        f.write(f'\t\tact_dirs_{str(be_router_message_name).lower()} = this.dir;\n')
        f.write(f'\t\tact_dlc_{str(be_router_message_name).lower()} = this.dlc;\n')
        f.write(f'\t\tact_id_{str(be_router_message_name).lower()}  = this.id;\n')
        f.write("}\n")
        f.close()
#
    #制作脚本
    with open(filepath_result, "a", encoding="utf-8") as f:
        f.write("testcase "+case_id+"() {\n")
        f.write("/*\n")
        Preconditions = str(get_row_data(case_id)["Preconditions"]).split("\n")
        print(Preconditions)
        #写前置条件
        for j in range(len(Preconditions)):
            if(j==0):
                f.write(f"\t\t前置条件：{Preconditions[j]}\n")
            else:
                f.write(f"\t\t\t\t\t\t\t{Preconditions[j]}\n")
#         # 写测试步骤
        TestSteps = str(get_row_data(case_id)["TestSteps"]).split("\n")
        for j in range(len(TestSteps)):
            if (j == 0):
                f.write(f"\t\t测试步骤：{TestSteps[j]}\n")
            else:
                f.write(f"\t\t\t\t\t\t\t{TestSteps[j]}\n")
        # 写期望期望
        Expectedresults = str(get_row_data(case_id)["Expectedresults"]).split("\n")
        for j in range(len(Expectedresults)):
            if (j == 0):
                f.write(f"\t\t期望结果：{Expectedresults[j]}\n")
            else:
                f.write(f"\t\t\t\t\t\t\t{Expectedresults[j]}\n")
        f.write("*/\n")
        f.write(f'\t\tmessage {be_channel}::{get_router_message_name(case_id)[-1]} testMessage;\n')
        f.write(f'\t\tdword expt_id = {get_router_message_id(case_id)[-1]};//路由后的报文ID\n')
        f.write(f'\t\tfloat MessageCycleTime = {get_be_router_message_cyctime(case_id)};//声明接收报文周期时间\n')
        f.write(f'\t\tint exp_dirs = 0;//声明接收报文方向\n')
        f.write(f'\t\t//用例标题\n')
        f.write(f'\t\tTestCaseTitle("106","{case_id}");\n')
        f.write(f'\t\ttestCaseDescription ("Test case is used to check the {get_router_message_id(case_id)[0]} router status");\n')
        f.close()
#         #制作步骤
        pr_router_signame = get_pr_router_signal(case_id)
        be_router_signame = make_be_router_signal(case_id)
        print(pr_router_signame)
        with open(filepath_result, "a", encoding="utf-8") as f:
            for i in range(len(pr_router_signame)):
                # 定义消息
                f.write(f'\t\tTestStep("步骤1-{i + 1}","{pr_router_signame[i]}-->{be_router_signame[i]}");\n')
                f.write('\t\tfor(i=canbus;i>=0;i=i-canbus){\n')
                f.write(f'\t\t\t\t@{pr_channel}::{pr_router_message_name}::')
                f.write(f'E_{pr_router_signame[i]} = i;\n')
                f.write(f'\t\t\t\t//根据路由表，进行映射\n')
                f.write(f'\t\t\t\texpt_value = i;\n')
                f.write(f'\t\t\t\ttestWaitForSignalChange(')
                f.write(F"{be_channel}::{be_router_message_name}::")
                f.write(f'{be_router_signame[i]},waitForMessageTime);\n')
                f.write(f'\t\t\t\tact_value = getSignal(')
                f.write(F"{be_channel}::{be_router_message_name}::")
                f.write(f'{be_router_signame[i]});\n')
                f.write(f'\t\t\t\ttestassertResult(testMessage,i,expt_value,act_value,')
                f.write(f'"{be_router_signame[i]}");\n')
                f.write('\t\t}\n')
            f.close()
#
#
        # 写检查周期、id/dlc
        with open(filepath_result, "a", encoding="utf-8") as f:
            f.write('\t\t//判断接收的报文ID、DLC、DIR、周期\n')
            f.write(f'\t\ttestassertID(testMessage,expt_id,act_id_{str(be_router_message_name).lower()});\n')
            f.write(f'\t\ttestassertDLC(testMessage,expt_dlc,act_dlc_{str(be_router_message_name).lower()});\n')
            f.write(f'\t\ttestassertDir(testMessage,exp_dirs,act_dirs_{str(be_router_message_name).lower()});\n')
            f.write('\t\ttestassertCyctime(testMessage,MessageCycleTime,CycleTimeOffset);\n')
            f.write('}\n')
            f.close()









if __name__ == '__main__':
    case_id = "TC_PuJin_Router_MessageRouter_027"
    pr_channel = "CAN8"
    be_channel = "CAN1"
    make_send_signal(case_id,pr_channel)
    make_eviments(case_id,pr_channel)
    make_capl(case_id,pr_channel,be_channel)