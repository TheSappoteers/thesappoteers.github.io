import os
import json
import email
from email import policy
from datetime import datetime
import chardet
import mimetypes
from bs4 import BeautifulSoup, Tag
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def decode_text(text):
    if isinstance(text, str):
        return text
    if isinstance(text, bytes):
        encodings = ['utf-8', 'iso-8859-1', 'windows-1252']
        for encoding in encodings:
            try:
                return text.decode(encoding)
            except UnicodeDecodeError:
                continue
        return text.decode('utf-8', errors='replace')
    return str(text)

def clean_html_content(html_content):
    if not html_content or not isinstance(html_content, str):
        logger.warning(f"Invalid html_content: {type(html_content)}")
        return ""  # Return empty string for None or non-string input

    try:
        soup = BeautifulSoup(html_content, 'html.parser')
    except Exception as e:
        logger.error(f"Error parsing HTML content: {e}")
        return html_content  # Return original content if parsing fails

    # Remove script and style elements
    for script in soup(["script", "style"]):
        if script:
            script.decompose()

    # Remove unwanted text patterns
    unwanted_patterns = [
        r"Some people who received this message don't often get email from.*\.",
        r"Learn why this is important",
        r"You don't often get email from.*\.",
        r"To unsubscribe from the MET-SOCIAL list, click the following link:",
        r"http://maillists\.reading\.ac\.uk/scripts/wa-READING\.exe\?SUBED1=MET-SOCIAL&A=1"
    ]

    for pattern in unwanted_patterns:
        for element in soup(text=re.compile(pattern)):
            if element:
                element.extract()

    # Remove the specific table that's causing the grey line
    for table in soup.find_all('table'):
        if table and hasattr(table, 'find'):
            td = table.find('td', attrs={'bgcolor': "#A6A6A6"})
            if td:
                table.decompose()

    # Remove any remaining horizontal rules or divs that might be causing lines
    for element in soup.find_all(['hr', 'div']):
        try:
            if element and hasattr(element, 'attrs'):
                style = element.attrs.get('style', '')
                if isinstance(style, str) and ('border' in style or 'background' in style):
                    element.decompose()
        except Exception as e:
            logger.error(f"Error processing element in clean_html_content: {e}")
            continue

    # Remove any empty paragraphs or divs
    for element in soup.find_all(['p', 'div']):
        try:
            if element and hasattr(element, 'contents') and hasattr(element, 'text'):
                if not element.contents or not element.text.strip():
                    element.decompose()
        except Exception as e:
            logger.error(f"Error removing empty element in clean_html_content: {e}")
            continue

    return str(soup)

def process_eml_files(directory, image_output_dir):
    email_data = []
    for filename in os.listdir(directory):
        if filename.endswith('.eml'):
            logger.info(f"Processing file: {filename}")
            try:
                with open(os.path.join(directory, filename), 'rb') as f:
                    msg = email.message_from_bytes(f.read(), policy=policy.default)
                
                logger.info("Extracting email headers")
                subject = decode_text(msg.get('subject', 'No Subject'))
                date = decode_text(msg.get('date', 'Unknown Date'))
                sender = decode_text(msg.get('from', 'Unknown Sender'))
                
                logger.info("Extracting email body")
                body_html = ""
                body_plain = ""
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        body_html += decode_text(part.get_payload(decode=True))
                    elif part.get_content_type() == "text/plain":
                        body_plain += decode_text(part.get_payload(decode=True))
                
                body = body_html if body_html else body_plain
                if not body:
                    body = "<p>This email may contain an image attachment. Please see below.</p>"
                elif not body_html and body_plain:
                    body = f"<pre>{body_plain}</pre>"
                
                logger.info(f"Body content type: {type(body)}")
                logger.info(f"Body content (first 500 chars): {body[:500]}")
                
                logger.info("Cleaning HTML content")
                body = clean_html_content(body)
                
                logger.info("Processing date")
                try:
                    date_obj = email.utils.parsedate_to_datetime(date)
                    iso_date = date_obj.date().isoformat()
                except Exception as e:
                    logger.error(f"Error processing date: {e}")
                    iso_date = "Unknown Date"
                
                logger.info("Processing attachments")
                flyer_image = ""
                for part in msg.iter_attachments():
                    if part.get_content_maintype() == 'image':
                        image_filename = part.get_filename()
                        if image_filename:
                            image_filename = decode_text(image_filename)
                            image_filename = "".join([c for c in image_filename if c.isalpha() or c.isdigit() or c in (' ','-','_')]).rstrip()
                            if not os.path.splitext(image_filename)[1]:
                                ext = mimetypes.guess_extension(part.get_content_type())
                                if ext:
                                    image_filename += ext
                            image_path = os.path.join(image_output_dir, image_filename)
                            with open(image_path, 'wb') as img_file:
                                img_file.write(part.get_payload(decode=True))
                            flyer_image = os.path.join('_images', image_filename)
                            break
                
                email_data.append({
                    "subject": subject,
                    "date": iso_date,
                    "sender": sender,
                    "flyer_image": flyer_image,
                    "body": body
                })
                logger.info(f"Successfully processed file: {filename}")
            except Exception as e:
                logger.error(f"Error processing file {filename}: {e}", exc_info=True)
                continue
    
    return email_data

if __name__ == "__main__":
    email_directory = 'emails'  # Path to your emails directory
    output_file = 'source/email_data.json'  # Path to output JSON file
    image_output_dir = 'source/_images'  # Path to save flyer images
    
    # Ensure the image output directory exists
    os.makedirs(image_output_dir, exist_ok=True)
    
    email_data = process_eml_files(email_directory, image_output_dir)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(email_data, f, ensure_ascii=False, indent=2)
    
    print(f"Processed {len(email_data)} emails and saved to {output_file}")
    print(f"Flyer images saved to {image_output_dir}")