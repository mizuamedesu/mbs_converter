## マークダウンと独自形式のmbsの書き方に対応している

## Markdown と MBS 形式の書き方比較表

## メタデータ
|要素|Markdown形式|MBS形式|出力例|
|---|------------|--------|------|
|タイトル|`#title ブログのタイトル`|`#title ブログのタイトル`|`<h1>ブログのタイトル</h1>`|
|説明文|`#description ブログの説明`|`#description ブログの説明`|`<p>ブログの説明</p>`|

## 見出し・テキスト
|要素|Markdown形式|MBS形式|出力例|
|---|------------|--------|------|
|見出し|`## 見出しテキスト`|`#h2(見出しテキスト)`|`<h2>見出しテキスト</h2>`|
|通常テキスト|`通常のテキスト`|`#text 通常のテキスト`|`<p>通常のテキスト</p>`|
|強調テキスト|`**強調テキスト**`|`#text <:>強調テキスト<:>`|`<p><b>強調テキスト</b></p>`|
|重要注意文|```> **重要:** 注意文```|`#strong 重要<:>注意文`|`<div class="note"><strong>重要</strong> 注意文</div>`|

## リンクと画像
|要素|Markdown形式|MBS形式|出力例|
|---|------------|--------|------|
|リンク|`[リンクテキスト](URL)`|`<a>リンクテキスト<:>URL<a>`|`<a href="URL">リンクテキスト</a>`|
|画像|`![代替テキスト](画像URL)`|`#img 画像URL<:>代替テキスト`|`<img src="画像URL" alt="代替テキスト">`|

## コードブロック
|要素|Markdown形式|MBS形式|出力例|
|---|------------|--------|------|
|コードブロック（タイトルなし）|```````python\nprint("Hello")\n```````|`#code コードの説明<:>print("Hello")`|`<div class="copyable"><pre><code>print("Hello")</code></pre></div>`|
|コードブロック（タイトル付き）|```# タイトル\n```python\nprint("Hello")\n```````|`#code タイトル<:>print("Hello")`|`<div class="copyable"><p>タイトル</p><pre><code>print("Hello")</code></pre></div>`|

## 使用例

### Markdown形式
```markdown
#title ブログのタイトル
#description ブログの説明

## はじめに
通常のテキストを書きます。**強調したい部分**はこのように書きます。

> **注意:** これは重要な注意書きです。

[リンク例](https://example.com)

![画像の説明](image.jpg)

### コードブロック
```python
def hello():
    print("Hello, World!")
```

### MBS形式
```
#title ブログのタイトル
#description ブログの説明

#h2(はじめに)
#text 通常のテキストを書きます。<:>強調したい部分<:>はこのように書きます。

#strong 注意<:>これは重要な注意書きです。

<a>リンク例<:>https://example.com<a>

#img image.jpg<:>画像の説明

#code Pythonコード<:>def hello():
    print("Hello, World!")
```
