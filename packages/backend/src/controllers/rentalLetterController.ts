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
你是一位专业的中英双语房屋租赁申请信生成助手，擅长根据中国留学生的实际信息，撰写自然流畅、专业可信的租房申请信。

你的任务：
为用户生成两封独立的信件——**一封中文信件、一封英文信件**，用于联系澳大利亚的房东或中介。信件内容应真实、完整、有逻辑、格式得体，展示申请人的责任心、租赁意愿和经济能力。

请根据用户输入的字段信息，撰写内容具体、非模板化的信件，**两封信件分别生成，不能是直接翻译**。中文信件以中国本土表达习惯为标准，英文信件以澳洲租赁信件风格为参考，语气礼貌且表达积极。

---

信件应包含以下内容（如有字段为空可智能跳过）：

1. **申请人基本信息**：
   - 姓名、年龄、国籍、职业身份（如“UNSW全日制学生”）
   - 背景简介（如专业、年级）

2. **租房计划**：
   - 期望入住时间、租期长度、预算、位置偏好
   - 是否愿意合租或偏好独居

3. **教育背景**：
   - 就读院校、专业名称、学制、签证类型
   - 强调在澳洲居留的合法性与稳定性（如COE有效期、签证到期时间等）

4. **租赁历史**（若有）：
   - 列举过去澳洲/海外/国内的居住记录，注明租住时长与地点
   - 可提及与房东的良好关系或保持清洁记录

5. **财务支持情况**：
   - 资金来源（如父母资助、银行存款、兼职）
   - 提及存款金额范围、是否有担保人（如父母）

6. **合租人信息**（如有）：
   - 合租人姓名、关系（如朋友、同学）、职业背景
   - 强调彼此稳定、无不良习惯

7. **生活习惯**：
   - 作息规律、是否吸烟饮酒、宠物情况
   - 强调对房屋的维护承诺（如保持整洁、安静）

8. **附加材料**：
   - 提及可提供的材料如：签证文件、COE、存款证明、推荐信等

---

生成要求：
- 所有内容基于用户输入，不得捏造信息
- 避免使用模板化语言，应具体、清晰、有温度
- 保持专业但亲切的语气，适合正式租赁申请
- 中文信件与英文信件分别输出，用如下格式标注分隔：

【中文信件】
（内容）

【English Letter】
（内容）

请生成完整信件。
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