"""
JSON to HTML Converter
Converts a JSON file containing articles to a standalone HTML page.
"""

import json
import argparse
import sys
from datetime import datetime
from html import escape

def load_json_file(input_file):
    """Load JSON data from file."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file '{input_file}': {e}")
        sys.exit(1)

def get_css_styles():
    """Return CSS styles as a string."""
    return """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        
        .subtitle {
            margin: 10px 0 0 0;
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .article {
            background: white;
            margin: 30px 0;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .article:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }
        
        .article-header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 25px;
        }
        
        .article-date {
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 8px;
            font-weight: 500;
        }
        
        .article-title {
            font-size: 1.4em;
            font-weight: 600;
            margin: 0;
            line-height: 1.3;
        }
        
        .article-content {
            padding: 25px;
        }
        
        .section {
            margin-bottom: 25px;
        }
        
        .section-title {
            font-size: 1.1em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e9ecef;
            display: flex;
            align-items: center;
        }
        
        .section-title::before {
            content: "";
            width: 4px;
            height: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin-right: 10px;
            border-radius: 2px;
        }
        
        .summary {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #4facfe;
            font-style: italic;
            color: #495057;
        }
        
        .source-content {
            background: #ffffff;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            font-size: 0.95em;
            line-height: 1.7;
            color: #495057;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .questions {
            list-style: none;
            padding: 0;
            counter-reset: question-counter;
        }
        
        .questions li {
            background: #f8f9fa;
            margin: 12px 0;
            padding: 15px 20px;
            border-radius: 8px;
            border-left: 4px solid #28a745;
            position: relative;
            transition: background-color 0.2s ease;
            counter-increment: question-counter;
            padding-left: 45px;
        }
        
        .questions li:hover {
            background: #e9ecef;
        }
        
        .questions li::before {
            content: "Q" counter(question-counter);
            position: absolute;
            left: -2px;
            top: 10px;
            background: #28a745;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .footer {
            text-align: center;
            margin-top: 50px;
            padding: 30px;
            background: #2c3e50;
            color: white;
            border-radius: 10px;
        }
        
        .article-count {
            background: rgba(255, 255, 255, 0.2);
            padding: 8px 16px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 10px;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .article-content {
                padding: 20px;
            }
            
            .source-content {
                max-height: 300px;
            }
        }
        
        .source-content::-webkit-scrollbar {
            width: 8px;
        }
        
        .source-content::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        
        .source-content::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 4px;
        }
        
        .source-content::-webkit-scrollbar-thumb:hover {
            background: #a1a1a1;
        }
    """

def generate_html(articles_data, size=None):
    """Generate HTML content from articles data."""
    
    # Sort articles by date (newest first)
    articles = sorted(articles_data, key=lambda x: x.get('date', ''), reverse=True)
    
    # Limit articles if size is specified
    if size is not None and size > 0:
        articles = articles[:size]
    
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>기술 뉴스 모음</title>
    <style>
{get_css_styles()}
    </style>
</head>
<body>
    <div class="header">
        <h1>기술 뉴스 모음</h1>
        <div class="subtitle">최신 기술 트렌드와 뉴스</div>
        <div class="article-count">총 {len(articles)}개 기사</div>
    </div>
"""

    for article in articles:
        # Escape HTML characters in the content
        title = escape(article.get('topic', 'No Title'))
        date = escape(article.get('date', 'No Date'))
        source = escape(article.get('source', 'No Source'))
        summary = escape(article.get('summary', 'No Summary'))
        questions = article.get('questions', [])
        
        # Format date for better display
        try:
            if date and date != 'No Date':
                # Try to parse different date formats
                for fmt in ['%Y-%m-%d', '%y/%m/%d', '%Y/%m/%d']:
                    try:
                        parsed_date = datetime.strptime(date, fmt)
                        formatted_date = parsed_date.strftime('%Y년 %m월 %d일')
                        break
                    except ValueError:
                        continue
                else:
                    formatted_date = date
            else:
                formatted_date = date
        except:
            formatted_date = date
        
        html_content += f"""
    <article class="article">
        <div class="article-header">
            <div class="article-date">{formatted_date}</div>
            <h2 class="article-title">{title}</h2>
        </div>
        
        <div class="article-content">
            <div class="section">
                <h3 class="section-title">요약</h3>
                <div class="summary">{summary}</div>
            </div>
            
            <div class="section">
                <h3 class="section-title">전체 내용</h3>
                <div class="source-content">{source.replace(chr(10), '<br>')}</div>
            </div>
            
            <div class="section">
                <h3 class="section-title">관련 질문</h3>
                <ol class="questions">"""
        
        for question in questions:
            escaped_question = escape(str(question))
            html_content += f"""
                    <li>{escaped_question}</li>"""
        
        html_content += """
                </ol>
            </div>
        </div>
    </article>"""

    # Add footer
    current_time = datetime.now().strftime('%Y년 %m월 %d일 %H:%M')
    html_content += f"""
    
    <div class="footer">
        <p>이 문서는 {current_time}에 생성되었습니다.</p>
        <p>총 {len(articles)}개의 기사가 포함되어 있습니다.</p>
    </div>

</body>
</html>"""

    return html_content

def save_html_file(html_content, output_file):
    """Save HTML content to file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML file successfully created: {output_file}")
    except Exception as e:
        print(f"Error saving HTML file: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Convert JSON articles to HTML format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python json_to_html.py --input contents.json --output articles.html
  python json_to_html.py -i data.json -o output.html
  python json_to_html.py --input contents.json --output recent.html --size 5
  python json_to_html.py -i contents.json -o latest.html -s 3
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input JSON file path'
    )
    
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output HTML file path'
    )
    
    parser.add_argument(
        '--size', '-s',
        type=int,
        help='Number of recent articles to include (default: all articles)'
    )
    
    args = parser.parse_args()
    
    # Load JSON data
    print(f"Loading JSON data from: {args.input}")
    articles_data = load_json_file(args.input)
    
    if not isinstance(articles_data, list):
        print("Error: JSON data should be a list of articles.")
        sys.exit(1)
    
    total_articles = len(articles_data)
    size_info = f" (showing {args.size} most recent)" if args.size else ""
    print(f"Found {total_articles} articles{size_info}")
    
    # Generate HTML
    print("Generating HTML content...")
    html_content = generate_html(articles_data, args.size)
    
    # Save HTML file
    print(f"Saving HTML to: {args.output}")
    save_html_file(html_content, args.output)

if __name__ == "__main__":
    print("Starting JSON to HTML conversion...")
    main()
