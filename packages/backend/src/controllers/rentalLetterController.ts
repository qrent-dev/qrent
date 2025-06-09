import { Request, Response } from 'express';
import axios from 'axios';

function buildUserPrompt(data: any): string {
  const { basicInfo, livingPlan, education, rentalHistory, financialSupport, roommates, lifestyle, attachments } = data;

  const lines: string[] = [];

  // 1. Basic Info
  lines.push(`Name: ${basicInfo.name}`);
  if (basicInfo.age) lines.push(`Age: ${basicInfo.age}`);
  if (basicInfo.nationality) lines.push(`Nationality: ${basicInfo.nationality}`);
  if (basicInfo.occupation) lines.push(`Occupation: ${basicInfo.occupation}`);
  if (basicInfo.background) lines.push(`Background: ${basicInfo.background}`);
  if (basicInfo.contact) {
    lines.push(`Contact: ${basicInfo.contact.email || basicInfo.contact.phone}`);
  }

  // 2. Rental Plan
  lines.push(`Rental intention: Looking to rent starting ${livingPlan.startDate} for ${livingPlan.durationMonths} months.`);
  lines.push(`Preferred budget: AUD ${livingPlan.budgetAUD}/week`);
  if (livingPlan.locationPreference) lines.push(`Preferred location: ${livingPlan.locationPreference}`);

  // 3. Education
  if (education) {
    lines.push(`Education: Studying ${education.program} at ${education.institution}.`);
    if (education.durationYears) lines.push(`Program length: ${education.durationYears} years`);
    if (education.visaType) lines.push(`Visa type: ${education.visaType}`);
  }

  // 4. Rental History
  if (rentalHistory && rentalHistory.length > 0) {
    lines.push(`Previous rental history:`);
    rentalHistory.forEach((r: any, i: number) => {
      lines.push(`- ${i + 1}. ${r.address} (${r.duration})`);
    });
  }

  // 5. Financials
  if (financialSupport) {
    lines.push(`Financial support: ${financialSupport.type}, approx. AUD ${financialSupport.amountAUD}.`);
    if (financialSupport.details) lines.push(`Details: ${financialSupport.details}`);
  }

  // 6. Roommates
  if (roommates && roommates.length > 0) {
    lines.push(`Roommates:`);
    roommates.forEach((r: any, i: number) => {
      lines.push(`- ${r.name}, ${r.relationship}${r.occupation ? `, ${r.occupation}` : ''}`);
    });
  }

  // 7. Lifestyle
  if (lifestyle) {
    lines.push(`Lifestyle & maintenance habits: ${lifestyle}`);
  }

  // 8. Attachments
  if (attachments && attachments.length > 0) {
    lines.push(`Supporting documents: ${attachments.join(', ')}`);
  }

  return lines.join('\n');
}

const DEEPSEEK_API_KEY = process.env.DEEPSEEK_API_KEY;
console.log("🔑 DeepSeek API Key loaded:", DEEPSEEK_API_KEY);
const DEEPSEEK_URL = 'https://api.deepseek.com/chat/completions';

const SYSTEM_PROMPT = `
你是一名专业的中英双语租房申请信生成器，专为在澳留学的中国学生撰写个性化的租房自我介绍信（Cover Letter）。请根据用户提供的信息，生成一份【中文版本】和一份【英文版本】的申请信，分别展示。
注意：此信是留学生已经找好房源后，向房东或中介发送的正式申请信。内容应该围绕学生各方面条件为何适合租住该房源。应在开头明确标注目标房源地址或名称
请确保内容真实可信、语气礼貌专业、逻辑清晰自然，符合澳洲文化语境，便于直接发送给房东或中介。500字左右。结构如下：

---

内容结构要求（中英双语分开生成）：
1. 申请人基本信息（姓名、年龄、国籍、职业、学习背景）
2. 租房计划（计划入住时间、租期、每周预算、意向房源）
3. 教育背景（学校名称、专业、学制、签证类别）
4. 居住历史（如无澳洲租房经历，可选择性省略或写国内住址）
5. 财务支持情况（父母资助、银行存款、金额、存款证明等）
6. 合租人信息（如有，介绍关系、背景、是否也是学生）
7. 生活习惯（作息规律、安静整洁、不吸烟、不办派对等）
8. 附加材料（如签证、COE、存款证明、父母担保函等）
9. 租赁意愿（如希望签几个月，是否可预付房租等）

---

风格语气要求：
- 避免模板化、内容空洞的表述
- 强调责任心、稳定性、支付能力和良好生活习惯
- 保持正式但亲切的语气，适用于发给房东或中介
- 中文版本用地道中文表达，英文版本符合英文书信规范
- 结尾应提醒读者发送者愿意随时提交额外材料，以及提供联系方式以便进一步沟通

---

禁止事项：
- 不要生成虚假信息，只使用用户提供的数据
- 如某些字段为空，请优雅地略去或合理衔接
- 不要出现AI字样，（例如“我是AI助手”，不常用的文字或符号,加粗字体或数字等）

返回格式如下：
【中文信件】
...（中文内容）

【English Letter】
...（English content）
`;

export const generateRentalLetter = async (req: Request, res: Response) => {
  try {
    const data = req.body;
    const requiredFields = ['basicInfo', 'livingPlan'];

    for (const field of requiredFields) {
      if (!data[field]) {
        return res.status(400).json({ error: `Missing ${field} in request` });
      }
    }

    const user_prompt = buildUserPrompt(data);

    const headers = {
      Authorization: `Bearer ${DEEPSEEK_API_KEY}`,
      'Content-Type': 'application/json',
    };

    const payload = {
      model: 'deepseek-chat',
      messages: [
        { role: 'system', content: SYSTEM_PROMPT },
        { role: 'user', content: user_prompt },
      ],
      temperature: 0.3,
      max_tokens: 5000,
    };

    const response = await axios.post(DEEPSEEK_URL, payload, { headers, timeout: 120000 });

    const content = response.data.choices[0].message.content;
    const processed = content.replace(/(AUD \d+)/g, '**$1**');

    return res.json({ success: true, letter: processed, usage: response.data.usage || {} });
  } catch (err: any) {
    if (err.code === 'ECONNABORTED') {
      return res.status(504).json({ success: false, error: '请求超时，请稍后重试' });
    }
    return res.status(500).json({ success: false, error: err.message });
  }
};