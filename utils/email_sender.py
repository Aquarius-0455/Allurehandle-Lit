# -*- coding:UTF-8 -*-
import glob
import os
import zmail
from utils.logger import logger


class EmailSender:
    """邮件发送工具类"""
    
    def __init__(self, sender_email: str, sender_password: str):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.server = {
            'host': 'smtp.163.com',
            'port': 465,
            'ssl': True,
            'user': sender_email,
            'password': sender_password
        }
    
    def send_report(self, recipients: list, include_locust_report: bool = False):
        """
        发送测试报告邮件
        
        Args:
            recipients: 收件人列表
            include_locust_report: 是否包含Locust报告
        """
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            report_dir = os.path.join(base_dir, 'report')
            
            # 获取最新的报告文件
            report_files = glob.glob(os.path.join(report_dir, 'report_*.html'))
            if not report_files:
                logger.warning("未找到测试报告文件")
                return
            
            latest_report = max(report_files, key=os.path.getctime)
            
            # 准备邮件内容
            mail_content = {
                'subject': f'自动化测试报告 - {os.path.basename(latest_report)}',
                'content_text': '请查看附件中的测试报告',
                'attachments': [latest_report]
            }
            
            # 添加Locust报告
            if include_locust_report:
                locust_files = glob.glob(os.path.join(report_dir, 'locust_report_*.html'))
                if locust_files:
                    latest_locust = max(locust_files, key=os.path.getctime)
                    mail_content['attachments'].append(latest_locust)
            
            # 发送邮件
            zmail.server(**self.server).send_mail(recipients, mail_content)
            logger.info(f"✅ 邮件发送成功: {recipients}")
            
        except Exception as e:
            logger.error(f"❌ 邮件发送失败: {e}")

