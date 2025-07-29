import sgMail from '@sendgrid/mail';

class EmailService {
  async sendVerificationEmail(to: string, code: number) {
    sgMail.setApiKey(process.env.SENDGRID_API_KEY!);
    const msg = {
      to,
      from: 'support@qrent.rent',
      subject: 'Email Verification Code',
      text: `Your email verification code is ${code}`,
      html: `<p>Your email verification code is <strong>${code}</strong></p>`,
    };

    await sgMail.send(msg);
  }
}

export const emailService = new EmailService();
