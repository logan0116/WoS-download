import json
from selenium import webdriver
import time
import os


def get_write_path(search_formula_path):
    write_path = os.path.abspath(search_formula_path).split('.')[0]
    if not os.path.exists(write_path):
        os.mkdir(write_path)
    return write_path


def search(search_formula_path, wait_time):
    search_formula = open(search_formula_path, 'r', encoding='UTF-8').read()
    # 切换数据库
    select_databases_1 = wos_web.find_element_by_id('select2-databases-container')
    select_databases_1.click()
    select_databases_2 = wos_web.find_element_by_xpath('/html/body/span[16]/span/span[2]/ul/li[2]')
    select_databases_2.click()
    time.sleep(wait_time)
    # 切换到高级检索
    advanced_search = wos_web.find_element_by_xpath('/html/body/div[1]/div[26]/div/ul/li[4]/a')
    advanced_search.click()
    time.sleep(wait_time)
    # 输入检索式
    search_box = wos_web.find_element_by_id('value(input1)')
    search_box.clear()
    search_box.send_keys(search_formula)
    time.sleep(wait_time)
    # 开始检索
    search_button = wos_web.find_element_by_id('search-button')
    search_button.click()
    time.sleep(wait_time)
    # 跳转到检索结果
    search_result = wos_web.find_element_by_id('hitCount')
    paper_num = search_result.text
    search_result.click()
    return int(paper_num.replace(',', ''))


def download_one(bit_start, bit_end, wait_time, write_path, index, first_time_flag):
    export_button_1 = wos_web.find_element_by_name('export')
    export_button_1.click()
    if first_time_flag == 0:
        export_button_2 = wos_web.find_element_by_name('导出为其他文件格式')
        export_button_2.click()
    time.sleep(wait_time)
    # 选择记录
    select = wos_web.find_element_by_id('numberOfRecordsRange')
    select.click()
    # 输入起始记录
    txt_start = wos_web.find_element_by_id('markFrom')
    txt_start.clear()
    txt_start.send_keys(bit_start)
    # 输入终止记录
    txt_end = wos_web.find_element_by_id('markTo')
    txt_end.clear()
    txt_end.send_keys(bit_end)
    # select2-bib_fields-container
    select2_1 = wos_web.find_element_by_id('select2-bib_fields-container')
    select2_1.click()
    select2_2 = wos_web.find_element_by_xpath('/html/body/span/span/span[2]/ul/li[4]')
    select2_2.click()
    # select2-saveOptions-container
    select3_1 = wos_web.find_element_by_id('select2-saveOptions-container')
    select3_1.click()
    select3_2 = wos_web.find_element_by_xpath('/html/body/span/span/span[2]/ul/li[5]')
    select3_2.click()
    export_button_2 = wos_web.find_element_by_id('exportButton')
    export_button_2.click()
    time.sleep(wait_time)
    # 给文件重命名
    file_list = os.listdir(write_path)
    new_file = ''
    for file in file_list:
        if file[:-4].isalpha():
            new_file = file
            break
    os.rename(os.path.join(write_path, new_file), os.path.join(write_path, str(index) + '.txt'))
    # 页面刷新一下
    wos_web.refresh()
    time.sleep(wait_time)


def download(paper_num, wait_time, write_path):
    bit_start_list = [i for i in range(1, paper_num, 500)]
    bit_end_list = [i for i in range(500, paper_num, 500)]
    if len(bit_end_list) < len(bit_start_list):
        bit_end_list.append(paper_num)
    bit_couple_list = [[bit_start_list[i], bit_end_list[i]] for i in range(len(bit_start_list))]
    # 断点续爬的机制
    excite_file_num = len(os.listdir(write_path))
    # 第一次下载需要特殊设置
    first_time_flag = 0
    for i in range(excite_file_num, len(bit_couple_list)):
        bit_start = bit_couple_list[i][0]
        bit_end = bit_couple_list[i][1]
        print('当前下载文件论文范围: %d-%d' % (bit_start, bit_end))
        download_one(bit_start, bit_end, wait_time, write_path, i, first_time_flag)
        if first_time_flag == 0:
            first_time_flag = 1


if __name__ == '__main__':
    search_formula_path = 'search_formula_1.txt'
    write_path = get_write_path(search_formula_path)
    # chrome参数设计
    chrome_options = webdriver.ChromeOptions()
    prefs = {'profile.default_content_settings.popups': 0,  # 防止保存弹窗
             'download.default_directory': write_path,  # 设置默认下载路径
             "profile.default_content_setting_values.automatic_downloads": 1  # 允许多文件下载
             }
    chrome_options.add_experimental_option('prefs', prefs)
    wos_web = webdriver.Chrome(chrome_options=chrome_options)
    wos_web.get(
        'https://apps.webofknowledge.com/WOS_AdvancedSearch_input.do?SID=6CPcR6MlBKuY1isRktZ&product=WOS&search_mode=AdvancedSearch')

    wait_time = 5
    # 检索
    paper_num = search(search_formula_path, wait_time)
    print('检索数量：', paper_num)
    # 下载
    download(paper_num, wait_time, write_path)
