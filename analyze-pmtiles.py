from pmtiles.reader import Reader
import os
import json
from tabulate import tabulate

def format_bytes(bytes_value):
    """バイト数を人間が読みやすい形式に変換"""
    if bytes_value == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    while bytes_value >= 1024 and i < len(units) - 1:
        bytes_value /= 1024.0
        i += 1
    
    return f"{bytes_value:.2f} {units[i]}"

def parse_bounds(bounds_str):
    """境界文字列をパース"""
    try:
        return [float(x) for x in bounds_str.split(',')]
    except:
        return None

def analyze_pmtiles(filename, include_zoom_analysis=False):
    """PMTilesファイルの詳細解析"""
    if not os.path.exists(filename):
        print(f"エラー: ファイル '{filename}' が見つかりません。")
        return
    
    print(f"# PMTilesファイル解析レポート")
    print()
    print(f"**ファイル:** `{filename}`  ")
    print(f"**サイズ:** {format_bytes(os.path.getsize(filename))}")
    print()
    
    try:
        with open(filename, 'rb') as f:
            def get_bytes(offset, length):
                f.seek(offset)
                return f.read(length)
            
            reader = Reader(get_bytes)
            header = reader.header()
            
            # メタデータ解析
            metadata_info = {}
            try:
                metadata = reader.metadata()
                if metadata:
                    if isinstance(metadata, dict):
                        metadata_info = metadata
                    elif isinstance(metadata, (str, bytes)):
                        if isinstance(metadata, bytes):
                            metadata = metadata.decode('utf-8')
                        metadata_info = json.loads(metadata)
            except Exception as e:
                print(f"メタデータ解析エラー: {e}")
            
            # 基本情報表示
            print("## 基本情報")
            print()
            
            min_zoom = metadata_info.get('minzoom', getattr(header, 'min_zoom', None))
            max_zoom = metadata_info.get('maxzoom', getattr(header, 'max_zoom', None))
            
            # 型を確実にintに変換
            if min_zoom is not None:
                min_zoom = int(min_zoom)
            if max_zoom is not None:
                max_zoom = int(max_zoom)
            bounds_str = metadata_info.get('antimeridian_adjusted_bounds', '')
            bounds = parse_bounds(bounds_str)
            
            basic_info = [
                ["タイルセット名", metadata_info.get('name', 'N/A')],
                ["生成ツール", metadata_info.get('generator', 'N/A')],
                ["タイル形式", metadata_info.get('format', 'N/A')],
                ["ズーム範囲", f"{min_zoom} - {max_zoom}" if min_zoom is not None and max_zoom is not None else "N/A"],
                ["PMTilesバージョン", header.get('version', 'N/A')],
                ["実タイル数", f"{header.get('addressed_tiles_count', 0):,}"],
                ["データサイズ", format_bytes(header.get('tile_data_length', 0))],
            ]
            
            if bounds and len(bounds) == 4:
                basic_info.extend([
                    ["地理的範囲", f"{bounds[2] - bounds[0]:.4f}° × {bounds[3] - bounds[1]:.4f}°"],
                    ["中心点", f"{(bounds[0] + bounds[2]) / 2:.6f}°, {(bounds[1] + bounds[3]) / 2:.6f}°"],
                ])
            
            for item in basic_info:
                print(f"- **{item[0]}:** {item[1]}")
            print()
            
            # レイヤー詳細
            tilestats_layers = metadata_info.get('tilestats', {}).get('layers', [])
            if tilestats_layers:
                print("## レイヤー詳細")
                print()
                
                for i, layer in enumerate(tilestats_layers):
                    layer_name = layer.get('layer', f'Layer {i+1}')
                    print(f"### {layer_name}")
                    print()
                    print(f"- **ジオメトリタイプ:** {layer.get('geometry', 'N/A')}")
                    print(f"- **フィーチャー数:** {layer.get('count', 0):,}")
                    print(f"- **属性数:** {layer.get('attributeCount', 0)}")
                    
                    # 属性詳細
                    attributes = layer.get('attributes', [])
                    if attributes:
                        print(f"- **属性:**")
                        for attr in attributes:
                            attr_name = attr.get('attribute', 'N/A')
                            attr_type = attr.get('type', 'N/A')
                            attr_count = attr.get('count', 0)
                            attr_min = attr.get('min', 'N/A')
                            attr_max = attr.get('max', 'N/A')
                            print(f"  - `{attr_name}` ({attr_type}): {attr_count:,}個の値, 範囲 {attr_min} - {attr_max}")
                    print()
            
            # ズームレベル分析（オプション）
            if include_zoom_analysis and min_zoom is not None and max_zoom is not None:
                print("## ズームレベル分析")
                print()
                
                # 実際のタイル分布を計算
                def deg2num(lat_deg, lon_deg, zoom):
                    import math
                    lat_rad = math.radians(lat_deg)
                    n = 2.0 ** zoom
                    x = int((lon_deg + 180.0) / 360.0 * n)
                    y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
                    return (x, y)
                
                # E7座標から度に変換
                min_lon = header.get('min_lon_e7', 0) / 10000000.0
                max_lon = header.get('max_lon_e7', 0) / 10000000.0
                min_lat = header.get('min_lat_e7', 0) / 10000000.0
                max_lat = header.get('max_lat_e7', 0) / 10000000.0
                
                zoom_data = []
                for zoom in range(min_zoom, max_zoom + 1):
                    # 理論的なタイル範囲を計算
                    min_x, max_y = deg2num(min_lat, min_lon, zoom)
                    max_x, min_y = deg2num(max_lat, max_lon, zoom)
                    theoretical_count = (max_x - min_x + 1) * (max_y - min_y + 1)
                    
                    # 実際のタイル数をカウント（効率的にするため範囲を限定）
                    actual_count = 0
                    total_size = 0
                    
                    for x in range(min_x, max_x + 1):
                        for y in range(min_y, max_y + 1):
                            try:
                                tile_data = reader.get(zoom, x, y)
                                if tile_data:
                                    actual_count += 1
                                    total_size += len(tile_data)
                            except Exception:
                                continue
                    
                    if actual_count > 0:
                        density = (actual_count / theoretical_count) * 100 if theoretical_count > 0 else 0
                        avg_tile_size_zoom = total_size / actual_count
                    else:
                        density = 0
                        avg_tile_size_zoom = 0
                    
                    zoom_data.append([
                        zoom, 
                        f"{theoretical_count:,}", 
                        f"{actual_count:,}", 
                        f"{density:.1f}%",
                        format_bytes(total_size),
                        format_bytes(avg_tile_size_zoom)
                    ])
                
                print(tabulate(zoom_data, 
                    headers=["ズーム", "理論最大", "実際数", "密度", "データサイズ", "平均タイルサイズ"], 
                    tablefmt="pipe"))
                print()
            
            # ファイル構造
            print("## ファイル構造")
            print()
            
            file_size = os.path.getsize(filename)
            
            # ヘッダーから構造情報を取得
            root_length = header.get('root_length', 0)
            metadata_length = header.get('metadata_length', 0)
            leaf_directory_length = header.get('leaf_directory_length', 0)
            tile_data_length = header.get('tile_data_length', 0)
            
            structure_data = [
                ["セクション", "サイズ", "割合"],
                ["ヘッダー", format_bytes(127), f"{(127/file_size*100):.2f}%"],
                ["ルートディレクトリ", format_bytes(root_length), f"{(root_length/file_size*100):.2f}%"],
                ["メタデータ", format_bytes(metadata_length), f"{(metadata_length/file_size*100):.2f}%"],
                ["リーフディレクトリ", format_bytes(leaf_directory_length), f"{(leaf_directory_length/file_size*100):.2f}%"],
                ["タイルデータ", format_bytes(tile_data_length), f"{(tile_data_length/file_size*100):.2f}%"],
                ["**総計**", f"**{format_bytes(file_size)}**", "**100.00%**"],
            ]
            
            print(tabulate(structure_data, headers="firstrow", tablefmt="pipe"))
            print()
            
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='PMTilesファイルの詳細解析')
    parser.add_argument('pmtiles_file', help='解析するPMTilesファイルのパス')
    parser.add_argument('-z', '--zoom-analysis', action='store_true', 
                       help='ズームレベル分析を実行（時間がかかる場合があります）')
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    analyze_pmtiles(args.pmtiles_file, args.zoom_analysis)