import pyotp
import json
from pydantic import BaseModel
import boto3
import os
import datetime


class Input(BaseModel):
    user_id: str
    totp_key: str


dynamodb_client = boto3.client("dynamodb")


def lambda_handler(event, context):

    input = Input.model_validate_json(event["body"])
    table_name = os.environ.get("DYNAMODB_TABLE_NAME")

    # DynamoDBからユーザー情報を取得する
    item = dynamodb_client.get_item(
        TableName=table_name,
        Key={"user_id": {"S": input.user_id}},
    )

    # OTPが期限切れ、または誤りであれば403を返す
    now = datetime.datetime.now().timestamp()
    expired_time = item.get("Item", {}).get("expired_time", {}).get("N", "0")
    words = item.get("Item", {}).get("words", {}).get("S", "")

    if now >= float(expired_time):
        return {
            "statusCode": 403,
            "body": json.dumps(
                {
                    "message": "Expired OTP",
                }
            ),
        }

    if words != input.totp_key:
        return {
            "statusCode": 403,
            "body": json.dumps(
                {
                    "message": "Invalid OTP",
                }
            ),
        }

    # 初回の認証が通ったのなら、ユーザー情報を保護する
    dynamodb_client.update_item(
        TableName=table_name,
        Key={"user_id": {"S": input.user_id}},
        AttributeUpdates={
            "protected": {"Value": {"BOOL": True}},
        },
    )

    # シークレットキーを元に、認証用のワンタイムパスワードを発行する
    secret_key = item.get("Item", {}).get("secret_key", {}).get("S", "")
    otp = pyotp.TOTP(secret_key).now()

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "http://localhost:5173",
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        "body": json.dumps(
            {
                "otp": otp,
            }
        ),
    }
