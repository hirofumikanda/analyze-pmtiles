# PMTiles解析ツール

PMTilesファイルの詳細な解析を行い、構造化されたマークダウンレポートを生成するPythonツールです。

## 概要

PMTiles（Protomaps Tiles）は、地理空間タイルの現代的なアーカイブ形式です。このツールは、PMTilesファイルから以下の詳細情報を抽出・分析します：

- **基本メタデータ**: ファイルサイズ、ズーム範囲、地理的境界
- **レイヤー詳細**: レイヤーの構造、フィーチャー数、属性情報
- **ズームレベル分析**: レベル別のタイル分布、密度、データサイズ（オプション）
- **ファイル構造**: PMTiles内部フォーマットの詳細分析

## 必要な環境

- Python 3.7+

## インストール

### 1. リポジトリのクローン

```bash
git clone https://github.com/hirofumikanda/analyze-pmtiles.git
cd read-pmtiles
```

### 2. 依存関係のインストール

```bash
pip install pmtiles==3.5.0 tabulate==0.9.0
```

## 使用方法

### 基本的な使用方法（高速）

```bash
python analyze-pmtiles.py <pmtiles_file_path>
```

### ズームレベル分析を含む詳細解析

```bash
python analyze-pmtiles.py -z <pmtiles_file_path>
# または
python analyze-pmtiles.py --zoom-analysis <pmtiles_file_path>
```

### ヘルプ表示

```bash
python analyze-pmtiles.py -h
```

### 使用例

```bash
# 基本解析（高速）
python analyze-pmtiles.py contour.pmtiles

# 詳細解析（ズームレベル分析を含む）
python analyze-pmtiles.py -z contour.pmtiles
```

## オプション

- `-z, --zoom-analysis`: ズームレベル分析を実行します。この分析は時間がかかる場合がありますが、各ズームレベルのタイル分布、密度、データサイズの詳細情報を提供します。

## 出力例

ツールは以下のような構造化されたマークダウンレポートを生成します：

### 基本解析の出力

```markdown
# PMTilesファイル解析レポート

**ファイル:** `dem_3857_contour.pmtiles`  
**サイズ:** 8.23 MB

## 基本情報

- **タイルセット名:** ./dem_3857_contour.mbtiles
- **生成ツール:** tippecanoe v2.78.0
- **タイル形式:** pbf
- **ズーム範囲:** 0 - 10
- **実タイル数:** 30
- **データサイズ:** 8.22 MB

## レイヤー詳細

### contour
- **ジオメトリタイプ:** LineString
- **フィーチャー数:** 23,139
- **属性数:** 2

## ファイル構造

| セクション        | サイズ   | 割合   |
|------------------|----------|--------|
| ヘッダー         | 127 B    | 0.00%  |
| ルートディレクトリ | 16 B     | 0.00%  |
| メタデータ       | 1.23 KB  | 0.01%  |
| リーフディレクトリ | 1.45 KB  | 0.02%  |
| タイルデータ     | 8.22 MB  | 99.97% |
| **総計**         | **8.23 MB** | **100.00%** |
```

### ズームレベル分析付きの出力（-zオプション使用時）

上記の基本情報に加えて、以下の詳細分析が追加されます：

```markdown
## ズームレベル分析

| ズーム | 理論最大 | 実際数 | 密度   | データサイズ | 平均タイルサイズ |
|--------|----------|--------|--------|--------------|------------------|
| 0      | 1        | 1      | 100.0% | 4.93 KB      | 4.93 KB          |
| 1      | 1        | 1      | 100.0% | 9.09 KB      | 9.09 KB          |
| 2      | 4        | 4      | 100.0% | 35.2 KB      | 8.80 KB          |
...
```

## ライセンス

MIT

## 関連リンク

- [PMTiles仕様](https://github.com/protomaps/PMTiles)
- [Tabulate](https://pypi.org/project/tabulate/) - テーブル整形ライブラリ