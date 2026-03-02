"""
OCI Object Storage — 아바타 이미지 Pre-Authenticated Request(PAR) 생성.

배포 환경에서 OCI SDK 설정:
  - ~/.oci/config 파일 또는
  - Instance Principal (OCI VM 내부에서 자동 인증)

로컬 개발:
  - OCI_NAMESPACE 환경변수가 없으면 자동으로 mock 모드 동작
  - PUT /api/v1/dev/avatars/{user_id} → static/avatars/ 로컬 저장
"""
import os
from datetime import datetime, timedelta, timezone

OCI_NAMESPACE = os.getenv("OCI_NAMESPACE", "")
OCI_BUCKET_NAME = os.getenv("OCI_BUCKET_NAME", "zipsa-avatars")
OCI_REGION = os.getenv("OCI_REGION", "ap-chuncheon-1")
DEV_BASE_URL = os.getenv("DEV_BASE_URL", "http://localhost:8000")


async def generate_avatar_par(user_id: str) -> dict:
    """OCI Object Storage Pre-Authenticated Request(PAR) URL 생성.

    OCI_NAMESPACE 미설정 시 로컬 mock 모드로 동작합니다.

    Args:
        user_id: 유저 ID (오브젝트 키 prefix로 사용)

    Returns:
        {"upload_url": str, "avatar_url": str}
        - upload_url: 클라이언트가 PUT 요청으로 파일을 업로드할 URL (5분 유효)
        - avatar_url: 업로드 완료 후 공개 조회 URL
    """
    if not OCI_NAMESPACE:
        return {
            "upload_url": f"{DEV_BASE_URL}/api/v1/dev/avatars/{user_id}",
            "avatar_url": f"{DEV_BASE_URL}/static/avatars/{user_id}",
        }

    import oci  # type: ignore

    config = oci.config.from_file()
    client = oci.object_storage.ObjectStorageClient(config)

    key = f"avatars/{user_id}"
    expires = datetime.now(timezone.utc) + timedelta(minutes=5)

    par = client.create_preauthenticated_request(
        namespace_name=OCI_NAMESPACE,
        bucket_name=OCI_BUCKET_NAME,
        create_preauthenticated_request_details=oci.object_storage.models.CreatePreauthenticatedRequestDetails(
            name=f"avatar-{user_id}",
            object_name=key,
            access_type="ObjectWrite",
            time_expires=expires,
        ),
    )

    public_url = (
        f"https://objectstorage.{OCI_REGION}.oraclecloud.com"
        f"/n/{OCI_NAMESPACE}/b/{OCI_BUCKET_NAME}/o/{key}"
    )

    return {"upload_url": par.data.full_path, "avatar_url": public_url}
