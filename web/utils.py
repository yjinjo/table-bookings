import hashlib
import uuid


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
