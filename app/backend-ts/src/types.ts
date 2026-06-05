export interface DatasetRecord {
  data: any[];
  columns: string[];
  accessToken: string;
}

export interface AnalyzeRequest {
  dataset_id: string;
  analysis_type: string;
  x?: string;
  y?: string;
  group_by?: string;
  value?: string;
  window?: number;
  aggregation?: string;
}
