import { Amplify } from "aws-amplify";

import {
  Authenticator,
  Button,
  Card,
  Flex,
  Grid,
  TextField,
  useAuthenticator,
} from "@aws-amplify/ui-react";
import "@aws-amplify/ui-react/styles.css";

import awsExports from "../amplify_outputs.json";
import { useEffect, useState } from "react";
Amplify.configure(awsExports);

function AppInternal() {
  const { route, updateForm, submitForm, totpSecretCode, username } =
    useAuthenticator((context) => [
      context.route,
      context.updateForm,
      context.submitForm,
      context.totpSecretCode,
      context.username,
    ]);

  const [customTotpCode, setCustomTotpCode] = useState("");

  // コードを送信する
  const sendConfirmationCode = (userName: string, totpCode: string) => {
    fetch(`${import.meta.env.VITE_ENDPOINT_URL}/verificate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: userName,
        totp_key: totpCode,
      }),
    })
      .then((response) => response.json())
      .then(({ otp }) => {
        updateForm({ name: "confirmation_code", value: otp });
        submitForm();
      });
  };

  // MFA入力画面であればTrueを返す
  const isMfaView = (routeName: string) => {
    return routeName === "confirmSignIn" || routeName === "setupTotp"
      ? true
      : false;
  };

  // MFAコードの送信リクエストを送信する
  const sendMfaRequest = (userName: string, secretKey: string | null) => {
    // 送信データを定義する
    const sendParameter: Record<string, string> = {
      user_id: userName,
    };
    if (secretKey !== null) {
      sendParameter["secret_key"] = secretKey;
    }
    // APIGatewayにリクエストを送信する
    fetch(`${import.meta.env.VITE_ENDPOINT_URL}/totp`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(sendParameter),
    })
      .then((response) => response.json())
      .then(() => {});
  };

  // 画面遷移の完了時にMFA送信リクエストを投げる
  useEffect(() => {
    if (isMfaView(route)) {
      if (route === "confirmSignIn") {
        sendMfaRequest(username, null);
      } else if (route === "setupTotp" && totpSecretCode !== null) {
        sendMfaRequest(username, totpSecretCode);
      }
    }
  }, [route, username, totpSecretCode]);

  return (
    <>
      {isMfaView(route) && (
        <Grid>
          <Card
            variation="outlined"
            style={{
              width:
                "var(--amplify-components-authenticator-container-width-max)",
              placeSelf: "center",
              padding: "32px",
            }}
          >
            <Flex direction="column">
              <TextField
                value={customTotpCode}
                onChange={(e) => setCustomTotpCode(e.currentTarget.value)}
                label="TOTPコード"
              />
              <Button
                variation="primary"
                isFullWidth
                onClick={() => {
                  sendConfirmationCode(username, customTotpCode);
                }}
              >
                TOTPコードを送信
              </Button>
              <Button
                variation="link"
                isFullWidth
                onClick={() => {
                  sendMfaRequest(username, null);
                }}
              >
                コードを再送信する
              </Button>
            </Flex>
          </Card>
        </Grid>
      )}
      <Authenticator className={isMfaView(route) ? "authClassName" : ""}>
        {({ signOut }) => (
          <>
            認証が通りました！！
            <Button variation="primary" onClick={() => signOut && signOut()}>
              ログアウト
            </Button>
          </>
        )}
      </Authenticator>
    </>
  );
}

export default function App() {
  return (
    <Authenticator.Provider>
      <AppInternal />
    </Authenticator.Provider>
  );
}
