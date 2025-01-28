interface GuidelineDetail {
    index: number;
    errorCode: string;
    error: string;
    fix: string;
    reference: string;
    level: string;
    description: string;
}

export class Analysis {
    total_initial_severity_score: number = 0;
    total_final_severity_score: number = 0;
    total_improvement: number = 0;
    corrected_html: string = '';
    csv_file_path: GuidelineDetail[] = [];
}