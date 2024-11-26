import os
import re
import requests  # 画像をダウンロードするために追加
from datetime import datetime
import markdown
from typing import Optional, Dict, Any

# HTMLテンプレートを直接スクリプト内に保持
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{description}" />
    <meta property="og:image" content="{og_image}" />
    <meta property="og:url" content="{og_url}" />
    <meta name="twitter:card" content="summary_large_image" />
    <title>{title}</title>
    <!-- Tailwind CSSの設定を追加 -->
    <script>
      tailwind.config = {{
        safelist: [
          'text-4xl', 'text-3xl', 'text-2xl', 'font-bold', 'text-gray-800', 'mb-4',
          'text-gray-700', 'bg-blue-600', 'hover:bg-blue-700', 'text-white',
          'py-1', 'px-3', 'rounded', 'copyable', 'mb-4', 'image-container',
          'responsive-image', 'blockquote', 'min-w-full', 'table-auto', 'border',
          'list-disc', 'list-decimal', 'list-inside', 'mb-2', 'mt-2', 'p-4',
          'bg-gray-100', 'rounded-lg', 'overflow-x-auto', 'my-12', 'mx-auto',
          'max-w-4xl', 'text-center', 'text-md', 'text-gray-600', 'bg-white',
          'p-8', 'rounded-lg', 'shadow', 'mb-12', 'bg-blue-50', 'hover:underline',
          'text-blue-600', 'mt-12', 'justify-center', 'flex', 'items-center',
          'fab', 'fa-twitter', 'fa-facebook-f', 'fas', 'fa-home'
        ],
      }}
    </script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <!-- Font Awesomeのリンクを修正 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <style>
        body {{
            font-family: 'Noto Sans JP', sans-serif;
        }}
        .copyable {{
            background: #f3f4f6;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            position: relative;
            margin-bottom: 1rem;
        }}
        .copyable button {{
            position: absolute;
            right: 10px;
            top: 10px;
        }}
        .note {{
            background: #fff3cd;
            border-left: 4px solid #ffeeba;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 1rem;
        }}
        .tag {{
            display: inline-block;
            background: #e2e8f0;
            border-radius: 9999px;
            padding: 0.25rem 0.75rem;
            font-size: 0.75rem;
            font-weight: 700;
            margin-right: 0.5rem;
            color: #1a202c;
        }}
        .share-buttons {{
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }}
        .share-button {{
            background: #edf2f7;
            color: #1a202c;
            padding: 8px;
            margin: 0 4px;
            border-radius: 9999px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .share-button i {{
            margin-right: 8px;
        }}
        .image-container {{
            margin-top: 20px;
            text-align: center;
        }}
        .responsive-image {{
            max-width: 100%;
            height: auto;
        }}
        .home-button {{
            background: #edf2f7;
            color: #1a202c;
            padding: 8px;
            margin: 0 4px;
            border-radius: 9999px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        @media (max-width: 768px) {{
            .copyable button {{
                position: static;
                margin-top: 10px;
            }}
            .copyable pre {{
                overflow-x: auto;
            }}
        }}
        blockquote {{
            background: #fff3cd;
            border-left: 4px solid #ffeeba;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 1rem;
            margin-top: 1rem;
        }}
        pre {{
            background: #f3f4f6;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            position: relative;
            margin-bottom: 1rem;
            margin-top: 1rem;
        }}
        code {{
            font-family: monospace;
        }}
        h1, h2, h3 {{
            color: #1a202c;
            margin-top: 1.25rem;
            margin-bottom: 0.75rem;
        }}
        h1 {{
            font-size: 2.25rem;
            line-height: 2.5rem;
        }}
        h2 {{
            font-size: 1.875rem;
            line-height: 2.25rem;
        }}
        h3 {{
            font-size: 1.5rem;
            line-height: 2rem;
        }}
        ul, ol {{
            margin-left: 1.5rem;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }}
        li {{
            margin-bottom: 0.5rem;
            color: #4a5568;
        }}
        p {{
            margin-bottom: 1rem;
            color: #4a5568;
        }}
        a {{
            color: #2563eb;
            text-decoration: underline;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 1rem;
        }}
        th, td {{
            border: 1px solid #e2e8f0;
            padding: 8px;
            text-align: left;
        }}
    </style>
</head>
<body class="bg-blue-50">
    <div class="max-w-4xl mx-auto my-12 bg-white p-8 rounded-lg shadow">
        <header class="mb-12 text-center">
            <h1 class="text-4xl font-bold text-gray-800">{title}</h1>
            <br>
            <p class="text-md text-gray-600">{description}</p>
        </header>

        {content}

        <div class="share-buttons">
            <div class="share-button" onclick="shareOnTwitter()">
                <i class="fab fa-twitter"></i>
                <span>ツイート</span>
            </div>
            <div class="share-button" onclick="shareOnFacebook()">
                <i class="fab fa-facebook-f"></i>
                <span>シェア</span>
            </div>
        </div>
        <div class="share-buttons">
            <div class="home-button" onclick="location.href='https://mizuame.works/blog/index.html'">
                <i class="fas fa-home"></i>
                <span>ホーム</span>
            </div>
        </div>
        <footer class="text-center text-gray-600 mt-12">
            <p>&copy; 2023~2024 mizuame. All rights reserved.</p>
        </footer>
    </div>
    <script>
        function copyToClipboard(button) {{
            var code = button.previousElementSibling.innerText;
            var textarea = document.createElement('textarea');
            textarea.value = code;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            button.textContent = 'コピーしました！';
            setTimeout(function () {{
                button.textContent = 'コピー';
            }}, 2000);
        }}

        function shareOnTwitter() {{
            var url = encodeURIComponent(document.location.href);
            var text = encodeURIComponent(document.title);
            var twitterUrl = "https://twitter.com/intent/tweet?url=" + url + "&text=" + text + " @mizuameisgodより";
            window.open(twitterUrl, '_blank');
        }}

        function shareOnFacebook() {{
            var url = encodeURIComponent(document.location.href);
            var facebookUrl = "https://www.facebook.com/sharer/sharer.php?u=" + url;
            window.open(facebookUrl, '_blank');
        }}
    </script>
</body>
</html>'''

class ContentConverter:
    def __init__(self):
        self.today = datetime.today()
        self.base_url = "https://mizuame.works/blog"
        
    def get_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata (title and description) from content"""
        metadata = {
            'title': 'ここはタイトルです。',
            'description': 'ここは一言コメントです。',
            'og_image': f'{self.base_url}/Card/Card_{self.today.strftime("%Y-%m-%d")}.png',
            'og_url': f'{self.base_url}/{self.today.strftime("%Y-%m-%d")}/index.html'
        }
        
        title_match = re.search(r'#title\s*(.*)', content)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
            
        desc_match = re.search(r'#description\s*(.*)', content)
        if desc_match:
            metadata['description'] = desc_match.group(1).strip()
            
        return metadata

    def download_image(self, img_url: str, output_dir: str) -> str:
        """Download image from URL and save it to the output directory"""
        try:
            # 画像ファイル名をURLから取得
            filename = os.path.basename(img_url)
            local_path = os.path.join(output_dir, filename)
            
            # 既に画像が存在する場合は再ダウンロードしない
            if not os.path.isfile(local_path):
                # 画像をダウンロード
                response = requests.get(img_url)
                response.raise_for_status()
                
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"画像をダウンロードしました: {local_path}")
            else:
                print(f"画像は既に存在します: {local_path}")
            
            return filename  # HTML内でのパスを更新するためにファイル名を返す
        except Exception as e:
            print(f"Error downloading image {img_url}: {str(e)}")
            return img_url  # ダウンロードに失敗した場合は元のURLを返す

    def process_images(self, html_content: str, output_dir: str) -> str:
        """Find image tags with remote URLs, download images, and update src attributes"""
        def replace_src(match):
            src = match.group(1)
            if src.startswith('http://') or src.startswith('https://'):
                # 画像をダウンロードしてローカルに保存
                filename = self.download_image(src, output_dir)
                return f'src="{filename}"'
            else:
                return f'src="{src}"'
        
        # imgタグのsrc属性を処理
        html_content = re.sub(r'src="(.*?)"', replace_src, html_content)
        return html_content

    def convert_mbs(self, content: str, output_dir: str) -> str:
        """Convert MBS format content to HTML"""
        def process_tags(content: str) -> str:
            # Remove metadata tags first
            content = re.sub(r'#title\s*.*?\n', '', content)
            content = re.sub(r'#description\s*.*?\n', '', content)
            
            # Process remaining tags
            tags = re.findall(r'(#\w+(?:\(.*?\))?)(.*?)(?=#\w+|$)', content, re.DOTALL)
            
            for tag, text in tags:
                if tag.startswith('#h1'):
                    content = content.replace(f"{tag}{text}", 
                        f'<h1 class="text-4xl font-bold text-gray-800 mb-4">{text.strip()}</h1>', 1)
                elif tag.startswith('#h2'):
                    content = content.replace(f"{tag}{text}", 
                        f'<h2 class="text-3xl font-bold text-gray-800 mb-4">{text.strip()}</h2>', 1)
                elif tag.startswith('#text'):
                    processed_text = re.sub(r'<:>(.*?)<:>', 
                        r'<b class="font-bold text-blue-600">\1</b>', text.strip())
                    content = content.replace(f"{tag}{text}", 
                        f'<p class="text-gray-700 mb-4">{processed_text}</p>', 1)
                elif tag.startswith('#code'):
                    try:
                        title, code = text.split('<:>', 1)
                        content = content.replace(f"{tag}{text}", 
                            f'<div class="copyable mb-4"><p>{title.strip()}</p><pre><code>{code.strip()}</code></pre>'
                            f'<button onclick="copyToClipboard(this)" class="bg-blue-600 hover:bg-blue-700 text-white '
                            f'font-bold py-1 px-3 rounded">コピー</button></div>', 1)
                    except ValueError:
                        print("Error: #codeタグの内容が不正です。'<:>'で区切られている必要があります。")
                elif tag.startswith('#img'):
                    try:
                        src, alt = text.strip().split('<:>')
                        # 画像のURLをダウンロードしてローカルに保存
                        if src.startswith('http://') or src.startswith('https://'):
                            filename = self.download_image(src, output_dir)
                            src = filename
                        content = content.replace(f"{tag}{text}", 
                            f'<div class="image-container mb-4"><img src="{src}" alt="{alt}" class="responsive-image"></div>', 1)
                    except ValueError:
                        print("Error: #imgタグの内容が不正です。'<:>'で区切られている必要があります。")
                elif tag.startswith('#strong'):
                    try:
                        title, body = text.strip().split('<:>')
                        content = content.replace(f"{tag}{text}", 
                            f'<div class="note mb-4"><strong>{title}</strong> {body}</div>', 1)
                    except ValueError:
                        print("Error: #strongタグの内容が不正です。'<:>'で区切られている必要があります。")
                elif tag.startswith('#blockquote'):
                    content = content.replace(f"{tag}{text}", 
                        f'<blockquote class="blockquote mb-4">{text.strip()}</blockquote>', 1)
                elif tag.startswith('#table'):
                    table_html = self.convert_table(text.strip())
                    if table_html:
                        content = content.replace(f"{tag}{text}", table_html, 1)
                else:
                    print(f"Warning: 未知のタグ '{tag}' が検出されました。")
    
            # Process link tags
            content = re.sub(r'<a>(.*?)<:>(.*?)<a>', 
                r'<a href="\2" class="text-blue-600 hover:underline">\1</a>', content)
            
            return content.strip()

        converted_content = process_tags(content)
        return converted_content

    def convert_table(self, table_text: str) -> Optional[str]:
        """
        簡易的なテーブル変換機能。
        テーブルのフォーマットが適切でない場合はNoneを返す。
        例:
        | Header1 | Header2 |
        |---------|---------|
        | Cell1   | Cell2   |
        """
        try:
            lines = table_text.split('\n')
            if len(lines) < 2:
                print("Error: テーブルの行数が不十分です。")
                return None

            headers = lines[0].strip().split('|')[1:-1]  # 最初と最後の'|'を除外
            headers = [header.strip() for header in headers]
            separator = lines[1]
            if not re.match(r'^(\|:-+:?\|)+$', separator):
                print("Error: テーブルのセパレータが不正です。")
                return None

            rows = lines[2:]
            table_html = '<table class="min-w-full table-auto mb-4 border">\n<thead>\n<tr>'
            for header in headers:
                table_html += f'<th class="px-4 py-2 border">{header}</th>'
            table_html += '</tr>\n</thead>\n<tbody>\n'

            for row in rows:
                cells = row.strip().split('|')[1:-1]  # 最初と最後の'|'を除外
                cells = [cell.strip() for cell in cells]
                table_html += '<tr>'
                for cell in cells:
                    table_html += f'<td class="px-4 py-2 border">{cell}</td>'
                table_html += '</tr>\n'

            table_html += '</tbody>\n</table>'
            return table_html
        except Exception as e:
            print(f"Error converting table: {str(e)}")
            return None

    def convert_markdown(self, content: str, output_dir: str) -> str:
        """Convert Markdown format content to HTML with custom styling"""
        # Remove metadata first
        content = re.sub(r'#title\s*.*?\n', '', content)
        content = re.sub(r'#description\s*.*?\n', '', content)
        
        # Convert markdown to HTML
        html = markdown.markdown(content, extensions=['fenced_code', 'tables'])
        
        # Add copy button to code blocks
        html = re.sub(
            r'(<pre><code.*?>)(.*?)(</code></pre>)',
            r'<div class="copyable mb-4">\1\2\3'
            r'<button onclick="copyToClipboard(this)" class="bg-blue-600 hover:bg-blue-700 '
            r'text-white font-bold py-1 px-3 rounded">コピー</button></div>',
            html,
            flags=re.DOTALL
        )
        
        # Add classes to h1, h2, h3 tags
        html = re.sub(
            r'<h1>(.*?)</h1>',
            r'<h1 class="text-4xl font-bold text-gray-800 mb-4">\1</h1>',
            html
        )
        html = re.sub(
            r'<h2>(.*?)</h2>',
            r'<h2 class="text-3xl font-bold text-gray-800 mb-4">\1</h2>',
            html
        )
        html = re.sub(
            r'<h3>(.*?)</h3>',
            r'<h3 class="text-2xl font-bold text-gray-800 mb-4">\1</h3>',
            html
        )
        
        # Add classes to blockquotes
        html = re.sub(
            r'<blockquote>(.*?)</blockquote>',
            r'<blockquote class="blockquote mb-4">\1</blockquote>',
            html,
            flags=re.DOTALL
        )
        
        # Add classes to ul and ol tags
        html = re.sub(
            r'<ul>',
            r'<ul class="list-disc list-inside mb-4">',
            html
        )
        html = re.sub(
            r'<ol>',
            r'<ol class="list-decimal list-inside mb-4">',
            html
        )
        
        # Add classes to li tags
        html = re.sub(
            r'<li>(.*?)</li>',
            r'<li class="mb-2 text-gray-700">\1</li>',
            html
        )
        
        # Add classes to paragraphs
        html = re.sub(
            r'<p>(.*?)</p>',
            r'<p class="text-gray-700 mb-4">\1</p>',
            html
        )
        
        # Add classes to images
        html = re.sub(
            r'<img(.*?)/>',
            r'<img\1 class="responsive-image mb-4"/>',
            html
        )
        
        # Add classes to tables
        html = re.sub(
            r'<table>',
            r'<table class="min-w-full table-auto mb-4 border">',
            html
        )
        html = re.sub(
            r'<th>',
            r'<th class="px-4 py-2 border">',
            html
        )
        html = re.sub(
            r'<td>',
            r'<td class="px-4 py-2 border">',
            html
        )
        
        # Add classes to code blocks
        html = re.sub(
            r'<code>(.*?)</code>',
            r'<code class="bg-gray-100 rounded-lg p-1">\1</code>',
            html
        )

        # Add classes to links
        html = re.sub(
            r'<a href="(.*?)">(.*?)</a>',
            r'<a href="\1" class="text-blue-600 hover:underline">\2</a>',
            html
        )

        # Return the HTML with images processed
        html = self.process_images(html, output_dir)
        
        return html

    def convert_file(self, file_path: str) -> Optional[str]:
        """Convert file to HTML based on its extension"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Get metadata
            metadata = self.get_metadata(content)
            
            # 出力ディレクトリを取得
            output_dir = os.path.dirname(os.path.abspath(file_path))
            
            # Convert content based on file extension
            if file_path.endswith('.mbs'):
                converted_content = self.convert_mbs(content, output_dir)
            elif file_path.endswith('.md'):
                converted_content = self.convert_markdown(content, output_dir)
            else:
                print(f"Unsupported file format: {file_path}")
                return None
            
            # Generate complete HTML
            html_output = HTML_TEMPLATE.format(
                title=metadata['title'],
                description=metadata['description'],
                og_image=metadata['og_image'],
                og_url=metadata['og_url'],
                content=converted_content
            )

            # 画像を処理してHTMLを更新
            html_output = self.process_images(html_output, output_dir)
            
            # Save the output
            output_path = os.path.splitext(file_path)[0] + '.html'
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_output)
                
            return output_path
                
        except Exception as e:
            print(f"Error converting file: {str(e)}")
            return None

def main():
    converter = ContentConverter()
    
    while True:
        file_path = input("変換するファイル(.mbs または .md)のパスを入力してください: ")
        file_path = file_path.replace('\\', '/')
        
        if not os.path.isfile(file_path):
            print(f"Error: File '{file_path}' does not exist.")
            continue
            
        if not (file_path.endswith('.mbs') or file_path.endswith('.md')):
            print("Error: Unsupported file format. Please provide .mbs or .md file.")
            continue
            
        output_path = converter.convert_file(file_path)
        if output_path:
            print(f"変換が完了しました。出力ファイル: {output_path}")
        break

if __name__ == "__main__":
    main()
