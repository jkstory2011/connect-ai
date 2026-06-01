import React, { useEffect, useState } from 'react';
import { generateThumbnail } from '../services/thumbnail_generator';
import { ThumbnailProps, LayerConfig } from '../types/thumbnail';

/**
 * L1: Wrapper – 기본 레이아웃, 배경
 * L2: Content – 텍스트/이미지 블록
 * L3: Overlay – 비주얼 강조(색상, 아이콘)
 */
export const ThumbnailGenerator: React.FC<ThumbnailProps> = ({ title, subtitle, imageUrl }) => {
  const [thumbSrc, setThumbSrc] = useState<string | null>(null);

  useEffect(() => {
    const createThumb = async () => {
      try {
        const src = await generateThumbnail({ title, subtitle, imageUrl });
        setThumbSrc(src);
      } catch (e) {
        console.error('Thumbnail generation failed', e);
      }
    };
    createThumb();
  }, [title, subtitle, imageUrl]);

  if (!thumbSrc) return <div className="loader">Generating...</div>;

  return (
    <img src={thumbSrc} alt={`${title} thumbnail`} className="thumbnail-img" />
  );
};