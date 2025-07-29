import sgMail from '@sendgrid/mail';

class EmailService {
  async sendVerificationEmail(to: string, code: number) {
    sgMail.setApiKey(process.env.SENDGRID_API_KEY!);
    const msg = {
      to,
      from: 'support@qrent.rent',
      subject: 'Email Verification Code',
      text: `Your email verification code is ${code}. This code will expire in 30 minutes.`,
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eaeaea; border-radius: 5px;">
          <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color: #333;">Email Verification</h2>
          </div>
          <div style="padding: 20px; background-color: #f9f9f9; border-radius: 5px;">
            <p style="margin-bottom: 15px;">Hello,</p>
            <p style="margin-bottom: 15px;">Thank you for registering with Qrent. To verify your email address, please use the verification code below:</p>
            <div style="text-align: center; margin: 30px 0;">
              <span style="font-size: 24px; font-weight: bold; padding: 10px 20px; background-color: #f0f0f0; border-radius: 5px;">${code}</span>
            </div>
            <p style="margin-bottom: 15px;"><strong>This code will expire in 30 minutes.</strong></p>
            <p style="margin-bottom: 15px;">If you did not request this verification, please ignore this email.</p>
          </div>
          <div style="margin-top: 20px; text-align: center; color: #666; font-size: 12px;">
            <p>© ${new Date().getFullYear()} Qrent. All rights reserved.</p>
          </div>
        </div>
      `,
    };

    await sgMail.send(msg);
  }
}

export const emailService = new EmailService();
