# Sudoku Solver

数独パズルを解くための Python アプリケーションです。

AI に指示して、ほとんどのコードを書いてもらいました。これが流行りのバイブコーディング？？

GUI モードとコンソールモードの両方で動作し、数独の自動生成や解答速度の調整機能を備えています。

Python の環境を整えるのが難しい方向けに Windows 上で動作する exe ファイルも用意しました。

---

## 特徴

- 数独パズルの解答機能
- 数独問題の自動生成（難易度：簡単、普通、難しい、ランダム）
- 解答速度を調整可能なスライダー付き GUI
- コンソールモードでの操作もサポート
- 日本語と英語の多言語対応
- ファイル保存・読み込み機能

---

## リリース版ダウンロード

最新のリリースは[Releases](https://github.com/groove-on-vibe-coding/sudoku_solver/releases)ページからダウンロードできます。各バージョンには以下が含まれます:

- Windows 用実行ファイル（`sudoku_solver_vX.Y.Z_win64.zip`）
- リリースノート
- サンプル数独問題

### リリースノート

各バージョンのリリースノートは `releases/vX.Y.Z/README.md` にあります。リリースノートには、新機能や修正点、そのバージョン特有の情報が記載されています。

---

## Windows 向け実行ファイル

Python の環境を整えるのが難しい場合、Windows 用の実行ファイルを使用することができます。

1. [Releases](https://github.com/groove-on-vibe-coding/sudoku_solver/releases)ページから最新版の `sudoku_solver_vX.Y.Z_win64.zip` をダウンロードします。
2. ZIPファイルを解凍し、`sudoku_solver.exe` をダブルクリックして実行します。
3. GUI モードが起動し、数独パズルを解くことができます。

### 注意事項

- 実行ファイルは Windows 環境でのみ動作します。
- コンソールモードは実行できません。常に GUI モードで起動します。
- 実行ファイルを使用する場合、Python や追加のライブラリをインストールする必要はありません。
- セキュリティソフトによって警告が表示される場合がありますが、これは一般的な現象です。信頼できる環境でのみ使用してください。

---

## 必要条件

このプロジェクトを実行するには、以下のソフトウェアが必要です：

- Python 3.8 以上
- [pygame](https://www.pygame.org/) (LGPL ライセンス)

### 注意事項

動作確認は Windows でしか行っていません。

---

## インストール

1. このリポジトリをクローンします：

   ```bash
   git clone https://github.com/groove-on-vibe-coding/sudoku_solver.git
   cd sudoku_solver
   ```

2. 必要なライブラリをインストールします：

   ```bash
   pip install pygame
   ```

---

## 使い方

### GUI モード

以下のコマンドで GUI モードを起動します：

```bash
cd ./src
python main.py
```

あらかじめ問題を読み込んで起動する場合：
```bash
cd ./src
python main.py <数独ファイルのパス>
```

#### 盤面の保存

保存ボタンをクリックすることで盤面を保存することができます。
GUI で問題を生成し、問題を保存したいときに使ってください。
解答済みの盤面を保存することもできます。

### コンソールモード

コンソールモードで数独を解く場合は、以下のコマンドを使用します：

```bash
cd ./src
python main.py --console <数独ファイルのパス>
```

数独ファイルは、以下のようなテキスト形式です。空のマスは、`0` にしてください。
```
006700300
010008020
000090004
040800009
007000100
300002050
700010000
050400060
002003500
```

#### 数独問題の自動生成

数独問題を自動生成して保存するには、以下のコマンドを使用します。
問題を一度に大量に生成したいときに利用してください。

```bash
python src/main.py --generate <生成する問題数> --difficulty <難易度>
```
難易度は、`easy`, `medium`, `hard`, `random` で指定できます。

例：

```bash
python src/main.py --generate 5 --difficulty medium
```

### 言語設定

アプリケーションは日本語と英語に対応しています。言語を切り替えるには以下の方法があります：

1. `ui_setting.json` ファイルを編集する：
   ```json
   {
     "language": "ja"  // "ja" for Japanese, "en" for English
   }
   ```

2. コマンドライン引数で指定する：
   ```bash
   python src/main.py --language en  # 英語で起動
   python src/main.py --language ja  # 日本語で起動
   ```

コマンドライン引数は設定ファイルよりも優先されます。

---

## 設定

UI 設定は `ui_setting.json` ファイルで管理されています。このファイルを編集することで、ウィンドウサイズや色、言語などをカスタマイズできます。

### 多言語対応

言語ファイルは `src/lang` ディレクトリに保存されています。現在は以下の言語に対応しています：

- 日本語 (`ja.json`)
- 英語 (`en.json`)

新しい言語を追加するには、既存の言語ファイルをコピーして翻訳し、`ui_setting.json` の `language` 設定を更新してください。

---

## ビルドとリリース（開発者向け）

### 実行ファイルのビルド

```bash
pip install pyinstaller
pyinstaller .\src\main.py --paths=.\src --onefile --noconsole --name=sudoku_solver
```

### リリースの作成

PowerShell スクリプト `release.ps1` を使用して、リリースパッケージを自動作成できます：

```bash
.\release.ps1 -releaseNoteFile .\release_notes\v1.0.0.md
```

このスクリプトは以下の処理を行います：
- リリースノートからバージョン情報を抽出
- PyInstaller を使用した実行ファイルのビルド
- サンプル問題の作成
- 必要なファイルのコピーと整理
- ZIP パッケージの作成
- `releases/vX.Y.Z/` ディレクトリへのファイルの配置

### リリースフォルダ構成

```
releases/
└── v1.0.0/
    ├── sudoku_solver.exe       # 実行ファイル
    ├── ui_setting.json         # UI 設定
    ├── lang/                   # 言語ファイル
    │   ├── en.json
    │   └── ja.json
    ├── sample_easy.txt         # サンプル問題
    ├── sample_medium.txt
    ├── sample_hard.txt
    ├── LICENSE                 # ライセンス
    ├── README.md               # リリースノート
    └── sudoku_solver_v1.0.0_win64.zip  # 配布用 ZIP パッケージ
```

---

## ライセンス

このプロジェクトは [MIT ライセンス](LICENSE) の下で公開されています。

---

## その他

バグ報告や機能リクエストは [Issues](https://github.com/groove-on-vibe-coding/sudoku_solver/issues) で受け付けています。
