# -*- coding: UTF-8 -*-
import codecs
import csv
import re

from ETH_MTBF.eth_mtbf import getRootPath

filepath = getRootPath() + "/makeCanRouteCase/"
def get_row_datas():
    '''
    将所有的用例整理出来，并按照发送报文的ID一样归纳
    :param case_id: 用例id
    :return: [[id1,id1],[id2,id2]
    '''
    case_datas = []
    with codecs.open(filepath+'/orl_file/router.csv',mode="r", encoding='gbk') as f:
        for row in csv.DictReader(f, skipinitialspace=True):
            # if str(row.get("Summary")) != "":
            case_datas.append(row)
    indexs = [] # 行号
    for i in range(len(case_datas)):
        if case_datas[i].get("Summary") == "" and case_datas[i].get("No.") != "":
            indexs.append(i)
    indexs.append(len(case_datas))
    ret_case_data = []
    for j in range(len(indexs)):
        if indexs[j] != 0:
            case_data = []
            for i in range(indexs[j-1]+1,indexs[j]):
                case_data.append(case_datas[i])
            ret_case_data.append(case_data)
    return ret_case_data

def get_data_from_case(ditc_value):
    #参数为第几条用例，{}字典
    teststep = str(ditc_value["TestSteps"]).split("\n")
    for j in range(len(teststep)):
        if "=" in teststep[j] and "DLC=" not in teststep[j]:
            pr_router_signame = (teststep[j].split("=")[0])
    # 路由后信号名称
    Expectedresults = str(ditc_value["Expectedresults"]).split("\n")
    print(Expectedresults)
    for j in range(len(Expectedresults)):
        if "=" in Expectedresults[j] and "DLC=" not in Expectedresults[j]:
            be_router_signame = (Expectedresults[j].split("=")[0])
    print(f"路由前的信号:{pr_router_signame}")
    print(f"路由后的信号:{be_router_signame}")

    # 获取报文的路由前后报文的名称
    teststep = str(ditc_value["TestSteps"])
    pr_router_message = re.search("发送报文名称：(.*?)，报文ID", teststep).group(1)
    Expectedresults = str(ditc_value["Expectedresults"])
    be_router_message = re.search("报文名称：(.*?)，报文ID", Expectedresults).group(1)
    print("路由前的报文名称：" + pr_router_message)
    print("路由后的报文名称：" + be_router_message)

    # 获取报文的路由前后ID
    Summary = str(ditc_value["Summary"])
    ids = re.search("CAN信号路由_(.*?)_(.*?)->(.*)", Summary)
    pr_router_id = ids.group(2)
    if "_" in pr_router_id:
        pr_router_id =pr_router_id.split("_")[1]
    be_router_id = ids.group(3)
    print(f"路由前的ID：{pr_router_id}")
    print(f"路由后的ID：{be_router_id}")

    Expectedresults = str(ditc_value["Expectedresults"])
    cyctime = re.search("周期为(.*?)ms", Expectedresults).group(1)
    print("路由后的周期："+cyctime)

    return {"pr_id":pr_router_id,"be_id":be_router_id,"pr_siname":pr_router_signame,"be_siname":be_router_signame,"pr_message":pr_router_message,"be_message":be_router_message,"cyctime":cyctime}


def make_caple_environment(case_ids,channel):
    # 升级环境变量
    #传入发送报文ID一样的用例,[id1,id1,di1]
    eviments_txt = []
    for i in range(len(case_ids)):
        #路由前信号名称
        dict_values  =get_data_from_case(case_ids[i])
        # 生成环境变量文件
        channel_txt = f'  <namespace name="{channel}" comment="" interface="">\n'
        message_txt = f'      <namespace name="{dict_values["pr_message"]}" comment="" interface="">\n'
        signal_txt = (
            f'        <variable anlyzLocal="2" readOnly="false" valueSequence="false" unit="" name="E_{dict_values["pr_siname"]}" comment="" bitcount="32" isSigned="true" encoding="65001" type="float" />\n')
        if i == 0:
            eviments_txt.append(channel_txt)
            eviments_txt.append(message_txt)
        eviments_txt.append(signal_txt)
    channel_end = f'      </namespace>\n'
    message_end = f'   </namespace>\n'
    enment_end = f'</systemvariables>\n'
    eviments_txt.append(channel_end)
    eviments_txt.append(message_end)
    eviments_txt.append(enment_end)
    filepath_ev = getRootPath() + "/makeCanRouteCase/out_file/" + "eviment.txt"
    with open(filepath_ev, "a", encoding="utf-8") as f:
        for ite in eviments_txt:
            f.write(ite)

def make_caple_environment_all(case_all,channel):
    # 参数传入 [[id1,id1],[id2,id2]
    filepath_ev = getRootPath() + "/makeCanRouteCase/out_file/" + "eviment.txt"
    channel_txt = f'  <namespace name="{channel}" comment="" interface="">\n'
    with open(filepath_ev, "a", encoding="utf-8") as f:
        f.write(channel_txt)
    for j in range(len(case_all)):
        eviments_txt = []
        for i in range(len(case_all[j])):
            #路由前信号名称
            dict_values  =get_data_from_case(case_all[j][i])
            # 生成环境变量文件
            message_txt = f'      <namespace name="{dict_values["pr_message"]}" comment="" interface="">\n'
            signal_txt = (
                f'        <variable anlyzLocal="2" readOnly="false" valueSequence="false" unit="" name="E_{dict_values["pr_siname"]}" comment="" bitcount="32" isSigned="true" encoding="65001" type="float" />\n')
            if i == 0:
                eviments_txt.append(message_txt)
            eviments_txt.append(signal_txt)
        channel_end = f'      </namespace>\n'
        eviments_txt.append(channel_end)
        with open(filepath_ev, "a", encoding="utf-8") as f:
            for ite  in eviments_txt:
                f.write(ite)
    message_end = f'   </namespace>\n'
    enment_end = f'</systemvariables>\n'
    with open(filepath_ev, "a", encoding="utf-8") as f:
        f.write(message_end)
        f.write(enment_end)


def make_send_signal(case_ids,channel):
    # 编写发送端d
    #传入发送报文ID一样的用例,[id1,id1,di1]
    for i in range(len(case_ids)):
        dict_values  =get_data_from_case(case_ids[i])
        # 写发送信号端---申请对象
        filepath_tx = getRootPath() + "/makeCanRouteCase/out_file/" + "tx.txt"
        if i ==0:
            with open(filepath_tx, "w", encoding="utf-8") as f:
                f.write(f"    message {channel}::{dict_values['pr_message']} m_{dict_values['pr_message']};//{dict_values['pr_id']}\n")
                f.close()
        # 写发送信号端-
        with open(filepath_tx, "a", encoding="utf-8") as f:
            f.write(f"//{dict_values['pr_id']}\n")
            f.write(f"on sysvar_update {channel}::{dict_values['pr_message']}::E_{dict_values['pr_message']}")
            f.write("{\n")
            f.write(f"		m_{dict_values['pr_message']}.{dict_values['pr_siname']}.phys\t=\t@this;\n")
            f.write(f"		output(m_{dict_values['pr_message']});\n")
            f.write("}\n")
            f.close()
def make_send_all_signal(case_all,channel):
    # 编写发送端d
    #传入发送报文ID一样的用例,[id1,id1,di1]
    send_title = [] # 存储申请对象
    for j in range(len(case_all)):
        for i in range(len(case_all[j])):
            dict_values  =get_data_from_case(case_all[j][i])
            # 写发送信号端---申请对象
            filepath_tx = getRootPath() + "/makeCanRouteCase/out_file/" + "tx.txt"
            if i == 0:
                send_title.append(f"    message {channel}::{dict_values['pr_message']} m_{dict_values['pr_message']};//{dict_values['pr_id']}\n")
            # 写发送信号端-
            with open(filepath_tx, "a", encoding="utf-8") as f:
                f.write(f"//{dict_values['pr_id']}\n")
                f.write(f"on sysvar_update {channel}::{dict_values['pr_message']}::E_{dict_values['pr_siname']}")
                f.write("{\n")
                f.write(f"		m_{dict_values['pr_message']}.{dict_values['pr_siname']}.phys\t=\t@this;\n")
                f.write(f"		output(m_{dict_values['pr_message']});\n")
                f.write("}\n")
                f.close()
    new_title =set(send_title) #排除重合的部分
    with open(filepath_tx, "r", encoding="utf-8") as f:
        data = f.readlines()
        for title in new_title:
            data.insert(0,title)

    with open(filepath_tx, "w", encoding="utf-8") as f:
        for i in range(len(data)):
            f.write(data[i])

def make_capl(case_ids,pr_channel="CAN1",be_channel="CAN8"):
    #默认使用CAN1发送，CAN8接收
    filepath_result = getRootPath() + "/makeCanRouteCase/out_file/" + "result.txt"
    for i in range(len(case_ids)):
        CASE_DATA = case_ids[i]
        dict_values = get_data_from_case(CASE_DATA)
        #申请变量
        if i == 0:
            with open(filepath_result, "w", encoding="utf-8") as f:
                f.write(f"\t\t//{dict_values['pr_id']}\n")
                f.write(f'\t\tint act_dirs_{str(dict_values["be_message"]).lower()};\n')
                f.write(f'\t\tint act_dlc_{str(dict_values["be_message"]).lower()};\n')
                f.write(f'\t\tint act_id_{str(dict_values["be_message"]).lower()};\n')
                f.write("\n")
                f.close()
            #制作接收端
            with open(filepath_result, "a", encoding="utf-8") as f:
                f.write(f'on message {be_channel}::{dict_values["be_message"]}')
                f.write("{\n")
                f.write(f'\t\tact_dirs_{str(dict_values["be_message"]).lower()} = this.dir;\n')
                f.write(f'\t\tact_dlc_{str(dict_values["be_message"]).lower()} = this.dlc;\n')
                f.write(f'\t\tact_id_{str(dict_values["be_message"]).lower()}  = this.id;\n')
                f.write("}\n")
                f.close()
#
        wirte_case_to_caple_testcase(filepath_result,CASE_DATA,pr_channel, be_channel)

        # 写检查周期、id/dlc
        with open(filepath_result, "a", encoding="utf-8") as f:
            if i == (len(case_ids) - 1):
                f.write('\t\t//判断接收的报文ID、DLC、DIR、周期\n')
                f.write(f'\t\ttestassertID(testMessage,expt_id,act_id_{str(dict_values["be_message"]).lower()});\n')
                f.write(f'\t\ttestassertDLC(testMessage,expt_dlc,act_dlc_{str(dict_values["be_message"]).lower()});\n')
                f.write(f'\t\ttestassertDir(testMessage,exp_dirs,act_dirs_{str(dict_values["be_message"]).lower()});\n')
                f.write('\t\ttestassertCyctime(testMessage,MessageCycleTime,CycleTimeOffset);\n')
            f.write('}\n')
            f.close()


def wirte_case_to_caple_testcase(filepath_result,CASE_DATA,pr_channel,be_channel):
    #传入某条用例，键值对

    dict_values = get_data_from_case(CASE_DATA)
    #制作脚本
    with open(filepath_result, "a", encoding="utf-8") as f:
        f.write("testcase "+CASE_DATA['No.']+"() {\n")
        f.write("/*\n")
        Preconditions = str(CASE_DATA["Preconditions"]).split("\n")
        print(Preconditions)
        #写前置条件
        for j in range(len(Preconditions)):
            if(j==0):
                f.write(f"\t\t前置条件：{Preconditions[j]}\n")
            else:
                f.write(f"\t\t\t\t\t\t\t{Preconditions[j]}\n")
#         # 写测试步骤
        TestSteps = str(CASE_DATA["TestSteps"]).split("\n")
        for j in range(len(TestSteps)):
            if (j == 0):
                f.write(f"\t\t测试步骤：{TestSteps[j]}\n")
            else:
                f.write(f"\t\t\t\t\t\t\t{TestSteps[j]}\n")
        # 写期望期望
        Expectedresults = str(CASE_DATA["Expectedresults"]).split("\n")
        for j in range(len(Expectedresults)):
            if (j == 0):
                f.write(f"\t\t期望结果：{Expectedresults[j]}\n")
            else:
                f.write(f"\t\t\t\t\t\t\t{Expectedresults[j]}\n")
        f.write("*/\n")
        f.write(f'\t\tmessage {be_channel}::{dict_values["pr_message"]} testMessage;\n')
        f.write(f'\t\tdword expt_id = {dict_values["be_id"]};//路由后的报文ID\n')
        f.write(f'\t\tfloat MessageCycleTime = {dict_values["cyctime"]};//声明接收报文周期时间\n')
        f.write(f'\t\tint exp_dirs = 0;//声明接收报文方向\n')
        f.write(f'\t\t//用例标题\n')
        f.write(f'\t\tTestCaseTitle("106","{CASE_DATA["No."]}");\n')
        f.write(f'\t\ttestCaseDescription ("Test case is used to check the {dict_values["pr_id"]} router status");\n')
        f.close()
#         #制作步骤
        pr_router_signame = dict_values["pr_siname"]
        be_router_signame = dict_values["be_siname"]
        pr_router_message_name = dict_values["pr_message"]
        be_router_message_name = dict_values["be_message"]
        with open(filepath_result, "a", encoding="utf-8") as f:
            # 定义消息
            f.write(f'\t\tTestStep("步骤1-1","{pr_router_signame}-->{be_router_signame}");\n')
            f.write('\t\tfor(i=1;i>=0;i=i-1){\n')
            f.write(f'\t\t\t\t@{pr_channel}::{pr_router_message_name}::')
            f.write(f'E_{pr_router_signame} = i;\n')
            f.write(f'\t\t\t\t//根据路由表，进行映射\n')
            f.write(f'\t\t\t\texpt_value = i;\n')
            f.write(f'\t\t\t\ttestWaitForSignalChange(')
            f.write(F"{be_channel}::{be_router_message_name}::")
            f.write(f'{be_router_signame},waitForMessageTime);\n')
            f.write(f'\t\t\t\tact_value = getSignal(')
            f.write(F"{be_channel}::{be_router_message_name}::")
            f.write(f'{be_router_signame});\n')
            f.write(f'\t\t\t\ttestassertResult(testMessage,i,expt_value,act_value,')
            f.write(f'"{be_router_signame}");\n')
            f.write('\t\t}\n')
            f.close()


def make_capl_all_case(case_all,pr_channel="CAN1",be_channel="CAN8"):
    #默认使用CAN1发送，CAN8接收
    # 参数传入 [[id1,id1],[id2,id2]
    filepath_result_case = getRootPath() + "/makeCanRouteCase/out_file/" + "result_case.txt"
    filepath_result_duixiang = getRootPath() + "/makeCanRouteCase/out_file/" + "result_duixiang.txt"
    filepath_result_onmenages = getRootPath() + "/makeCanRouteCase/out_file/" + "result_onmenages.txt"
    filepath_result_do_case = getRootPath() + "/makeCanRouteCase/out_file/" + "result_do_case.txt"
    for j in range(len(case_all)):
        for i in range(len(case_all[j])):
            CASE_DATA = case_all[j][i]
            dict_values = get_data_from_case(CASE_DATA)
            #写所有的ID,用于脚本执行
            with open(filepath_result_do_case, "a", encoding="utf-8") as f:
                f.write(f"    {CASE_DATA['No.']}(); \n")

            #申请变量
            if i == 0:
                with open(filepath_result_duixiang, "a", encoding="utf-8") as f:
                    f.write(f"\t\t//{dict_values['pr_id']}\n")
                    f.write(f'\t\tint act_dirs_{str(dict_values["be_message"]).lower()};\n')
                    f.write(f'\t\tint act_dlc_{str(dict_values["be_message"]).lower()};\n')
                    f.write(f'\t\tint act_id_{str(dict_values["be_message"]).lower()};\n')
                    f.write("\n")
                    f.close()
                #制作接收端
                with open(filepath_result_onmenages, "a", encoding="utf-8") as f:
                    f.write(f'on message {be_channel}::{dict_values["be_message"]}')
                    f.write("{\n")
                    f.write(f'\t\tact_dirs_{str(dict_values["be_message"]).lower()} = this.dir;\n')
                    f.write(f'\t\tact_dlc_{str(dict_values["be_message"]).lower()} = this.dlc;\n')
                    f.write(f'\t\tact_id_{str(dict_values["be_message"]).lower()}  = this.id;\n')
                    f.write("}\n")
                    f.close()
    #
            wirte_case_to_caple_testcase(filepath_result_case,CASE_DATA,pr_channel, be_channel)

            # 写检查周期、id/dlc
            with open(filepath_result_case, "a", encoding="utf-8") as f:
                if i == (len(case_all[j]) - 1):
                    f.write('\t\t//判断接收的报文ID、DLC、DIR、周期\n')
                    f.write(f'\t\ttestassertID(testMessage,expt_id,act_id_{str(dict_values["be_message"]).lower()});\n')
                    f.write(f'\t\ttestassertDLC(testMessage,expt_dlc,act_dlc_{str(dict_values["be_message"]).lower()});\n')
                    f.write(f'\t\ttestassertDir(testMessage,exp_dirs,act_dirs_{str(dict_values["be_message"]).lower()});\n')
                    f.write('\t\ttestassertCyctime(testMessage,MessageCycleTime,CycleTimeOffset);\n')
                f.write('}\n')
                f.close()



def run_all_caple():
    all = get_row_datas()
    make_capl_all_case(all, "CAN1", "CAN2")
    make_caple_environment_all(all, "CAN1")
    make_send_all_signal(all, "CAN1")



if __name__ == '__main__':
    run_all_caple()







