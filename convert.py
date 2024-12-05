import os
import re
from datetime import datetime
import markdown
from typing import Optional, Dict, Any
import traceback  # For displaying exception stack traces
import requests  # For downloading files
from urllib.parse import urlparse  # For parsing URLs

# HTML template is kept directly within the script
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ja">
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
          'fab', 'fa-twitter', 'fa-facebook-f', 'fas', 'fa-home', 'cursor-pointer',
          'responsive-media', 'video-container'
        ],
      }}
    </script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <style>
        body {{
            font-family: 'Noto Sans JP', sans-serif;
            font-size: 14px;
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
            transform-origin: center;
            transform: scale(0.9);
        }}
        .share-button {{
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
        .responsive-media {{
            max-width: 100%;
            height: auto;
        }}
        .home-button {{
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
        }}
        
        @media (max-width: 768px) {{
            body {{
                font-size: 14px;
            }}
            .max-w-4xl {{
                width: 92%;
                margin: 0.75rem auto;
            }}
            .p-8 {{
                padding: 1rem;
            }}
            h1 {{
                font-size: 1.5rem !important;
                line-height: 2rem !important;
            }}
            .text-md {{
                font-size: 0.875rem;
            }}
            #giscus-container {{
                width: 92%;
                margin: 0.75rem auto;
                transform: scale(0.95);
                transform-origin: top center;
            }}
            .share-buttons {{
                transform: scale(0.85);
            }}
            .modal-content {{
                width: 95%;
            }}
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
            margin: 1rem 0;
            font-size: 0.95rem;
        }}
        pre {{
            background: #f3f4f6;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            position: relative;
            margin: 1rem 0;
            font-size: 0.9rem;
        }}
        code {{
            font-family: monospace;
            font-size: 0.9rem;
        }}
        h1, h2, h3 {{
            color: #1a202c;
            margin-top: 1.25rem;
            margin-bottom: 0.75rem;
        }}
        h1 {{
            font-size: 2rem;
            line-height: 2.25rem;
        }}
        h2 {{
            font-size: 1.5rem;
            line-height: 2rem;
        }}
        h3 {{
            font-size: 1.25rem;
            line-height: 1.75rem;
        }}
        ul, ol {{
            margin-left: 1.5rem;
            margin: 1rem 0;
        }}
        li {{
            margin-bottom: 0.5rem;
            color: #4a5568;
            font-size: 0.95rem;
        }}
        p {{
            margin-bottom: 1rem;
            color: #4a5568;
            font-size: 0.95rem;
        }}
        a {{
            color: #2563eb;
            text-decoration: underline;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1rem 0;
            font-size: 0.9rem;
        }}
        th, td {{
            border: 1px solid #e2e8f0;
            padding: 8px;
            text-align: left;
        }}
        .modal {{
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
        }}
        .modal-content {{
            position: relative;
            margin: auto;
            max-width: 90%;
            max-height: 90%;
        }}
        .modal-content img,
        .modal-content video {{
            width: 100%;
            height: auto;
            border-radius: 8px;
        }}
        .close-modal {{
            position: absolute;
            top: 20px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }}
        @media (max-width: 768px) {{
            .close-modal {{
                top: 10px;
                right: 20px;
                font-size: 30px;
            }}
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

        function openModal(src, type) {{
            var modal = document.getElementById('mediaModal');
            var modalImg = document.getElementById('modalImage');
            var modalVid = document.getElementById('modalVideo');
            var modalVidSrc = document.getElementById('modalVideoSource');

            if (type === 'image') {{
                modalImg.src = src;
                modalImg.style.display = 'block';
                modalVid.style.display = 'none';
            }} else if (type === 'video') {{
                modalVidSrc.src = src;
                modalVid.load();
                modalVid.style.display = 'block';
                modalImg.style.display = 'none';
            }}

            modal.style.display = 'flex';
        }}

        function closeModal() {{
            var modal = document.getElementById('mediaModal');
            var modalVid = document.getElementById('modalVideo');
            modal.style.display = 'none';
            modalVid.pause();
        }}

        window.onclick = function(event) {{
            var modal = document.getElementById('mediaModal');
            if (event.target == modal) {{
                closeModal();
            }}
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

    def download_media(self, content: str, file_dir: str) -> str:
        """Download images and videos from absolute URLs and replace with relative paths"""
        def replace_media_link(match):
            full_match = match.group(0)
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
                    # Replace the URL with the local filename
                    new_src = local_filename
                except Exception as e:
                    print(f"Failed to download {src}: {e}")
                    new_src = src  # Keep the original URL if download fails
            else:
                new_src = src  # Keep the original src if it's not an absolute URL

            # Return the modified markdown image/video link
            return f'![{alt_text}]({new_src})'

        # Pattern to find markdown image syntax ![alt_text](src)
        pattern = r'!\[(.*?)\]\((.*?)\)'
        content = re.sub(pattern, replace_media_link, content)

        return content

    def convert_markdown(self, content: str, file_dir: str) -> str:
        """Convert Markdown content to HTML with custom styling and video support"""
        # Remove metadata first
        content = re.sub(r'#title\s*.*?\n', '', content)
        content = re.sub(r'#description\s*.*?\n', '', content)

        # Download media and replace URLs
        content = self.download_media(content, file_dir)

        # Convert markdown to HTML with nl2br extension to preserve line breaks
        html = markdown.markdown(content, extensions=['fenced_code', 'tables', 'nl2br'])

        # Add copy button to code blocks
        html = re.sub(
            r'(<pre><code.*?>)(.*?)(</code></pre>)',
            r'<div class="copyable mb-4">\1\2\3'
            r'<button onclick="copyToClipboard(this)" class="bg-blue-600 hover:bg-blue-700 '
            r'text-white font-bold py-1 px-3 rounded">コピー</button></div>',
            html,
            flags=re.DOTALL
        )

        # Add classes to headings WITHOUT onclick
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

        # Add classes to lists
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

        # Add classes to list items
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

        # Handle images and videos
        def replace_media(match):
            alt_text = match.group(1)
            src = match.group(2)
            ext = os.path.splitext(src)[1].lower()
            if ext == '.mp4':
                # Embed the video directly in the page
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

        return html

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
            converted_content = self.convert_markdown(content, file_dir)

            # Generate complete HTML
            html_output = HTML_TEMPLATE.format(
                title=metadata['title'],
                description=metadata['description'],
                og_image=metadata['og_image'],
                og_url=metadata['og_url'],
                content=converted_content
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
