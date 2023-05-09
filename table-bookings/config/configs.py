from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    # 업로드된 파일들이 media 디렉터리에 저장되도록 설정
    location = "media"
    # 업로드할 때 똑같은 파일이 있으면 overwrite 하지 않도록 설정
    file_overwrite = False
