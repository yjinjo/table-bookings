import hashlib
import uuid

from web.models import RestaurantTable


def create_email_key(user_id):
    random_key = str(uuid.uuid4())
    # 복호화할 필요가 없으므로 단방향 암호화 알고리즘인 sha256을 사용합니다.
    sha_data = hashlib.sha256()
    sha_data.update(str(user_id).encode("utf-8"))
    # byte code를 16진수로 바꿉니다.
    hash_key = sha_data.hexdigest()

    # uuid의 경우 가능성은 매우 적지만 중복되는 경우가 있을 수 있으므로 hash_key를 더해
    # 고유성을 높여줍니다.
    return random_key[::2] + hash_key[::2]


def convert_weekday(weekday_value):
    """해당 숫자를 클래스 타입으로 변환하는 함수"""
    if weekday_value == 0:
        return RestaurantTable.Weekday.MONDAY
    elif weekday_value == 1:
        return RestaurantTable.Weekday.TUESDAY
    elif weekday_value == 2:
        return RestaurantTable.Weekday.WEDNESDAY
    elif weekday_value == 3:
        return RestaurantTable.Weekday.THURSDAY
    elif weekday_value == 4:
        return RestaurantTable.Weekday.FRIDAY
    elif weekday_value == 5:
        return RestaurantTable.Weekday.SATURDAY
    elif weekday_value == 6:
        return RestaurantTable.Weekday.SUNDAY
