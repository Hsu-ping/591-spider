import time
import random
import requests
from bs4 import BeautifulSoup
import csv
import tkinter as tk
from tkinter import messagebox
import datetime
import os
import re
import sys
import traceback



# 設定 CSV 檔案的欄位名稱
fields = [
    'id','is_available','house_id','register_use','shape_name','region_name','section_name',
    'road_name','title','parking_space','bed_room','living_room','bathroom','balcony',
    'room_layout','floor_from','floor_to','total_floor','floor','house_age','full_address',
    'price','unit_price','estimate_price','community_name','latitude','longitude','land_area',
    'land_zoning','total_area','main_building_area','common_area','sub_building_area',
    'room_layout','car_type','car_building','car_model','car_ownership','parking_fee',
    'tag','text_info','school','direction','img','is_elevator','is_management',
    'post_date','browsenum','community_sale_num','update_date'

]

region_map = {
    '1': 'taipei_city',
    '2': 'keelung_city',
    '3': 'new_taipei_city',
    '4': 'hsinchu_city',
    '5': 'hsinchu_county',
    '6': 'taoyuan_city',
    '7': 'miaoli_county',
    '8': 'taichung_city',
    '10': 'changhua_county',
    '11': 'nantou_county',
    '12': 'chiayi_city',
    '13': 'chiayi_county',
    '14': 'yunlin_county',
    '15': 'tainan_city',
    '17': 'kaohsiung_city',
    '19': 'pingtung_county',
    '21': 'yilan_county',
    '22': 'taitung_county',
    '23': 'hualien_county',
    '24': 'penghu_county',
    '25': 'kinmen_county',
    '26': 'lienchiang_county',
    # '苗栗市': 'miaoli_city',
    # '彰化市': 'changhua_city',
    # '南投市': 'nantou_city',
    # '屏東市': 'pingtung_city',
    # '宜蘭市': 'yilan_city',
    # '花蓮市': 'hualien_city',
    # '台東市': 'taitung_city',
    # '綠島': 'green_island',
    # '蘭嶼': 'orchid_island',
    # '馬祖': 'matsu'
}

# 定義範圍
totalRows = 'weeeee'
wantPage = 355
# cityName = region_map.get(regionid, 'unknown_city')
# 設定要寫入的 CSV 檔案名稱
csv_file_path = f'./rawData/{datetime.datetime.now().strftime("%Y-%m-%d")}/'
if not os.path.exists(csv_file_path):
    os.mkdir(csv_file_path)


class House591Spider():
    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.68',
        }

    def search(self, filter_params=None, sort_params=None, want_page=1):
        """ 搜尋房屋

        :param filter_params: 篩選參數
        :param sort_params: 排序參數
        :param want_page: 想要抓幾頁
        :return total_count: requests 房屋總數
        :return house_list: requests 搜尋結果房屋資料
        """
        total_count = 0
        house_list = []
        page = 0
        headers = {}


        # 紀錄 Cookie 取得 X-CSRF-TOKEN
        s = requests.Session()
        url = 'https://sale.591.com.tw/'
        s.cookies.set('urlJumpIp', filter_params.get('region', '17') if filter_params else '17', domain='.591.com.tw',path="/")
        r = s.get(url, headers=self.headers)
        # print(r.text)
        soup = BeautifulSoup(r.text, 'html.parser')
        # token_item = soup.select_one('meta[name="csrf-token"]')
        token_item = soup.find('meta', {'name': 'csrf-token'})
        if token_item:
            headers['X-CSRF-TOKEN'] = token_item.get('content')
        else:
            print("無法獲取 CSRF token。")


        headers = self.headers.copy()
        headers['X-CSRF-TOKEN'] = token_item.get('content')

        # 搜尋房屋
        url = 'https://sale.591.com.tw/home/search/list'
        # params = 'is_format_data=1&is_new_list=1&type=1'
        params=""
        if filter_params:
            # 加上篩選參數，要先轉換為 URL 參數字串格式
            params += 'type=2'
            params += ''.join([f'&{key}={value}' for key, value, in filter_params.items()])
        else:
            params += '&regionid=1&kind=0'
        # 在 cookie 設定地區縣市，避免某些條件無法取得資料
        # print(filter_params)
        s.cookies.set('urlJumpIp', filter_params.get('region', '1') if filter_params else '1', domain='.591.com.tw',path="/")

        # 排序參數
        if sort_params:
            params += ''.join([f'&{key}={value}' for key, value, in sort_params.items()])

        while 1:
            params += f'&firstRow={page*30}'
            r = s.get(url, params=params, headers=headers)
            # print(r.text)
            if r.status_code != requests.codes.ok:
                print('請求失敗', r.status_code)
                break
            page += 1

            data = r.json()
            house_list = data['data']['house_list']  # 修正此行
            # print(house_list)
            try:
                filtered_house_list = [
                    {
                        'house_id': house['houseid'],
                        'register_use': house.get('kind_name', ''),
                        'shape_name': house.get('shape_name', ''),
                        'region_name': house.get('region_name', ''),
                        'section_name': house.get('section_name', ''),
                        'road_name': house.get('address', ''),
                        'title': house.get('title', ''),
                        'parking_space': house.get('has_carport', ''),
                        # 'bed_room': house.get('bed_room', ''),
                        # 'living_room': house.get('living_room', ''),
                        # 'bathroom': house.get('bathroom', ''),
                        # 'balcony': house.get('balcony', ''),
                        'total_floor': house.get('floor', '').replace('B', '-').replace('F', ''),
                        'floor': house.get('floor', ''),
                        'house_age': house.get('houseage', ''),
                        # 'full_address': house.get('full_address', ''),
                        'price': house.get('price', ''),
                        'unit_price': house.get('unitprice', ''),
                        'community_name': house.get('community_name', ''),
                        # 'latitude': house.get('latitude', ''),
                        # 'longitude': house.get('longitude', ''),
                        # 'land_area': house.get('land_area', ''),
                        # 'land_zoning': house.get('land_zoning', ''),
                        'total_area': house.get('area', ''),
                        'main_building_area': house.get('mainarea', ''),
                        # 'common_area': house.get('common_area', ''),
                        # 'sub_building_area': house.get('sub_building_area', ''),
                        'room_layout': house.get('room', ''),
                        'car_building': house.get('carttype', ''),
                        'car_model': house.get('cartmodel', ''),
                        # 'car_ownership': house.get('car_ownership', ''),
                        # 'parking_fee': house.get('parking_fee', ''),
                        'tag': house.get('tag', []),
                        # 'text_info': house.get('text_info', ''),
                        'school': house.get('school', []),
                        # 'direction': house.get('direction', ''),
                        'img': house.get('photo_url', ''),
                        'is_elevator': house.get('is_elevator', ''),
                        # 'is_management': house.get('is_management', ''),
                        'post_date': house.get('posttime', ''),
                        'community_sale_num': house.get('community_sale_num', ''),
                        'browsenum': house.get('browsenum', ''),
                        'update_date': f'{datetime.datetime.now().strftime("%Y-%m-%d")}',
                    }
                    for house in house_list
                        if house.get('is_newhouse') != 1
                ]
                for house in filtered_house_list:
                    if house['total_floor'].isascii() and '~' not in house['total_floor']:
                        house['floor_from'] = house.get('total_floor', '').split('/')[0]
                        house['floor_to'] = house.get('total_floor', '').split('/')[0]
                    elif house['total_floor'].isascii() and '~' in house['total_floor']:
                        house['floor_from'] = house.get('total_floor', '').split('/')[0].split('~')[0]
                        house['floor_to'] = house.get('total_floor', '').split('/')[0].split('~')[1]
                    elif '整棟' in house['total_floor']:
                        house['floor_from'] = '1'
                        house['floor_to'] = house['total_floor'].split('/')[1]
                    elif '頂樓加蓋' in house['total_floor']:
                        house['floor_from'] = f"{int(house['total_floor'].split('/')[1])+1}"
                        house['floor_to'] = f"{int(house['total_floor'].split('/')[1])+1}"
                    house['total_floor'] = house.get('total_floor', '').partition('/')[2]

                    if house['shape_name'] == '公寓':
                        house['shape_name'] = '公寓(5樓含以下無電梯)'
                    elif house['shape_name'] == '電梯大樓' and int(house['total_floor']) > 10 :
                        house['shape_name'] = '住宅大樓(11層含以上有電梯)'
                        house['is_elevator'] = 1
                    elif house['shape_name'] == '電梯大樓' and int(house['total_floor']) <= 10 :
                        house['shape_name'] = '華廈(10層含以下有電梯)'
                        house['is_elevator'] = 1
                    elif house['shape_name'] == '別墅':
                        house['shape_name'] = '透天厝'

                    if house.get('car_model', '') == '平面式':
                        house['car_type'] = '平面式'
                    elif house.get('car_model', '') != '':
                        house['car_type'] = '有車位'
                    else:
                        house['car_type'] = '無車位'
                    
                    if '有陽台' in house['tag']:
                        house['balcony'] = '1'

                    room = house.get('room_layout')
                    if room == '' or room == '開放式格局':
                        room = '0房0廳0衛'
                    if '房' in room:
                        house['bed_room'] = room.split('房')[0]
                        room = room.partition('房')[2]
                    if '廳' in room:
                        house['living_room'] = room.split('廳')[0]
                        room = room.partition('廳')[2]
                    if '衛' in room:
                        house['bathroom'] = room.split('衛')[0]
                        room = room.partition('衛')[2]
                    if '陽台' in room:
                        house['balcony'] = room.split('陽台')[0]
                    
                    house['full_address'] = house['region_name'] + house['section_name'] + house['road_name']
                
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(f"An error occurred: {exc_type}: {exc_value}")
                with open(csv_file_path+f'591_error.txt', 'a', newline='', encoding='utf-8') as f:
                    f.write(str(house_list)+', ')
                


            # 現在 filtered_house_list 就包含了符合條件的欄位資料
            # print(filtered_house_list)
            # 過濾出 'is_newhouse': 1 的情況
            # houseid_list = [house['houseid'] for house in house_list if house.get('is_newhouse') != 1]
            # print(houseid_list)
            # 提取每個 JSON 對象中的 number 值
            # houseid_list = [obj['houseid'] for obj in house_list]
            
            # 開啟 CSV 檔案，使用 newline='' 以避免換行符號問題
            with open(csv_file_path+f'591_test.csv', 'a', newline='', encoding='utf-8') as csv_file:
            # with open(csv_file_path+f'591_{region_map.get(regionid)}.csv', 'a', newline='', encoding='utf-8') as csv_file:
                # 如果檔案是空的，寫入標題行
                if csv_file.tell() == 0:
                    csv_writer = csv.DictWriter(csv_file, fieldnames=fields)
                    csv_writer.writeheader()

                # 建立 CSV 寫入物件
                csv_writer = csv.DictWriter(csv_file, fieldnames=fields)
                # 寫入資料
                csv_writer.writerows(filtered_house_list)

            print(f'資料已成功寫入 {page}/{want_page}頁 {int(page*100/want_page)}%')

            # 將每個 number 值逐一寫入文本檔案
            # with open('./houseid_list.csv', 'a', encoding='utf-8') as file:
            #     for num in houseid_list:
            #         file.write('"' + str(num) + '"' + '\n')
            print(len(house_list))
            if(len(house_list)<30):
                break

            # total_count = data['data']['total']
            # house_list.extend(data['data']['house_list'])

            # total_count = data['records']
            # house_list.extend(data['data']['data'])
            # 隨機 delay 一段時間
            time.sleep(random.uniform(1, 1.5))

        return total_count, house_list

    def get_house_detail(self, house_id):
        """取得房屋詳細資訊

        Args:
            house_id (int): 房屋 ID

        Returns:
            dict: 包含房屋詳細資訊的字典
        """
        # 使用 Session 來保持連線狀態
        s = requests.Session()
        
        # 發送 GET 請求取得房屋頁面，獲取 X-CSRF-TOKEN 和 deviceid
        url = f'https://sale.591.com.tw/home/{house_id}'
        r = s.get(url, headers=self.headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        token_item = soup.select_one('meta[name="csrf-token"]')

        # 複製原始 headers 並添加 X-CSRF-TOKEN 和 deviceid
        headers = self.headers.copy()
        headers['X-CSRF-TOKEN'] = token_item.get('content')
        headers['deviceid'] = s.cookies.get_dict()['T591_TOKEN']
        # headers['token'] = s.cookies.get_dict()['PHPSESSID']
        headers['device'] = 'pc'

        # 發送 API 請求獲取房屋詳細資訊
        url = f'https://bff.591.com.tw/v1/house/sale/detail?id={house_id}'
        r = s.get(url, headers=headers)
        
        # 檢查請求是否成功
        if r.status_code != requests.codes.ok:
            print('請求失敗', r.status_code)
            return
        
        # 解析 JSON 資料並返回
        house_detail = r.json()['data']
        return house_detail


def show_notification(message):
    root = tk.Tk()
    root.withdraw()  # 隱藏主視窗

    # 顯示提示視窗
    messagebox.showwarning('提示', message)

if __name__ == "__main__":
    house591_spider = House591Spider()

    for regionid in region_map:
        
        # 篩選條件
        filter_params = {
            # 'type': '2',
            'shType': 'list',
            'regionid': f'{regionid}',  # (地區) 台北
            'totalRows': f'{totalRows}',
            'timestamp': str(int(time.time())),
            'recom_community': '1'
            # 'searchtype': '4',  # (位置1) 按捷運
            # 'mrtline': '125',  # (位置2) 淡水信義線
            # 'mrtcoods': '4198,4163',  # (位置3) 新北投 & 淡水
            # 'kind': '2',  # (類型) 獨立套房
            # 'multiPrice': '0_5000,5000_10000',  # (租金) 5000元以下 & 5000-10000元
            # 'saleprice': '3000,6000',  # (自訂租金範圍) 3000~6000元
            # 'multiRoom': '2,3',  # (格局) 2房 & 3房
            # 'other': 'near_subway,cook,lease',  # (特色) 近捷運 & 可開伙 & 可短期租賃
            # --- 以下要加 showMore=1 ---
            # 'showMore': '1',
            # 'shape': '3',  # (型態) 透天厝
            # 'multiArea': '10_20,20_30,30_40',  # (坪數) 10-20坪 & 20-30坪 & 30-40坪
            # 'area': '20,50',  # (自訂坪數範圍) 20~50坪
            # 'multiFloor': '2_6',  # (樓層) 2-6層
            # 'option': 'cold,washer,bed',  # (設備) 有冷氣 & 有洗衣機 & 床
            # 'multiNotice': 'all_sex',  # (須知) 男女皆可
        }
        # 排序依據
        sort_params = {
            # 租金由小到大
            # 'order': 'money',  # posttime, area
            # 'orderType': 'desc'  # asc
        }
        total_count, houses = house591_spider.search(filter_params, sort_params, want_page=wantPage) #746
        print('搜尋結果房屋總數：', total_count)
        

    show_notification('爬蟲爬完溜！')
    # with open('house.json', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(houses))

    # house_detail = house591_spider.get_house_detail(houses[0]['post_id'])
    # house_detail = house591_spider.get_house_detail(houses[0]['houseid'])

    # print(house_detail)

    
