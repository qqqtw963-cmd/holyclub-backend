import json

import boto3
from botocore.exceptions import ClientError


def get_secret(secret_id, aws_access_key_id=None, aws_secret_access_key=None):
    """
    AWS Secrets Manager에서 시크릿을 가져와 JSON으로 파싱합니다.

    Args:
        secret_id: 시크릿 ID
        aws_access_key_id: AWS 액세스 키 (선택)
        aws_secret_access_key: AWS 시크릿 키 (선택)

    Returns:
        dict: 파싱된 시크릿 데이터

    Raises:
        ClientError: AWS Secrets Manager 관련 에러
        ValueError: JSON 파싱 실패
    """
    client = boto3.client(
        service_name="secretsmanager",
        region_name="ap-northeast-2",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    try:
        response = client.get_secret_value(SecretId=secret_id)
        return json.loads(response["SecretString"])
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        # 에러 코드별 구체적인 메시지 제공
        error_messages = {
            "ResourceNotFoundException": f"시크릿 '{secret_id}'을(를) 찾을 수 없습니다.",
            "InvalidParameterException": f"잘못된 파라미터: {secret_id}",
            "InvalidRequestException": "잘못된 요청입니다.",
            "DecryptionFailureException": "시크릿 복호화에 실패했습니다.",
            "InternalServiceErrorException": "AWS 내부 서비스 오류가 발생했습니다.",
        }
        error_message = error_messages.get(error_code, f"알 수 없는 오류: {error_code}")
        raise ClientError({"Error": {"Code": error_code, "Message": error_message}}, "get_secret_value") from e
    except json.JSONDecodeError as e:
        raise ValueError(
            f"시크릿 '{secret_id}'의 JSON 파싱에 실패했습니다. "
            f"AWS Secrets Manager에서 시크릿 형식을 확인해주세요. "
            f"오류 위치: line {e.lineno}, column {e.colno}"
        ) from e
