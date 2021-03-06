## アプリケーション概要

- 英語で書かれているHTMLファイルよりテキストに出現する英単語で単語データを作成します。データには、単語名、語義、品詞、出現頻度が含まれます。



## ホスト先URL

- https://www.wordbook-generator.net/



## 使用した技術と機能一覧

### 技術スタック

- Django verion=3.2
- Postgresql version12
- pythonのCeleryライブラリ
- ブローカーにRabbitMQ
- SemanticUIによるスタイリング
- Digital OceanのUbuntu Server Droplet上にてNginxによるリバースプロキシとguniornによるアプリケーションサーバを構築
- nltkライブラリで英語ドキュメントのトークン化、正規化などの自然言語処理
- pandasまたはdjango-pandasライブラリでデータ加工

### 機能一覧

#### アプリケーション

- ファイルアップロードと保存
- 時間のかかる自然言語処理部分やデータ分析部分をPythonのジョブキューシステムであるCeleryにタスクとして実行
- 以下はCeleryワーカーとブローカの関係の図である。
![](celery.svg)
- タスクの結果とファイルダウンロード機能。

#### 自然言語処理

- 英語ドキュメントのトークン化。ex: Do you know cat I don't know cat
- ステミング処理。具体的には活用形語尾の除去や複数形を単数形にする処理。ex: doing -> do, stopped->stop
- レマタイズ処理。具体的には品詞によって不規則な活用する単語の見出し語化。ex: ate -> eat, better->good
- ストップワード除去。be動詞やyou, Iなどどのような文書で出現する一般的な単語を除去。



## アプリケーション作成背景、目的

- Webで英語のドキュメントを読むことで日本語だけでの情報収集と比べて、圧倒的な情報量を得ることができる。一方で、日本人が英文を読みこなすための壁の一つとして語彙の問題が一番最初に存在している。
- そこで、多くの人が学生時代に行っていた単語帳を用いた学習方法を簡単に導入するためにHTMLベースのドキュメントから簡単に単語帳を作れる、そんなアプリケーションが必要であると考えた。


## 使い方

- ソースコードを取得
```
git clone https://github.com/Koki-Sato-Daito/wordbook_generator.git
cd wordbook_generator
```

- dockerコンテナ構築、起動
```
$ docker-compose up --build -d
```

- Pythonライブラリのインストール
```
$ docker-compose exec python bash
# tmux
# python3 -m venv venv
# source venv/bin/activate
# pip install -r requirements.txt
```

- nltkのデータダウンロード
```
# python
>>> import nltk
>>> nltk.download('punkt')
>>> nltk.download('wordnet')
>>> nltk.download('averaged_perceptron_tagger')
>>> nltk.download('stopwords')
>>> nltk.download('omw-1.4')
```

- 環境変数をセット。シークレットキーには[こちら](https://miniwebtool.com/ja/django-secret-key-generator/)を使います。
```
# vi .env
SECRET_KEY=xxxxxxxxxxxxx
ALLOWED_HOSTS=*
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672
CELERY_RESULT_BACKEND=django-db
```

- マイグレーション、サーバ起動
```
そのままコンテナ内で
# python manage.py migrate --settings=wordbook_generator.settings.development
# vi wordbook_generator/celery.py
- os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'wordbook_generator.settings.production')
+ os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'wordbook_generator.settings.development')
以上に変更してから

# celery -A wordbook_generator worker --loglevel=INFO

tmuxのペインを追加させて(デフォルトはCtrl+bを押して%)
# source venv/bin/activate
# python manage.py runserver 0.0.0.0:8000 --settings=wordbook_generator.settings.development
```
- http://localhost:8000/ でアクセス可能です。



## パッケージ構成
![](uml.svg)