import os
import re
from datetime import datetime

def convert_file(file_path, html_content):
    # <here></here>タグを探索
    here_pattern = r'<here>(.*?)</here>'
    here_match = re.search(here_pattern, html_content, re.DOTALL)

    if here_match:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # #title タグの置換
        title_pattern = r'#title\s*(.*)'
        title_match = re.search(title_pattern, content)
        if title_match:
            title = title_match.group(1)
            html_content = re.sub(r'<meta property="og:title" content=".*?"\s*/>', f'<meta property="og:title" content="{title}" />', html_content)
            html_content = re.sub(r'<h1 class="text-4xl font-bold text-gray-800">.*?</h1>', f'<h1 class="text-4xl font-bold text-gray-800">{title}</h1>', html_content)
            html_content = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', html_content)
            content = re.sub(title_pattern, '', content)

        # #description タグの置換
        description_pattern = r'#description\s*(.*)'
        description_match = re.search(description_pattern, content)
        if description_match:
            description = description_match.group(1)
            html_content = re.sub(r'<meta property="og:description" content=".*?"\s*/>', f'<meta property="og:description" content="{description}" />', html_content)
            html_content = re.sub(r'<p class="text-md text-gray-600">.*?</p>', f'<p class="text-md text-gray-600">{description}</p>', html_content)
            content = re.sub(description_pattern, '', content)

        # og:image の置換
        today = datetime.today()
        image_url = f'https://mizuame.works/blog/Card/Card_{today.strftime("%Y-%m-%d")}.png'
        html_content = re.sub(r'<meta property="og:image" content=".*?"\s*/>', f'<meta property="og:image" content="{image_url}" />', html_content)

        # og:url の置換
        url = f'https://mizuame.works/blog/{today.strftime("%Y-%m-%d")}/index.html'
        html_content = re.sub(r'<meta property="og:url" content=".*?"\s*/>', f'<meta property="og:url" content="{url}" />', html_content)

        # h2 タグの置換
        content = re.sub(r'#h2\((.*?)\)', r'<br><h2 class="text-3xl font-bold text-gray-800 mb-4">\1</h2><br>', content, flags=re.UNICODE)

        # text タグの置換
        content = re.sub(r'#text\s*(.*)', lambda x: '<p class="text-gray-700 mb-4">' + re.sub(r'<:>(.*?)<:>', r'<b class="font-bold text-blue-600">\1</b>', x.group(1), flags=re.UNICODE) + '</p>', content, flags=re.UNICODE)

        # link タグの置換
        content = re.sub(r'<a>(.*?)<:>(.*?)<a>', r'<a href="\2" class="text-blue-600 hover:underline">\1</a>', content, flags=re.UNICODE)

        # img タグの置換
        content = re.sub(r'#img\s*(.*?)<:>(.*)', r'<div class="image-container mb-4"><img src="\1" alt="\2" class="responsive-image"></div>', content, flags=re.UNICODE)

        # code タグの置換
        content = re.sub(r'#code\s*(.*?)<:>(.*?)(?=#|\Z)', r'<div class="copyable mb-4"><p>\1</p><pre><code>\2</code></pre><button onclick="copyToClipboard(this)" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-1 px-3 rounded">コピー</button></div>', content, flags=re.DOTALL | re.UNICODE)

        # strong タグの置換
        content = re.sub(r'#strong\s*(.*?)<:>(.*)', r'<div class="note mb-4"><strong>\1</strong> \2</div>', content, flags=re.UNICODE)

        # 変換後の要素をHTML内容に反映
        output_content = html_content.replace(here_match.group(0), content)

        new_file_path = os.path.splitext(file_path)[0] + '.html'
        with open(new_file_path, 'w', encoding='utf-8') as new_file:
            new_file.write(output_content)
    else:
        print("<here></here>タグが見つかりませんでした。")
        
# ファイルパスの入力を求める
mbs_file_path = input("変換するmbsファイルのパスを入力してください: ")

# バックスラッシュをスラッシュに置換
mbs_file_path = mbs_file_path.replace('\\', '/')

# 指定されたmbsファイルが存在するかチェック
while not os.path.isfile(mbs_file_path):
    print(f"Error: File '{mbs_file_path}' does not exist.")
    mbs_file_path = input("変換するmbsファイルのパスを入力してください: ")
    mbs_file_path = mbs_file_path.replace('\\', '/')

# HTMLファイルの内容を読み込む
html_file_path = 'index.html'  # HTMLファイルのパスを指定してください
with open(html_file_path, 'r', encoding='utf-8') as html_file:
    html_content = html_file.read()

# 指定されたmbsファイルを変換
convert_file(mbs_file_path, html_content)
print(f"変換が完了しました。出力ファイル: {os.path.splitext(mbs_file_path)[0] + '.html'}")