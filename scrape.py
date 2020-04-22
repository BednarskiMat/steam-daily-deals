import scrapy
from scrapy.crawler import CrawlerProcess
import os,logging,email, smtplib, ssl, time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class SteamSpider(scrapy.Spider):
    name = "steam_spider"
    start_urls = ['https://store.steampowered.com/specials#tab=TopSellers']
    logging.getLogger('scrapy').propagate = False
    def parse(self, response):
        row_select = '//div[@class="tabarea"]/div[@class="tab_content_ctn sub"]/div[@id="tab_content_TopSellers"]/div[@id="TopSellersTable"]/div[@id="TopSellersRows"]/a'
        for game in response.xpath(row_select):
            name = 'div[@class="tab_item_content"]/div[@class="tab_item_name"]/text()'
            sale_price = 'div[@class="discount_block tab_item_discount"]/div[@class="discount_prices"]/div[@class="discount_original_price"]/text()'
            original_price ='div[@class="discount_block tab_item_discount"]/div[@class="discount_prices"]/div[@class="discount_final_price"]/text()'
            discount_percent ='div[@class="discount_block tab_item_discount"]/div[@class="discount_pct"]/text()'
            yield {
                'name': game.xpath(name).get(),
                'sale_price': game.xpath(sale_price).get(),
                'original_price': game.xpath(original_price).get(),
                'discount_percent': game.xpath(discount_percent).get(),
            }
def sendEmail(file):
    subject = "Daily Steam Sale Update"
    body = "Steam games are attached"
    sender_email = "mbednarski216@gmail.com"
    receiver_email = "bednarskimat@sehs.net"
    password = 'Velocity720'
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    filename = file
    with open(filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

process = CrawlerProcess(settings={
    'FEED_FORMAT': 'csv',
    'FEED_URI': 'games.csv'
})



if os.path.exists('games.csv'):
    os.remove('games.csv')
process.crawl(SteamSpider)
process.start()
sendEmail('./games.csv')
print("Email with games sent!")



