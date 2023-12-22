import csv
import re

import xlrd


def read_excel(sheetname):
    #打开excel表，填写路径
    book = xlrd.open_workbook("./orl_file/适配钇为线控平台的路由表_V1.0_20231215.xlsx")
    #找到sheet页
    table = book.sheet_by_name(sheetname)
    #获取总行数总列数
    row_Num = table.nrows
    col_Num = table.ncols
    all_data = []
    for i in range(2,row_Num):
        row =table.row_values(i)# 这是第一行数据，作为字典的key值
        row_data = []
        for j in range(1,col_Num):#将每列数据填入list
                row_data.append(row[j])
        all_data.append(row_data)
    return all_data

def get_single_number(all_data):

    #找出报文条数
    nums=[]
    for i in range(len(all_data)):
        if all_data[i][0] != "":
            nums.append(i)
    nums.append(len(all_data))
    return nums

def run_cases(sheetname):
    all_data = read_excel(sheetname)
    single_nums = get_single_number(all_data)
    cases= []
    print(all_data[0])
    #获取对应单元格的列号
    for i in range(len(all_data[0])):
        if "报文名称" in all_data[0][i] and i < (len(all_data[0])/2):
            tx_msg_name_col = i
    for i in range(len(all_data[0])):
        if "报文标识符" in all_data[0][i] and i < (len(all_data[0]) / 2):
            tx_msg_id_col = i
    for i in range(len(all_data[0])):
        if "报文周期时间" in all_data[0][i] and i < (len(all_data[0]) / 2):
            tx_msg_cycle_col = i
    for i in range(len(all_data[0])):
        if "报文长度" in all_data[0][i] and i < (len(all_data[0]) / 2):
            tx_msg_len_col = i
    for i in range(len(all_data[0])):
        if "信号名称" in all_data[0][i] and i < (len(all_data[0]) / 2) and "信号名称（中文）" not in all_data[0][i]:
            tx_msg_signal_name_col = i
    for i in range(len(all_data[0])):
        if "Msg ID" in all_data[0][i] and i > (len(all_data[0]) / 2):
            rx_msg_name_col = i
    for i in range(len(all_data[0])):
        if "报文标识符" in all_data[0][i] and i > (len(all_data[0]) / 2):
            rx_msg_id_col = i
    for i in range(len(all_data[0])):
        if "报文周期时间" in all_data[0][i] and i > (len(all_data[0]) / 2):
            rx_msg_cycle_col = i
    for i in range(len(all_data[0])):
        if "报文长度" in all_data[0][i] and i > (len(all_data[0]) / 2):
            rx_msg_len_col = i
    for i in range(len(all_data[0])):
        if "信号名称" in all_data[0][i] and i > (len(all_data[0]) / 2) and "信号名称（中文）" not in all_data[0][i]:
            rx_msg_signal_name_col_col = i


    print(all_data[1])
    for i in range(1,len(single_nums)-1):
        case =[]
        Summary = "CAN信号路由_" +all_data[single_nums[i]][tx_msg_id_col]+"->"+all_data[single_nums[i]][rx_msg_id_col]
        Preconditions = "canbus.被测板的CAN1连接CANoe的CAN1，被测板的CAN8连接CANoe的CAN2连接\n2.被测板子正常启动"
        #测试步骤
        TestSteps1 = f"canbus.使用CANoe工具，在CAN1上发送报文名称：{all_data[single_nums[i]][tx_msg_name_col]}，报文ID：{all_data[single_nums[i]][tx_msg_id_col]}中信号\n"
        router_pre = ""
        cha = single_nums[i+1]-single_nums[i]
        for j in range(cha):
            sig_values = ""
            #处理信号值
            if all_data[single_nums[i]+j][10] != "":
                sig_value = re.findall(r'(.*?):', all_data[single_nums[i]+j][10])
                if sig_value != "":
                    for k in range(len(sig_value)):
                        if k != 0:
                            sig_values =sig_values +"/" +sig_value[k]
                        else:
                            sig_values =sig_value[k]
             #处理信号名称
            if j !=0 and router_pre !="":
                router_pre = router_pre + f"={sig_values}\n" + str(all_data[single_nums[i]+j][tx_msg_signal_name_col])
            else:
                router_pre = str(all_data[single_nums[i]+j][tx_msg_signal_name_col])
        dlc = f"2.报文周期设定为{str(all_data[single_nums[i]][tx_msg_cycle_col]).split('.')[0]}ms，DLC={str(all_data[single_nums[i]][tx_msg_len_col]).split('.')[0]}发送报文\n"
        TestSteps =TestSteps1 + router_pre+"=\n" + dlc

        Expectedresults = f"2.CAN2能收到报文名称：{all_data[single_nums[i]][rx_msg_name_col]}，报文ID：{all_data[single_nums[i]][rx_msg_id_col]}分别对应以下信号值\n"
        router_hou = ""
        cha = single_nums[i+1]-single_nums[i]
        for j in range(cha):
            #处理信号值
            sig_values = ""
            if all_data[single_nums[i]+j][10] != "":
                sig_value = re.findall(r'(.*?):', all_data[single_nums[i]+j][10])
                if sig_value != "":
                    for k in range(len(sig_value)):
                        if k != 0:
                            sig_values =sig_values +"/" +sig_value[k]
                        else:
                            sig_values =sig_value[k]
            if j != 0 and router_hou !="":
                router_hou =router_hou + f"={sig_values}\n" + str(all_data[single_nums[i]+j][rx_msg_signal_name_col_col])
            else:
                router_hou = str(all_data[single_nums[i] + j][rx_msg_signal_name_col_col])
        dlc = f"收到报文周期为{str(all_data[single_nums[i]][rx_msg_cycle_col]).split('.')[0]}ms，DLC={str(all_data[single_nums[i]][rx_msg_len_col]).split('.')[0]}\n"
        Expectedresults =Expectedresults + router_hou +"=\n"+ dlc
        case.append(Summary)
        case.append(Preconditions)
        case.append(TestSteps)
        case.append(Expectedresults)
        cases.append(case)
    return cases


def make_case(sheetname):
    file = open('case.csv', 'w', newline='')
    writer = csv.writer(file)
    data =run_cases(sheetname)
    print(data)
    for i in range(len(data)):
        writer.writerow(data[i])
    file.close()


if __name__ == '__main__':
    #基于路由表，编写测试用例
    sheetname = "底盘域到智驾域"
    make_case(sheetname)