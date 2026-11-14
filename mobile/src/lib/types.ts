// Shapes of the JSON the backend returns. Keep in step with backend/app/schemas.py.

export type Category = 'paper' | 'plastic' | 'metal' | 'organic';

export type Detection = {
  id: number;
  category: Category;
  confidence: number;
  low_confidence: boolean;
  /** [x1, y1, x2, y2] in pixels of the upright image. */
  bbox: [number, number, number, number];
};

export type DetectResponse = {
  success: boolean;
  image_width: number;
  image_height: number;
  total_objects: number;
  counts: Record<Category, number>;
  detections: Detection[];
  message: string | null;
};

export type Guidance = {
  category: Category;
  bin: string;
  tips: string[];
  disclaimer: string;
};

/** The photo the user picked, as the image picker describes it. */
export type Photo = {
  uri: string;
  mimeType?: string;
  fileName?: string | null;
  /** Only set on web. */
  file?: File;
};

export type ScanResult = {
  photo: Photo;
  response: DetectResponse;
  guidance: Guidance[];
};
