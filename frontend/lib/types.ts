/**
 * TypeScript type definitions for KORMARC Frontend
 * Aligned with SPEC-WEB-001 FastAPI backend Pydantic models
 */

// BookInfo input form data
export interface BookInfo {
  isbn: string;           // 13-digit ISBN-13
  title: string;         // Book title
  author: string;        // Author name
  publisher: string;     // Publisher name
  publicationYear: number; // Publication year
  edition?: string;      // Edition statement (optional)
  seriesName?: string;   // Series title (optional)
}

// KORMARC field structure
export interface KORMARCField {
  tag: string;           // MARC field tag (e.g., "040", "245")
  ind1?: string;         // Indicator 1
  ind2?: string;         // Indicator 2
  subfields: Record<string, string>; // Subfield code -> value mapping
}

// Validation result for each tier
export interface TierValidation {
  pass: boolean;
  message: string;
  details?: string[];    // Detailed error/warning messages
}

// Complete validation result
export interface ValidationResult {
  tier1: TierValidation; // Technical validation (format, structure)
  tier2: TierValidation; // Syntax validation (MARC field syntax)
  tier3: TierValidation; // Semantic validation (Nowon-gu 040 field)
  tier4: TierValidation; // Consistency validation (field values)
  tier5: TierValidation; // Institutional rules (additional requirements)
}

// KORMARC record response from API
export interface KORMARCRecord {
  isbn: string;
  json: Record<string, unknown>; // KORMARC JSON format
  xml: string;                   // MARCXML format
  validation: ValidationResult;
}

// API error response
export interface ErrorResponse {
  error: {
    code: string;        // Error code (INVALID_ISBN, etc.)
    message: string;     // User-friendly message
    details?: string;    // Technical details (dev mode only)
  };
}

// API request options
export interface APIOptions {
  timeout?: number;      // Request timeout in milliseconds
  retries?: number;      // Number of retry attempts
}

// Form validation state
export interface FormState {
  isValid: boolean;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
}

// Preview tab type
export type PreviewTab = 'json' | 'xml';

// Component props types
export interface BookInfoFormProps {
  onSubmit: (data: BookInfo) => Promise<void>;
  isLoading?: boolean;
  initialData?: Partial<BookInfo>;
}

export interface ISBNInputProps {
  value: string;
  onChange: (value: string) => void;
  onValidationChange?: (isValid: boolean, message?: string) => void;
  disabled?: boolean;
}

export interface KORMARCPreviewProps {
  kormarc: KORMARCRecord | null;
  isLoading?: boolean;
  activeTab: PreviewTab;
  onTabChange: (tab: PreviewTab) => void;
}

export interface ValidationStatusProps {
  validation: ValidationResult | null;
}

export interface ExportButtonsProps {
  kormarc: KORMARCRecord | null;
}

// Environment variable type
export interface EnvConfig {
  apiBaseUrl: string;
  appVersion: string;
  analyticsId?: string;
}

// Helper type for form field names
export type BookInfoField = keyof BookInfo;

// Validation error type
export interface ValidationError {
  field: BookInfoField;
  message: string;
  code: string;
}

// ISBN validation result
export interface ISBNValidationResult {
  isValid: boolean;
  message: string;
  errorType?: 'length' | 'format' | 'checksum';
}
