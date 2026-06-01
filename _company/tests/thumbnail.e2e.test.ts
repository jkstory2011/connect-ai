import path from 'path';
import { generateThumbnail } from '../src/services/thumbnail_generator';
import fs from 'fs';

describe('Thumbnail Generation E2E', () => {
  const testImage = path.join(process.cwd(), 'tests/assets/test.jpg');

  it('should create a PNG file with correct dimensions', async () => {
    const outPath = await generateThumbnail({
      title: 'Test Title',
      subtitle: 'Subtitle',
      imageUrl: testImage,
    });

    expect(fs.existsSync(outPath)).toBeTruthy();

    const metadata = await sharp(outPath).metadata();
    expect(metadata.width).toBe(1280);
    expect(metadata.height).toBe(720);

    // cleanup
    fs.unlinkSync(outPath);
  });

  it('should include overlay icon', async () => {
    const outPath = await generateThumbnail({
      title: 'Icon Test',
      subtitle: '',
      imageUrl: testImage,
    });

    // Basic pixel check near icon position
    const img = await sharp(outPath).raw().toBuffer({ resolveWithObject: true });
    // pixel at (60,60) should not be white (icon present)
    const idx = 3 * ((60 * img.info.width) + 60);
    const pixelNonWhite = !(img.data[idx] === 255 && img.data[idx + 1] === 255 && img.data[idx + 2] === 255);
    expect(pixelNonWhite).toBeTruthy();

    fs.unlinkSync(outPath);
  });
});