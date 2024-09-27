import os
import json
import email
import base64
import chardet
from email import policy
from email.parser import BytesParser
from bs4 import BeautifulSoup
from datetime import datetime

def decode_text(text):
    if isinstance(text, str):
        return text
    
    if isinstance(text, bytes):
        encodings = ['utf-8', 'iso-8859-1', 'windows-1252']
        for encoding in encodings:
            try:
                return text.decode(encoding)
            except UnicodeDecodeError:
                pass
    
    # If all else fails, try to detect the encoding
    detected = chardet.detect(text)
    if detected['encoding']:
        try:
            return text.decode(detected['encoding'])
        except UnicodeDecodeError:
            pass
    
    # If we still can't decode, return as is (may contain garbage characters)
    return text.decode('utf-8', errors='replace')

def extract_email_content(eml_file):
    with open(eml_file, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)
    
    sender = decode_text(msg['From'])
    subject = decode_text(msg['Subject'])
    date = decode_text(msg['Date'])
    
    body = ""
    attachments = []
    
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            body = decode_text(part.get_payload(decode=True))
        elif part.get_content_type() == "text/plain" and not body:
            body = decode_text(part.get_payload(decode=True))
        elif part.get_content_disposition() == 'attachment':
            filename = part.get_filename()
            if filename:
                attachments.append({
                    'filename': decode_text(filename),
                    'content': base64.b64encode(part.get_payload(decode=True)).decode()
                })
    
    return sender, subject, date, body, attachments

def save_html(content, filename):
    with open(filename, 'w', encoding='utf-8', errors='replace') as f:
        f.write(content)

def save_attachment(attachment, output_dir):
    filename = os.path.join(output_dir, attachment['filename'])
    with open(filename, 'wb') as f:
        f.write(base64.b64decode(attachment['content']))
    return filename

def process_eml_files(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    metadata = []
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.eml'):
            try:
                eml_path = os.path.join(input_dir, filename)
                sender, subject, date, body, attachments = extract_email_content(eml_path)
                
                # Save email body as HTML
                html_filename = f"{os.path.splitext(filename)[0]}.html"
                html_path = os.path.join(output_dir, html_filename)
                save_html(body, html_path)
                
                # Save attachments
                attachment_paths = []
                for attachment in attachments:
                    attachment_path = save_attachment(attachment, output_dir)
                    attachment_paths.append(attachment_path)
                
                # Extract sender name
                sender_name = email.utils.parseaddr(sender)[0]
                
                # Add metadata
                metadata.append({
                    'filename': filename,
                    'sender': sender,
                    'sender_name': sender_name,
                    'subject': subject,
                    'date': date,
                    'html_file': html_filename,
                    'attachments': [os.path.basename(path) for path in attachment_paths]
                })
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    # Save metadata as JSON
    with open(os.path.join(output_dir, 'metadata.json'), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    input_directory = 'emails'
    output_directory = 'source/_static/emails_html'
    process_eml_files(input_directory, output_directory)