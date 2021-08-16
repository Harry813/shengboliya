from .data.area_list import area_list
from .models import Location


def add_area_to_db():
    for a in area_list:
        province = Location(code=a["provinceCode"], name=a["provinceName"], level=1)
        province.save()
        print("{} 已添加！".format(str(province)))
        for b in a["mallCityList"]:
            city = Location(code=b["cityCode"], name=b["cityName"], parent=province, level=2)
            city.save()
            print("{} 已添加！".format(str(city)))
            for c in b["mallAreaList"]:
                district = Location(code=c["areaCode"], name=c["areaName"], parent=city, level=3)
                district.save()
                print("{} 已添加！".format(str(district)))
