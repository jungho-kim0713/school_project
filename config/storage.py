import os
import oci
import logging
from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.core.files.base import ContentFile
import mimetypes

# 시스템 로그(journalctl)에 출력하기 위한 로거 설정
logger = logging.getLogger('django')

@deconstructible
class OCIStorage(Storage):
    """
    OCI Native SDK를 사용하는 Django 커스텀 스토리지 백엔드 (디버깅 강화판)
    """
    def __init__(self, option=None):
        try:
            # 1. 설정 로드
            self.config_profile = "DEFAULT"
            
            # [수정] 서버 경로와 로컬 경로 모두 확인
            server_config = "/home/ubuntu/.oci/config"
            local_config = os.path.expanduser("~/.oci/config")
            
            if os.path.exists(server_config):
                self.config_path = server_config
            elif os.path.exists(local_config):
                self.config_path = local_config
            else:
                if settings.DEBUG:
                    logger.warning("⚠️ [Local Dev] OCI Config 파일을 찾을 수 없어 더미 모드로 동작합니다.")
                    self.object_storage = None
                    # [Fix] 조기 리턴 시에도 필수 속성은 반드시 채워야 함
                    self.namespace = "dummy_namespace"
                    self.bucket_name = "dummy_bucket"
                    self.region = "ap-chuncheon-1"
                    return
                else:
                    raise FileNotFoundError(f"🚨 OCI Config 파일을 찾을 수 없습니다: {server_config}")

            logger.info(f"🔧 [OCI Init] 설정 파일 경로: {self.config_path}")

            self.config = oci.config.from_file(self.config_path, self.config_profile)
            self.object_storage = oci.object_storage.ObjectStorageClient(self.config)
            
            # 2. 버킷 정보
            self.namespace = settings.OCI_NAMESPACE
            self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            self.region = self.config['region']
            
            logger.info(f"🔧 [OCI Init] 연결 준비 완료: Bucket={self.bucket_name}, Namespace={self.namespace}")

        except Exception as e:
            if settings.DEBUG:
                logger.error(f"❌ [OCI Init Error] 초기화 실패 (로컬 디버그 모드라 무시함): {e}")
                self.object_storage = None
                self.namespace = "dummy_namespace"
                self.bucket_name = "dummy_bucket"
                self.region = "ap-chuncheon-1"
            else:
                logger.error(f"❌ [OCI Init Error] 초기화 실패: {e}")
                raise e

    def _open(self, name, mode='rb'):
        if not self.object_storage:
             return ContentFile(b"dummy content")
        response = self.object_storage.get_object(self.namespace, self.bucket_name, name)
        return ContentFile(response.data.content)

    def _save(self, name, content):
        if not self.object_storage:
            logger.warning(f"⚠️ [Dummy Save] OCI가 연결되지 않아 저장을 건너뜁니다: {name}")
            return name

        try:
            # 1. 파일 데이터 읽기
            content.seek(0)
            file_data = content.read()
            file_size = len(file_data)
            
            logger.info(f"🚀 [OCI Upload 시작] 파일명: {name}, 크기: {file_size} bytes")
            logger.info(f"🎯 [Target] Namespace: {self.namespace}, Bucket: {self.bucket_name}")

            # 2. MIME 타입 추론
            content_type, _ = mimetypes.guess_type(name)
            if not content_type:
                content_type = 'application/octet-stream'

            # 3. OCI 업로드 (PutObject)
            self.object_storage.put_object(
                self.namespace,
                self.bucket_name,
                name,
                file_data,
                content_type=content_type
            )
            logger.info(f"✅ [OCI Upload 요청 완료] PutObject 호출 성공")

            # 4. [중요] 현장 검증: 진짜 올라갔는지 바로 확인
            try:
                self.object_storage.head_object(self.namespace, self.bucket_name, name)
                logger.info(f"🔍 [검증 성공] 파일이 확실히 존재합니다: {name}")
            except Exception as check_e:
                logger.error(f"😱 [검증 실패] 업로드 직후 파일을 찾을 수 없습니다! 에러: {check_e}")
                raise Exception(f"업로드 검증 실패: 파일이 OCI에 생성되지 않았습니다. ({check_e})")

            return name

        except Exception as e:
            logger.error(f"❌ [OCI Upload Error] 업로드 중 치명적 오류: {e}")
            raise e

    def delete(self, name):
        if not self.object_storage:
            return
        try:
            self.object_storage.delete_object(self.namespace, self.bucket_name, name)
        except Exception:
            pass

    def exists(self, name):
        if not self.object_storage:
            return False
        try:
            self.object_storage.head_object(self.namespace, self.bucket_name, name)
            return True
        except oci.exceptions.ServiceError as e:
            if e.status == 404:
                return False
            raise e

    def url(self, name):
        # 공개 버킷 URL 생성
        return f"https://objectstorage.{self.region}.oraclecloud.com/n/{self.namespace}/b/{self.bucket_name}/o/{name}"
        