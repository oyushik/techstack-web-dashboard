[English](./README.md) | [한국어](./README.ko.md) | [日本語](./README.ja.md)

---

# 🚀 IT採用情報分析ダッシュボード

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

韓国の主要IT採用プラットフォーム（Wanted、Jumpit、Rallit）から収集した採用公告データを分析し、視覚化するインタラクティブダッシュボードです。リアルタイムの技術スタックトレンド分析と関連学習資料の推薦機能を提供します。

![Dashboard Preview](data/wordcloud_TECH_STACK.png)

## 📋 プロジェクト概要

- **開発期間**: 2025.04.16 ~ 2025.04.22
- **チーム構成**: 3名 (Backend 2名, Frontend 1名)

## 👥 チーム構成と役割

| 役割         | 名前       | 担当業務                               | GitHub                                      |
| ------------ | ---------- | ---------------------------------------------- | ------------------------------------------- |
| **Backend**  | オ・ユシク   | チームリーダー、プロジェクト企画、データ収集・精製 | [oyushik](https://github.com/oyushik)       |
| **Backend**  | キム・ウジュン | データ視覚化、ダッシュボード連携・最適化 | [Ra1nJun](https://github.com/Ra1nJun)       |
| **Frontend** | キム・ミンジョン | Webダッシュボード実装、UI/UX改善 | [Mineong](https://github.com/Mineong) |

## ✨ 主な機能

- 📊 **技術スタックトレンド分析**: TOP 20の技術スタックをインタラクティブなグラフで視覚化
- 🔍 **職務別分析**: 全体/バックエンド/フロントエンドの職群別データフィルタリング
- 🎯 **スキルベース検索**: 特定の技術スタックやキーワードで採用公告を検索
- 📺 **学習資料推薦**: 選択した技術のYouTubeチュートリアルを自動検索
- 💼 **リアルタイム採用情報**: Work24 API連携で関連採用公告を表示
- 📈 **データ視覚化**: Plotlyベースの動的チャートおよびワードクラウド

## 🏗️ プロジェクト構造

```
project-data-scraping/
├── src/
│   ├── scrapers/              # データ収集
│   │   ├── data_utils.py      # 共通ユーティリティ
│   │   └── notebooks/         # スクレイピングJupyterノートブック
│   ├── processing/            # データ前処理
│   │   └── csv_merge.py       # CSVマージと重複排除
│   ├── visualization/         # データ視覚化
│   │   └── notebooks/         # 視覚化ノートブック
│   └── dashboard/             # Streamlitダッシュボード
│       ├── app.py             # メインアプリケーション
│       ├── charts.py          # チャート生成
│       ├── data_loader.py     # データローディング
│       ├── renderer.py        # UIレンダリング
│       └── search/            # 外部API検索
│           ├── youtube.py
│           └── work24.py
├── data/                      # データファイル
├── requirements.txt           # Python依存関係
└── README.md
```

## 🚦 始め方

### 必須要件

- Python 3.9 以上
- pip パッケージマネージャー

### インストール

1.  **リポジトリをクローン**
    ```bash
    git clone https://github.com/your-username/project-data-scraping.git
    cd project-data-scraping
    ```

2.  **依存関係をインストール**
    ```bash
    pip install -r requirements.txt
    ```

3.  **環境変数を設定** (任意)

    APIを使用するには、`.env`ファイルを作成し、APIキーを追加してください:
    ```bash
    YOUR_YOUTUBE_API_KEY=your_api_key_here
    YOUR_WORK24_API_KEY=your_api_key_here
    ```

### ダッシュボードの実行

```bash
streamlit run src/dashboard/app.py
```

ブラウザで `http://localhost:8501` にアクセスすると、ダッシュボードを確認できます。

### 外部アクセスを許可 (オプション)

```bash
streamlit run src/dashboard/app.py --server.address=0.0.0.0 --server.port=8501
```

## 📊 データ収集と処理

### 1. データスクレイピング

Jupyterノートブックを使用して、各採用プラットフォームからデータを収集します:

- `src/scrapers/notebooks/scraping_wanted.ipynb` - Wanted
- `src/scrapers/notebooks/scraping_jumpit.ipynb` - Jumpit
- `src/scrapers/notebooks/scraping_rallit.ipynb` - Rallit

各ノートブックで職群(`total`, `backend`, `frontend`)を選択して実行します。

### 2. データマージ

収集したCSVファイルをマージし、重複を排除します:

```bash
python src/processing/csv_merge.py
```

マージされたファイルは `data/merged_data_{category}.csv` 形式で保存されます。

### 3. データ視覚化

ワードクラウドやその他の視覚化を生成します:

- `src/visualization/notebooks/visualization_wordcloud.ipynb`
- `src/visualization/notebooks/visualization_graph.ipynb`

## 🎯 主な機能の使い方

### 技術スタック分析

1.  ダッシュボードで **"🧩 技術スタック分析"** タブを選択
2.  全体/バックエンド/フロントエンドボタンで職群をフィルタリング
3.  グラフのバーをクリックして、該当技術の詳細情報を確認

### スキル検索

1.  サイドバーの **"代表スキル選択"** ドロップダウンを使用
2.  または、 **"キーワード検索"** 入力欄に直接入力
3.  選択したスキルのYouTubeチュートリアルと採用公告が自動的に表示されます

### データフィルタリング

- **要約情報**: 選択したキーワード関連の公告数と企業数を表示
- **職務分析**: 関連職務TOP 20チャート
- **データテーブル**: ページネーション機能付きの詳細データテーブル

## 🔧 技術スタック

### データ収集 & 処理
- **Python 3.9+**: メイン言語
- **Pandas**: データ処理と分析
- **Requests**: HTTPリクエスト

### ダッシュボード
- **Streamlit**: Webアプリケーションフレームワーク
- **Plotly**: インタラクティブチャート作成

### 外部API
- **YouTube Data API v3**: チュートリアル検索
- **Work24 API**: 採用情報照会

## 📝 データ構造

### CSVファイル形式

収集されたデータには、次のカラムが含まれます:

| カラム名 | 説明 |
|-------------|-------------|
| `company`   | 会社名 |
| `position`  | 職務/ポジション |
| `skill`     | 要求技術スタック (カンマ区切り) |

### スキルデータ精製

`data_utils.py`の`filter_skill_data()`関数が次の作業を実行します:

- ハングル文字の削除
- 特殊文字の整理 (# と + を除く)
- 重複スキルの削除
- 正規化された形式に変換

## 🤝 貢献する

貢献はいつでも大歓迎です！次の手順に従ってください:

1.  プロジェクトをフォークする
2.  機能ブランチを作成する (`git checkout -b feature/AmazingFeature`)
3.  変更をコミットする (`git commit -m 'Add some AmazingFeature'`)
4.  ブランチにプッシュする (`git push origin feature/AmazingFeature`)
5.  プルリクエストを開く

## 📄 ライセンス

このプロジェクトはMITライセンスの下で配布されています。詳細については、[LICENSE](LICENSE)ファイルを参照してください。

## 🔗 参考資料

- [Streamlit Documentation](https://docs.streamlit.io)
- [Plotly Python](https://plotly.com/python/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## 📮 お問い合わせ

プロジェクトに関する質問や提案がある場合は、Issueを作成してください。

---
