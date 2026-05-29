import pandas as pd
import numpy as np
import os
import re
import src.config as config

def normalize_numbers_in_string(s):
    if not s:
        return ""
    def repl(m):
        try:
            val = float(m.group(0))
            if val.is_integer():
                return str(int(val))
            else:
                return str(val)
        except ValueError:
            return m.group(0)
    return re.sub(r'\b\d+(?:\.\d+)?\b', repl, s)

def clean_value(val):
    """Clean and normalize values for comparison."""
    if pd.isna(val) or val is None:
        return None
    val_str = str(val).strip()
    if val_str.lower() in ['nan', 'none', '']:
        return None
    return val_str

def is_numeric(val):
    try:
        float(val)
        return True
    except (ValueError, TypeError):
        return False

def compare_values(val1, val2):
    """
    Compare two values. Returns True if they are matching.
    Supports robust numeric comparisons and normalized string comparisons.
    """
    c1 = clean_value(val1)
    c2 = clean_value(val2)
    
    if c1 is None and c2 is None:
        return True
    if c1 is None or c2 is None:
        return False
        
    # If both are numeric, compare as floats
    if is_numeric(c1) and is_numeric(c2):
        return abs(float(c1) - float(c2)) < 1e-4
        
    # For string comparisons, clean whitespaces and lowercase
    # Replace standard comma, semicolon or ideographic comma with a standardized comma to allow slight separator mismatch
    norm1 = c1.replace(' ', '').replace('、', ',').replace(';', ',').lower()
    norm2 = c2.replace(' ', '').replace('、', ',').replace(';', ',').lower()
    
    norm1 = normalize_numbers_in_string(norm1)
    norm2 = normalize_numbers_in_string(norm2)
    
    return norm1 == norm2

def run_evaluation(extracted_excel_path, ground_truth_excel_path=None):
    if not ground_truth_excel_path:
        ground_truth_excel_path = config.GROUND_TRUTH_EXCEL
        
    if not os.path.exists(extracted_excel_path):
        print(f"Error: Extracted file {extracted_excel_path} does not exist.")
        return None
    if not os.path.exists(ground_truth_excel_path):
        print(f"Error: Ground truth file {ground_truth_excel_path} does not exist.")
        return None
        
    if extracted_excel_path.lower().endswith('.csv'):
        df_ext = pd.read_csv(extracted_excel_path, encoding='utf-8-sig')
    else:
        df_ext = pd.read_excel(extracted_excel_path)
    df_gt = pd.read_excel(ground_truth_excel_path)
    
    # Columns to evaluate
    eval_cols = [
        "Part Number",
        "Minimum Operating Temperature(°C)",
        "Maximum Operating Temperature (°C)",
        "Maximum Length (mm)",
        "Maximum Width (mm)",
        "Maximum Height (mm)",
        "PIN Number",
        "I_O、I_F (A)",
        "V_F(Forward Voltage) (V)",
        "V_RRM(Peak Repetitive Reverse Voltage) (V)",
        "I_R(Reverse Current) " # Trailing space as in ground truth
    ]
    
    # Ensure columns exist
    for col in eval_cols:
        if col not in df_ext.columns:
            df_ext[col] = None
        if col not in df_gt.columns:
            print(f"Warning: Column '{col}' not found in ground truth Excel.")
            return None

    # We will map records by matching Part Number (ignoring case/whitespace)
    df_ext['join_key'] = df_ext['Part Number'].astype(str).str.strip().str.upper()
    df_gt['join_key'] = df_gt['Part Number'].astype(str).str.strip().str.upper()
    
    correct_counts = {col: 0 for col in eval_cols}
    total_records = len(df_gt)
    
    comparison_details = []
    
    for idx, gt_row in df_gt.iterrows():
        part_no = gt_row['join_key']
        # Find matching row in extracted data
        ext_rows = df_ext[df_ext['join_key'] == part_no]
        
        detail = {"Part Number": gt_row['Part Number'], "Status": "Matched" if not ext_rows.empty else "Missing"}
        
        if ext_rows.empty:
            # If missing, all columns are incorrect
            for col in eval_cols:
                detail[col] = f"MISSING | GT: {gt_row[col]}"
            comparison_details.append(detail)
            continue
            
        ext_row = ext_rows.iloc[0]
        
        for col in eval_cols:
            gt_val = gt_row[col]
            ext_val = ext_row[col]
            
            is_match = compare_values(gt_val, ext_val)
            if is_match:
                correct_counts[col] += 1
                if col == "Part Number":
                    detail[col] = gt_row['Part Number']
                else:
                    detail[col] = "✓"
            else:
                detail[col] = f"✗ (Got: {ext_val} | GT: {gt_val})"
                
        comparison_details.append(detail)
        
    # Calculate accuracy
    accuracy_report = {}
    print("\n================== ACCURACY REPORT ==================")
    print(f"{'Column Name':<45} | {'Correct':<8} | {'Total':<5} | {'Accuracy':<8}")
    print("-" * 75)
    for col in eval_cols:
        correct = correct_counts[col]
        acc = (correct / total_records) * 100
        accuracy_report[col] = acc
        print(f"{col:<45} | {correct:<8} | {total_records:<5} | {acc:.2f}%")
    print("=====================================================")
    
    # Save a detailed comparison log for diagnostics
    df_details = pd.DataFrame(comparison_details)
    diag_path = os.path.join(os.path.dirname(extracted_excel_path), "evaluation_diagnostic.xlsx")
    df_details.to_excel(diag_path, index=False)
    print(f"Detailed comparison diagnostic saved to: {diag_path}")
    
    # Generate detailed Markdown Accuracy & Error Report
    md_lines = []
    md_lines.append("# 規格書參數提取準確率與錯誤分析報告 (Accuracy & Error Report)\n")
    md_lines.append("## 一、 各欄位準確率統計 (Accuracy Statistics)\n")
    md_lines.append("| 欄位名稱 (Column Name) | 正確數 (Correct) | 總件數 (Total) | 準確率 (Accuracy) |")
    md_lines.append("| :--- | :---: | :---: | :---: |")
    for col in eval_cols:
        correct = correct_counts[col]
        acc = (correct / total_records) * 100
        md_lines.append(f"| {col} | {correct} | {total_records} | {acc:.2f}% |")
    
    md_lines.append("\n## 二、 錯誤與不一致詳細列表 (Detailed Error Analysis)\n")
    md_lines.append("以下為所有提取結果與標準答案 (Ground Truth) 存在差異或缺失的詳細列表：\n")
    
    has_errors = False
    for detail in comparison_details:
        part_no = detail["Part Number"]
        status = detail["Status"]
        
        # Collect errors for this part number
        errors_for_part = []
        for col in eval_cols:
            if col == "Part Number":
                continue
            val = detail[col]
            if val != "✓":
                errors_for_part.append((col, val))
                
        if status == "Missing" or errors_for_part:
            has_errors = True
            md_lines.append(f"### 📄 元件: {part_no} ({status})")
            if status == "Missing":
                md_lines.append("- *此元件規格書未出現在提取結果中 (Missing in extracted data)*\n")
            else:
                for col, err_val in errors_for_part:
                    # err_val is like "✗ (Got: ... | GT: ...)" or "MISSING | GT: ..."
                    md_lines.append(f"- **{col}**:")
                    md_lines.append(f"  - {err_val}")
                md_lines.append("")
                
    if not has_errors:
        md_lines.append("🎉 恭喜！所有提取欄位與標準答案完全一致，無任何錯誤！\n")
        
    md_report_path = os.path.join(os.path.dirname(extracted_excel_path), "accuracy_and_errors_report.md")
    with open(md_report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"Detailed Markdown report saved to: {md_report_path}")
    
    return accuracy_report

if __name__ == "__main__":
    # Test run evaluator with the current specbook_output.xlsx if it exists
    out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "specbook_output.xlsx")
    run_evaluation(out_path)
