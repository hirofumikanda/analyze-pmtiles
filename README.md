# PMTiles解析ツール

PMTilesファイルの詳細な解析を行い、構造化されたマークダウンレポートを生成するPythonツールです。

## 概要

PMTiles（Protomaps Tiles）は、地理空間タイルの現代的なアーカイブ形式です。このツールは、PMTilesファイルから以下の詳細情報を抽出・分析します：

- **基本メタデータ**: ファイルサイズ、ズーム範囲、地理的境界
- **レイヤー詳細**: レイヤーの構造、フィーチャー数、属性情報
- **ズームレベル分析**: レベル別のタイル分布、密度、データサイズ
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

### 基本的な使用方法

```bash
python analyze-pmtiles.py <pmtiles_file_path>
```

### 使用例

```bash
python analyze-pmtiles.py contour.pmtiles
```

## 出力例

ツールは以下のような構造化されたマークダウンレポートを生成します：

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

## ズームレベル分析

| ズーム | 理論最大 | 実際数 | 密度   | データサイズ | 平均タイルサイズ |
|--------|----------|--------|--------|--------------|------------------|
| 0      | 1        | 1      | 100.0% | 4.93 KB      | 4.93 KB          |
| 1      | 1        | 1      | 100.0% | 9.09 KB      | 9.09 KB          |
...
```

## ライセンス

MIT

## 関連リンク

- [PMTiles仕様](https://github.com/protomaps/PMTiles)
- [Tabulate](https://pypi.org/project/tabulate/) - テーブル整形ライブラリ