import fs from 'fs';
import path from 'path';
import sharp from 'sharp';

/**
 * 비동기 썸네일 생성
 * - L1: 배경색(흰색)
 * - L2: 이미지 + 텍스트 오버레이
 * - L3: 붉은 경고 아이콘 (L1과 L2 위)
 */
export const generateThumbnail = async ({
  title,
  subtitle,
  imageUrl,
}: {
  title: string;
  subtitle: string;
  imageUrl: string;
}) => {
  const tmpDir = path.join(process.cwd(), 'tmp');
  if (!fs.existsSync(tmpDir)) fs.mkdirSync(tmpDir);

  const base = await sharp(imageUrl)
    .resize(1280, 720)
    .flatten({ background: '#FFFFFF' })
    .toBuffer();

  const composite = [
    {
      input: Buffer.from(
        `<svg width="1280" height="720">
          <text x="50%" y="200" font-size="80" fill="#1A2B38" text-anchor="middle">${title}</text>
          <text x="50%" y="320" font-size="48" fill="#1A2B38" text-anchor="middle">${subtitle}</text>
        </svg>`
      ),
      top: 0,
      left: 0,
    },
    {
      input: path.resolve(__dirname, '../../assets/icons/alert.svg'),
      top: 50,
      left: 50,
    },
  ];

  const outPath = path.join(tmpDir, `thumb_${Date.now()}.png`);
  await sharp(base).composite(composite).toFile(outPath);
  return outPath;
};