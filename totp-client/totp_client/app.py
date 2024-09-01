import json
from pydantic import BaseModel, Field
import boto3
from botocore.exceptions import ClientError
import os
import what3words
import random
import datetime
from typing import Optional


class Input(BaseModel):
    secret_key: Optional[str] = Field(None)
    user_id: str


sns_client = boto3.client("sns")
dynamodb_client = boto3.client("dynamodb")


def lambda_handler(event, context):

    input = Input.model_validate_json(event["body"])
    topic_arn = os.environ.get("SNS_TOPIC_ARN")
    api_key = os.environ.get("WHAT3WORDS_API_KEY")
    table_name = os.environ.get("DYNAMODB_TABLE_NAME")

    geocoder = what3words.Geocoder(api_key=api_key, language="ja")
    words = geocoder.convert_to_3wa(
        what3words.Coordinates(
            lat=random.random() * 180 - 90.0,  # 緯度をランダムに生成
            lng=random.random() * 360 - 180.0,  # 経度をランダムに生成
        )
    )

    # シークレットキーを更新する
    if (input.secret_key is not None) and (len(input.secret_key) >= 1):
        try:
            # シークレットキーをDynamoDBに登録する
            dynamodb_client.put_item(
                TableName=table_name,
                Item={
                    "user_id": {"S": input.user_id},
                    "secret_key": {"S": input.secret_key},
                },
                # 初回更新が登録済みなら、登録リクエストを無視する
                ConditionExpression="attribute_not_exists(protected)",
            )
        except ClientError as e:
            print(e)

    # ワンタイムパスワードの期限を設定する
    expired = datetime.datetime.now() + datetime.timedelta(minutes=60)
    expired_timestamp = str(expired.timestamp())

    # ワンタイムパスワードをDynamoDBに登録する
    dynamodb_client.update_item(
        TableName=table_name,
        Key={"user_id": {"S": input.user_id}},
        AttributeUpdates={
            "words": {"Value": {"S": words["words"]}},
            "expired_time": {"Value": {"N": expired_timestamp}},
        },
    )

    # ワンタイムパスワードをSMSで送信する
    sns_client.publish(
        TopicArn=topic_arn,
        Message=f"ワンタイムパスワードは「{words['words']}」です",
        Subject="OTP",
    )

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
                "message": "ok",
            }
        ),
    }
