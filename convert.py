import os
import re
from datetime import datetime
import markdown
from typing import Optional, Dict, Any
import traceback  # For displaying exception stack traces
import requests  # For downloading files
from urllib.parse import urlparse  # For parsing URLs
import unicodedata
from string import Template  # 新たに追加

# HTML template with added sidebar navigation on the left using string.Template
HTML_TEMPLATE = Template('''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta property="og:title" content="$title" />
    <meta property="og:description" content="$description" />
    <meta property="og:image" content="$og_image" />
    <meta property="og:url" content="$og_url" />
    <meta name="twitter:card" content="summary_large_image" />
    <title>$title</title>
    <script>
      tailwind.config = {
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
          'fab', 'fa-twitter', 'fa-facebook-f', 'fas', 'fa-home', 'cursor-pointer',
          'responsive-media', 'video-container'
        ],
      }
    </script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script data-name="BMC-Widget" data-cfasync="false" src="https://cdnjs.buymeacoffee.com/1.0.0/widget.prod.min.js" data-id="mizuame" data-description="Support me on Buy me a coffee!" data-message="コーヒー買って下さい" data-color="#5F7FFF" data-position="Right" data-x_margin="18" data-y_margin="18"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <style>
        body {
            font-family: 'Noto Sans JP', sans-serif;
            font-size: 14px;
            margin-left: 270px; /* サイドバーの幅（250px） + 20pxの余白 */
        }
        @media (max-width: 1024px) {
            body {
                margin-left: 0; /* レスポンシブ対応 */
            }
        }
        .copyable {
            background: #f3f4f6;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            position: relative;
            margin-bottom: 1rem;
        }
        .copyable button {
            position: absolute;
            right: 10px;
            top: 10px;
        }
        .note {
            background: #fff3cd;
            border-left: 4px solid #ffeeba;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 1rem;
        }
        .tag {
            display: inline-block;
            background: #e2e8f0;
            border-radius: 9999px;
            padding: 0.25rem 0.75rem;
            font-size: 0.75rem;
            font-weight: 700;
            margin-right: 0.5rem;
            color: #1a202c;
        }
        .share-buttons {
            display: flex;
            justify-content: center;
            margin-top: 20px;
            transform-origin: center;
            transform: scale(0.9);
        }
        .share-button {
            background: #edf2f7;
            color: #1a202c;
            padding: 6px;
            margin: 0 4px;
            border-radius: 9999px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9rem;
        }
        .share-button i {
            margin-right: 8px;
        }
        .image-container {
            margin-top: 20px;
            text-align: center;
        }
        .responsive-image {
            max-width: 100%;
            height: auto;
        }
        .responsive-media {
            max-width: 100%;
            height: auto;
        }
        .home-button {
            background: #edf2f7;
            color: #1a202c;
            padding: 6px;
            margin: 0 4px;
            border-radius: 9999px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            body {
                font-size: 14px;
            }
            .max-w-4xl {
                width: 92%;
                margin: 0.75rem auto;
            }
            .p-8 {
                padding: 1rem;
            }
            h1 {
                font-size: 1.5rem !important;
                line-height: 2rem !important;
            }
            .text-md {
                font-size: 0.875rem;
            }
            #giscus-container {
                width: 92%;
                margin: 0.75rem auto;
                transform: scale(0.95);
                transform-origin: top center;
            }
            .share-buttons {
                transform: scale(0.85);
            }
            .modal-content {
                width: 95%;
            }
            .copyable button {
                position: static;
                margin-top: 10px;
            }
            .copyable pre {
                overflow-x: auto;
            }
        }
        
        blockquote {
            background: #fff3cd;
            border-left: 4px solid #ffeeba;
            padding: 10px;
            border-radius: 5px;
            margin: 1rem 0;
            font-size: 0.95rem;
        }
        pre {
            background: #f3f4f6;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            position: relative;
            margin: 1rem 0;
            font-size: 0.9rem;
        }
        code {
            font-family: monospace;
            font-size: 0.9rem;
        }
        h1, h2, h3 {
            color: #1a202c;
            margin-top: 1.25rem;
            margin-bottom: 0.75rem;
        }
        h1 {
            font-size: 2rem;
            line-height: 2.25rem;
        }
        h2 {
            font-size: 1.5rem;
            line-height: 2rem;
        }
        h3 {
            font-size: 1.25rem;
            line-height: 1.75rem;
        }
        ul, ol {
            margin-left: 1.5rem;
            margin: 1rem 0;
        }
        li {
            margin-bottom: 0.5rem;
            color: #4a5568;
            font-size: 0.95rem;
        }
        p {
            margin-bottom: 1rem;
            color: #4a5568;
            font-size: 0.95rem;
        }
        a {
            color: #2563eb;
            text-decoration: underline;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1rem 0;
            font-size: 0.9rem;
        }
        th, td {
            border: 1px solid #e2e8f0;
            padding: 8px;
            text-align: left;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.8);
            align-items: center;
            justify-content: center;
        }
        .modal-content {
            position: relative;
            margin: auto;
            max-width: 90%;
            max-height: 90%;
        }
        .modal-content img,
        .modal-content video {
            width: 100%;
            height: auto;
            border-radius: 8px;
        }
        .close-modal {
            position: absolute;
            top: 20px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }
        @media (max-width: 768px) {
            .close-modal {
                top: 10px;
                right: 20px;
                font-size: 30px;
            }
        }

        /* サイドナビゲーションスタイル */
        .sidebar {
            position: fixed;
            top: 0;
            left: 0; /* 右から左に変更 */
            height: 100%;
            width: 250px;
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0; /* border-leftからborder-rightに変更 */
            box-shadow: 2px 0 5px rgba(0,0,0,0.1); /* -2pxから2pxに変更 */
            padding: 1rem;
            overflow-y: auto;
        }
        .sidebar h2 {
            font-size: 1.25rem;
            margin-bottom: 1rem;
            font-weight: bold;
            color: #1a202c;
        }
        .sidebar ul {
            list-style: none;
            padding-left: 0;
        }
        .sidebar li {
            margin-bottom: 0.5rem;
        }
        .sidebar li a {
            color: #2563eb;
            text-decoration: underline;
            font-size: 0.9rem;
        }
        .sidebar li a:hover {
            text-decoration: none;
        }

    </style>
</head>
<body class="bg-blue-50">
    <div class="max-w-4xl mx-auto my-12 bg-white p-8 rounded-lg shadow> 
        <header class="mb-12 text-center">
            <h1 class="text-4xl font-bold text-gray-800">$title</h1>
            <br>
            <p class="text-md text-gray-600">$description</p>
        </header>

        $content

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
    </div>

    <div id="giscus-container" class="mt-12 max-w-4xl mx-auto">
        <script src="https://giscus.app/client.js"
                data-repo="mizuamedesu/giscus"
                data-repo-id="R_kgDONY9v_Q"
                data-category="Announcements"
                data-category-id="DIC_kwDONY9v_c4Ck5ot"
                data-mapping="og:title"
                data-strict="0"
                data-reactions-enabled="1"
                data-emit-metadata="0"
                data-input-position="top"
                data-theme="light_tritanopia"
                data-lang="ja"
                crossorigin="anonymous"
                async>
        </script>
    </div>

    <footer class="text-center text-gray-600 mt-12">
        <p>&copy; 2023~2024 mizuame. All rights reserved.</p>
        <br><br>
    </footer>

    <div id="mediaModal" class="modal">
        <span class="close-modal" onclick="closeModal()">&times;</span>
        <div class="modal-content">
            <img id="modalImage" src="" alt="" style="display: none;">
            <video id="modalVideo" controls style="display: none;">
                <source id="modalVideoSource" src="" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
    </div>

    <!-- サイドナビゲーション（PC表示のみ） -->
    <div class="hidden lg:block sidebar">
        <h2>$title</h2>
        <ul>
          $nav_items
        </ul>
        <div class="mt-4">
            <button class="home-button w-full" onclick="location.href='https://mizuame.works/blog/index.html'">
                <i class="fas fa-home"></i>
                <span>ホームへ</span>
            </button>
        </div>
    </div>

    <script>
        function copyToClipboard(button) {
            var code = button.previousElementSibling.innerText;
            var textarea = document.createElement('textarea');
            textarea.value = code;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            button.textContent = 'コピーしました！';
            setTimeout(function () {
                button.textContent = 'コピー';
            }, 2000);
        }

        function shareOnTwitter() {
            var url = encodeURIComponent(document.location.href);
            var text = encodeURIComponent(document.title);
            var twitterUrl = "https://twitter.com/intent/tweet?url=" + url + "&text=" + text + " @mizuameisgodより";
            window.open(twitterUrl, '_blank');
        }

        function shareOnFacebook() {
            var url = encodeURIComponent(document.location.href);
            var facebookUrl = "https://www.facebook.com/sharer/sharer.php?u=" + url;
            window.open(facebookUrl, '_blank');
        }

        function openModal(src, type) {
            var modal = document.getElementById('mediaModal');
            var modalImg = document.getElementById('modalImage');
            var modalVid = document.getElementById('modalVideo');
            var modalVidSrc = document.getElementById('modalVideoSource');

            if (type === 'image') {
                modalImg.src = src;
                modalImg.style.display = 'block';
                modalVid.style.display = 'none';
            } else if (type === 'video') {
                modalVidSrc.src = src;
                modalVid.load();
                modalVid.style.display = 'block';
                modalImg.style.display = 'none';
            }

            modal.style.display = 'flex';
        }

        function closeModal() {
            var modal = document.getElementById('mediaModal');
            var modalVid = document.getElementById('modalVideo');
            modal.style.display = 'none';
            modalVid.pause();
        }

        window.onclick = function(event) {
            var modal = document.getElementById('mediaModal');
            if (event.target == modal) {
                closeModal();
            }
        }
    </script>
</body>
</html>''')

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

    def download_media(self, content: str, file_dir: str) -> str:
        """Download images and videos from absolute URLs and replace with relative paths"""
        def replace_media_link(match):
            alt_text = match.group(1)
            src = match.group(2)
            parsed_url = urlparse(src)
            filename = os.path.basename(parsed_url.path)

            # Check if the URL is absolute
            if parsed_url.scheme in ('http', 'https'):
                # Handle potential duplicate filenames
                local_filename = filename
                counter = 1
                while os.path.exists(os.path.join(file_dir, local_filename)):
                    name, ext = os.path.splitext(filename)
                    local_filename = f"{name}_{counter}{ext}"
                    counter += 1

                try:
                    # Download the file
                    response = requests.get(src, stream=True)
                    response.raise_for_status()
                    with open(os.path.join(file_dir, local_filename), 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"Downloaded: {src} -> {local_filename}")
                    new_src = local_filename
                except Exception as e:
                    print(f"Failed to download {src}: {e}")
                    new_src = src
            else:
                new_src = src

            return f'![{alt_text}]({new_src})'

        pattern = r'!\[(.*?)\]\((.*?)\)'
        content = re.sub(pattern, replace_media_link, content)

        return content

    def slugify(self, text: str) -> str:
        """Generate a URL-friendly slug from a heading text."""
        # 正規化
        text = unicodedata.normalize('NFKC', text)
        # 全角英数字を半角に、記号などを除去
        text = text.strip().lower()
        # 記号類をハイフンに
        text = re.sub(r'[^\w\s-]', '', text)
        text = text.replace(' ', '-')
        text = re.sub(r'-+', '-', text)
        return text

    def extract_headings(self, content: str) -> list:
        """
        Extract headings from the Markdown content.
        Return a list of tuples: (level, text).
        """
        headings = []
        # Markdownの見出し形式: ^(#{1,6})\s+(.*)
        for match in re.finditer(r'^(#{1,6})\s+(.*)', content, flags=re.MULTILINE):
            hashes = match.group(1)
            text = match.group(2).strip()
            level = len(hashes)
            # #title, #description行などは削除済み後に実行するため関係なし
            # ただし、#title行はメタ情報で取り除くため、そこは実際のheadingとして存在しないはず
            headings.append((level, text))
        return headings

    def add_ids_to_headings(self, html: str) -> (str, list):
        """
        Add id attributes to headings in the HTML and return a list of (level, text, id).
        """
        headings_data = []

        def replace_h1(m):
            text = m.group(1)
            id_ = self.slugify(text)
            headings_data.append((1, text, id_))
            return f'<h1 id="{id_}" class="text-4xl font-bold text-gray-800 mb-4">{text}</h1>'

        def replace_h2(m):
            text = m.group(1)
            id_ = self.slugify(text)
            headings_data.append((2, text, id_))
            return f'<h2 id="{id_}" class="text-3xl font-bold text-gray-800 mb-4">{text}</h2>'

        def replace_h3(m):
            text = m.group(1)
            id_ = self.slugify(text)
            headings_data.append((3, text, id_))
            return f'<h3 id="{id_}" class="text-2xl font-bold text-gray-800 mb-4">{text}</h3>'

        # Replace h1, h2, h3 with IDs and classes
        html = re.sub(r'<h1>(.*?)</h1>', replace_h1, html, flags=re.DOTALL)
        html = re.sub(r'<h2>(.*?)</h2>', replace_h2, html, flags=re.DOTALL)
        html = re.sub(r'<h3>(.*?)</h3>', replace_h3, html, flags=re.DOTALL)

        return html, headings_data

    def convert_markdown(self, content: str, file_dir: str) -> (str, list):
        """Convert Markdown content to HTML with custom styling and video support"""

        # メタ情報行を削除(#titleと#description)
        content = re.sub(r'#title\s.*?\n', '', content)
        content = re.sub(r'#description\s.*?\n', '', content)

        # メディアダウンロード
        content = self.download_media(content, file_dir)

        # MarkdownをHTMLへ変換
        html = markdown.markdown(content, extensions=['fenced_code', 'tables', 'nl2br'])

        # コードブロックにコピー機能追加
        html = re.sub(
            r'(<pre><code.*?>)(.*?)(</code></pre>)',
            r'<div class="copyable mb-4">\1\2\3'
            r'<button onclick="copyToClipboard(this)" class="bg-blue-600 hover:bg-blue-700 '
            r'text-white font-bold py-1 px-3 rounded">コピー</button></div>',
            html,
            flags=re.DOTALL
        )

        # blockquote
        html = re.sub(
            r'<blockquote>(.*?)</blockquote>',
            r'<blockquote class="blockquote mb-4">\1</blockquote>',
            html,
            flags=re.DOTALL
        )

        # lists
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

        html = re.sub(
            r'<li>(.*?)</li>',
            r'<li class="mb-2 text-gray-700">\1</li>',
            html
        )

        # paragraphs
        html = re.sub(
            r'<p>(.*?)</p>',
            r'<p class="text-gray-700 mb-4">\1</p>',
            html
        )

        # images/videos
        def replace_media(match):
            alt_text = match.group(1)
            src = match.group(2)
            ext = os.path.splitext(src)[1].lower()
            if ext == '.mp4':
                return f'''
<div class="video-container mb-4">
    <video controls class="responsive-media">
        <source src="{src}" type="video/mp4">
        Your browser does not support the video tag.
    </video>
</div>
                '''
            else:
                return f'<img src="{src}" alt="{alt_text}" class="responsive-media mb-4 cursor-pointer" onclick="openModal(\'{src}\', \'image\')"/>'

        html = re.sub(
            r'<img\s+alt="(.*?)"\s+src="(.*?)"\s*/?>',
            replace_media,
            html
        )

        # tables
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

        # code inline
        html = re.sub(
            r'<code>(.*?)</code>',
            r'<code class="bg-gray-100 rounded-lg p-1">\1</code>',
            html
        )

        # links
        html = re.sub(
            r'<a href="(.*?)">(.*?)</a>',
            r'<a href="\1" class="text-blue-600 hover:underline">\2</a>',
            html
        )

        # 見出しにidを付与（同時にh1,h2,h3のclass付与もこのステップで実施）
        html, headings_data = self.add_ids_to_headings(html)

        return html, headings_data

    def generate_nav(self, headings_data: list) -> str:
        """
        headings_dataは (level, text, id) のリスト
        #titleはメタデータから取得しているので、ここではheadingsは記事内のh1,h2,h3等が対象
        """
        nav_html = ""
        # h1,h2,h3程度を想定
        # levelに応じてインデントをつけてもいいが、今回はシンプルに列挙
        for level, text, id_ in headings_data:
            indent = "　" * (level - 1)  # レベルに応じてインデント(全角スペース)を増やす
            nav_html += f'<li>{indent}<a href="#{id_}">{text}</a></li>'
        return nav_html

    def convert_file(self, file_path: str) -> Optional[str]:
        """Convert Markdown file to HTML"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Get metadata
            metadata = self.get_metadata(content)

            # Get the directory of the Markdown file
            file_dir = os.path.dirname(file_path)

            # Convert content
            converted_content, headings_data = self.convert_markdown(content, file_dir)

            # ナビゲーション生成
            nav_items = self.generate_nav(headings_data)

            # Generate complete HTML
            html_output = HTML_TEMPLATE.substitute(
                title=metadata['title'],
                description=metadata['description'],
                og_image=metadata['og_image'],
                og_url=metadata['og_url'],
                content=converted_content,
                nav_items=nav_items
            )

            # Save the output
            output_dir = file_dir
            output_filename = 'index.html'
            output_path = os.path.join(output_dir, output_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_output)

            return output_path

        except Exception as e:
            print("Error converting file:")
            traceback.print_exc()  # Display stack trace
            return None

def main():
    converter = ContentConverter()

    while True:
        file_path = input("変換するファイル(.md)のパスを入力してください: ")
        file_path = file_path.replace('\\', '/')

        if not os.path.isfile(file_path):
            print(f"Error: File '{file_path}' does not exist.")
            continue

        if not file_path.endswith('.md'):
            print("Error: Unsupported file format. Please provide a .md file.")
            continue

        output_path = converter.convert_file(file_path)
        if output_path:
            print(f"変換が完了しました。出力ファイル: {output_path}")
        break

if __name__ == "__main__":
    main()
