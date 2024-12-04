import streamlit as st
from openai import OpenAI
import json
import datetime
import io
import os
import re
import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
    Table, TableStyle, Image, NextPageTemplate,
    PageTemplate, Frame
)
from reportlab.lib.pagesizes import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Image, Frame
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_CENTER
import io
import os
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, PageTemplate, Frame, PageBreak, Image, Paragraph, NextPageTemplate
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import io
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
    Table, TableStyle, Image, NextPageTemplate,
    PageTemplate, Frame
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import datetime
import ssl
import logging
BUSINESS_OPTIONS = {
    "Business Valuation": "I want to assess my company's worth, helping me make informed decisions and gain investor trust.",
    "Financial Healthcheck": "I want to review my finances, checking assets, debts, cash flow, and overall stability",
    "Business Partnering": "I want to build partnerships to grow, sharing strengths and resources with others for mutual benefit.",
    "Fund Raising": "I want to secure funds from investors to expand, innovate, or support my business operations.",
    "Bankability and Leverage": "I want to evaluate my creditworthiness, improving access to financing and managing debt effectively.",
    "Mergers and Acquisitions": "I want to pursue growth by combining my business with others, expanding resources and market reach.",
    "Budget and Resourcing": "I want to allocate resources wisely to achieve my goals efficiently and boost productivity.",
    "Business Remodelling": "I want to reshape my operations to stay relevant and seize new market opportunities.",
    "Succession Planning": "I want to prepare for future leadership transitions, ensuring the right people continue my business legacy."
}

# Email Configuration
# EMAIL_SENDER = "thaqiyuddin58@gmail.com"  # Your Gmail address
# EMAIL_PASSWORD = "nwkw nhyj maii hxtb"    # Your Gmail App Password 
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 465 
EMAIL_SENDER = "kai@ceaiglobal.com"
EMAIL_PASSWORD = "MyFinB2024123#"
SMTP_SERVER = "mail.ceaiglobal.com"  # Changed to hostinger server
SMTP_PORT = 465
# Set up logging
context = ssl.create_default_context()

def send_email_with_attachment(receiver_email, company_name, subject, body, pdf_buffer, statistics):
    """
    Send email with PDF report attachment using ceaiglobal.com email
    
    Args:
        receiver_email (str): Recipient's email address
        company_name (str): Name of the company for the report
        subject (str): Email subject
        body (str): Email body text
        pdf_buffer (BytesIO): PDF report as a buffer
        statistics (dict): Analysis statistics to include in email
    """
    try:
        # Log attempt
        logging.info(f"Attempting to send email to: {receiver_email}")
        
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = receiver_email
        msg['Subject'] = f"{subject} - {company_name}"

        # Create statistics tables
        summary_headers = ['Metric', 'Input', 'Output', 'Total']
        summary_rows = [
            ['Words', 
             f"{statistics['total_input_words']:,}", 
             f"{statistics['total_output_words']:,}",
             f"{statistics['total_input_words'] + statistics['total_output_words']:,}"],
            ['Tokens', 
             f"{statistics['total_input_tokens']:,}", 
             f"{statistics['total_output_tokens']:,}",
             f"{statistics['total_input_tokens'] + statistics['total_output_tokens']:,}"]
        ]
        summary_table = create_ascii_table(summary_headers, summary_rows)

        # Create the email body with formatting
        formatted_body = f"""Dear Recipient,

{body}

Contact Details:
Full Name: {st.session_state.user_data.get('full_name', 'N/A')}
Email: {st.session_state.user_data.get('email', 'N/A')}
Mobile: {st.session_state.user_data.get('mobile_number', 'N/A')}

Company Name: {company_name}
Generated Date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

ANALYSIS STATISTICS SUMMARY:
{summary_table}

Best regards,
CEAI Business Analysis Team"""

        # Attach the formatted body
        msg.attach(MIMEText(formatted_body, 'plain'))

        # Prepare and attach PDF
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(pdf_buffer.getvalue())
        encoders.encode_base64(attachment)
        
        # Create sanitized filename
        sanitized_company_name = "".join(x for x in company_name if x.isalnum() or x in (' ', '-', '_')).strip()
        filename = f"business_analysis_{sanitized_company_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        
        attachment.add_header(
            'Content-Disposition',
            f'attachment; filename="{filename}"'
        )
        msg.attach(attachment)

        # Create SSL context
        context = ssl.create_default_context()
        
        # Attempt to send email
        logging.info("Connecting to SMTP server...")
        try:
            # Try SSL first (port 465)
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
                logging.info("Connected with SSL")
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.send_message(msg)
        except Exception as ssl_error:
            logging.warning(f"SSL connection failed: {str(ssl_error)}")
            logging.info("Trying TLS connection...")
            # If SSL fails, try TLS (port 587)
            with smtplib.SMTP(SMTP_SERVER, 587) as server:
                server.starttls(context=context)
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.send_message(msg)
                
        st.success(f"Report sent successfully to {receiver_email} for {company_name}.")
        logging.info(f"Email sent successfully to {receiver_email}")
        
    except Exception as e:
        error_msg = f"Error sending email: {str(e)}"
        logging.error(error_msg, exc_info=True)
        st.error(error_msg)
        print(f"Detailed email error: {str(e)}")  # For debugging
def send_email_with_attachment2(receiver_email, company_name, subject, body, pdf_buffer, statistics):
    """
    Send email with PDF report attachment using ceaiglobal.com email
    
    Args:
        receiver_email (str): Recipient's email address
        company_name (str): Name of the company for the report
        subject (str): Email subject
        body (str): Email body text
        pdf_buffer (BytesIO): PDF report as a buffer
        statistics (dict): Analysis statistics to include in email
    """
    try:
        # Log attempt
        logging.info(f"Attempting to send email to: {receiver_email}")
        
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = receiver_email
        msg['Subject'] = f"{subject} - {company_name}"

        # Create statistics tables
        summary_headers = ['Metric', 'Input', 'Output', 'Total']
        summary_rows = [
            ['Words', 
             f"{statistics['total_input_words']:,}", 
             f"{statistics['total_output_words']:,}",
             f"{statistics['total_input_words'] + statistics['total_output_words']:,}"],
            ['Tokens', 
             f"{statistics['total_input_tokens']:,}", 
             f"{statistics['total_output_tokens']:,}",
             f"{statistics['total_input_tokens'] + statistics['total_output_tokens']:,}"]
        ]
        summary_table = create_ascii_table(summary_headers, summary_rows)

        # Create the email body with formatting
        formatted_body = f"""Dear Recipient,

{body}

Contact Details:
Full Name: {st.session_state.user_data.get('full_name', 'N/A')}
Email: {st.session_state.user_data.get('email', 'N/A')}
Mobile: {st.session_state.user_data.get('mobile_number', 'N/A')}

Company Name: {company_name}
Generated Date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

ANALYSIS STATISTICS SUMMARY:
{summary_table}

Best regards,
CEAI Business Analysis Team"""

        # Attach the formatted body
        msg.attach(MIMEText(formatted_body, 'plain'))

        # Prepare and attach PDF
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(pdf_buffer.getvalue())
        encoders.encode_base64(attachment)
        
        # Create sanitized filename
        sanitized_company_name = "".join(x for x in company_name if x.isalnum() or x in (' ', '-', '_')).strip()
        filename = f"business_analysis_{sanitized_company_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        
        attachment.add_header(
            'Content-Disposition',
            f'attachment; filename="{filename}"'
        )
        msg.attach(attachment)

        # Create SSL context
        context = ssl.create_default_context()
        
        # Attempt to send email
        logging.info("Connecting to SMTP server...")
        try:
            # Try SSL first (port 465)
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
                logging.info("Connected with SSL")
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.send_message(msg)
        except Exception as ssl_error:
            logging.warning(f"SSL connection failed: {str(ssl_error)}")
            logging.info("Trying TLS connection...")
            # If SSL fails, try TLS (port 587)
            with smtplib.SMTP(SMTP_SERVER, 587) as server:
                server.starttls(context=context)
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.send_message(msg)
                
        st.success(f"Report sent successfully to {receiver_email} for {company_name}.")
        logging.info(f"Email sent successfully to {receiver_email}")
        
    except Exception as e:
        error_msg = f"Error sending email: {str(e)}"
        logging.error(error_msg, exc_info=True)
        st.error(error_msg)
        print(f"Detailed email error: {str(e)}")  # For debugging

def create_ascii_table(headers, rows, column_widths=None):
    """Create an ASCII table for email formatting."""
    if column_widths is None:
        # Calculate column widths based on content
        column_widths = []
        for i in range(len(headers)):
            column_content = [str(row[i]) for row in rows] + [headers[i]]
            column_widths.append(max(len(str(x)) for x in column_content) + 2)

    # Create the header separator
    separator = '+' + '+'.join('-' * width for width in column_widths) + '+'

    # Create the header
    header_row = '|' + '|'.join(
        str(headers[i]).center(column_widths[i])
        for i in range(len(headers))
    ) + '|'

    # Create the rows
    data_rows = []
    for row in rows:
        data_row = '|' + '|'.join(
            str(row[i]).center(column_widths[i])
            for i in range(len(row))
        ) + '|'
        data_rows.append(data_row)

    # Combine all parts
    table = '\n'.join([
        separator,
        header_row,
        separator,
        '\n'.join(data_rows),
        separator
    ])

    return table

BUSINESS_OPTIONS = {
    "Business Valuation": "I want to assess my company's worth, helping me make informed decisions and gain investor trust.",
    "Financial Healthcheck": "I want to review my finances, checking assets, debts, cash flow, and overall stability",
    "Business Partnering": "I want to build partnerships to grow, sharing strengths and resources with others for mutual benefit.",
    "Fund Raising": "I want to secure funds from investors to expand, innovate, or support my business operations.",
    "Bankability and Leverage": "I want to evaluate my creditworthiness, improving access to financing and managing debt effectively.",
    "Mergers and Acquisitions": "I want to pursue growth by combining my business with others, expanding resources and market reach.",
    "Budget and Resourcing": "I want to allocate resources wisely to achieve my goals efficiently and boost productivity.",
    "Business Remodelling": "I want to reshape my operations to stay relevant and seize new market opportunities.",
    "Succession Planning": "I want to prepare for future leadership transitions, ensuring the right people continue my business legacy."
}
INDUSTRY_OPTIONS = {
    "Accommodation and Food Service Activities": "1.2.1",
    "Administrative and Support Service Activities": "1.2.2",
    "Agriculture, Forestry, and Fishing": "1.2.3",
    "Arts, Entertainment, and Recreation": "1.2.4",
    "Construction": "1.2.5",
    "Education": "1.2.6",
    "Electricity, Gas, Steam, and Air Conditioning Supply": "1.2.7",
    "Financial and Insurance/Takaful Activities": "1.2.8",
    "Human Health and Social Work Activities": "1.2.9",
    "Information and Communication": "1.2.10",
    "Manufacturing": "1.2.11",
    "Mining and Quarrying": "1.2.12",
    "Professional, Scientific, and Technical Activities": "1.2.13",
    "Public Administration and Defence; Compulsory Social Security": "1.2.14",
    "Real Estate Activities": "1.2.15",
    "Transportation and Storage": "1.2.16",
    "Water Supply, Sewerage, Waste Management, and Remediation Activities": "1.2.17",
    "Wholesale and Retail Trade; Repair of Motor Vehicles and Motorcycles": "1.2.18",
    "Others": "1.2.19"
}
CURRENCY_OPTIONS = {
    "Malaysian Ringgit (MYR)": "1.4.1",
    "United States Dollar (USD)": "1.4.2",
    "Euro (EUR)": "1.4.3",
    "British Pound Sterling (GBP)": "1.4.4",
    "Japanese Yen (JPY)": "1.4.5",
    "Australian Dollar (AUD)": "1.4.6",
    "Canadian Dollar (CAD)": "1.4.7",
    "Swiss Franc (CHF)": "1.4.8",
    "Chinese Yuan (CNY)": "1.4.9",
    "Singapore Dollar (SGD)": "1.4.10",
    "Indian Rupee (INR)": "1.4.11",
    "New Zealand Dollar (NZD)": "1.4.12",
    "South Korean Won (KRW)": "1.4.13",
    "Hong Kong Dollar (HKD)": "1.4.14",
    "Thai Baht (THB)": "1.4.15",
    "Philippine Peso (PHP)": "1.4.16",
    "Indonesian Rupiah (IDR)": "1.4.17",
    "Vietnamese Dong (VND)": "1.4.18",
    "Saudi Riyal (SAR)": "1.4.19",
    "Emirati Dirham (AED)": "1.4.20",
    "Turkish Lira (TRY)": "1.4.21",
    "Brazilian Real (BRL)": "1.4.22",
    "South African Rand (ZAR)": "1.4.23",
    "Mexican Peso (MXN)": "1.4.24",
    "Russian Ruble (RUB)": "1.4.25"
}

PROFIT_RANGES = {
    "<100k": "1.6.1",
    "100 - 500k": "1.6.2",
    ">500k - 1m": "1.6.3",
    ">1 - 5m": "1.6.4",
    ">5 - 10m": "1.6.5",
    ">10m": "1.6.6"
}

CASHFLOW_RANGES = {
    "<0": "1.7.1",
    "0 - 100k": "1.7.2",
    "100 - 500k": "1.7.3",
    ">500k - 1m": "1.7.4",
    ">1 - 5m": "1.7.5",
    ">5m": "1.7.6"
}

DEBT_EQUITY_RANGES = {
    "<0.5": "1.8.1",
    "0.5-1.0x": "1.8.2",
    ">1.0 - 3x": "1.8.3",
    ">3x": "1.8.4"
}

SHAREHOLDERS_FUNDS_RANGES = {
    "<500k": "1.9.1",
    "500k - 1m": "1.9.2",
    "1 - 5m": "1.9.3",
    ">5 - 10m": "1.9.4",
    ">10 - 30m": "1.9.5",
    ">30 - 50m": "1.9.6",
    ">50m": "1.9.7"
}

STAFF_STRENGTH_RANGES = {
    "<5": "1.10.1",
    "5 - 10": "1.10.2",
    ">10 - 30": "1.10.3",
    ">30-50": "1.10.4",
    ">50-80": "1.10.5",
    ">80 - 100": "1.10.6",
    ">100": "1.10.7"
}

CUSTOMER_TYPES = {
    "Only domestic": "1.11.1",
    "Mix of domestic and foreign/off-shore": "1.11.2",
    "Only off-shore": "1.11.3"
}
def clean_text(text):
    """Clean and format text by removing HTML tags and normalizing line breaks"""
    if not text:
        return ""
    
    # Remove HTML tags while preserving line breaks
    text = re.sub(r'<br\s*/?>', '\n', text)  # Convert <br> to newlines
    text = re.sub(r'<para>', '', text)        # Remove <para> tags
    text = re.sub(r'</para>', '', text)       # Remove </para> tags
    text = re.sub(r'<[^>]+>', '', text)       # Remove any other HTML tags
    
    # Remove style tags
    text = re.sub(r'<userStyle>.*?</userStyle>', '', text)
    
    # Remove Markdown formatting while preserving structure
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
    text = re.sub(r'_(.*?)_', r'\1', text)        # Underscore
    
    # Improve spacing around punctuation
    text = re.sub(r':(?!\s)', ': ', text)         # Add space after colons
    text = re.sub(r'\s+([.,;!?])', r'\1', text)   # Remove space before punctuation
    text = re.sub(r'([.,;!?])(?!\s)', r'\1 ', text)  # Add space after punctuation
    
    # Handle multiple newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Normalize multiple newlines to double
    text = text.replace('\r\n', '\n')         # Normalize Windows line endings
    
    # Handle bullet points and dashes
    lines = text.split('\n')
    processed_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith(('-', '•', '*')):
            line = '• ' + line[1:].strip()  # Normalize bullet points
        processed_lines.append(line)
    
    text = '\n'.join(processed_lines)
    
    return text.strip()

def process_content(content, styles, elements):
    """Process content with improved handling of lists and formatting"""
    if not content:
        return
    
    # Clean the content first
    content = clean_text(content)
    
    # Split content into sections
    sections = content.split('\n')
    current_paragraph = []
    
    i = 0
    while i < len(sections):
        line = sections[i].strip()
        
        # Skip empty lines
        if not line:
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                elements.append(Paragraph(para_text, styles['content']))
                elements.append(Spacer(1, 0.1*inch))
                current_paragraph = []
            i += 1
            continue
        
        # Handle headings
        if line.startswith('###') and not line.startswith('####'):
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                elements.append(Paragraph(para_text, styles['content']))
                current_paragraph = []
            
            heading_text = line.replace('###', '').strip()
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph(heading_text, styles['subheading']))
            elements.append(Spacer(1, 0.15*inch))
            
        elif line.startswith('####'):
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                elements.append(Paragraph(para_text, styles['content']))
                current_paragraph = []
            
            subheading_text = line.replace('####', '').strip()
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph(subheading_text, styles['subheading']))
            elements.append(Spacer(1, 0.1*inch))
            
        # Handle bullet points
        elif line.startswith('•'):
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                elements.append(Paragraph(para_text, styles['content']))
                current_paragraph = []
            
            bullet_text = line[1:].strip()
            elements.append(Paragraph(bullet_text, styles['bullet']))
            
        # Handle tables
        elif '|' in line:
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                elements.append(Paragraph(para_text, styles['content']))
                current_paragraph = []
            
            # Collect table lines
            table_lines = [line]
            while i + 1 < len(sections) and '|' in sections[i + 1]:
                i += 1
                table_lines.append(sections[i].strip())
            
            # Process table
            if table_lines:
                process_table_content(table_lines, styles, elements)
                
        else:
            # Handle bold text and normal content
            processed_line = line
            if '**' in processed_line:
                processed_line = re.sub(r'\*\*(.*?)\*\*', lambda m: f'<b>{m.group(1)}</b>', processed_line)
            
            current_paragraph.append(processed_line)
        
        i += 1
    
    # Handle any remaining paragraph content
    if current_paragraph:
        para_text = ' '.join(current_paragraph)
        elements.append(Paragraph(para_text, styles['content']))
        elements.append(Spacer(1, 0.1*inch))
def create_formatted_table(table_data, styles):
    """Create a professionally formatted table with consistent styling"""
    # Ensure all rows have the same number of columns
    max_cols = max(len(row) for row in table_data)
    table_data = [row + [''] * (max_cols - len(row)) for row in table_data]
    
    # Calculate dynamic column widths based on content length
    total_width = 6.5 * inch
    col_widths = []
    
    if max_cols > 1:
        # Calculate max content length for each column
        col_lengths = [0] * max_cols
        for row in table_data:
            for i, cell in enumerate(row):
                content_length = len(str(cell))
                col_lengths[i] = max(col_lengths[i], content_length)
                
        # Distribute widths proportionally based on content length
        total_length = sum(col_lengths)
        for length in col_lengths:
            width = max((length / total_length) * total_width, inch)  # Minimum 1 inch
            col_widths.append(width)
            
        # Adjust widths to fit page
        scale = total_width / sum(col_widths)
        col_widths = [w * scale for w in col_widths]
    else:
        col_widths = [total_width]
    
    # Create table with calculated widths
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Define table style commands
    style_commands = [
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E5E7EB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1F2937')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
        ('TOPPADDING', (0, 0), (-1, 0), 15),
        
        # Content styling
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#374151')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 12),
        
        # Grid styling
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2B6CB0')),
        
        # Alignment
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Cell padding
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]
    
    # Apply style commands
    table.setStyle(TableStyle(style_commands))
    
    # Apply word wrapping
    wrapped_data = []
    for i, row in enumerate(table_data):
        wrapped_row = []
        for cell in row:
            if isinstance(cell, (str, int, float)):
                # Use content style for all cells except headers
                style = styles['subheading'] if i == 0 else styles['content']
                wrapped_cell = Paragraph(str(cell), style)
            else:
                wrapped_cell = cell
            wrapped_row.append(wrapped_cell)
        wrapped_data.append(wrapped_row)
    
    # Create final table with wrapped data
    final_table = Table(wrapped_data, colWidths=col_widths, repeatRows=1)
    final_table.setStyle(TableStyle(style_commands))
    
    return final_table

def create_highlight_box(text, styles):
    """Create a highlighted box with improved styling"""
    content = Paragraph(f"• {text}", styles['content'])
    
    table = Table(
        [[content]],
        colWidths=[6*inch],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.white),
            ('BORDER', (0,0), (-1,-1), 1, colors.black),
            ('PADDING', (0,0), (-1,-1), 15),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOX', (0,0), (-1,-1), 2, colors.HexColor('#E2E8F0')),
            ('BOTTOMPADDING', (0,0), (-1,-1), 18),
            ('TOPPADDING', (0,0), (-1,-1), 18),
        ])
    )
    
    return table

def process_table_content(lines, styles, elements):
    """Process table content with improved header handling"""
    table_data = []
    header_processed = False
    
    for line in lines:
        if '-|-' in line:  # Skip separator lines
            continue
            
        cells = [cell.strip() for cell in line.split('|')]
        cells = [cell for cell in cells if cell]
        
        if cells:
            # Handle cells with bold markers
            cells = [re.sub(r'\*\*(.*?)\*\*', r'\1', cell) for cell in cells]
            
            # Create paragraphs with appropriate styles
            if not header_processed:
                cells = [Paragraph(str(cell), styles['subheading']) for cell in cells]
                header_processed = True
            else:
                cells = [Paragraph(str(cell), styles['content']) for cell in cells]
                
            table_data.append(cells)
    
    if table_data:
        elements.append(Spacer(1, 0.2*inch))
        table = create_formatted_table(table_data, styles)
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))
def get_openai_response(prompt, system_content, api_key):
    try:
        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error communicating with OpenAI API: {str(e)}")
        return None
def render_company_info_form():
    st.write("### Company Information")
    with st.form(key="company_info_form"):
        # Contact Information Section
        st.write("#### Contact Information")
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name*")
            mobile_number = st.text_input("Mobile Number*")
        with col2:
            email = st.text_input("Email Address*")
        
        # Basic Information
        st.write("#### Company Details")
        company_name = st.text_input("Company Name*")
        
        # Industry Selection
        selected_industry = st.selectbox(
            "Select your industry*",
            options=list(INDUSTRY_OPTIONS.keys()),
            key="industry_select"
        )
        
        other_industry_details = None
        if selected_industry == "Others":
            other_industry_details = st.text_input("Please specify your industry*")
        
        # Incorporation Status
        st.write("Is your company incorporated in Malaysia with primary business operations based locally?*")
        incorporation_status = st.radio(
            "Select incorporation status",
            ["Yes", "No", "Others"],
            key="incorporation_status"
        )
        
        other_incorporation_details = None
        if incorporation_status == "Others":
            other_incorporation_details = st.text_input("Please specify your incorporation status*")
        
        selected_currency = st.selectbox(
            "Select your primary currency*",
            options=list(CURRENCY_OPTIONS.keys()),
            key="currency_select"
        )
        
        # Financial Information
        profit_range = st.selectbox(
            "Select profit range*",
            options=list(PROFIT_RANGES.keys()),
            key="profit_select"
        )
        
        cashflow_range = st.selectbox(
            "Select cashflow range*",
            options=list(CASHFLOW_RANGES.keys()),
            key="cashflow_select"
        )
        
        debt_equity_ratio = st.selectbox(
            "Select Debt/Equity ratio*",
            options=list(DEBT_EQUITY_RANGES.keys()),
            key="debt_equity_select"
        )
        
        shareholders_funds = st.selectbox(
            "Select shareholder's funds range*",
            options=list(SHAREHOLDERS_FUNDS_RANGES.keys()),
            key="shareholders_funds_select"
        )
        
        staff_strength = st.selectbox(
            "Select staff strength*",
            options=list(STAFF_STRENGTH_RANGES.keys()),
            key="staff_strength_select"
        )
        
        customer_type = st.selectbox(
            "Select customer type*",
            options=list(CUSTOMER_TYPES.keys()),
            key="customer_type_select"
        )
        
        # Text Descriptions
        st.write("Business Description")
        business_model = st.text_area(
            "Describe how your company makes money*",
            max_chars=1000,
            height=100
        )
        
        products_services = st.text_area(
            "Describe your products/services*",
            max_chars=1000,
            height=100
        )
        
        differentiation = st.text_area(
            "Explain how you differentiate your business*",
            max_chars=1000,
            height=100
        )

        submit = st.form_submit_button("Submit Company Information")
        
        if submit:
            # Validation
            required_fields = {
                "Company Name": company_name,
                "Full Name": full_name,
                "Email": email,
                "Mobile Number": mobile_number,
                "Business Model": business_model,
                "Products/Services": products_services,
                "Business Differentiation": differentiation
            }
            
            # Check all required fields
            missing_fields = [field for field, value in required_fields.items() 
                            if not value or not value.strip()]
            
            if missing_fields:
                st.error(f"Please fill in all required fields: {', '.join(missing_fields)}")
                return None
                
            # Validate industry
            if selected_industry == "Others" and not other_industry_details:
                st.error("Please specify your industry details.")
                return None
                
            # Validate incorporation status
            if incorporation_status == "Others" and not other_incorporation_details:
                st.error("Please specify your incorporation status details.")
                return None
                
            # Validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.error("Please enter a valid email address.")
                return None
                
            # Validate phone number
            if not re.match(r"^[+\d][\d\s-]{8,}$", mobile_number):
                st.error("Please enter a valid mobile number.")
                return None
                
            # Validate text lengths
            min_words = 20
            if len(business_model.split()) < min_words:
                st.error(f"Please provide a more detailed business model description (minimum {min_words} words).")
                return None
                
            if len(products_services.split()) < min_words:
                st.error(f"Please provide a more detailed products/services description (minimum {min_words} words).")
                return None
                
            if len(differentiation.split()) < min_words:
                st.error(f"Please provide a more detailed business differentiation (minimum {min_words} words).")
                return None

            # All validations passed, return the data
            return {
                "full_name": full_name,
                "email": email,
                "mobile_number": mobile_number,
                "company_name": company_name,
                "industry": (
                    f"Others: {other_industry_details}" 
                    if selected_industry == "Others" 
                    else selected_industry
                ),
                "industry_code": INDUSTRY_OPTIONS[selected_industry],
                "incorporation_status": (
                    f"Others: {other_incorporation_details}" 
                    if incorporation_status == "Others" 
                    else incorporation_status
                ),
                "primary_currency": selected_currency,
                "currency_code": CURRENCY_OPTIONS[selected_currency],
                "profit_range": profit_range,
                "profit_code": PROFIT_RANGES[profit_range],
                "cashflow_range": cashflow_range,
                "cashflow_code": CASHFLOW_RANGES[cashflow_range],
                "debt_equity_ratio": debt_equity_ratio,
                "debt_equity_code": DEBT_EQUITY_RANGES[debt_equity_ratio],
                "shareholders_funds": shareholders_funds,
                "shareholders_funds_code": SHAREHOLDERS_FUNDS_RANGES[shareholders_funds],
                "staff_strength": staff_strength,
                "staff_strength_code": STAFF_STRENGTH_RANGES[staff_strength],
                "customer_type": customer_type,
                "customer_type_code": CUSTOMER_TYPES[customer_type],
                "business_model": business_model,
                "products_services": products_services,
                "differentiation": differentiation
            }
    return None
def get_company_analysis(company_info, openai_api_key):
    """
    Get comprehensive analysis of company based on provided information with specific sections
    for industry overview, SWOT analysis, financial summary, and business needs.
    """
    prompt = f"""Based on the following detailed company information, provide a comprehensive 1500-word analysis with supporting facts and figures:

    Company Name: {company_info.get('company_name')}
    Industry: {company_info.get('industry')}
    Primary Currency: {company_info.get('primary_currency')}
    Profit Range: {company_info.get('profit_range')}
    Cashflow Range: {company_info.get('cashflow_range')}
    Debt/Equity Ratio: {company_info.get('debt_equity_ratio')}
    Shareholders Funds: {company_info.get('shareholders_funds')}
    Staff Strength: {company_info.get('staff_strength')}
    Customer Type: {company_info.get('customer_type')}
    
    Business Model: {company_info.get('business_model')}
    Products/Services: {company_info.get('products_services')}
    Business Differentiation: {company_info.get('differentiation')}

    Please provide a structured analysis with the following sections:

    1. Company Profile Analysis
    
    2. Industry Overview
    - Provide comprehensive industry analysis with current market size
    - Include key trends and growth rates
    - Detail relevant industry statistics and benchmarks
    - Analyze regulatory environment and compliance requirements
    - Discuss market dynamics and competitive landscape
    
    3. SWOT Analysis
    - Strengths: Internal capabilities and resources
    - Weaknesses: Internal limitations and challenges
    - Opportunities: External factors that could benefit the business
    - Threats: External challenges and risks to consider
    
    4. Financial and Operating Summary
    - Analyze key financial metrics provided
    - Compare against industry benchmarks
    - Evaluate operational efficiency
    - Consider macro-economic factors affecting the business
    - Assess competitive position in the market
    
    3. Business Needs Analysis
    - Identify critical business requirements
    - Analyze growth and expansion needs
    - Evaluate operational improvement requirements
    - Assess resource and capability gaps
    - Recommend priority areas for development

    1..main header comes w summary for that section : 600 words. 
    2. Section header: dedicate and force 2 pages only per section.. means all the sub sections force to 2 pages for that section: 1500 words
    3. *Model Illustration*
    -Create a summary table with a basic explanation based on the above(must be in table format) """

    return get_openai_response(
        prompt,
        "You are a senior business analyst providing comprehensive company analysis with specific focus on industry context, SWOT analysis, financial performance, and business needs assessment.",
        openai_api_key
    )
def business_priority(business_info, openai_api_key):
    """
    Analyze business priorities with expanded analysis, synthesis, examples, 
    and strategic implications in 450 words.
    """
    prompt = f"""Based on the following business priorities:

{business_info}

Please provide a comprehensive 450-word analysis with the following structure:

1. Expanded Analysis 
   - Break down each priority into key components
   - Identify underlying objectives and goals
   - Highlight critical success factors
   - Discuss potential challenges and constraints

2. Synthesis and Organization 
   - Categorize priorities by strategic importance
   - Identify interconnections between different priorities
   - Create a logical framework for implementation
   - Establish priority hierarchy

3. Practical Examples 
   - For each major priority, provide:
     * A specific implementation example
     * Real-world success case
     * Potential adaptation strategies

4. Strategic Implications 
   - Impact on business operations
   - Resource requirements
   - Timeline considerations
   - Risk assessment
   - Success metrics

Include supporting facts and figures throughout the analysis to validate recommendations and insights.
Ensure all sections include supporting facts, figures, and relevant industry statistics where applicable. 
The analysis should be data-driven and provide actionable insights.
Format all numerical examples in plain text with proper spacing no numbering point
*Model Illustration*
-Create a summary table with a basic explanation based on the above(must be in table format)"""

    return get_openai_response(
        prompt,
        "You are a strategic business advisor providing comprehensive priority analysis with practical insights and clear examples.",
        openai_api_key
    )

def get_specific_suggestions(business_info, suggestion_type, openai_api_key):
    prompt = f"""Based on the user's stated business priorities:
{business_info}

Provide a {suggestion_type} analysis with exactly these requirements (Maximum 200 words):

1. Explain how to focus energy and resources on activities that directly support your stated priority - give 3 examples 
2. How to develop a clear plan with measurable milestones to ensure consistent progress toward your goal. Highlight and explain the importance of structured goal-setting in the specific context. 
3. Explain how to delegate tasks that do not align with your priority to maintain focus and efficiency - give examples om how to promote  prioritization and productivity.
4. Explain how to Communicate your priorities clearly to your team to ensure alignment and collective action." Provide examples on how to emphasize the value of shared understanding and collaboration.
5. Explain how to Regularly review your progress and adapt your approach to stay aligned with your desired outcomes." Give examples on how to Advocate for continuous evaluation and flexibility in this situation.

Ensure all sections include supporting facts, figures, and relevant industry statistics where applicable. 
The analysis should be data-driven and provide actionable insights.
Format all numerical examples in plain text with proper spacing no numbering point
*Model Illustration*
-Create a summary table with a basic explanation based on the above(must be in table format)
{business_info}"""

    return get_openai_response(prompt, 
        f"You are a specialized {suggestion_type} consultant responding to specific business priorities.",
        openai_api_key)

def get_company_summary(profile_info, openai_api_key):
    """
    Get a comprehensive summary of the company's funding plans with detailed analysis
    """
    # Extract funding information
    funding_amount = profile_info.get('funding_amount', 'Not specified')
    
    # Convert funding purposes dictionary to readable text
    funding_purposes = []
    if profile_info.get('funding_purposes'):
        for purpose, selected in profile_info['funding_purposes'].items():
            if selected:
                readable_purpose = purpose.replace('_', ' ').title()
                funding_purposes.append(readable_purpose)
    funding_purposes_text = ', '.join(funding_purposes) if funding_purposes else 'Not specified'
    
    # Get other funding details
    other_purpose = profile_info.get('other_purpose', '')
    if other_purpose:
        funding_purposes_text += f", {other_purpose}"
    
    # Convert funding types to readable text
    funding_types = []
    if profile_info.get('funding_types'):
        for ftype, selected in profile_info['funding_types'].items():
            if selected:
                funding_types.append(ftype.title())
    funding_types_text = ', '.join(funding_types) if funding_types else 'Not specified'
    
    other_funding_type = profile_info.get('other_funding_type', '')
    if other_funding_type:
        funding_types_text += f", {other_funding_type}"

    prompt = f"""Based on the following funding information, provide a detailed analysis (maximum 600 words) with supporting facts and figures:

    Funding Amount: {funding_amount}
    Funding Purposes: {funding_purposes_text}
    Funding Types: {funding_types_text}

    Please provide a structured analysis that includes:

    1. Working Planning Requirements Summary:
    - Outline the key planning elements needed to execute the funding strategy
    - Timeline considerations
    - Resource requirements
    
    2. Required Amount vs Purpose Analysis:
    - Detailed breakdown of how the {funding_amount} funding amount aligns with each stated purpose
    - Cost-benefit analysis for each major funding purpose
    - Justification of the funding amount based on industry standards and benchmarks
    
    3. Potential Risks Assessment:
    - Specific risks associated with each funding purpose
    - Risk mitigation strategies
    - Impact assessment of potential risks
    
    4. Benefits and Impact Analysis:
    - Expected ROI for each funding purpose
    - Tangible and intangible benefits
    - Timeline for realizing benefits
    - Impact on business growth and sustainability
    1..main header comes w summary for that section : 600 words. 
    2. Section header: dedicate and force 2 pages only per section.. means all the sub sections force to 2 pages for that section: 1500 words

    *Model Illustration*
    -Create a summary table with a basic explanation based on the above(must be in table format)"""

    return get_openai_response(
        prompt,
        "You are a senior financial analyst providing detailed funding analysis with practical insights and recommendations.",
        openai_api_key
    )
def initialize_session_state():
    if 'show_options' not in st.session_state:
        st.session_state.show_options = False
    if 'show_profile' not in st.session_state:
        st.session_state.show_profile = False
    if 'show_business_priority' not in st.session_state:
        st.session_state.show_business_priority = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

def render_header():
    col1, col2 = st.columns([3, 1])
    with col1:
        if os.path.exists("kldxlogoonly.png"):
            st.image("kldxlogoonly.png", width=100)
    with col2:
        if os.path.exists("finb.jpg"):
            st.image("finb.jpg", width=100)

def render_business_priority_form():
    with st.form(key="business_priority_form"):
        st.markdown("### Business Priorities")
        st.markdown("Please describe your business priorities for the next 6-12 months in detail*")
        
        business_priorities = st.text_area(
            "Enter your business priorities",
            height=200,
            help="Minimum 50 words required for comprehensive analysis"
        )
        
        submit_button = st.form_submit_button("Submit Business Priorities")
        
        if submit_button:
            # Validation
            if not business_priorities or not business_priorities.strip():
                st.error("Please describe your business priorities before proceeding.")
                return None
                
            # Word count validation
            word_count = len(business_priorities.split())
            if word_count < 50:
                st.error("Please provide more detailed business priorities (minimum 50 words required).")
                st.info(f"Current word count: {word_count}")
                return None
                
            # Content validation
            if len(set(business_priorities.split())) < 20:
                st.error("Please provide more diverse content in your business priorities.")
                return None
            
            return business_priorities
    return None
def render_business_options(business_priorities, openai_api_key):
    if 'business_priority_suggestions' not in st.session_state.user_data:
        with st.spinner("Analyzing your business priorities..."):
            suggestions = business_priority(business_priorities, openai_api_key)
            if suggestions:
                st.session_state.user_data['business_priority_suggestions'] = suggestions
    
    if st.session_state.user_data.get('business_priority_suggestions'):
        with st.expander("Business Priority Suggestions", expanded=True):
            st.write("Here are some business priority suggestions based on your input:")
            st.markdown(st.session_state.user_data['business_priority_suggestions'])
    
    st.write("### Business Areas for Analysis")
    st.write("Based on your priorities, select the relevant business areas*")
    
    with st.form(key="business_options_form"):
        selected_options = {}
        cols = st.columns(3)
        
        for idx, (option, description) in enumerate(BUSINESS_OPTIONS.items()):
            col = cols[idx % 3]
            with col:
                with st.expander(f"📊 {option}", expanded=False):
                    st.markdown(f"**{description}**")
                    selected_options[option] = st.checkbox("Select this area", 
                                                         key=f"checkbox_{option}")
        
        submit = st.form_submit_button("💫 Generate Analysis for Selected Areas")
        
        if submit:
            # Validate at least one option selected
            if not any(selected_options.values()):
                st.error("Please select at least one business area before proceeding.")
                return None
            
            # Validate maximum selections (optional)
            selected_count = sum(selected_options.values())
            if selected_count > 5:
                st.error("Please select a maximum of 5 business areas for focused analysis.")
                return None
            
            return selected_options
    return None

def render_business_profile_form():
    st.write("### Business Profile")
    
    with st.form(key="business_profile_form"):
        st.write("#### Funding Requirements")
        funding_amount = st.radio(
            "How much funding do you plan to set aside at present and in the future?*",
            ["<1m", "1 - 5m", ">5 - 10m", ">10 - 30m", ">30 - 50m", ">50m"]
        )
        
        st.write("#### Purpose of Funding")
        st.write("Select at least one purpose for raising funds*")
        purpose_options = {
            "expand_ops": "To expand business operations",
            "new_products": "To launch new products or services",
            "pay_debts": "To pay off existing debts",
            "tech_upgrade": "To invest in technology upgrades",
            "hire_staff": "To hire and train additional staff",
            "new_markets": "To enter new markets",
            "cash_flow": "To improve cash flow and working capital",
            "acquisition": "To acquire another company",
            "marketing": "To enhance marketing and branding efforts",
            "inventory": "To build inventory and manage supply chain demands"
        }
        
        funding_purposes = {}
        for key, label in purpose_options.items():
            funding_purposes[key] = st.checkbox(label)
        
        other_purpose = st.text_input("Other purpose (if any)")
        
        st.write("#### Funding Type")
        st.write("Select at least one funding type*")
        funding_types = {
            "debt": st.checkbox("Debt"),
            "equity": st.checkbox("Equity"),
            "both": st.checkbox("Both")
        }
        
        other_funding_type = st.text_input("Other funding type (if any)")
        
        submit = st.form_submit_button("Submit Business Profile")
        
        if submit:
            # Validate funding purposes
            has_purpose = any(funding_purposes.values()) or other_purpose
            if not has_purpose:
                st.error("Please select at least one funding purpose or specify other purpose.")
                return None
            
            # Validate funding types
            has_type = any(funding_types.values()) or other_funding_type
            if not has_type:
                st.error("Please select at least one funding type or specify other type.")
                return None
            
            # Create profile info
            profile_info = {
                "funding_amount": funding_amount,
                "funding_purposes": funding_purposes,
                "other_purpose": other_purpose,
                "funding_types": funding_types,
                "other_funding_type": other_funding_type
            }
            
            return profile_info
    return None

def process_paragraph(para, styles, elements):
    """Process individual paragraph with formatting"""
    clean_para = clean_text(para)
    if not clean_para:
        return
    
    # Handle bullet points and dashes
    if clean_para.startswith(('•', '-', '*')):
        text = clean_para.lstrip('•-* ').strip()
        elements.append(Paragraph(f"• {text}", styles['bullet']))
    
    # Handle numbered points
    elif re.match(r'^\d+\.?\s+', clean_para):
        text = re.sub(r'^\d+\.?\s+', '', clean_para)
        elements.extend([
            Spacer(1, 0.1*inch),
            create_highlight_box(text, styles),
            Spacer(1, 0.1*inch)
        ])
    
    # Handle scores and metrics
    elif "Overall Score:" in clean_para:
        # Remove asterisks and preserve the score
        text = clean_para.replace('**', '').strip()
        elements.append(Paragraph(text, styles['content']))
    
    # Handle quoted text
    elif clean_para.strip().startswith('"') and clean_para.strip().endswith('"'):
        quote_style = ParagraphStyle(
            'Quote',
            parent=styles['content'],
            fontSize=24,  # Increased from 18 to 24 for bigger text
            leftIndent=20,
            rightIndent=20,
            leading=28,   # Increased leading (line height) to match larger font
            textColor=colors.black  # Added to make text black
        )
        elements.append(Paragraph(clean_para, quote_style))
        elements.append(Spacer(1, 0.1*inch))
    
    else:
        # Normal black text for everything else
        elements.append(Paragraph(clean_para, styles['content']))
        elements.append(Spacer(1, 0.05*inch))

def get_financing_eligibility(company_info, profile_info, openai_api_key):
    """
    Get financing eligibility assessment based on company and profile information
    """
    analysis_info = {
        "company_financials": {
            "profit_range": company_info.get('profit_range'),
            "cashflow_range": company_info.get('cashflow_range'),
            "debt_equity_ratio": company_info.get('debt_equity_ratio'),
            "shareholders_funds": company_info.get('shareholders_funds'),
        },
        "business_profile": {
            "industry": company_info.get('industry'),
            "staff_strength": company_info.get('staff_strength'),
            "customer_type": company_info.get('customer_type'),
            "incorporation_status": company_info.get('incorporation_status'),
        },
        "funding_request": {
            "amount": profile_info.get('funding_amount'),
            "purposes": profile_info.get('funding_purposes', {}),
            "types": profile_info.get('funding_types', {})
        }
    }

    prompt = f"""Generate narrative insights that THE SUBJECT COMPANY HAS MET OR NOT MET THE KLDX CRITERIA

 if the user has met for each of the KLDX criteria set forth or partially or none, and provide a brief explanation 

Explain the eligibility in % terms how much the user fulfills the requirement and provide a narrative explanation in 650   words, with supporting facts, figures

KLDX Criteria

Financing Eligibility Assessment (KLDX)

1. Shareholders' Funds:
The company must maintain shareholders' funds exceeding RM500,000.

2. Incorporation and Operations:
The company must be incorporated in Malaysia with primary business operations based locally.

3. Gearing Ratio:
The company's gearing ratio should be no more than 3x.

4. Operating Cash Flow:
The company must demonstrate a positive operating cash flow.

Based on the financial and business profile provided:
- Shareholders' Funds: {analysis_info['company_financials']['shareholders_funds']}
- Incorporation Status: {analysis_info['business_profile']['incorporation_status']}
- Customer Base: {analysis_info['business_profile']['customer_type']}
- Debt/Equity Ratio: {analysis_info['company_financials']['debt_equity_ratio']}
- Cash Flow Range: {analysis_info['company_financials']['cashflow_range']}

Additionally, where available, assess against these matrices:

| Matrices                | Broad Criteria    |
|------------------------|-------------------|
| Revenue Growth (YoY)    | Above 5%         |
| Operating Profit Margin | Above 20%        |
| EBITDA Margin          | Above 25%        |
| Operating Cash Flows    | Must be positive |
| Shareholder funds      | Must be positive |
| Gearing Ratio          | Below 3x         |
| Net Gearing            | Below 2.5x       |
| Current Ratio          | Above 1x         |
| DSCR                   | Above 1.25x      |
| FCF – to – Net Debt    | Above 20%        |

Eligibility Assessment Criteria for Potential Issuers

1. Shareholders' Funds:
The company must maintain shareholders' funds exceeding RM500,000.

2. Incorporation and Operations:
The company must be incorporated in Malaysia with primary business operations based locally.

3. Gearing Ratio:
The company's gearing ratio should be no more than 3x.

4. Operating Cash Flow:
The company must demonstrate a positive operating cash flow.

Analyze each criterion and provide:
1. Clear evaluation of whether each criterion is met
2. Percentage-based assessment of overall eligibility
3. Detailed explanation supporting the assessment
4. Areas requiring improvement

Format the response with: 
    1..main header comes w summary for that section : 600 words. 
    2. Section header: dedicate and force 2 pages only per section.. means all the sub sections force to 2 pages for that section: 1500 words

    *Model Illustration*
   -Create a summary table with a basic explanation based on the above(must be in table format)"""

    return get_openai_response(
        prompt,
        "You are a senior financial analyst specializing in SME financing eligibility assessment. Provide a detailed, criterion-by-criterion analysis with clear percentage-based assessment.",
        openai_api_key
    )
def get_business_option_summary(selected_areas, suggestions_data, openai_api_key):
    """
    Create a high-level summary of all selected business options and their suggestions.
    
    Args:
        selected_areas (list): List of selected business options
        suggestions_data (dict): Dictionary containing the detailed suggestions for each area
        openai_api_key (str): OpenAI API key for generating the summary
    
    Returns:
        str: A concise summary of all selected areas and key recommendations
    """
    # Create a consolidated view of all selected areas and their suggestions
    consolidated_info = "\n\n".join([
        f"Area: {area}\n"
        f"Description: {BUSINESS_OPTIONS[area]}\n"
        f"Detailed Analysis: {suggestions_data.get(f'{area.lower().replace(' ', '_')}_analysis', 'No analysis available')}"
        for area in selected_areas
    ])
    
    prompt = f"""Based on the following selected business areas and their detailed analyses, 
    provide a concise executive summary:

    {consolidated_info}

    Please provide a summary that includes:
    1. Overview of selected focus areas and their strategic importance
    2. Key synergies between the different areas
    3. Critical success factors across all areas
    4. Top 3-5 immediate action items
    5. Potential challenges and mitigation strategies

    1..main header comes w summary for that section : 600 words. 
    2. Section header: dedicate and force 2 pages only per section.. means all the sub sections force to 2 pages for that section: 1500 words
    3. Dedicate 1 extra page for that section with a summary table of the key points
    That summary table comes with a basic explanation in 200 words"""

    return get_openai_response(
        prompt,
        "You are a strategic business consultant providing executive-level summaries. Focus on practical, actionable insights.",
        openai_api_key
    )
def get_conclusion_analysis(user_data, openai_api_key):
    """
    Generate a comprehensive conclusion analysis based on all previous analyses and user data.
    
    Args:
        user_data (dict): Contains all previous analyses and company information
        openai_api_key (str): OpenAI API key for generating the conclusion
    
    Returns:
        str: A detailed conclusion analysis following the specified format
    """
    # Gather all previous analyses
    analyses = {
        'company_analysis': user_data.get('company_analysis', ''),
        'business_priorities': user_data.get('business_priority_suggestions', ''),
        'executive_summary': user_data.get('executive_summary', ''),
        'company_profile': user_data.get('company_summary', ''),
        'financing_eligibility': user_data.get('financing_eligibility', '')
    }
    
    # Add any specific business area analyses
    selected_areas = user_data.get('selected_areas', [])
    for area in selected_areas:
        key = f"{area.lower().replace(' ', '_')}_analysis"
        if key in user_data:
            analyses[f"area_{area}"] = user_data[key]

    # Create consolidated analysis text
    consolidated_info = "\n\n".join([
        f"{key.replace('_', ' ').title()}:\n{value}"
        for key, value in analyses.items()
        if value
    ])

    prompt = f"""Based on the comprehensive analysis of the business:

{consolidated_info}

Please provide an conclusion that includes:

1. Advisor/Coach Need Analysis:
   Explain 5 compelling reasons why the business needs an advisor/coach to help execute the plan, considering:
   - Current business challenges
   - Growth objectives
   - Implementation complexity
   - Risk management needs
   - Expertise requirements

2. Targeted Solutions:
   List specific ways an advisor/coach can address the business's key pain points and needs, based on:
   - The detailed business analysis provided
   - Industry-specific challenges
   - Growth priorities
   - Operational requirements
   - Financial objectives

3. KPI Timeline Breakdown:
   Define measurable KPIs and objectives across three timeframes:
   
   Short-term (<3 months) put numbering point below:
   - Immediate objectives
   - Quick wins
   - Initial milestones
   
   Medium-term (3-6 months) put numbering point below:
   - Development goals
   - Progress indicators
   - Intermediate achievements
   
   Long-term (6-12 months) put numbering point below:
   - Strategic objectives
   - Growth targets
   - Long-range milestones

    1..main header comes w summary for that section : 600 words. 
    2. Section header: dedicate and force 2 pages only per section.. means all the sub sections force to 2 pages for that section: 1500 words

    *Model Illustration*
   -Create a summary table with a basic explanation based on the above(must be in table format)"""

    return get_openai_response(
        prompt,
        "You are a senior business strategist providing a comprehensive conclusion analysis. Focus on practical, actionable insights with clear timelines and measurable outcomes.",
        openai_api_key
    )
def create_header_footer_disclaimer(canvas, doc):
    """Add header and footer with smaller, transparent images in the top right and a line below the header."""
    canvas.saveState()
    
    # Register Lato fonts if available
    try:
        pdfmetrics.registerFont(TTFont('Lato', 'fonts/Lato-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('Lato-Bold', 'fonts/Lato-Bold.ttf'))
        base_font = 'Lato'
        bold_font = 'Lato-Bold'
    except:
        # Fallback to Helvetica if Lato fonts are not available
        base_font = 'Helvetica'
        bold_font = 'Helvetica-Bold'
    
    if doc.page > 1:
        # Add logos if they exist
        x_start = doc.width + doc.leftMargin - 2.0 * inch
        y_position = doc.height + doc.topMargin - 0.1 * inch
        image_width = 2.0 * inch
        image_height = 0.5 * inch
        
        if os.path.exists("kldxlogo.png"):
            canvas.drawImage(
                "kldxlogo.png", 
                x_start, 
                y_position, 
                width=image_width, 
                height=image_height, 
                mask="auto"
            )
        
        # Add Header Text
        canvas.setFillColor(colors.HexColor('#8B0000'))  # Dark red color
        canvas.rect(doc.leftMargin, 
                   doc.height + doc.topMargin - 0.1*inch,  # Adjusted position
                   doc.width-2.3*inch,
                   0.5*inch,
                   fill=1)

        # Add Header Text
        canvas.setFillColor(colors.white)
        canvas.setFont(bold_font, 27)
        canvas.drawString(doc.leftMargin + 20, 
                         doc.height + doc.topMargin - 0.07*inch,  # Adjusted position
                         "DISCLAIMER")

        # Draw line below the header text
        line_y_position = doc.height + doc.topMargin - 0.30 * inch
        canvas.setLineWidth(0.5)
        canvas.line(doc.leftMargin, line_y_position, doc.width + doc.rightMargin, line_y_position)

        # Footer
        canvas.setFont(base_font, 9)
        canvas.drawString(doc.leftMargin, 0.5 * inch, 
                         f"Generated on {datetime.datetime.now().strftime('%B %d, %Y')}")
        canvas.drawRightString(doc.width + doc.rightMargin, 0.5 * inch, 
                             f"Page {doc.page}")
    
    canvas.restoreState()
def generate_pdf_report(user_data, analyses_data, company_info):
    """
    Generate PDF report for business analysis with enhanced formatting
    
    Args:
        user_data (dict): User's business information and priorities
        analyses_data (dict): All analyses results
        company_info (dict): Company profile information
    """
    buffer = io.BytesIO()
    
    doc = PDFWithTOC(
        buffer,
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=1.5*inch,
        bottomMargin=inch,
        company_name=company_info['name']
    )
    
    # Define frames for different page types
    full_page_frame = Frame(
        0, 0, letter[0], letter[1],
        leftPadding=0, rightPadding=0,
        topPadding=0, bottomPadding=0
    )
    
    normal_frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        id='normal'
    )
    
    # Create page templates
    templates = [
        PageTemplate(id='First', frames=[full_page_frame],
                    onPage=lambda canvas, doc: None),
        PageTemplate(id='Later', frames=[normal_frame],
                    onPage=create_header_footer),
        PageTemplate(id='dis', frames=[normal_frame],
                    onPage=create_header_footer_disclaimer),
    ]
    doc.addPageTemplates(templates)
    
    styles = create_custom_styles()
    elements = []
    
    # Cover page
    elements.append(NextPageTemplate('First'))
    if os.path.exists("kldxfrontnew.png"):
        img = Image("kldxfrontnew.png", width=letter[0], height=letter[1])
        elements.append(img)
    
    # Table of Contents
    elements.append(NextPageTemplate('Later'))
    elements.append(PageBreak())
    elements.append(Paragraph("Table of Contents", styles['heading']))
    
    # Content sections with fixed page numbers
    sections = [
        ("Company Profile Analysis", analyses_data.get('company_analysis')),
        ("KLDX Assessment", analyses_data.get('financing_eligibility')),
        ("Business Priority Analysis", analyses_data.get('business_priority_suggestions')),
        ("Business Priorities", analyses_data.get('executive_summary')),
        ("Financial Profile Analysis", analyses_data.get('company_profile')),
        ("Conclusion", analyses_data.get('conclusion_analysis'))
    ]
    
    # Add TOC entries with dots
    toc_style = ParagraphStyle(
        'TOCEntry',
        parent=styles['normal'],
        fontSize=12,
        leading=20,
        leftIndent=20,
        rightIndent=30,
        spaceBefore=10,
        spaceAfter=10,
        fontName='Helvetica'
    )
    
    def create_toc_entry(num, title, page_num):
        title_with_num = f"{num}. {title}"
        dots = '.' * (50 - len(title_with_num))
        return f"{title_with_num} {dots} {page_num}"

    # Add TOC entries
    for i, (title, _) in enumerate(sections, 1):
        toc_entry = create_toc_entry(i, title, i+2)  # Starting from page 3
        elements.append(Paragraph(toc_entry, toc_style))
    
    elements.append(PageBreak())
    
    # Add company profile page
    elements.extend(create_company_profile_page(styles, company_info))
    elements.append(PageBreak())
    
    # Add main content sections
    for i, (title, content) in enumerate(sections):
        elements.append(Paragraph(title, styles['heading']))
        if content:
            process_content(content, styles, elements)
        # Only add page break if it's not the last section
        if i < len(sections) - 1:
            elements.append(PageBreak())
    
    # Add disclaimer
    elements.append(NextPageTemplate('dis'))
    elements.append(PageBreak())
    create_disclaimer_page(styles, elements)
    
    # Back cover
    elements.append(NextPageTemplate('First'))
    elements.append(PageBreak())
    if os.path.exists("kldxback.jpg"):
        img = Image("kldxback.jpg", width=letter[0], height=letter[1])
        elements.append(img)
    
    # Build the PDF with page numbers
    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            canvas.Canvas.__init__(self, *args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.draw_page_number(num_pages)
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)

        def draw_page_number(self, page_count):
            if hasattr(self, '_pageNumber'):
                page = str(self._pageNumber)
                self.setFont("Helvetica", 9)
                self.drawRightString(
                    7.5*inch,
                    0.5*inch,
                    f"Page {page} of {page_count}"
                )
    
    # Build document with page numbers
    doc.build(elements, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer

def create_custom_styles():
    """Create enhanced custom styles for PDF formatting"""
    base_styles = getSampleStyleSheet()
    
    try:
        pdfmetrics.registerFont(TTFont('Lato', 'fonts/Lato-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('Lato-Bold', 'fonts/Lato-Bold.ttf'))
        base_font = 'Lato'
        bold_font = 'Lato-Bold'
    except:
        base_font = 'Helvetica'
        bold_font = 'Helvetica-Bold'

    styles = {
        'Normal': ParagraphStyle(
            'Normal',
            parent=base_styles['Normal'],
            fontSize=10,
            leading=12,
            fontName=base_font,
            alignment=TA_JUSTIFY
        ),
        'title': ParagraphStyle(
            'CustomTitle',
            parent=base_styles['Normal'],
            fontSize=24,
            textColor=colors.HexColor('#2B6CB0'),
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName=bold_font,
            leading=28.8
        ),
        'heading': ParagraphStyle(
            'CustomHeading',
            parent=base_styles['Normal'],
            fontSize=26,
            textColor=colors.HexColor('#1a1a1a'),
            spaceBefore=20,
            spaceAfter=15,
            fontName=bold_font,
            leading=40.5,
            alignment=TA_JUSTIFY
        ),
        'subheading': ParagraphStyle(
            'CustomSubheading',
            parent=base_styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#4A5568'),
            spaceBefore=15,
            spaceAfter=10,
            fontName=bold_font,
            leading=18.2,
            alignment=TA_JUSTIFY
        ),
        'content': ParagraphStyle(
            'CustomContent',
            parent=base_styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=TA_JUSTIFY,
            spaceBefore=6,
            spaceAfter=6,
            fontName=base_font,
            leading=15.4
        ),
        'bullet': ParagraphStyle(
            'CustomBullet',
            parent=base_styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1a1a1a'),
            leftIndent=20,
            firstLineIndent=0,
            fontName=base_font,
            leading=15.4,
            alignment=TA_JUSTIFY
        )
    }
    
    # Add normal lowercase variant and TOC style
    styles['normal'] = styles['Normal']
    styles['toc'] = ParagraphStyle(
        'TOCEntry',
        parent=styles['normal'],
        fontSize=12,
        leading=20,
        leftIndent=20,
        rightIndent=30,
        spaceBefore=10,
        spaceAfter=10,
        fontName=base_font
    )
    
    return styles
def create_disclaimer_page(styles, elements):
    """Create a single-page disclaimer with specific styling."""
    
    # Register fonts
    try:
        pdfmetrics.registerFont(TTFont('Lato', 'fonts/Lato-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('Lato-Bold', 'fonts/Lato-Bold.ttf'))
        base_font = 'Lato'
        bold_font = 'Lato-Bold'
    except:
        base_font = 'Helvetica'
        bold_font = 'Helvetica-Bold'

    # Define updated styles
    disclaimer_styles = {
        'header': ParagraphStyle(
            'Header',
            parent=styles['normal'],
            fontSize=13,
            fontName=bold_font,
            textColor=colors.HexColor('#4A5568'),  # Dark gray
            leading=14,
            spaceBefore=12.5,
            spaceAfter=7.5,
        ),
        'subheader': ParagraphStyle(
            'SubHeader',
            parent=styles['normal'],
            fontSize=11,
            fontName=bold_font,
            textColor=colors.black,
            leading=12,
            spaceBefore=5.5,
            spaceAfter=2.5,
        ),
        'body_text': ParagraphStyle(
            'BodyText',
            parent=styles['normal'],
            fontSize=9,
            fontName=base_font,
            leading=10,
            spaceBefore=1.5,
            spaceAfter=1.5,
            textColor=colors.black,
        )
    }

    # Add main header
    elements.append(Paragraph("Limitations of AI in Financial and Strategic Evaluations", disclaimer_styles['header']))

    # Add sections
    sections = [
        ("1. Data Dependency and Quality", 
         "AI models rely heavily on the quality and completeness of the data fed into them. The accuracy of the analysis is contingent upon the integrity of the input data. Inaccurate, outdated, or incomplete data can lead to erroneous conclusions and recommendations. Users should ensure that the data used in AI evaluations is accurate and up-to-date."),
        ("2. Algorithmic Bias and Limitations", 
         "AI algorithms are designed based on historical data and predefined models. They may inadvertently incorporate biases present in the data, leading to skewed results. Additionally, AI models might not fully capture the complexity and nuances of human behavior or unexpected market changes, potentially impacting the reliability of the analysis."),
        ("3. Predictive Limitations", 
         "While AI can identify patterns and trends, it cannot predict future events with certainty. Financial markets and business environments are influenced by numerous unpredictable factors such as geopolitical events, economic fluctuations, and technological advancements. AI's predictions are probabilistic and should not be construed as definitive forecasts."),
        ("4. Interpretation of Results", 
         "AI-generated reports and analyses require careful interpretation. The insights provided by AI tools are based on algorithms and statistical models, which may not always align with real-world scenarios. It is essential to involve human expertise in interpreting AI outputs and making informed decisions."),
        ("5. Compliance and Regulatory Considerations", 
         "The use of AI in financial evaluations and business strategy formulation must comply with relevant regulations and standards. Users should be aware of legal and regulatory requirements applicable to AI applications in their jurisdiction and ensure that their use of AI tools aligns with these requirements."),
    ]

    for title, content in sections:
        elements.append(Paragraph(title, disclaimer_styles['subheader']))
        elements.append(Paragraph(content, disclaimer_styles['body_text']))
    
    # Add company disclaimer header
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Kapital DX Sdn Bhd (KLDX), Centre for AI Innovation (CEAI) and Advisory Partners’ Disclaimer", disclaimer_styles['header']))

    disclaimers = [
        ("1. No Guarantee of Accuracy or Completeness", 
         "While Kapital DX Sdn Bhd (KLDX), Centre for AI Innovation (CEAI) and its advisory partners strive to ensure that the AI-generated reports and insights are accurate and reliable, we do not guarantee the completeness or accuracy of the information provided. The insights are based on the data and models used, which may not fully account for all relevant factors or changes in the market."),
        ("2. Not Financial or Professional Advice", 
         "The AI-generated reports and insights are not intended as financial, investment, legal, or professional advice. Users should consult with qualified professionals before making any financial or strategic decisions based on AI-generated reports. Kapital DX Sdn Bhd (KLDX), Centre for AI Innovation (CEAI) and its advisory partners are not responsible for any decisions made based on the reports provided."),
        ("3. Limitation of Liability", 
         "Kapital DX Sdn Bhd (KLDX), Centre for AI Innovation (CEAI) and its advisory partners shall not be liable for any loss or damage arising from the use of AI-generated reports and insights. This includes, but is not limited to, any direct, indirect, incidental, or consequential damages resulting from reliance on the reports or decisions made based on them."),
        ("4. No Endorsement of Third-Party Tools", 
         "The use of third-party tools and data sources in AI evaluations is at the user’s discretion. Kapital DX Sdn Bhd (KLDX), Centre for AI Innovation (CEAI) and its advisory partners do not endorse or guarantee the performance or accuracy of any third-party tools or data sources used in conjunction with the AI-generated reports."),
    ]

    for title, content in disclaimers:
        elements.append(Paragraph(title, disclaimer_styles['subheader']))
        elements.append(Paragraph(content, disclaimer_styles['body_text']))
    
    return elements


class PDFWithTOC(SimpleDocTemplate):
    """Enhanced PDF document class with Table of Contents support and company name"""
    def __init__(self, *args, **kwargs):
        company_name = kwargs.pop('company_name', '')  # Extract company name from kwargs
        SimpleDocTemplate.__init__(self, *args, **kwargs)
        self.company_name = company_name
        self.page_numbers = {}
        self.current_page = 1


def create_company_profile_page(styles, company_info):
    """Create an enhanced company profile page with modern design elements"""
    elements = []
    report_id = str(uuid.uuid4())[:8]
    
    # Reduce top spacing
    elements.append(Spacer(1, 0.5*inch))  # Reduced from 1*inch
    
    # Create a more compact title banner
    title_table = Table(
        [[Paragraph("Company Profile Analysis", styles['heading'])]],
        colWidths=[7*inch],
        style=TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),    # Reduced from 30
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15), # Reduced from 30
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black), # Reduced line thickness
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black), # Reduced line thickness
        ])
    )
    elements.append(title_table)
    
    # Reduce spacing before company info
    elements.append(Spacer(0.5, 0.1*inch))  # Reduced from 0.2*inch
    
    # Create a more compact info table
    company_info_content = [
        [Paragraph("Business Profile", 
                  ParagraphStyle('SubHeading', 
                               parent=styles['subheading'],
                               fontSize=10,      # Reduced font size
                               spaceBefore=6,    # Reduced spacing
                               spaceAfter=6))],  # Reduced spacing
        [Table(
            [
                # Remove duplicate Industry entry and combine related information
                [
                    Paragraph("Company Name", 
                             ParagraphStyle('Label', parent=styles['content'], 
                                          textColor=colors.black, fontSize=10)),
                    Paragraph(str(company_info.get('name', 'N/A')), styles['content'])
                ],
                [
                    Paragraph("Industry",
                             ParagraphStyle('Label', parent=styles['content'], 
                                          textColor=colors.black, fontSize=10)),
                    Paragraph(str(company_info.get('industry', 'N/A')), styles['content'])
                ],
                [
                    Paragraph("Name",
                             ParagraphStyle('Label', parent=styles['content'], 
                                          textColor=colors.black, fontSize=10)),
                    Paragraph(str(company_info.get('full_name', 'N/A')), styles['content'])
                ],
                [
                    Paragraph("Mobile Number",
                             ParagraphStyle('Label', parent=styles['content'], 
                                          textColor=colors.black, fontSize=10)),
                    Paragraph(str(company_info.get('mobile_number', 'N/A')), styles['content'])
                ],
                [
                    Paragraph("Email",
                             ParagraphStyle('Label', parent=styles['content'], 
                                          textColor=colors.black, fontSize=10)),
                    Paragraph(str(company_info.get('email', 'N/A')), styles['content'])
                ],
                [
                    Paragraph("Report Date",
                             ParagraphStyle('Label', parent=styles['content'], 
                                          textColor=colors.black, fontSize=10)),
                    Paragraph(str(company_info.get('date', 'N/A')), styles['content'])
                ],
                [
                    Paragraph("Status / ID",  # Combined Status and Report ID
                             ParagraphStyle('Label', parent=styles['content'], 
                                          textColor=colors.black, fontSize=10)),
                    Paragraph(f"POC | ID: {report_id}", styles['content'])
                ]
            ],
            colWidths=[1.5*inch, 4.5*inch],  # Adjusted column widths
            style=TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),    # Reduced padding
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8), # Reduced padding
                ('LEFTPADDING', (0, 0), (-1, -1), 10),  # Reduced padding
                ('RIGHTPADDING', (0, 0), (-1, -1), 10), # Reduced padding
            ])
        )]
    ]
    
    info_table = Table(
        company_info_content,
        colWidths=[6.5*inch],
        style=TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 15),    # Reduced padding
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15), # Reduced padding
            ('LEFTPADDING', (0, 0), (-1, -1), 20),   # Reduced padding
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),  # Reduced padding
        ])
    )
    elements.append(info_table)
    
    return elements
def create_custom_styles():
    base_styles = getSampleStyleSheet()
    
    try:
        pdfmetrics.registerFont(TTFont('Lato', 'fonts/Lato-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('Lato-Bold', 'fonts/Lato-Bold.ttf'))
        pdfmetrics.registerFont(TTFont('Lato-Italic', 'fonts/Lato-Italic.ttf'))
        pdfmetrics.registerFont(TTFont('Lato-BoldItalic', 'fonts/Lato-BoldItalic.ttf'))
        base_font = 'Lato'
        bold_font = 'Lato-Bold'
    except:
        base_font = 'Helvetica'
        bold_font = 'Helvetica-Bold'

    styles = {
        'Normal': base_styles['Normal'],
        'TOCEntry': ParagraphStyle(
            'TOCEntry',
            parent=base_styles['Normal'],
            fontSize=12,
            leading=16,
            leftIndent=20,
            fontName=base_font,
            alignment=TA_JUSTIFY  # Add this line
        ),
        'title': ParagraphStyle(
            'CustomTitle',
            parent=base_styles['Normal'],
            fontSize=24,
            textColor=colors.HexColor('#2B6CB0'),
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName=bold_font,
            leading=28.8
        ),
        'heading': ParagraphStyle(
            'CustomHeading',
            parent=base_styles['Normal'],
            fontSize=26,
            textColor=colors.HexColor('#1a1a1a'),
            spaceBefore=20,
            spaceAfter=15,
            fontName=bold_font,
            leading=40.5,
            tracking=0,
            alignment=TA_JUSTIFY  # Add this line
        ),
        'subheading': ParagraphStyle(
            'CustomSubheading',
            parent=base_styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#4A5568'),
            spaceBefore=15,
            spaceAfter=10,
            fontName=bold_font,
            leading=18.2,
            alignment=TA_JUSTIFY  # Add this line
        ),
        'normal': ParagraphStyle(
            'CustomNormal',
            parent=base_styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1a1a1a'),
            spaceBefore=6,
            spaceAfter=6,
            fontName=base_font,
            leading=15.4,
            tracking=0,
            alignment=TA_JUSTIFY  # Add this line
        ),
        'content': ParagraphStyle(
            'CustomContent',
            parent=base_styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=TA_JUSTIFY,  # This was already correct
            spaceBefore=6,
            spaceAfter=6,
            fontName=base_font,
            leading=15.4,
            tracking=0
        ),
        'bullet': ParagraphStyle(
            'CustomBullet',
            parent=base_styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1a1a1a'),
            leftIndent=20,
            firstLineIndent=0,
            fontName=base_font,
            leading=15.4,
            tracking=0,
            alignment=TA_JUSTIFY  # Add this line
        )
    }
    
    return styles
def create_header_footer(canvas, doc):
    """Create header and footer for pages with company name"""
    canvas.saveState()
    
    if doc.page > 1:
        # Add logos if they exist
        x_start = doc.width + doc.leftMargin - 2.0 * inch
        y_position = doc.height + doc.topMargin - 0.2 * inch
        image_width = 2.0 * inch
        image_height = 0.5 * inch
        
        if os.path.exists("kldxlogo.png"):
            canvas.drawImage(
                "kldxlogo.png", 
                x_start, 
                y_position, 
                width=image_width, 
                height=image_height, 
                mask="auto"
            )
        
        # Add company name below the report title
        canvas.setFont("Helvetica-Bold", 16)  # Smaller font for company name
        canvas.drawString(
            doc.leftMargin,
            doc.height + doc.topMargin - 0.1*inch,  # Position it below the title
            f"{doc.company_name if hasattr(doc, 'company_name') else ''}"
        )
        
        # Add line below header (adjusted position to account for company name)
        line_y_position = doc.height + doc.topMargin - 0.35 * inch  # Moved down to accommodate company name
        canvas.setLineWidth(0.5)
        canvas.line(
            doc.leftMargin,
            line_y_position,
            doc.width + doc.rightMargin,
            line_y_position
        )
        
        # Add footer
        canvas.setFont("Helvetica", 9)
        canvas.drawString(
            doc.leftMargin,
            0.5 * inch,
            f"Generated on {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        )
    
    canvas.restoreState()


def create_highlight_box(text, styles):
    """Create highlighted box with consistent styling"""
    return Table(
        [[Paragraph(f"• {text}", styles['content'])]],
        colWidths=[6*inch],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
            ('BORDER', (0,0), (-1,-1), 1, colors.HexColor('#90CDF4')),
            ('PADDING', (0,0), (-1,-1), 12),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ])
    )
def calculate_analysis_statistics(user_data):
    """
    Calculate word and token counts for input and output separately.
    
    Args:
        user_data (dict): Dictionary containing all user input and generated analyses
    
    Returns:
        dict: Statistics including word and token counts for inputs and outputs
    """
    statistics = {
        'total_input_words': 0,
        'total_input_tokens': 0,
        'total_output_words': 0,
        'total_output_tokens': 0,
        'input_counts': {},
        'output_counts': {}
    }
    
    # Input fields to analyze
    input_keys = [
        'company_name',
        'industry',
        'business_model',
        'products_services',
        'differentiation',
        'raw_priorities'
    ]
    
    # Output fields to analyze
    output_keys = [
        'company_analysis',
        'business_priority_suggestions',
        'executive_summary',
        'company_summary',
        'financing_eligibility',
        'conclusion_analysis'
    ]
    
    def count_words(text):
        """Count words in text."""
        if not text:
            return 0
        return len([word for word in str(text).split() if word.strip()])
    
    def count_tokens(text):
        """Estimate tokens (words + punctuation)."""
        if not text:
            return 0
        words = count_words(text)
        punctuation = len([char for char in str(text) if char in '.,!?;:()[]{}""\''])
        return words + punctuation
    
    # Calculate input counts
    for key in input_keys:
        if key in user_data and user_data[key]:
            words = count_words(user_data[key])
            tokens = count_tokens(user_data[key])
            statistics['input_counts'][key] = {
                'words': words,
                'tokens': tokens
            }
            statistics['total_input_words'] += words
            statistics['total_input_tokens'] += tokens
    
    # Calculate output counts
    for key in output_keys:
        if key in user_data and user_data[key]:
            words = count_words(user_data[key])
            tokens = count_tokens(user_data[key])
            statistics['output_counts'][key] = {
                'words': words,
                'tokens': tokens
            }
            statistics['total_output_words'] += words
            statistics['total_output_tokens'] += tokens
    
    # Add selected areas analysis if present
    if 'selected_areas' in user_data:
        for area in user_data['selected_areas']:
            key = f"{area.lower().replace(' ', '_')}_analysis"
            if key in user_data and user_data[key]:
                words = count_words(user_data[key])
                tokens = count_tokens(user_data[key])
                statistics['output_counts'][key] = {
                    'words': words,
                    'tokens': tokens
                }
                statistics['total_output_words'] += words
                statistics['total_output_tokens'] += tokens
    
    return statistics
def display_funding_info(data_key, label, user_data):
    """Helper function to display funding information with proper handling of 'Others'"""
    if data_key not in user_data.get('working_capital', {}):
        return "N/A"
        
    value = user_data['working_capital'][data_key]
    
    # Handle dictionary cases (funding purposes and types)
    if isinstance(value, dict):
        selected_items = [k for k, v in value.items() if v]
        
        # Add "Other" option if it exists
        other_key = f"other_{data_key}"
        if other_key in user_data['working_capital'] and user_data['working_capital'][other_key]:
            other_value = user_data['working_capital'][other_key]
            selected_items.append(f"Others: {other_value}")
            
        return "\n".join(f"- {item.replace('_', ' ').title()}" for item in selected_items) if selected_items else "None selected"
    
    return str(value)

def display_value(key, value):
    """Helper function to properly display values including 'Others' cases"""
    # Handle None/empty values
    if value is None:
        return 'N/A'
        
    # Handle "Others:" prefix cases
    if isinstance(value, str):
        if value.startswith("Others:"):
            # Map of fields that can have "Others" values to their corresponding detail fields
            other_details_map = {
                'industry': 'other_industry_details',
                'incorporation_status': 'other_incorporation_details',
                'funding_purposes': 'other_purpose',
                'funding_types': 'other_funding_type'
            }
            
            # If this is a known "Others" field, look up its details
            if isinstance(key, str) and key in other_details_map:
                return st.session_state.user_data.get(other_details_map[key], 'N/A')
            return value.strip()
    
    # Handle dictionary cases (like funding purposes)
    if isinstance(value, dict):
        selected_items = [k for k, v in value.items() if v]
        # Handle "other" fields for dictionaries
        if isinstance(key, str):
            other_key = f"other_{key.lower()}"
            if other_key in st.session_state.user_data and st.session_state.user_data[other_key]:
                selected_items.append(f"Others: {st.session_state.user_data[other_key]}")
        return "\n".join(f"- {item}" for item in selected_items) if selected_items else "None selected"
    
    # Handle list cases
    if isinstance(value, list):
        return "\n".join(f"- {item}" for item in value) if value else "None selected"
    
    # Default case: convert to string
    return str(value)

# Section Configuration
sections = {
    "Company Information": {
        "key": "company_analysis",
        "form_data": {
            "Company Name": "company_name",
            "Industry": "industry",
            "Primary Currency": "primary_currency",
            "Business Model": "business_model",
            "Products/Services": "products_services",
            "Differentiation": "differentiation",
            "Full Name": "full_name",
            "Email": "email",
            "Mobile Number": "mobile_number",
            "Incorporation Status": "incorporation_status"
        },
        "analysis_key": "company_analysis",
        "can_edit": True,
        "edit_step": 0
    },
    "Business Priorities": {
        "key": "raw_priorities",
        "form_data": {
            "Business Priorities": "raw_priorities"
        },
        "analysis_key": "business_priority_suggestions",
        "can_edit": True,
        "edit_step": 1
    },
    "Business Options": {
        "key": "selected_areas",
        "form_data": {
            "Selected Areas": "selected_areas"
        },
        "analysis_key": "executive_summary",
        "can_edit": True,
        "edit_step": 2
    },
    "Business Profile & Financing": {
        "key": "company_summary",
        "form_data": {
            "Funding Amount": ["working_capital", "funding_amount"],
            "Funding Purposes": ["working_capital", "funding_purposes"],
            "Other Purpose": ["working_capital", "other_purpose"],
            "Funding Types": ["working_capital", "funding_types"],
            "Other Funding Type": ["working_capital", "other_funding_type"]
        },
        "analysis_keys": {
            "Company Summary": "company_summary",
            "Financing Eligibility": "financing_eligibility"
        },
        "can_edit": True,
        "edit_step": 3
    },
    "Final Analysis": {
        "key": "conclusion_analysis",
        "analysis_key": "conclusion_analysis",
        "can_edit": False
    }
}
def main():
    initialize_session_state()
    render_header()

    # Initialize step tracking
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0

    # API Key handling
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.", icon="🗝️")
        return
    
    # Step 1: Company Information
    with st.container():
        st.write("## Step 1: Company Information")
        if st.session_state.current_step == 0:
            company_info = render_company_info_form()
            if company_info:
                st.session_state.user_data.update(company_info)
                with st.spinner("Analyzing company information..."):
                    company_analysis = get_company_analysis(company_info, openai_api_key)
                    if company_analysis:
                        st.session_state.user_data['company_analysis'] = company_analysis
                        st.session_state.current_step = 1
                        st.rerun()
        elif "company_analysis" in st.session_state.user_data:
            st.success("✓ Company Information Completed")
            with st.expander("View Company Analysis"):
                st.markdown(st.session_state.user_data['company_analysis'])

    # Step 2: Business Priorities
    if st.session_state.current_step >= 1:
        with st.container():
            st.write("## Step 2: Business Priorities")
            if st.session_state.current_step == 1:
                business_priorities = render_business_priority_form()
                if business_priorities:
                    st.session_state.user_data['raw_priorities'] = business_priorities
                    st.session_state.current_step = 2
                    st.rerun()
            elif "raw_priorities" in st.session_state.user_data:
                st.success("✓ Business Priorities Completed")
                with st.expander("View Business Priorities"):
                    st.markdown(st.session_state.user_data['raw_priorities'])

    # Step 3: Business Options
    if st.session_state.current_step >= 2:
        with st.container():
            st.write("## Step 3: Business Options")
            if st.session_state.current_step == 2:
                selected_options = render_business_options(
                    st.session_state.user_data.get('raw_priorities', ''), 
                    openai_api_key
                )
                if selected_options:
                    selected_areas = [opt for opt, selected in selected_options.items() if selected]
                    if selected_areas:
                        st.session_state.user_data['selected_areas'] = selected_areas
                        analyses = {}
                        for option in selected_areas:
                            suggestion = get_specific_suggestions(
                                st.session_state.user_data.get('raw_priorities', ''),
                                option,
                                openai_api_key
                            )
                            analyses[f"{option.lower().replace(' ', '_')}_analysis"] = suggestion
                        st.session_state.user_data.update(analyses)
                        
                        executive_summary = get_business_option_summary(
                            selected_areas,
                            st.session_state.user_data,
                            openai_api_key
                        )
                        st.session_state.user_data['executive_summary'] = executive_summary
                        st.session_state.current_step = 3
                        st.rerun()
            elif "selected_areas" in st.session_state.user_data:
                st.success("✓ Business Options Completed")
                with st.expander("View Business Options Analysis"):
                    st.markdown(st.session_state.user_data['executive_summary'])
                    for area in st.session_state.user_data['selected_areas']:
                        analysis_key = f"{area.lower().replace(' ', '_')}_analysis"
                        if analysis_key in st.session_state.user_data:
                            st.subheader(area)
                            st.markdown(st.session_state.user_data[analysis_key])

    # Step 4: Business Profile and Financing
    if st.session_state.current_step >= 3:
        with st.container():
            st.write("## Step 4: Business Profile and Financing")
            if st.session_state.current_step == 3:
                profile_info = render_business_profile_form()
                if profile_info:
                    with st.spinner("Analyzing business profile..."):
                        company_summary = get_company_summary(profile_info, openai_api_key)
                        st.session_state.user_data['working_capital'] = profile_info
                        financing_eligibility = get_financing_eligibility(
                            st.session_state.user_data,
                            profile_info,
                            openai_api_key
                        )
                        
                        st.session_state.user_data.update({
                            'company_summary': company_summary,
                            'financing_eligibility': financing_eligibility,
                        })
                        
                        conclusion = get_conclusion_analysis(
                            st.session_state.user_data,
                            openai_api_key
                        )
                        st.session_state.user_data['conclusion_analysis'] = conclusion
                        st.session_state.current_step = 4
                        st.rerun()
            elif "company_summary" in st.session_state.user_data:
                st.success("✓ Business Profile Completed")
                with st.expander("View Profile Analysis"):
                    st.markdown("### Company Summary")
                    st.markdown(st.session_state.user_data['company_summary'])
                    st.markdown("### Financing Eligibility Assessment")
                    st.markdown(st.session_state.user_data['financing_eligibility'])

    # Review and Generate Report
    if st.session_state.current_step == 4:
        st.write("## Review and Generate Report")
        
        # Review sections
        for title, config in sections.items():
            with st.expander(f"Review {title}", expanded=True):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    if config["can_edit"]:
                        if st.button(f"📝 Edit {title}", key=f"edit_{title.lower().replace(' ', '_')}"):
                            st.session_state.current_step = config["edit_step"]
                            st.rerun()
                
                with col2:
                    # Display form data if available
                    if "form_data" in config:
                        st.markdown("### Submitted Data")
                        for label, key in config["form_data"].items():
                            if isinstance(key, list):
                                # Special handling for nested data in working_capital
                                if key[0] == "working_capital":
                                    if title == "Business Profile & Financing":
                                        if label == "Funding Purposes":
                                            purposes = display_funding_info('funding_purposes', label, st.session_state.user_data)
                                            st.markdown(f"**{label}:**")
                                            st.markdown(purposes)
                                        elif label == "Funding Types":
                                            types = display_funding_info('funding_types', label, st.session_state.user_data)
                                            st.markdown(f"**{label}:**")
                                            st.markdown(types)
                                        elif label in ["Other Purpose", "Other Funding Type"]:
                                            other_value = st.session_state.user_data.get(key[0], {}).get(key[1], "")
                                            if other_value:
                                                st.markdown(f"**{label}:** {other_value}")
                                        else:
                                            value = st.session_state.user_data.get(key[0], {}).get(key[1], "N/A")
                                            st.markdown(f"**{label}:** {value}")
                                else:
                                    if key[0] in st.session_state.user_data and key[1] in st.session_state.user_data[key[0]]:
                                        value = st.session_state.user_data[key[0]][key[1]]
                                    else:
                                        value = "N/A"
                                    formatted_value = display_value(key[1], value)
                                    if "\n" in formatted_value:
                                        st.markdown(f"**{label}:**")
                                        st.markdown(formatted_value)
                                    else:
                                        st.markdown(f"**{label}:** {formatted_value}")
                            else:
                                value = st.session_state.user_data.get(key, "N/A")
                                formatted_value = display_value(key, value)
                                if "\n" in formatted_value:
                                    st.markdown(f"**{label}:**")
                                    st.markdown(formatted_value)
                                else:
                                    st.markdown(f"**{label}:** {formatted_value}")
                    
                    # Display analysis
                    st.markdown("### Analysis")
                    if "analysis_key" in config and config["analysis_key"] in st.session_state.user_data:
                        st.markdown(st.session_state.user_data[config["analysis_key"]])
                    
                    # Display multiple analyses if available
                    if "analysis_keys" in config:
                        for label, key in config["analysis_keys"].items():
                            if key in st.session_state.user_data:
                                st.markdown(f"### {label}")
                                st.markdown(st.session_state.user_data[key])

            st.markdown("---")  # Add separator between sections

        # Generate Report Button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.write("## Generate Final Report")
            if st.button("📄 Generate Complete Report", type="primary"):
                try:
                    analyses_data = {
                        'company_analysis': st.session_state.user_data['company_analysis'],
                        'business_priority_suggestions': st.session_state.user_data.get('business_priority_suggestions', ''),
                        'executive_summary': st.session_state.user_data['executive_summary'],
                        'company_profile': st.session_state.user_data['company_summary'],
                        'financing_eligibility': st.session_state.user_data['financing_eligibility'],
                        'conclusion_analysis': st.session_state.user_data['conclusion_analysis']
                    }
                    
                    company_info = {
                        'name': st.session_state.user_data['company_name'],
                        'industry': st.session_state.user_data['industry'],
                        'full_name': st.session_state.user_data['full_name'],
                        'mobile_number': st.session_state.user_data['mobile_number'],
                        'email': st.session_state.user_data['email'],
                        'type': 'Business Analysis Report',
                        'date': datetime.datetime.now().strftime('%B %d, %Y')
                    }
                    
                    with st.spinner("Generating PDF report..."):
                        pdf_buffer = generate_pdf_report(
                            st.session_state.user_data,
                            analyses_data,
                            company_info
                        )
                        
                        if pdf_buffer:
                            st.success("PDF report generated successfully!")
                            st.download_button(
                                "📥 Download Business Analysis Report",
                                data=pdf_buffer,
                                file_name=f"business_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                mime="application/pdf"
                            )
                            
                            with st.spinner("Sending report via email..."):
                                analysis_statistics = calculate_analysis_statistics(st.session_state.user_data)
                                for email in [st.session_state.user_data.get('email'), EMAIL_SENDER]:
                                    send_email_with_attachment(
                                        receiver_email=email,
                                        company_name=st.session_state.user_data['company_name'],
                                        subject="KLDX Analysis Report",
                                        body="KLDX Analysis Report from KLDX Lite GenAI.",
                                        pdf_buffer=pdf_buffer,
                                        statistics=analysis_statistics
                                    )
                        
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
                    print(f"Detailed error: {str(e)}")

if __name__ == "__main__":
    main()