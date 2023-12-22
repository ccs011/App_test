import csv
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
    for i in range(1,len(all_data)):
        if all_data[i][0] != "":
            nums.append(i)
    nums.append(len(all_data))
    return nums

def run_cases(sheetname,send_chl="CAN1",rx_chl="CAN8",dir=0):
    '''
    :param sheetname: excel表格中sheet页
    :param first: ADC表示OBU网关在excel表格前面，其他字符时表示OBU网关在excel表格后面
    :param dir: 0表示从左向右路由，1表示从右向左路由
    :return:
    '''

    all_data = read_excel(sheetname)
    single_nums = get_single_number(all_data)
    cases = []
    print(single_nums)
    print(all_data[0])
    #获取对应单元格的列号
    for i in range(len(all_data[0])):
        if ("报文名称" in str(all_data[0][i])) and i < (len(all_data[0])/2):
            first_msg_name_col = i   #报文名称
    #路由后的报文列号
        if ("报文名称" in str(all_data[0][i])) and i > ((len(all_data[0])-1) / 2):
            second_msg_name_col = i   #报文名称

    if dir == 1:
        tmp = first_msg_name_col
        first_msg_name_col = second_msg_name_col
        second_msg_name_col = tmp

    tx_msg_name_col = first_msg_name_col   #报文名称
    tx_msg_id_col = first_msg_name_col +1  #报文标识符
    tx_msg_cycle_col = first_msg_name_col + 3   #报文周期时间
    tx_msg_len_col = first_msg_name_col  + 4    #报文长度
    tx_msg_signal_name_col = first_msg_name_col + 5#信号名称
    rx_msg_name_col = second_msg_name_col   #报文名称
    rx_msg_id_col = second_msg_name_col + 1  #报文标识符
    rx_msg_cycle_col = second_msg_name_col + 3   #报文周期时间
    rx_msg_len_col = second_msg_name_col + 4     #报文长度
    rx_msg_signal_name_col = second_msg_name_col + 5 #信号名称

    print("xxxxxxxxxxxxxxxx")
    for i in range(len(single_nums)-1):
        tx_msg_name = all_data[single_nums[i]][tx_msg_name_col]
        pre_canid = all_data[single_nums[i]][tx_msg_id_col]
        router_canid = all_data[single_nums[i]][rx_msg_id_col]
        print(f"报文名称：{tx_msg_name}")
        cases.append([pre_canid])
        for j in range(single_nums[i],single_nums[i+1]-1):
            tx_msg_signal_name =all_data[j+1][tx_msg_signal_name_col]

            Summary = f"CAN信号路由_({tx_msg_signal_name})_" + pre_canid + "->" + router_canid
            print(f"用例标题：{Summary}")
            print(f"信号名称：{tx_msg_signal_name}")
            Preconditions = f"1.被测板的{send_chl}连接CANoe的CAN1，被测板的{rx_chl}连接CANoe的CAN2连接\n2.被测板子正常启动"
            print(f"预置条件：{Preconditions}")
            TestSteps1 = f"1.使用CANoe工具，在CANOE中对应CAN1通道上发送报文名称：{all_data[single_nums[i]][tx_msg_name_col]}，报文ID：{all_data[single_nums[i]][tx_msg_id_col]}中信号\n"
            dlc = f"2.报文周期设定为{str(all_data[single_nums[i]][tx_msg_cycle_col]).split('.')[0]}ms，DLC={str(all_data[single_nums[i]][tx_msg_len_col]).split('.')[0]}发送报文\n"
            TestSteps =TestSteps1 + tx_msg_signal_name+"=\n" + dlc
            print(f"测试步骤：{TestSteps}")

            ###################################################################
            #期望结果
            Expectedresults = f"2.在CANOE中对应CAN2通道能收到报文名称：{all_data[single_nums[i]][rx_msg_name_col]}，报文ID：{router_canid}分别对应以下信号值\n"
            rx_msg_signal_name = all_data[j + 1][rx_msg_signal_name_col]
            print(f"路由后信号名称：{rx_msg_signal_name}")
            dlc = f"收到报文周期为{str(all_data[single_nums[i]][rx_msg_cycle_col]).split('.')[0]}ms，DLC={str(all_data[single_nums[i]][rx_msg_len_col]).split('.')[0]}\n"
            Expectedresults =Expectedresults + rx_msg_signal_name +"=\n"+ dlc
            print(f"期望结果：{Expectedresults}")
            #补充信息
            ''''''''''''''''''''''''''''''
            caseid = f"TC_YW_Router_NotMessageRouter_{pre_canid}_001"
            swrs_id = "SWRS-1"
            dengji = "A"
            Feature ="CAN路由"
            Category ="基本功能"
            TestMethod ="手动测试"
            Subfunction =pre_canid
            Author = "陈昌松"
            cases.append([caseid,swrs_id,dengji,Feature,Category,TestMethod,Subfunction,Summary,Preconditions,TestSteps,Expectedresults,Author])

    return cases


def make_case(sheetname,send_chl="CAN1",rx_chl="CAN8",dir=0):
    file = open('case.csv', 'w', newline='')
    writer = csv.writer(file)
    data =run_cases(sheetname,send_chl,rx_chl,dir)
    print(len(data))
    for i in range(len(data)):
        writer.writerow(data[i])
    file.close()


if __name__ == '__main__':
    #基于路由表，编写测试用例
    sheetname = "底盘域到智驾域"
    #dir 参数主要以路由表为准，路由表从左向右时dir=0,反之则为dir=1
    make_case(sheetname,send_chl="CAN1",rx_chl="CAN8",dir=1)
