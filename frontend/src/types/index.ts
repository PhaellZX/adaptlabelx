// Geometria de detecção (bbox)
export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

// Geometria de segmentação (polígono)
export type Polygon = [number, number][];

export interface Annotation {
  id: number;
  class_label: string;
  confidence: number;
  annotation_type: 'detection' | 'segmentation';
  // A geometria pode ser uma ou outra
  geometry: BoundingBox | Polygon;
}

export interface Image {
  id: number;
  file_name: string;
  file_path: string;
  annotations: Annotation[];
}

export interface Dataset {
  id: number;
  name: string;
  description: string;
  images: Image[];
}