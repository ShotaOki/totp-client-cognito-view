# プロジェクトのデプロイ方法

### API をデプロイする

totp-client のディレクトリで、以下のコマンドを実行してください

```bash
sam build
```

```bash
sam deploy --guided
```

SAM からメールアドレスと What3Words の API キーを聞かれますので、通知を受け取りたいメールアドレスを設定してください。  
※実際の運用では Cognito のフックでメールアドレスを登録するべきですが、今回は簡略のためにメールアドレスを固定します

What3Words 以外でワンタイムパスワードを生成する場合は、totp_client/app.py の 30 行目を変更、自身の作りたいワンタイムパスワードを指定してください。

### 画面を実行する

amplify-view/web のディレクトリで、以下のコマンドを実行してください

```bash
npm install
```

amplify-view/web に以下の内容の.env ファイルを作成してください  
URL は totp-client をデプロイして作成した APIGateway の URL を指定してください

```txt
VITE_ENDPOINT_URL=https://xxxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/Prod
```

また、Cognito を作成するため、以下の A,B いずれかの手順を踏んでください。

A.cloudformation にある template.yml をデプロイ、作成した情報を同じディレクトリにある amplify_outputs.json に書き込む  
書き込んだ amplify_output.json を amplify-view/web にコピーして配置する

B.amplify-view/web で、Amplify をデプロイする

### 実行する

以下のコマンドを実行して、サーバを立ち上げてください

```bash
npm run dev
```
